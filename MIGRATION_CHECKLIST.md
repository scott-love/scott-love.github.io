# HugoBlox Migration Checklist

**Repository:** `scott-love/scott-love.github.io`  
**Active branch:** `master`  
**Live site:** https://scott-love.github.io/  
**Status:** Phase 0 complete; Phase 1 starting  
**Last updated:** October 1, 2026

> `scott-love/scott-love.github.io` is the **single active repository** for this site. The former `scott-love/personal-site` repository is archived. The historical `migrate/hugoblox` branch is retained only for migration traceability.

---

## Phase 0 Status: Complete ✅

Phase 0 was merged into `master` and deployed to GitHub Pages. The production workflow is `.github/workflows/deploy.yml`, and pushes to `master` trigger deployment.

### Pre-Migration Setup

- [x] **TASK-1**: Back up current site
  - [x] Create local backup branch
  - [x] Export/document configuration and versions
  - [x] Capture the deployed site for comparison
- [x] **TASK-2**: Review HugoBlox migration guidance
- [x] **TASK-3**: Plan Hugo, Go, and module versions

### Hugo, Go, and Module Updates

- [x] **TASK-4**: Upgrade Hugo from `0.78.2` to Hugo Extended `0.165.0`
  - [x] Install and verify Hugo
  - [x] Build the site locally
  - [x] Record migration warnings and compatibility notes
- [x] **TASK-5**: Upgrade the Go requirement from `1.15` to `1.23+`
  - [x] Run `go mod tidy`
  - [x] Validate the Hugo build
- [x] **TASK-6**: Migrate Wowchemy module references to HugoBlox
  - [x] Verify HugoBlox module resolution
  - [x] Run `hugo mod graph`
  - [x] Validate the build and deployment workflow

### Configuration, Layout, and Content

- [x] **TASK-7**: Update Hugo configuration for the modern stack
- [x] **TASK-8**: Replace the old Netlify/submodule deployment model
  - [x] Remove obsolete Netlify configuration
  - [x] Remove the stale self-referencing Git submodule
  - [x] Confirm GitHub Actions is the deployment source
- [x] **TASK-9**: Migrate legacy Wowchemy layout/content assumptions to HugoBlox
- [x] **TASK-10**: Verify Tailwind CSS and responsive styling
- [x] **TASK-11**: Verify core content rendering
  - [x] Homepage
  - [x] Publications
  - [x] Posts
  - [x] About/CV content
  - [x] Navigation and search where enabled

### GitHub Pages Deployment

- [x] **TASK-13**: Create and validate `.github/workflows/deploy.yml`
  - [x] Checkout source
  - [x] Install Node.js dependencies
  - [x] Install Hugo Extended `0.165.0`
  - [x] Build the site
  - [x] Upload and deploy the Pages artifact
- [x] **TASK-14**: Configure GitHub Pages to use GitHub Actions
- [x] **TASK-15**: Complete the first deployment and verify the live site
- [x] Merge migration work into `master`
- [x] Confirm successful deployment runs from `master`

### Repository Consolidation

- [x] `scott-love/scott-love.github.io` is the only active repository
- [x] Former `scott-love/personal-site` repository is archived
- [x] `master` is the production branch and source of truth
- [x] Historical `migrate/hugoblox` branch is reference-only
- [x] Legacy Wowchemy/Academic updater artifacts removed
- [x] Generated `public/` and `_vendor/` directories remain ignored locally

---

## Phase 0 Follow-up Items

These are ongoing site-maintenance checks rather than blockers to the completed migration.

- [ ] **TASK-12**: Verify metadata and SEO
  - [ ] Check page titles
  - [ ] Inspect meta descriptions
  - [ ] Verify Open Graph tags
  - [ ] Check the RSS feed at https://scott-love.github.io/index.xml
  - [ ] Test representative pages with an Open Graph checker
- [ ] **TASK-16**: Complete full functionality regression testing
  - [ ] External links
  - [ ] Downloads and media
  - [ ] Email and social links
  - [ ] Images and embedded content
- [ ] **TASK-17**: Measure performance with Lighthouse or PageSpeed Insights
- [ ] **TASK-18**: Run an accessibility audit
  - [ ] Heading hierarchy
  - [ ] Image alternative text
  - [ ] Color contrast
  - [ ] Keyboard navigation
  - [ ] Screen-reader review
- [ ] **TASK-19**: Complete cross-browser testing
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Mobile browsers
- [x] **TASK-20**: Update repository documentation
  - [x] Update `README.md`
  - [x] Update `MIGRATION.md`
  - [x] Add `.github/CONTRIBUTING.md`
  - [x] Add `PHASE_0_SUMMARY.md`
  - [x] Document the archived repository and production branch

---

## Phase 1: Data Pipeline Discovery — Starting 🔵

Phase 1 investigates how structured information from `scott-love/academic-cv` should flow into this HugoBlox site. This phase is discovery and design only; it should not introduce automated content mutations in production until the design is approved.

### Goals

1. Inventory the current HugoBlox publication and profile content structure.
2. Inspect the available outputs and schema in `scott-love/academic-cv`.
3. Map academic-cv fields to HugoBlox Markdown and front matter.
4. Identify other automatable content: education, employment, talks, teaching, supervision, and service.
5. Define a versioned and testable data-flow specification.

### Phase 1 Tasks

