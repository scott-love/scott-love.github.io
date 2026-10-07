# Publication pipeline recovery

Use this guide when a HAL refresh produces incorrect publication content, a
CV build fails, editorial overrides are invalid, or a site build fails.

## If the refresh PR is still open

1. Review the workflow run logs and the generated changes.
2. Close the PR or correct the source/override data and rerun
   **Update publications and CV**.
3. Do not bypass the workflow's publication-removal guard without reviewing
   the removed HAL IDs.

## If a bad change was merged

1. Revert the offending merge or commit on `master`.
2. Wait for `.github/workflows/deploy.yml` to complete.
3. Verify the live site and the publication/CV download links.
4. Correct the source data or overrides and run the refresh workflow again.

## Troubleshooting

- **HAL is unavailable:** the fetcher retries transient failures and reuses
  `cv-builder/data/publications.json` when it is readable. Check the workflow
  logs and manually dispatch another run when HAL is reachable.
- **Unexpected publication removals:** the workflow stops before creating a
  PR. Inspect the current cache and HAL results; resolve the cause before
  updating the publication set.
- **Override validation fails:** fix `data/publication_overrides.yml`, then
  run `uv run python scripts/apply_publication_overrides.py --check`.
- **LaTeX compilation fails:** inspect `cv-builder/cv/cv.log` and verify
  `xelatex` is installed.
- **Hugo build/deployment fails:** inspect the Pages workflow logs and confirm
  the repository's Pages source is set to GitHub Actions.

## Recovery checklist

- [ ] Identify the failing source or generated change.
- [ ] Correct or revert the change.
- [ ] Rerun Python tests and Hugo validation.
- [ ] Confirm the Pages deployment and live outputs.
