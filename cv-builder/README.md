# CV builder

This directory contains the CV source data, HAL publication fetcher, Hugo
publication exporter, ModernCV assets, schema, and tests. Its Python scripts
derive project paths from their own location, so use the Makefile from this
directory (or with `make -C cv-builder` at the repository root).

## Requirements and local build

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)
- TeX Live with `xelatex` on `PATH`

From the repository root:

```bash
uv sync --dev
make -C cv-builder build-all
```

The build fetches HAL publications, generates `cv/cv.tex` and
`cv/cv_short.tex`, then compiles `cv/cv.pdf` and `cv/cv_short.pdf`. Useful
targets include:

- `make -C cv-builder fetch-publications`
- `make -C cv-builder generate-latex`
- `make -C cv-builder export-hugo`
- `make -C cv-builder render-all`
- `make -C cv-builder clean`

The HAL identifier is configured in `data/profile.yml`. HAL requests retry
transient errors; if HAL remains unavailable and the cached
`data/publications.json` is readable, the fetcher keeps that cache so the CV
can still be built.

## Website publications

`scripts/generate_hugo_content.py` exports valid journal-article records from
`data/publications.json` as Hugo content bundles. Other categories are
intentionally excluded. The monthly/manual website workflow sends the exporter
output directly to `content/en/publication/` and reapplies the website-owned
editorial overrides from the repository root.

The exporter defaults to `build/hugo/content/en/publication` within this
directory. Its schema and category/date policies are described in `schemas/`
and `docs/`.

The workflow publishes both PDFs as GitHub Release assets and puts the full
`cv.pdf` at the website's existing `static/files/cv.pdf` download path.
`cv-builder/cv/*.tex` and generated PDFs are build artifacts and are ignored by
Git; the HAL publication cache is retained in `data/publications.json`.

Run the combined Python tests from the repository root:

```bash
uv run pytest -q
```

The root README documents the scheduled/manual refresh, PR review, permissions,
and deployment flow.
