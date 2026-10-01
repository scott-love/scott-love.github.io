#!/usr/bin/env python3
"""Apply website-owned editorial overrides to generated publication bundles.

Publication bundles under ``content/en/publication/hal-*/index.md`` are
generated/regenerated from canonical data in ``scott-love/academic-cv``.
Regeneration overwrites those files, so website-only editorial fields
(featured flag, tags, abstract, image, extra links) are kept separately in
``data/publication_overrides.yml`` and re-applied with this script after
every regeneration:

    academic-cv generated fields
            |
            v
    website editorial overrides (data/publication_overrides.yml)
            |
            v
    final Hugo content (content/en/publication/hal-*/index.md)

See the header comment in ``data/publication_overrides.yml`` for the override
schema, and ``docs/data-flow-specification.md`` for the overall design.

Only fields in ``ALLOWED_OVERRIDE_FIELDS`` may be changed by overrides.
Canonical fields (title, authors, date, publication_types, publication,
``hugoblox.ids.*``, canonical HAL links, etc.) are always preserved
unchanged.

Unknown HAL IDs in the override file (keys with no matching active bundle)
and malformed override entries are treated as validation errors, so stale or
typo'd overrides fail fast instead of silently accumulating. Active bundles
with no override entry are reported, but are not an error.
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import OrderedDict
from pathlib import Path

import yaml

ALLOWED_OVERRIDE_FIELDS = ("featured", "tags", "abstract", "image", "links")

# HAL IDs look like `hal-01432430`; this matches the bundle directory naming
# convention used under content/en/publication/hal-*/.
HAL_ID_PATTERN = re.compile(r"hal-\d+")

# Canonical front-matter field order used when writing bundles back out, so
# output is deterministic regardless of input key order. Fields not listed
# here are kept, in their original relative order, after these.
FIELD_ORDER = [
    "title",
    "authors",
    "date",
    "publication_types",
    "publication",
    "abstract",
    "tags",
    "featured",
    "image",
    "hugoblox",
    "links",
]


class Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: yaml.Dumper, value: str):
    if "\n" in value:
        return dumper.represent_scalar("tag:yaml.org,2002:str", value, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", value)


Dumper.add_representer(str, _str_presenter)
Dumper.add_representer(OrderedDict, lambda dumper, value: dumper.represent_dict(value.items()))


class OverrideError(Exception):
    """Raised for a single malformed override entry."""


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply website editorial overrides to generated publication bundles."
    )
    parser.add_argument(
        "--overrides",
        default="data/publication_overrides.yml",
        help="Path to the editorial overrides YAML file (default: %(default)s)",
    )
    parser.add_argument(
        "--content-dir",
        default="content/en/publication",
        help="Directory containing hal-* publication bundles (default: %(default)s)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and report without writing any files.",
    )
    return parser.parse_args(argv)


FRONT_MATTER_DELIMITER = re.compile(r"^---[ \t]*\r?\n", re.MULTILINE)


def read_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    # Use the same delimiter pattern for the opening line as for the closing
    # line, so bundles with trailing whitespace or CRLF line endings on the
    # opening "---" are accepted consistently with how the closing delimiter
    # is matched below.
    opening = FRONT_MATTER_DELIMITER.match(text)
    if not opening:
        raise ValueError(f"{path} does not contain recognized front matter")
    # Split on the closing "---" delimiter line rather than the first
    # occurrence of the literal substring "---\n", so a multi-line field
    # value (e.g. an abstract) that happens to contain that substring mid-text
    # cannot be mistaken for the end of the front matter block.
    match = FRONT_MATTER_DELIMITER.search(text, opening.end())
    if not match:
        raise ValueError(f"{path} front matter is not terminated with a '---' line")
    fm = text[opening.end():match.start()]
    body = text[match.end():]
    data = yaml.safe_load(fm) or {}
    return data, body


def write_front_matter(path: Path, data: "OrderedDict", body: str) -> None:
    front_matter = yaml.dump(
        data,
        Dumper=Dumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=100000,
    ).strip()
    content = f"---\n{front_matter}\n---"
    if body:
        if not body.startswith("\n"):
            content += "\n"
        content += body
    else:
        content += "\n"
    path.write_text(content, encoding="utf-8")


def discover_bundles(content_dir: Path) -> "OrderedDict[str, Path]":
    """Return an ordered mapping of HAL ID -> index.md path."""
    bundles: "OrderedDict[str, Path]" = OrderedDict()
    for index_path in sorted(content_dir.glob("hal-*/index.md")):
        hal_id = index_path.parent.name
        bundles[hal_id] = index_path
    return bundles


def _require(condition: bool, hal_id: str, message: str) -> None:
    if not condition:
        raise OverrideError(f"{hal_id}: {message}")


def _require_non_empty_str(value: object, hal_id: str, field_label: str) -> None:
    _require(isinstance(value, str) and bool(value), hal_id, f"'{field_label}' must be a non-empty string")


def _require_no_unknown_fields(mapping: dict, allowed: set, hal_id: str, field_label: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    _require(not unknown, hal_id, f"unknown {field_label} field(s) {unknown}")


def _is_safe_bundle_filename(filename: str) -> bool:
    """Reject anything but a plain file name (no directory components, no
    absolute paths, no '..' traversal, no control/null characters) so an
    override cannot reference a file outside its own bundle directory.

    Checked explicitly by character rather than via `pathlib`, since
    `pathlib.Path` only recognizes '/' as a separator on POSIX systems and
    would otherwise accept a string containing a literal '\\' as a single
    path component.
    """
    if not filename or filename != filename.strip() or filename in (".", ".."):
        return False
    if "/" in filename or "\\" in filename:
        return False
    return all(ord(char) >= 0x20 and char != "\x7f" for char in filename)


def validate_override_entry(hal_id: str, entry: object) -> dict:
    """Validate a single override entry. Raises OverrideError if malformed."""
    _require(isinstance(entry, dict), hal_id, f"override entry must be a mapping, got {type(entry).__name__}")

    _require_no_unknown_fields(
        entry, set(ALLOWED_OVERRIDE_FIELDS), hal_id,
        f"override; allowed fields are {list(ALLOWED_OVERRIDE_FIELDS)}",
    )

    if "featured" in entry:
        _require(isinstance(entry["featured"], bool), hal_id, "'featured' must be a boolean")

    if "tags" in entry:
        tags = entry["tags"]
        _require(
            isinstance(tags, list) and all(isinstance(tag, str) for tag in tags),
            hal_id, "'tags' must be a list of strings",
        )

    if "abstract" in entry:
        _require(isinstance(entry["abstract"], str), hal_id, "'abstract' must be a string")

    if "image" in entry:
        image = entry["image"]
        _require(isinstance(image, dict), hal_id, "'image' must be a mapping")
        _require_no_unknown_fields(image, {"filename", "preview_only"}, hal_id, "'image'")
        _require_non_empty_str(image.get("filename"), hal_id, "image.filename")
        if isinstance(image.get("filename"), str):
            _require(
                _is_safe_bundle_filename(image["filename"]),
                hal_id,
                "'image.filename' must be a plain file name within the bundle directory "
                "(no path separators or '..' segments)",
            )
        if "preview_only" in image:
            _require(isinstance(image["preview_only"], bool), hal_id, "'image.preview_only' must be a boolean")

    if "links" in entry:
        links = entry["links"]
        _require(isinstance(links, list), hal_id, "'links' must be a list")
        for link in links:
            _require(isinstance(link, dict), hal_id, "each 'links' entry must be a mapping")
            _require_no_unknown_fields(link, {"type", "url"}, hal_id, "link")
            _require_non_empty_str(link.get("type"), hal_id, "link.type")
            _require_non_empty_str(link.get("url"), hal_id, "link.url")

    return entry


def load_overrides(path: Path) -> tuple["OrderedDict[str, dict]", list[str]]:
    """Load and validate the overrides file.

    Returns a mapping of hal_id -> validated entry, plus a list of malformed
    entry error messages. Entries that fail validation are omitted from the
    returned mapping so callers can continue processing the valid ones.
    """
    if not path.exists():
        raise FileNotFoundError(f"Overrides file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: top-level overrides document must be a mapping of HAL ID -> override")

    valid: "OrderedDict[str, dict]" = OrderedDict()
    errors: list[str] = []
    for hal_id, entry in raw.items():
        if not isinstance(hal_id, str) or not HAL_ID_PATTERN.fullmatch(hal_id):
            errors.append(
                f"{hal_id!r}: override key must be a string matching 'hal-<digits>' "
                "(YAML may have parsed it as a non-string type, e.g. a date or number)"
            )
            continue
        try:
            valid[hal_id] = validate_override_entry(hal_id, entry)
        except OverrideError as exc:
            errors.append(str(exc))
    return valid, errors


def merge_links(canonical_links: list, override_links: list) -> list:
    """Preserve canonical links and append editorial links, skipping exact
    (type, url) duplicates.

    Canonical link entries are copied through as-is (preserving any extra
    keys HAL/HugoBlox may attach beyond ``type``/``url``). Editorial override
    links are normalized to just ``type``/``url``, since the override schema
    only documents those two fields.
    """
    merged = [OrderedDict(link) for link in canonical_links]
    seen = {(link.get("type"), link.get("url")) for link in canonical_links}
    for link in override_links:
        key = (link.get("type"), link.get("url"))
        if key in seen:
            continue
        seen.add(key)
        merged.append(OrderedDict([("type", link["type"]), ("url", link["url"])]))
    return merged


def apply_override(front_matter: dict, override: dict) -> OrderedDict:
    """Return a new front matter mapping with the override applied.

    Canonical fields are copied through unchanged. Only fields in
    ALLOWED_OVERRIDE_FIELDS are added/changed, using FIELD_ORDER for
    deterministic key ordering.
    """
    merged = dict(front_matter)

    if "featured" in override:
        # Keep an explicit False so a stale True does not persist.
        merged["featured"] = bool(override["featured"])

    if "tags" in override:
        merged["tags"] = list(override["tags"])

    if "abstract" in override:
        merged["abstract"] = override["abstract"]

    if "image" in override:
        image = OrderedDict()
        image["filename"] = override["image"]["filename"]
        if "preview_only" in override["image"]:
            image["preview_only"] = bool(override["image"]["preview_only"])
        merged["image"] = image

    if "links" in override:
        canonical_links = front_matter.get("links") or []
        merged["links"] = merge_links(canonical_links, override["links"])

    ordered = OrderedDict()
    for key in FIELD_ORDER:
        if key in merged:
            ordered[key] = merged[key]
    for key, value in merged.items():
        if key not in ordered:
            ordered[key] = value
    return ordered


def _normalize(value):
    """Recursively convert mappings/sequences into plain, order-independent
    structures for equality comparison (OrderedDict vs dict, list order of
    dict keys, etc. should not matter)."""
    if isinstance(value, dict):
        return {key: _normalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    return value


def front_matter_equal(a: dict, b: dict) -> bool:
    return _normalize(a) == _normalize(b)


def main(argv=None) -> int:
    args = parse_args(argv)
    overrides_path = Path(args.overrides)
    content_dir = Path(args.content_dir)

    try:
        overrides, malformed_errors = load_overrides(overrides_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    bundles = discover_bundles(content_dir)

    unknown_hal_ids = sorted(set(overrides) - set(bundles))
    bundles_without_override = sorted(set(bundles) - set(overrides))
    applicable_hal_ids = sorted(set(overrides) & set(bundles))

    applied: list[str] = []
    unchanged: list[str] = []
    missing_image_warnings: list[str] = []
    unreadable_bundles: list[str] = []

    for hal_id in applicable_hal_ids:
        index_path = bundles[hal_id]
        try:
            front_matter, body = read_front_matter(index_path)
        except (ValueError, yaml.YAMLError) as exc:
            unreadable_bundles.append(f"{hal_id}: {exc}")
            continue
        updated = apply_override(front_matter, overrides[hal_id])

        if "image" in overrides[hal_id]:
            image_path = index_path.parent / overrides[hal_id]["image"]["filename"]
            if not image_path.exists():
                # Intentionally a non-fatal warning, not a validation error: the
                # override YAML is metadata-only and may legitimately be applied
                # before the corresponding image asset is copied into the bundle
                # directory (e.g. in --check runs against a partially prepared
                # tree). Front matter is still written/reported so the warning
                # is visible without blocking the rest of the override run.
                missing_image_warnings.append(f"{hal_id}: image file not found at {image_path}")

        if front_matter_equal(front_matter, updated):
            unchanged.append(hal_id)
            continue

        applied.append(hal_id)
        if not args.check:
            write_front_matter(index_path, updated, body)

    print(f"Overrides file: {overrides_path}")
    print(f"Content directory: {content_dir}")
    print(f"Active bundles discovered: {len(bundles)}")
    total_entries = len(overrides) + len(malformed_errors)
    print(
        f"Override entries: {total_entries} total "
        f"({len(applicable_hal_ids)} applicable, {len(unknown_hal_ids)} unknown HAL ID, "
        f"{len(malformed_errors)} malformed)"
    )
    print()

    verb = "Would apply" if args.check else "Applied"
    print(f"{verb} override(s): {len(applied)}")
    for hal_id in applied:
        print(f"  - {hal_id}")

    print(f"Already up to date (idempotent, no change needed): {len(unchanged)}")
    for hal_id in unchanged:
        print(f"  - {hal_id}")

    print(f"Active bundles with no override (not an error): {len(bundles_without_override)}")
    for hal_id in bundles_without_override:
        print(f"  - {hal_id}")

    print(f"Unknown HAL ID(s) in overrides file (validation error): {len(unknown_hal_ids)}")
    for hal_id in unknown_hal_ids:
        print(f"  - {hal_id}")

    print(f"Malformed override entries (validation error): {len(malformed_errors)}")
    for message in malformed_errors:
        print(f"  - {message}")

    print(f"Unreadable bundle front matter (validation error): {len(unreadable_bundles)}")
    for message in unreadable_bundles:
        print(f"  - {message}")

    if missing_image_warnings:
        print(f"Warnings: {len(missing_image_warnings)}")
        for message in missing_image_warnings:
            print(f"  - WARNING: {message}")

    if args.check and applied:
        print()
        print("--check: files were not modified.")

    # Only unknown HAL IDs, malformed override entries, and unreadable
    # bundles are blocking validation errors. `missing_image_warnings`
    # (reported above) is intentionally excluded from this decision: it is
    # informational only and never affects the exit code.
    if malformed_errors or unknown_hal_ids or unreadable_bundles:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
