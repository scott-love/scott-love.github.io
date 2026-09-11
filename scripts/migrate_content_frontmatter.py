#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import os
import re
import shutil
import sys
import tomllib
from collections import OrderedDict
from datetime import date, datetime, timezone
from pathlib import Path

import yaml


LEGACY_LINK_FIELDS = OrderedDict(
    [
        ("external_link", "site"),
        ("url_pdf", "pdf"),
        ("url_code", "code"),
        ("url_dataset", "dataset"),
        ("url_poster", "poster"),
        ("url_project", "project"),
        ("url_slides", "slides"),
        ("url_source", "source"),
        ("url_video", "video"),
    ]
)

PUBLICATION_TYPE_MAP = {
    "2": "article-journal",
    "6": "chapter",
}

SECTION_VIEW_MAP = {
    2: "article-grid",
    4: "citation",
}

HOME_VIEW_MAP = {
    2: "article-grid",
    3: "card",
    4: "citation",
}


class Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: yaml.Dumper, value: str):
    if "\n" in value:
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", value)


Dumper.add_representer(str, _str_presenter)


def _ordered_dict_presenter(dumper: yaml.Dumper, value: OrderedDict):
    return dumper.represent_dict(value.items())


Dumper.add_representer(OrderedDict, _ordered_dict_presenter)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate Wowchemy content front matter to HugoBlox.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--apply", action="store_true", help="Write migrated files")
    parser.add_argument("--check", action="store_true", help="Validate migrated content")
    parser.add_argument("--sample", help="Print migrated YAML for one file without writing")
    return parser.parse_args()


def read_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        _, fm, body = text.split("---\n", 2)
        data = yaml.safe_load(fm) or {}
        return data, body
    if text.startswith("+++\n"):
        _, fm, body = text.split("+++\n", 2)
        data = tomllib.loads(fm)
        return data, body
    raise ValueError(f"{path} does not contain recognized front matter")


