# Publication and CV data flow

## Sources and outputs

The CV builder and website share one repository. Structured CV information and
the HAL identifier are in `cv-builder/data/`; the publications cache is
`cv-builder/data/publications.json`.

The scheduled/manual `.github/workflows/update-site.yml` workflow:

1. Fetches publication records from HAL with `cv-builder/scripts/fetch_hal.py`.
2. Exports journal-article records to Hugo bundles with
   `cv-builder/scripts/generate_hugo_content.py`.
3. Synchronizes the generated bundles to `content/en/publication/` and applies
   the website-owned fields in `data/publication_overrides.yml`.
4. Generates and compiles the full and short CV PDFs. It publishes both as
   release assets and copies the full CV to `static/files/cv.pdf`.
5. Opens or updates the fixed `automation/update-publications` PR when tracked
   publications, the HAL cache, or the site PDF changed.

Publication removals are blocked by the automated workflow and require manual
review. No generated publication or PDF changes are pushed directly to
`master`.

## Editorial ownership

HAL and CV source data provide canonical publication fields such as title,
authors, date, publication type, venue, identifiers, and HAL links.
`data/publication_overrides.yml` contains only website presentation fields:
`featured`, `tags`, `abstract`, `image`, and additional links. The override
script preserves canonical fields, reports stale or invalid overrides as
errors, and is idempotent.

## Local validation

Run the combined Python test suites and check the website build:

```bash
uv sync --dev
uv run pytest -q
uv run python scripts/apply_publication_overrides.py --check
hugo --gc --minify
```

The GitHub Pages deployment runs from `master` after a reviewed PR is merged.
