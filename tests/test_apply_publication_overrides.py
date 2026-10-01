"""Tests for scripts/apply_publication_overrides.py.

Run with:

    python3 -m pytest tests/test_apply_publication_overrides.py
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import apply_publication_overrides as apo  # noqa: E402


CANONICAL_BUNDLE = """---
title: 'Example Publication Title'
authors:
- Jane Doe
- John Smith
date: '2020-01-01T00:00:00Z'
publication_types:
- article-journal
publication: Example Journal
hugoblox:
  ids:
    hal: hal-00000001
    doi: 10.1234/example.doi
links:
- type: url
  url: https://hal.science/hal-00000001v1
---
"""


def make_bundle(content_dir: Path, hal_id: str, text: str = CANONICAL_BUNDLE) -> Path:
    bundle_dir = content_dir / hal_id
    bundle_dir.mkdir(parents=True, exist_ok=True)
    index_path = bundle_dir / "index.md"
    index_path.write_text(text, encoding="utf-8")
    return index_path


def read_result(index_path: Path) -> dict:
    data, _ = apo.read_front_matter(index_path)
    return data


@pytest.fixture
def content_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "content" / "en" / "publication"
    directory.mkdir(parents=True)
    return directory


def write_overrides(tmp_path: Path, mapping: dict) -> Path:
    path = tmp_path / "publication_overrides.yml"
    path.write_text(yaml.safe_dump(mapping, sort_keys=False), encoding="utf-8")
    return path


def run(overrides_path: Path, content_dir: Path, check: bool = False) -> int:
    argv = ["--overrides", str(overrides_path), "--content-dir", str(content_dir)]
    if check:
        argv.append("--check")
    return apo.main(argv)


def test_apply_featured_tags_and_abstract(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {
            "hal-00000001": {
                "featured": True,
                "tags": ["mri", "baboon"],
                "abstract": "A short website abstract.",
            }
        },
    )

    exit_code = run(overrides_path, content_dir)

    assert exit_code == 0
    data = read_result(index_path)
    assert data["featured"] is True
    assert data["tags"] == ["mri", "baboon"]
    assert data["abstract"] == "A short website abstract."


def test_apply_image_override(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"image": {"filename": "featured.png", "preview_only": True}}},
    )

    exit_code = run(overrides_path, content_dir)

    assert exit_code == 0
    data = read_result(index_path)
    assert data["image"] == {"filename": "featured.png", "preview_only": True}


def test_append_link_preserves_canonical_hal_link(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"links": [{"type": "pdf", "url": "https://example.org/article.pdf"}]}},
    )

    exit_code = run(overrides_path, content_dir)

    assert exit_code == 0
    data = read_result(index_path)
    assert {"type": "url", "url": "https://hal.science/hal-00000001v1"} in data["links"]
    assert {"type": "pdf", "url": "https://example.org/article.pdf"} in data["links"]
    assert len(data["links"]) == 2


def test_append_link_does_not_duplicate_identical_link(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"links": [{"type": "url", "url": "https://hal.science/hal-00000001v1"}]}},
    )

    run(overrides_path, content_dir)

    data = read_result(index_path)
    assert len(data["links"]) == 1


def test_explicit_featured_false_overrides_stale_true(tmp_path, content_dir):
    bundle_text = CANONICAL_BUNDLE.replace(
        "links:\n- type: url",
        "featured: true\nlinks:\n- type: url",
    )
    index_path = make_bundle(content_dir, "hal-00000001", text=bundle_text)
    overrides_path = write_overrides(tmp_path, {"hal-00000001": {"featured": False}})

    exit_code = run(overrides_path, content_dir)

    assert exit_code == 0
    data = read_result(index_path)
    assert data["featured"] is False


def test_unknown_hal_id_is_reported_and_fails(tmp_path, content_dir, capsys):
    make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(tmp_path, {"hal-99999999": {"featured": True}})

    exit_code = run(overrides_path, content_dir)
    output = capsys.readouterr().out

    assert exit_code != 0
    assert "hal-99999999" in output
    assert "Unknown HAL ID" in output


def test_malformed_override_is_reported_and_fails(tmp_path, content_dir, capsys):
    make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"featured": "yes"}},  # must be bool, not str
    )

    exit_code = run(overrides_path, content_dir)
    output = capsys.readouterr().out

    assert exit_code != 0
    assert "Malformed override entries" in output
    data = read_result(content_dir / "hal-00000001" / "index.md")
    assert "featured" not in data


def test_malformed_override_unknown_field(tmp_path, content_dir):
    make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"not_a_real_field": "value"}},
    )

    exit_code = run(overrides_path, content_dir)

    assert exit_code != 0


def test_malformed_override_image_missing_filename(tmp_path, content_dir):
    make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"image": {"preview_only": True}}},  # missing required filename
    )

    exit_code = run(overrides_path, content_dir)

    assert exit_code != 0


def test_missing_image_file_warns_but_does_not_fail(tmp_path, content_dir, capsys):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"image": {"filename": "does-not-exist.png"}}},
    )

    exit_code = run(overrides_path, content_dir)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "does-not-exist.png" in output
    data = read_result(index_path)
    assert data["image"]["filename"] == "does-not-exist.png"


def test_check_mode_does_not_modify_files(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    original_text = index_path.read_text(encoding="utf-8")
    overrides_path = write_overrides(tmp_path, {"hal-00000001": {"featured": True}})

    exit_code = run(overrides_path, content_dir, check=True)

    assert exit_code == 0
    assert index_path.read_text(encoding="utf-8") == original_text


def test_idempotent_repeated_application(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"featured": True, "tags": ["mri"], "abstract": "Summary."}},
    )

    run(overrides_path, content_dir)
    first_pass_text = index_path.read_text(encoding="utf-8")
    run(overrides_path, content_dir)
    second_pass_text = index_path.read_text(encoding="utf-8")

    assert first_pass_text == second_pass_text


def test_canonical_fields_remain_unchanged(tmp_path, content_dir):
    index_path = make_bundle(content_dir, "hal-00000001")
    overrides_path = write_overrides(
        tmp_path,
        {"hal-00000001": {"featured": True, "tags": ["mri"], "abstract": "Summary."}},
    )

    run(overrides_path, content_dir)

    data = read_result(index_path)
    assert data["title"] == "Example Publication Title"
    assert data["authors"] == ["Jane Doe", "John Smith"]
    assert data["date"] == "2020-01-01T00:00:00Z"
    assert data["publication_types"] == ["article-journal"]
    assert data["publication"] == "Example Journal"
    assert data["hugoblox"]["ids"]["hal"] == "hal-00000001"
    assert data["hugoblox"]["ids"]["doi"] == "10.1234/example.doi"
    assert {"type": "url", "url": "https://hal.science/hal-00000001v1"} in data["links"]


def test_bundle_without_override_is_reported_not_failed(tmp_path, content_dir, capsys):
    make_bundle(content_dir, "hal-00000001")
    make_bundle(content_dir, "hal-00000002")
    overrides_path = write_overrides(tmp_path, {"hal-00000001": {"featured": True}})

    exit_code = run(overrides_path, content_dir)
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "hal-00000002" in output
    assert "Active bundles with no override (not an error)" in output
