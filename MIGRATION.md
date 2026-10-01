# Migration Guide

**Status:** Phase 0 complete; Phase 1 starting  
**Repository:** `scott-love/scott-love.github.io`  
**Production branch:** `master`  
**Live site:** https://scott-love.github.io/  
**Last updated:** October 1, 2026

## Repository consolidation

`scott-love/scott-love.github.io` is now the **single active repository** for the website. The former `scott-love/personal-site` repository is archived. The historical `migrate/hugoblox` branch is retained for reference, but all new work is done on `master` or feature branches targeting `master`.

## Phase status

| Phase | Focus | Status |
|---|---|---|
| Phase 0 | Hugo, Go, HugoBlox, content, and deployment modernization | Complete |
| Phase 1 | Data pipeline discovery | Starting |
| Phase 2 | Data pipeline implementation | Planned |
| Phase 3 | CI/CD integration with `academic-cv` | Planned |
| Phase 4 | Extended automation and polish | Planned |

## Phase 0 completion

Phase 0 modernized the site from the legacy Wowchemy/Academic and Netlify workflow to HugoBlox and GitHub Pages.

Completed work:

- Upgraded Hugo from `0.78.2` to Hugo Extended `0.165.0`.
- Updated the Go toolchain requirement to `1.23+`.
- Migrated module references from Wowchemy to HugoBlox.
- Migrated legacy content front matter into the HugoBlox structure.
- Updated the styling/build path for Tailwind CSS.
- Replaced the old deployment process with `.github/workflows/deploy.yml`.
- Configured GitHub Pages to deploy through GitHub Actions.
- Merged the migration into `master` and verified successful production deployments.
- Removed obsolete Netlify, submodule, Wowchemy updater, and Academic updater artifacts.
- Confirmed the site is live at https://scott-love.github.io/.

## Phase 1: Data Pipeline Discovery

Phase 1 will document the data architecture before implementation begins.

Goals:

1. Inventory the current HugoBlox publication and profile content structure.
2. Inspect the available outputs and schema in `scott-love/academic-cv`.
3. Map academic-cv data to HugoBlox Markdown/front matter.
4. Identify other automatable content such as education, employment, talks, teaching, and supervision.
5. Define a versioned, testable data-flow specification.

Deliverables:

- `docs/data-flow-specification.md`.
- A proposed schema for publications and other profile data.
- A mapping of source fields to HugoBlox fields.
- Identified integration points and open decisions.

### Phase 1 progress: initial publication migration

The `academic-cv` publication exporter (`scripts/generate_hugo_content.py`,
merged in `scott-love/academic-cv#24`) now produces HAL-identified Hugo
publication bundles. This repository has completed the first integration
pass:

- Legacy author/year publication bundles were archived (not deleted) under
  `content/en/publication_archive_pre_hal_migration/`, excluded from the
  Hugo build via `build: {render: never, list: never}`.
- The active `content/en/publication/` collection was repopulated with
  HAL-based generated bundles (`hal-<id>/index.md`) produced by the
  exporter from `academic-cv`'s `data/publications.json`.
- The Hugo build was validated locally and the homepage's featured/recent
  publication collection blocks continue to resolve without config changes.
- Editorial overrides (featured flags, tags, images, custom abstracts) were
  intentionally not re-applied in this pass and remain a follow-up task.

## Deployment architecture

The production flow is now:

```text
commit to master
       ↓
GitHub Actions (.github/workflows/deploy.yml)
       ↓
Hugo Extended build
       ↓
GitHub Pages deployment
       ↓
https://scott-love.github.io/
```

The future data flow will extend this with `academic-cv` as a source, but Phase 1 is discovery only.

## Rollback

If a production change causes a problem:

1. Revert the offending commit on `master`, or create a corrective commit.
2. Monitor the GitHub Pages workflow.
3. Use the historical `migrate/hugoblox` branch and repository history for migration reference.
4. Confirm the live site after deployment.

For development and deployment instructions, see [`.github/CONTRIBUTING.md`](./.github/CONTRIBUTING.md).
