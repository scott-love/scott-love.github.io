#!/usr/bin/env python3

import json
import time
from pathlib import Path

import requests
import yaml

import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

PROFILE_FILE = ROOT / "data" / "profile.yml"
OUTPUT_FILE = ROOT / "data" / "publications.json"

API_URL = "https://api.archives-ouvertes.fr/search/"
REQUEST_TIMEOUT_SECONDS = 60
MAX_FETCH_ATTEMPTS = 3
BACKOFF_BASE_SECONDS = 1


# 2) Expand FIELDS list (replace current FIELDS with this version)
FIELDS = [
    # Identifiers
    "docid",
    "halId_s",
    "uri_s",
    # General bibliographic information
    "docType_s",
    "title_s",
    "authFullName_s",

    # Date fields (richer precision)
    "producedDateY_i",
    "producedDateM_i",
    "producedDateD_i",
    "producedDate_tdate",
    "publicationDateY_i",
    "publicationDateM_i",
    "publicationDateD_i",
    "publicationDate_tdate",
    "submittedDate_tdate",
    "releasedDate_tdate",

    # Journal information
    "journalTitle_s",
    "doiId_s",

    # Conference information
    "conferenceTitle_s",
    "conferenceStartDate_s",
    "conferenceEndDate_s",
    "conferenceOrganizer_s",
    "city_s",
    "country_s",
    "publisherLink_s",

    # Conference characteristics
    "invitedCommunication_s",
    "peerReviewing_s",
    "audience_s",
    "proceedings_s",

    # Other potentially useful bibliographic information
    "source_s",
    "volume_s",
    "issue_s",
    "page_s",
    "publisher_s",
    "serie_s",

    # Book chapter/container metadata (if available)
    "bookTitle_s",
    "editorFullName_s",

    # Abstract candidates (HAL index can vary naming)
    "abstract_s",
    "abstract_t",
    "en_abstract_s",
    "fr_abstract_s",

    # Fallback source for abstract extraction
    "label_xml",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# 3) Add helpers (place in Helpers section)

HAL_TEI_NS = {"tei": "http://www.tei-c.org/ns/1.0"}


def _to_int(value):
    try:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _iso_date_from_parts(year, month=None, day=None):
    y = _to_int(year)
    if not y or y < 1 or y > 9999:
        return None

    m = _to_int(month)
    d = _to_int(day)

    # HAL sometimes uses 0 for unknown month/day
    if not m or m < 1 or m > 12:
        m = 1
    if not d or d < 1 or d > 31:
        d = 1

    try:
        return f"{y:04d}-{m:02d}-{d:02d}T00:00:00Z"
    except ValueError:
        return None


def _strip_xml_text(value):
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", str(value)).strip()
    return cleaned or None


def _extract_abstract_from_label_xml(label_xml, preferred_langs=("en", "fr")):
    if not label_xml:
        return None

    try:
        root = ET.fromstring(label_xml)
    except ET.ParseError:
        return None

    # HAL TEI usually has abstract/p blocks with xml:lang
    abstracts = root.findall(".//tei:abstract", HAL_TEI_NS)
    if not abstracts:
        return None

    xml_lang_attr = "{http://www.w3.org/XML/1998/namespace}lang"

    # Pass 1: preferred language
    for lang in preferred_langs:
        for node in abstracts:
            if (node.get(xml_lang_attr) or "").lower() == lang.lower():
                text = " ".join(node.itertext())
                text = _strip_xml_text(text)
                if text:
                    return text

    # Pass 2: first non-empty abstract
    for node in abstracts:
        text = " ".join(node.itertext())
        text = _strip_xml_text(text)
        if text:
            return text

    return None


def _pick_abstract(doc):
    # prefer explicit indexed fields first
    for key in ("en_abstract_s", "abstract_s", "fr_abstract_s", "abstract_t"):
        value = first_value(doc.get(key))
        value = _strip_xml_text(value)
        if value:
            return value

    # fallback to TEI payload
    return _extract_abstract_from_label_xml(doc.get("label_xml"))

def first_value(value):
    """Return the first value if HAL provides a list."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def clean_authors(authors):
    """Return a clean list of author names."""
    if not authors:
        return []

    if isinstance(authors, str):
        return [authors]

    return authors


def is_peer_reviewed(value):
    """Return True when HAL marks the record as peer-reviewed."""
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes"}


def classify_document(
    doc_type,
    invited,
    peer_reviewed,
    *,
    doi=None,
    journal=None,
    conference=None,
    book_title=None,
):
    """
    Map HAL document types onto CV categories.

    For COMM records, use HAL's invitedCommunication_s field to
    distinguish invited talks from ordinary oral presentations.
    """

    if doc_type == "ART":
        category = "Journal article" if is_peer_reviewed(peer_reviewed) else "Other scientific contribution"
        return {
            "category": category,
            "presentation_type": None,
        }

    if doc_type == "COUV":
        return {
            "category": "Book chapter",
            "presentation_type": None,
        }

    if doc_type == "COMM":
        if invited == "1":
            presentation_type = "Invited talk"
        elif invited == "0":
            presentation_type = "Oral presentation"
        else:
            presentation_type = "Oral presentation"

        return {
            "category": "Conference presentation",
            "presentation_type": presentation_type,
        }

    if doc_type == "POSTER":
        return {
            "category": "Conference presentation",
            "presentation_type": "Poster",
        }

    if doc_type == "REPORT":
        return None

    if doc_type == "PREPRINT":
        return {
            "category": "Preprint",
            "presentation_type": None,
        }

    if doc_type == "UNDEFINED":
        doi_value = str(doi or "").strip().lower()
        has_structured_venue = any(
            str(value or "").strip()
            for value in (journal, conference, book_title)
        )
        if doi_value.startswith("10.5281/zenodo.") and not has_structured_venue:
            return {
                "category": "Preprint",
                "presentation_type": None,
            }

    return {
        "category": "Other scientific contribution",
        "presentation_type": None,
    }


def load_idhal(profile_file):
    with open(profile_file, encoding="utf-8") as f:
        profile = yaml.safe_load(f) or {}
    return profile["hal"]


def is_retryable_error(error):
    if isinstance(
        error,
        (requests.exceptions.Timeout, requests.exceptions.ConnectionError),
    ):
        return True

    if isinstance(error, requests.exceptions.HTTPError):
        response = error.response
        if response is not None and 500 <= response.status_code < 600:
            return True

    return False


def fetch_hal_records(idhal, *, get=requests.get, sleep=time.sleep):
    params = {
        "q": f"authIdHal_s:{idhal}",
        "rows": 1000,
        "sort": "producedDateY_i desc",
        "wt": "json",
        "fl": ",".join(FIELDS),
    }

    print(f"Querying HAL for idHAL '{idhal}'...")

    last_error = None
    for attempt in range(1, MAX_FETCH_ATTEMPTS + 1):
        try:
            response = get(
                API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            result = response.json()["response"]
            docs = result["docs"]
            total = result["numFound"]
            print(f"HAL reports {total} records.")
            return docs, total
        except requests.exceptions.RequestException as error:
            last_error = error
            retryable = is_retryable_error(error)
            if not retryable or attempt == MAX_FETCH_ATTEMPTS:
                break
            backoff_seconds = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
            print(
                f"Warning: HAL fetch attempt {attempt}/{MAX_FETCH_ATTEMPTS} failed "
                f"({error.__class__.__name__}: {error}). "
                f"Retrying in {backoff_seconds} second(s)..."
            )
            sleep(backoff_seconds)
        except (ValueError, KeyError, TypeError) as error:
            last_error = error
            break

    raise RuntimeError(
        f"HAL fetch failed after {MAX_FETCH_ATTEMPTS} attempt(s): {last_error}"
    ) from last_error


def cache_is_readable(output_file):
    if not output_file.exists():
        return False

    try:
        with open(output_file, encoding="utf-8") as f:
            json.load(f)
    except (OSError, json.JSONDecodeError) as error:
        print(
            f"Error: local publications cache exists but cannot be read: "
            f"{output_file} ({error})"
        )
        return False

    return True


def main(
    *,
    get=requests.get,
    sleep=time.sleep,
    output_file=OUTPUT_FILE,
    profile_file=PROFILE_FILE,
):
    idhal = load_idhal(profile_file)

    try:
        docs, total = fetch_hal_records(idhal, get=get, sleep=sleep)
    except RuntimeError as error:
        if cache_is_readable(output_file):
            print(f"Warning: {error}. Using existing local publications cache at {output_file}.")
            return 0

        print(
            f"Error: {error}. No readable local publications cache found at "
            f"{output_file}. Run this command again when HAL is reachable."
        )
        return 1

    if total > 1000:
        raise RuntimeError(
            f"HAL returned {total} records, which exceeds the current "
            "1000-record limit. Pagination needs to be implemented."
        )

    publications = []
    for doc in docs:
            hal_id = first_value(doc.get("halId_s"))
            doc_type = first_value(doc.get("docType_s"))
            invited = first_value(doc.get("invitedCommunication_s"))
            peer_reviewed = first_value(doc.get("peerReviewing_s"))
            classification = classify_document(
                doc_type,
                invited,
                peer_reviewed,
                doi=first_value(doc.get("doiId_s")),
                journal=first_value(doc.get("journalTitle_s")),
                conference=first_value(doc.get("conferenceTitle_s")),
                book_title=first_value(doc.get("bookTitle_s")),
            )
            if classification is None:
                continue
            publication = {
                # ---------------------------------------------------------------
                # Identifiers
                # ---------------------------------------------------------------
                "hal_id": hal_id,
                "docid": doc.get("docid"),
                "hal_url": first_value(doc.get("uri_s")),
                # ---------------------------------------------------------------
                # General bibliographic information
                # ---------------------------------------------------------------
                "title": first_value(doc.get("title_s")),
                "authors": clean_authors(doc.get("authFullName_s")),
                "year": doc.get("producedDateY_i"),

                # NEW: richer date precision fields
                "publication_date": (
                    first_value(doc.get("publicationDate_tdate"))
                    or first_value(doc.get("producedDate_tdate"))
                    or first_value(doc.get("releasedDate_tdate"))
                    or first_value(doc.get("submittedDate_tdate"))
                ),
                "year_month_day": (
                    _iso_date_from_parts(
                        first_value(doc.get("publicationDateY_i")),
                        first_value(doc.get("publicationDateM_i")),
                        first_value(doc.get("publicationDateD_i")),
                    )
                    or _iso_date_from_parts(
                        first_value(doc.get("producedDateY_i")),
                        first_value(doc.get("producedDateM_i")),
                        first_value(doc.get("producedDateD_i")),
                    )
                ),

                # NEW: HAL abstract extraction
                "abstract": _pick_abstract(doc),

                # ---------------------------------------------------------------
                # HAL classification
                # ---------------------------------------------------------------
                "hal_type": doc_type,
                "category": classification["category"],
                "presentation_type": classification["presentation_type"],
                # ---------------------------------------------------------------
                # Journal information
                # ---------------------------------------------------------------
                "journal": first_value(doc.get("journalTitle_s")),
                "doi": first_value(doc.get("doiId_s")),
                # ---------------------------------------------------------------
                # Conference information
                # ---------------------------------------------------------------
                "conference": first_value(doc.get("conferenceTitle_s")),
                "conference_start": first_value(doc.get("conferenceStartDate_s")),
                "conference_end": first_value(doc.get("conferenceEndDate_s")),
                "conference_organizer": first_value(doc.get("conferenceOrganizer_s")),
                "city": first_value(doc.get("city_s")),
                "country": first_value(doc.get("country_s")),
                "conference_url": first_value(doc.get("publisherLink_s")),
                # ---------------------------------------------------------------
                # Conference characteristics
                # ---------------------------------------------------------------
                "invited": invited,
                "peer_reviewed": peer_reviewed,
                "audience": first_value(doc.get("audience_s")),
                "proceedings": first_value(doc.get("proceedings_s")),
                # ---------------------------------------------------------------
                # Additional bibliographic information
                # ---------------------------------------------------------------
                "source": first_value(doc.get("source_s")),
                "volume": first_value(doc.get("volume_s")),
                "issue": first_value(doc.get("issue_s")),
                "pages": first_value(doc.get("page_s")),
                "publisher": first_value(doc.get("publisher_s")),
                "series": first_value(doc.get("serie_s")),
                # ---------------------------------------------------------------
                # Book chapter metadata
                # ---------------------------------------------------------------
                "book_title": first_value(doc.get("bookTitle_s")),
                "editors": clean_authors(doc.get("editorFullName_s")),
            }

            publications.append(publication)

    publications.sort(
        key=lambda p: (
            p["year"] or 0,
            p["hal_id"] or "",
        ),
        reverse=True,
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            publications,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Saved {len(publications)} publications to {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
