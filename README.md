# Scott Love — Website and CV

This repository contains the Hugo website and the CV builder that supplies its
publication content and CV downloads.

**Live site:** https://scott-love.github.io/

## Repository layout

- `content/`, `layouts/`, `config/`, `static/`, and `assets/` — Hugo website.
- `content/en/publication/` — generated HAL publication bundles with website
  editorial overrides applied.
- `data/publication_overrides.yml` and `scripts/apply_publication_overrides.py`
  — website-owned presentation choices for publications.
- `cv-builder/` — CV source data, HAL fetching/export scripts, ModernCV assets,
  schema, documentation, tests, and Makefile.
- `static/files/cv.pdf` — the PDF served by the existing website CV download.

Python dependencies for both publication tooling and tests are managed from
the repository root with `uv` and `uv.lock`.

## Local development

Install website dependencies and run Hugo locally:

```bash
npm ci
hugo server -D
```

Build the site:

```bash
hugo --gc --minify
```

Build the CV locally (requires Python 3.12+, `uv`, and TeX Live with
`xelatex`):

```bash
uv sync --dev
make -C cv-builder build-all
```

The CV PDFs are generated as `cv-builder/cv/cv.pdf` and
`cv-builder/cv/cv_short.pdf`. To fetch HAL publications or export website
bundles separately:

```bash
make -C cv-builder fetch-publications
uv run python cv-builder/scripts/generate_hugo_content.py --output /tmp/publications
```

Run both the website and CV Python tests with:

```bash
uv run pytest -q
```

## Monthly publication and CV refresh

`.github/workflows/update-site.yml` runs on the first of each month and can
also be started with **Actions → Update publications and CV → Run workflow**.
It fetches publications from HAL using the identifier in
`cv-builder/data/profile.yml` (no HAL secret or API key is required), exports
publication bundles directly into the website, reapplies editorial overrides,
and builds both CV PDFs.

The workflow publishes `cv.pdf` and `cv_short.pdf` as GitHub Release assets.
It also copies `cv.pdf` to `static/files/cv.pdf`, where the existing site link
serves it after deployment. Publication removals are blocked for manual review.
When there are changes, the workflow opens or updates the fixed branch
`automation/update-publications` as a PR to `master`; it does not push the
publication or PDF changes directly to the production branch. The site PDF is
included in that same PR so the deployed download stays in sync with the CV
release.

Review the generated publications, any CV/PDF changes, and the removal guard
before merging. A merge to `master` triggers `.github/workflows/deploy.yml`,
which builds and deploys the site to GitHub Pages. The override workflow also
validates editorial overrides, runs the Python test suites, and builds Hugo
for relevant pull requests.

### GitHub Actions setup and checks

- In **Settings → Actions → General**, enable **Allow GitHub Actions to create
  and approve pull requests** so the refresh workflow can open its PR.
- GitHub Actions requires no repository secrets for HAL access. The default
  `GITHUB_TOKEN` is used with `contents: write` and `pull-requests: write`.
- PRs created with the default `GITHUB_TOKEN` do **not** trigger other
  workflows. The generated PR therefore needs manual validation. To run CI
  automatically on generated PRs, configure a PAT or GitHub App token with the
  necessary repository permissions and use it for the pull-request action.
- Confirm **Settings → Pages → Build and deployment → Source** is set to
  **GitHub Actions**.
- After verifying the unified workflow, archive the former
  `scott-love/academic-cv` repository if it is no longer needed.

Run the workflow manually once after setup to verify live HAL access, the
release assets, the generated PR, the `/files/cv.pdf` path, and deployment after
merging. These live GitHub/HAL behaviors cannot be verified by local tests.

## Publication editorial overrides

Generated publication fields are kept separate from website presentation
choices. `data/publication_overrides.yml` stores optional `featured`, `tags`,
`abstract`, `image`, and additional `links` keyed by HAL ID. The override
script preserves canonical bibliographic fields and is idempotent:

```bash
uv run python scripts/apply_publication_overrides.py --check
uv run python scripts/apply_publication_overrides.py
```

See [the publication pipeline guide](docs/data-flow-specification.md) and
[`cv-builder/README.md`](cv-builder/README.md) for more detail.