def write_markdown(path: Path, data: dict, body: str) -> None:
    front_matter = yaml.dump(
        data,
        Dumper=Dumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=1000,
    ).strip()
    content = f"---\n{front_matter}\n---"
    if body:
        if not body.startswith("\n"):
            content += "\n"
        content += body
    else:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def has_meaningful_value(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(has_meaningful_value(item) for item in value)
    if isinstance(value, dict):
        return any(has_meaningful_value(item) for item in value.values())
    return True


def clean_string(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", str(value)).strip()
    return cleaned or None


def normalize_date(value):
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, date):
        dt = datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    else:
        text = str(value).strip().replace(" ", "")
        text = re.sub(r"^(\d{4}):(\d{2})-(\d{2})", r"\1-\2-\3", text)
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            dt = datetime.strptime(text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        else:
            if text.endswith("Z"):
                text = text[:-1] + "+00:00"
            dt = datetime.fromisoformat(text)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
    return dt.replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = str(value).strip().replace(" ", "")
    slash = doi.find("/")
    if slash != -1:
        prefix = doi[: slash + 1]
        suffix = doi[slash + 1 :].replace(":", "-")
        doi = prefix + suffix
    return doi


def prune(value):
    if isinstance(value, dict):
        cleaned = OrderedDict()
        for key, item in value.items():
            pruned = prune(item)
            if has_meaningful_value(pruned) or pruned is False:
                cleaned[key] = pruned
        return cleaned
    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            pruned = prune(item)
            if has_meaningful_value(pruned) or pruned is False:
                cleaned_list.append(pruned)
        return cleaned_list
    if isinstance(value, str):
        return value.rstrip()
    return value


def build_links(data: dict) -> list[dict]:
    links = []
    seen = set()

    for entry in data.get("links") or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") and entry.get("url"):
            normalized = OrderedDict([("type", entry["type"]), ("url", entry["url"])])
            if clean_string(entry.get("label")):
                normalized["label"] = clean_string(entry["label"])
            key = (normalized["type"], normalized["url"])
            if key not in seen:
                seen.add(key)
                links.append(normalized)
            continue
        if clean_string(entry.get("url")):
            normalized = OrderedDict([("type", "custom"), ("url", clean_string(entry["url"]))])
            if clean_string(entry.get("name")):
                normalized["label"] = clean_string(entry["name"])
            key = (normalized["type"], normalized["url"])
            if key not in seen:
                seen.add(key)
                links.append(normalized)

    for legacy_key, link_type in LEGACY_LINK_FIELDS.items():
        url = clean_string(data.get(legacy_key))
        if not url:
            continue
        normalized = OrderedDict([("type", link_type), ("url", url)])
        key = (link_type, url)
        if key not in seen:
            seen.add(key)
            links.append(normalized)

    return links


def migrate_publication(data: dict) -> dict:
    migrated = OrderedDict()
    migrated["title"] = clean_string(data.get("title"))
    if data.get("authors"):
        migrated["authors"] = data["authors"]
    author_notes = [note for note in (data.get("author_notes") or []) if clean_string(note)]
    if author_notes:
        migrated["author_notes"] = author_notes
    migrated["date"] = normalize_date(data.get("date"))

    publication_types = []
    for item in data.get("publication_types") or []:
        mapped = PUBLICATION_TYPE_MAP.get(str(item), str(item))
        if mapped:
            publication_types.append(mapped)
    if publication_types:
        migrated["publication_types"] = publication_types

    publication = data.get("publication")
    publication_name = clean_string(publication if isinstance(publication, str) else (publication or {}).get("name"))
    if publication_name:
        migrated["publication"] = publication_name

    abstract = clean_string(data.get("abstract"))
    if abstract:
        migrated["abstract"] = abstract
    summary = clean_string(data.get("summary"))
    if summary:
        migrated["summary"] = summary
    if data.get("tags"):
        migrated["tags"] = data["tags"]
    if "featured" in data:
        migrated["featured"] = bool(data["featured"])

    doi = normalize_doi(data.get("doi"))
    if doi:
        migrated["hugoblox"] = OrderedDict([("ids", OrderedDict([("doi", doi)]))])

    links = build_links(data)
    if links:
        migrated["links"] = links

    image = prune(copy.deepcopy(data.get("image") or {}))
    if image:
        migrated["image"] = image

    projects = prune(copy.deepcopy(data.get("projects") or []))
    if projects:
        migrated["projects"] = projects

    slides = data.get("slides")
    if has_meaningful_value(slides):
        migrated["slides"] = slides

    return prune(migrated)


def migrate_project(data: dict) -> dict:
    migrated = OrderedDict()
    migrated["title"] = clean_string(data.get("title"))
    summary = clean_string(data.get("summary"))
    if summary:
        migrated["summary"] = summary
    if data.get("tags"):
        migrated["tags"] = data["tags"]
    migrated["date"] = normalize_date(data.get("date"))

    links = build_links(data)
    if links:
        migrated["links"] = links

    image = prune(copy.deepcopy(data.get("image") or {}))
    if image:
        migrated["image"] = image

    slides = clean_string(data.get("slides"))
    if slides:
        migrated["slides"] = slides

    return prune(migrated)


def migrate_post(data: dict) -> dict:
    migrated = OrderedDict()
    migrated["title"] = clean_string(data.get("title"))
    if data.get("date") is not None:
        migrated["date"] = normalize_date(data.get("date"))
    if "draft" in data:
        migrated["draft"] = bool(data["draft"])
    return prune(migrated)


def migrate_section_index(data: dict) -> dict:
    migrated = OrderedDict()
    migrated["title"] = clean_string(data.get("title"))
    view = data.get("view")
    if isinstance(view, int) and view in SECTION_VIEW_MAP:
        migrated["view"] = SECTION_VIEW_MAP[view]
    elif isinstance(view, str) and clean_string(view):
        migrated["view"] = clean_string(view)
    banner = prune(copy.deepcopy(data.get("banner") or data.get("header") or {}))
    if banner:
        migrated["banner"] = banner
    return prune(migrated)


def migrate_page(data: dict) -> dict:
    migrated = OrderedDict()
    migrated["title"] = clean_string(data.get("title"))
    if data.get("date") is not None:
        migrated["date"] = normalize_date(data.get("date"))
    if "draft" in data:
        migrated["draft"] = bool(data["draft"])
    return prune(migrated)


def markdown_block_text(text: str | None, fallback: str) -> str:
    candidate = (text or "").strip()
    return candidate if candidate else fallback


def migrate_home_section(lang: str, name: str, data: dict, body: str) -> dict | None:
    active = data.get("active", True)
    if active is False:
        return None

    title = clean_string(data.get("title"))
    subtitle = clean_string(data.get("subtitle"))
    body_text = body.strip()

    if name == "about":
        username = clean_string(data.get("author")) or "scott"
        section = OrderedDict(
            [
                ("block", "resume-biography-3"),
                ("id", "about"),
                ("content", OrderedDict([("username", username), ("text", body_text or "")])),
            ]
        )
        return prune(section)

    if name == "experience":
        content = OrderedDict()
        if title:
            content["title"] = title
        date_format = clean_string(data.get("date_format")) or clean_string(
            ((data.get("design") or {}).get("spacing") or {}).get("date_format")
        )
        if date_format:
            content["date_format"] = date_format
        if data.get("experience"):
            content["items"] = data["experience"]
        section = OrderedDict([("block", "resume-experience"), ("id", "experience"), ("content", content)])
        design = OrderedDict()
        spacing = prune(copy.deepcopy((data.get("design") or {}).get("spacing") or {}))
        if isinstance(spacing, dict):
            spacing.pop("date_format", None)
        if spacing:
            design["spacing"] = spacing
        if design:
            section["design"] = design
        return prune(section)

    if name in {"featured", "publications", "posts", "projects"}:
        folder_map = {
            "featured": "publication",
            "publications": "publication",
            "posts": "post",
            "projects": "project",
        }
        design_view = None
        if name == "publications":
            design_view = "citation"
        else:
            raw_view = (data.get("design") or {}).get("view")
            if isinstance(raw_view, int):
                design_view = HOME_VIEW_MAP.get(raw_view, "card")
            elif isinstance(raw_view, str):
                design_view = clean_string(raw_view)

        content = OrderedDict()
        if title:
            content["title"] = title
        if subtitle:
            content["subtitle"] = subtitle
        if body_text:
            content["text"] = body_text
        filters = OrderedDict([("folders", [folder_map[name]])])
        if name == "featured":
            filters["featured_only"] = True
        else:
            exclude_featured = (data.get("content") or {}).get("filters", {}).get("exclude_featured")
            if exclude_featured is not None:
                filters["exclude_featured"] = bool(exclude_featured)
        content["filters"] = filters

        count = (data.get("content") or {}).get("count")
        if count is not None:
            content["count"] = count
        order = clean_string((data.get("content") or {}).get("order"))
        if order:
            content["order"] = order
        offset = (data.get("content") or {}).get("offset")
        if offset:
            content["offset"] = offset

        section = OrderedDict([("block", "collection"), ("id", name), ("content", content)])
        design = OrderedDict()
        if design_view:
            design["view"] = design_view
        columns = (data.get("design") or {}).get("columns")
        if columns:
            design["columns"] = int(columns) if str(columns).isdigit() else columns
        if design:
            section["design"] = design
        return prune(section)

    if name == "contact":
        fallback = (
            "Find me through the profile links above."
            if lang == "en"
            else "Retrouvez-moi via les liens du profil ci-dessus."
        )
        section = OrderedDict(
            [
                ("block", "markdown"),
                ("id", "contact"),
                ("content", OrderedDict([("title", title or "Contact"), ("text", markdown_block_text(body_text, fallback))])),
            ]
        )
        if subtitle:
            section["content"]["subtitle"] = subtitle
        design_columns = clean_string((data.get("design") or {}).get("columns"))
        if design_columns:
            section["design"] = OrderedDict([("columns", design_columns)])
        return prune(section)

    if name == "tags":
        tag_link = "/tag/" if lang == "en" else "/fr/tag/"
        fallback = f"[Browse all tags]({tag_link})" if lang == "en" else f"[Parcourir tous les tags]({tag_link})"
        text = body_text or fallback
        section = OrderedDict(
            [
                ("block", "markdown"),
                ("id", "tags"),
                ("content", OrderedDict([("title", title or "Tags"), ("text", text)])),
            ]
        )
        return prune(section)

    return None


def build_landing_page(lang_dir: Path) -> tuple[dict, list[Path]]:
    home_dir = lang_dir / "home"
    weighted_sections: list[tuple[int, dict]] = []
    consumed = []
    for path in sorted(home_dir.glob("*.md")):
        data, body = read_front_matter(path)
        if path.name == "index.md":
            consumed.append(path)
            continue
        weight = int(data.get("weight", 999))
        section = migrate_home_section(lang_dir.name, path.stem, data, body)
        consumed.append(path)
        if section:
            weighted_sections.append((weight, section))

    weighted_sections.sort(key=lambda item: (item[0], item[1].get("id", "")))
    landing = OrderedDict(
        [
            ("title", ""),
            ("date", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")),
            ("type", "landing"),
            ("sections", [section for _, section in weighted_sections]),
        ]
    )
    return landing, consumed


def migrate_repo(root: Path) -> dict:
    content_dir = root / "content"
    backup_dir = root / "content.wowchemy-backup"
    if backup_dir.exists():
        raise FileExistsError(f"{backup_dir} already exists")

    migrated_files = []
    removed_files = []

    shutil.copytree(content_dir, backup_dir)

    for lang_dir in sorted(path for path in content_dir.iterdir() if path.is_dir()):
        home_dir = lang_dir / "home"
        if home_dir.exists():
            landing, consumed = build_landing_page(lang_dir)
            write_markdown(lang_dir / "_index.md", landing, "")
            migrated_files.append(lang_dir / "_index.md")
            for path in consumed:
                path.unlink()
                removed_files.append(path)
            try:
                home_dir.rmdir()
            except OSError:
                pass

    for path in sorted(content_dir.rglob("*.md")):
        relative_parts = path.relative_to(content_dir).parts
        if "home" in relative_parts:
            continue
        if len(relative_parts) >= 2 and relative_parts[1] == "authors":
            continue
        data, body = read_front_matter(path)
        if len(relative_parts) >= 2 and relative_parts[1] == "publication" and path.name == "_index.md":
            migrated = migrate_section_index(data)
        elif len(relative_parts) >= 3 and relative_parts[1] == "publication":
            migrated = migrate_publication(data)
        elif len(relative_parts) >= 3 and relative_parts[1] == "project":
            migrated = migrate_project(data)
        elif len(relative_parts) >= 2 and relative_parts[1] == "post" and path.name == "_index.md":
            migrated = migrate_section_index(data)
        elif len(relative_parts) >= 2 and relative_parts[1] == "post":
            migrated = migrate_post(data)
        elif path.name == "_index.md" and len(relative_parts) == 2 and relative_parts[1] == "_index.md":
            continue
        else:
            migrated = migrate_page(data)
        write_markdown(path, migrated, body)
        migrated_files.append(path)

    return {
        "migrated_files": migrated_files,
        "removed_files": removed_files,
        "backup_dir": backup_dir,
    }


def detect_legacy_keys(root: Path) -> list[str]:
    legacy_patterns = [
        r"^\s*widget\s*:",
        r'^\s*widget\s*=',
        r"^\s*headless\s*:",
        r'^\s*headless\s*=',
        r"^\s*active\s*:",
        r'^\s*active\s*=',
        r"^\s*weight\s*:",
        r'^\s*weight\s*=',
        r"^\s*external_link\s*:",
        r"^\s*url_(pdf|code|dataset|poster|project|slides|source|video)\s*:",
        r"^\s*publishDate\s*:",
        r"^\s*publication_short\s*:",
        r"^\s*type\s*:\s*widget_page\s*$",
        r'^\s*type\s*=\s*"widget_page"\s*$',
    ]
    findings = []
    for path in sorted((root / "content").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for pattern in legacy_patterns:
            if re.search(pattern, text, flags=re.MULTILINE):
                findings.append(f"{path}: {pattern}")
                break
    return findings


def detect_non_iso_dates(root: Path) -> list[str]:
    failures = []
    for path in sorted((root / "content").rglob("*.md")):
        data, _ = read_front_matter(path)
        for key in ("date",):
            value = data.get(key)
            if value is None:
                continue
            normalized = normalize_date(value)
            if normalized and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", normalized):
                continue
            failures.append(f"{path}: {key}={value!r}")
    return failures


def sample_file(root: Path, sample_path: str) -> int:
    path = (root / sample_path).resolve()
    data, body = read_front_matter(path)
    parts = path.relative_to(root / "content").parts
    if len(parts) >= 3 and parts[1] == "publication":
        migrated = migrate_publication(data)
    elif len(parts) >= 3 and parts[1] == "project":
        migrated = migrate_project(data)
    elif len(parts) >= 2 and parts[1] == "post" and path.name == "_index.md":
        migrated = migrate_section_index(data)
    elif len(parts) >= 2 and parts[1] == "post":
        migrated = migrate_post(data)
    else:
        migrated = migrate_page(data)
    write_markdown(Path("/tmp/migrate-content-sample.md"), migrated, body)
    print(Path("/tmp/migrate-content-sample.md").read_text(encoding="utf-8"))
    return 0


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()

    if args.sample:
        return sample_file(root, args.sample)

    if args.apply:
        result = migrate_repo(root)
        print(f"Created backup: {result['backup_dir']}")
        print(f"Migrated {len(result['migrated_files'])} files")
        print(f"Removed {len(result['removed_files'])} legacy home files")

    if args.check:
        legacy = detect_legacy_keys(root)
        non_iso_dates = detect_non_iso_dates(root)
        if legacy or non_iso_dates:
            if legacy:
                print("Legacy fields still detected:")
                for item in legacy:
                    print(f" - {item}")
            if non_iso_dates:
                print("Non-ISO dates still detected:")
                for item in non_iso_dates:
                    print(f" - {item}")
            return 1
        print("Migration checks passed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
