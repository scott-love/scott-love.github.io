# Repository Instructions

## Repository and deployment

- This is the unified website and CV repository.
- `master` is the production branch.
- `.github/workflows/deploy.yml` deploys to GitHub Pages after changes merge to
  `master`.

## Publications and CV

- CV data and HAL tooling live under `cv-builder/`.
- `cv-builder/scripts/fetch_hal.py` refreshes `cv-builder/data/publications.json`.
- `cv-builder/scripts/generate_hugo_content.py` exports publications directly
  for `content/en/publication/`.
- `data/publication_overrides.yml` owns website-only editorial fields; apply
  them with `scripts/apply_publication_overrides.py`.
- Preserve the current CV design and website appearance. The full CV download
  is served from `static/files/cv.pdf`.
- The monthly/manual update workflow creates a reviewable PR on the fixed
  `automation/update-publications` branch. Publication removals require manual
  review.

## Validation

Use the root `uv` project:

```bash
uv sync --dev
uv run pytest -q
uv run python scripts/apply_publication_overrides.py --check
hugo --gc --minify
```

The Python test command runs both `tests/` and `cv-builder/tests/`.