- [ ] **TASK-23**: Inventory current site data structures
  - [ ] List publication bundles and their front matter fields
  - [ ] Identify profile, education, employment, project, talk, and teaching content
  - [ ] Identify manually maintained versus generated data
  - [ ] Record current HugoBlox block and collection types
- [ ] **TASK-24**: Inspect `scott-love/academic-cv`
  - [ ] Identify source files and canonical data formats
  - [ ] Document current commands and generated outputs
  - [ ] Record data ownership and update workflow
  - [ ] Identify stable identifiers for publications and people/organizations
- [ ] **TASK-25**: Map academic-cv data to HugoBlox
  - [ ] Map publication fields
  - [ ] Map identifiers, DOI, URLs, authors, venues, dates, and abstracts
  - [ ] Map education and employment fields where available
  - [ ] Identify fields requiring manual editorial input
  - [ ] Document handling for missing, changed, or deleted records
- [ ] **TASK-26**: Design the unified data schema
  - [ ] Define canonical source schema
  - [ ] Define HugoBlox output schema
  - [ ] Define stable IDs and deduplication rules
  - [ ] Define validation and error-reporting requirements
  - [ ] Define generated-file ownership and review policy
- [ ] **TASK-27**: Document the Phase 1 architecture
  - [ ] Create `docs/data-flow-specification.md`
  - [ ] Include source, transform, output, and deployment stages
  - [ ] Record integration points between `academic-cv` and this repository
  - [ ] Record open decisions and risks
  - [ ] Review and approve the design before implementation

### Phase 1 Deliverables

- [x] Data Flow Specification: `docs/data-flow-specification.md`
- [x] Source-to-HugoBlox field mapping (implemented in `academic-cv`'s
      `scripts/generate_hugo_content.py`)
- [x] Proposed publication/profile schema
- [ ] Inventory of automation candidates
- [ ] List of unresolved design decisions

### Phase 1 Progress: Publication Migration

- [x] Archive legacy author/year publication bundles to
      `content/en/publication_archive_pre_hal_migration/` (27 bundles)
- [x] Exclude the archive from the Hugo build
      (`build: {render: never, list: never}`)
- [x] Generate and import HAL-based bundles into `content/en/publication/`
      (30 active journal-article bundles, from `academic-cv`'s journal-only
      exporter policy; 81 non-journal records — conference presentations,
      posters, preprints, book chapters, and other contributions — are
      excluded by design)
- [x] Validate the Hugo build succeeds
- [x] Confirm homepage featured/recent publication collection blocks render
- [x] Re-apply website-specific editorial overrides (featured/tags/images)
      via `data/publication_overrides.yml` and
      `scripts/apply_publication_overrides.py` — 22 of the 30 active bundles
      have overrides recovered from the pre-migration archive; 8 bundles
      (all added after the journal-only refresh) have no matching archived
      editorial data yet and remain a follow-up item. Note: many records
      only carry a year-level date fallback (January 1); date precision is a
      separate, unresolved `academic-cv` exporter concern, not addressed by
      the override layer.

---

## Phase 2: Data Pipeline Implementation — Planned

- [ ] Refactor or extend `academic-cv` output support
- [ ] Implement transforms for publications
- [ ] Implement transforms for additional approved content types
- [ ] Add tests and fixtures for the transformation pipeline
- [ ] Define how generated content is reviewed and committed

## Phase 3: CI/CD Integration — Planned

- [ ] Trigger site updates when approved `academic-cv` data changes
- [ ] Validate generated content before deployment
- [ ] Deploy only after successful Hugo build and checks
- [ ] Add status reporting and failure notifications

## Phase 4: Extended Automation & Polish — Planned

- [ ] Extend automation to education, employment, teaching, and supervision
- [ ] Document maintenance procedures
- [ ] Review optional CMS support
- [ ] Remove remaining migration technical debt

---

## Quick Reference

```bash
# Check versions
hugo version
go version
node --version
npm --version

# Install JavaScript dependencies
npm ci

# Local development
hugo server -D

# Production-style build
hugo --gc --minify

# Validate migrated content when relevant
python scripts/migrate_content_frontmatter.py --root . --check

# Set up Python tooling and tests
uv sync --dev

# Apply/validate website editorial overrides for publications
uv run python scripts/apply_publication_overrides.py --check
uv run pytest -q

# Production deployment
# Push to master; GitHub Actions deploys automatically
 git push origin master
```

Workflow: `.github/workflows/deploy.yml`  
Actions: https://github.com/scott-love/scott-love.github.io/actions  
Live site: https://scott-love.github.io/

---

## Troubleshooting

| Issue | Possible cause | Solution |
|---|---|---|
| `hugo: command not found` | Hugo is not installed or not on `PATH` | Install Hugo Extended and verify `hugo version` |
| Module resolution failure | Stale or incomplete module cache | Run `hugo mod tidy` and retry the build |
| CSS is missing | npm dependencies were not installed | Run `npm ci`, then rebuild |
| Content does not render | Invalid front matter or changed block fields | Check the page front matter and Hugo build output |
| GitHub Pages deployment fails | Workflow, permissions, or Pages settings issue | Inspect the failed Actions job and verify Pages uses GitHub Actions |
| Unexpected `public/` or `_vendor/` files | Local/generated output | Leave them untracked; both directories are ignored |

---

**Phase 0:** Complete ✅  
**Phase 1:** Starting — Data Pipeline Discovery  
**Production branch:** `master`  
**Single active repository:** `scott-love/scott-love.github.io`  
**Archived repository:** `scott-love/personal-site`
