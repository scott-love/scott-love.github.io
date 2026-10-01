# Scott Love — HugoBlox Website

This repository is the **single active repository** for Scott Love's personal academic website:

**Live site:** https://scott-love.github.io/

## Repository status

- `master` is the production branch and source of truth.
- Phase 0 (HugoBlox modernization) is complete and deployed.
- The former `scott-love/personal-site` repository is archived and should not receive new work.
- The historical `migrate/hugoblox` branch is retained only as migration history; new work belongs on `master` or a feature branch targeting `master`.

## Stack

- Hugo Extended `v0.165.0`
- Go `1.23+`
- HugoBlox modules
- Tailwind CSS via the project npm dependencies
- GitHub Pages deployment through GitHub Actions

## Local development

```bash
npm ci
hugo server -D
```

Open http://localhost:1313/ to view the local site. For a production-style build:

```bash
hugo --gc --minify
```

## Publications

Publication content under `content/en/publication/` is generated from the
canonical data maintained in [`scott-love/academic-cv`](https://github.com/scott-love/academic-cv),
using HAL identifiers as stable bundle names (`hal-<id>/index.md`). The
`academic-cv` repository owns HAL ingestion and the publication exporter
(`scripts/generate_hugo_content.py`); this repository owns Hugo integration,
editorial overrides, and deployment.

Legacy, pre-migration publication bundles (author/year naming) are preserved
for reference under `content/en/publication_archive_pre_hal_migration/` and
are excluded from the Hugo build output (`build: {render: never, list: never}`
in that directory's `_index.md`).

To refresh publications:

1. Run the exporter in `academic-cv` (`make export-hugo` or
   `python scripts/generate_hugo_content.py --input data/publications.json
   --output build/hugo/content/en/publication`).
2. Copy the generated `hal-*` bundles into `content/en/publication/` in this
   repository.
3. Re-apply website-specific editorial overrides (featured flags, tags,
   abstracts, images, custom links) with
   `scripts/apply_publication_overrides.py` (see below) and rebuild/validate
   before merging.

See [`docs/data-flow-specification.md`](./docs/data-flow-specification.md) for
the full data-flow design.

### Editorial overrides

Generated publication bundles contain canonical bibliographic fields only.
Website-owned presentation fields (featured flag, tags, abstract, image,
extra links) are kept separately in
[`data/publication_overrides.yml`](./data/publication_overrides.yml), keyed
by HAL ID, so that regenerating `content/en/publication/hal-*/index.md` never
erases them:

```text
academic-cv generated fields
        ↓
website editorial overrides (data/publication_overrides.yml)
        ↓
final Hugo content
```

Apply the overrides with:

```bash
python scripts/apply_publication_overrides.py \
  --overrides data/publication_overrides.yml \
  --content-dir content/en/publication
```

Use `--check` to validate and report without writing any files (suitable for
CI):

```bash
python scripts/apply_publication_overrides.py --check
```

Override schema (see the header of `data/publication_overrides.yml` for the
full documented schema):

```yaml
hal-01464145:
  featured: true          # bool
  tags:                   # list[str]
    - mri
    - baboon
  abstract: "..."         # str
  image:
    filename: featured.png
    preview_only: true
  links:                  # appended to, not replacing, canonical HAL links
    - type: pdf
      url: https://example.org/article.pdf
```

Only `featured`, `tags`, `abstract`, `image`, and `links` may be set by
overrides; canonical fields (`title`, `authors`, `date`, `publication_types`,
`publication`, `hugoblox.ids.*`, and the canonical HAL link) are always
preserved unchanged. Canonical HAL links are kept and editorial links are
appended, without duplicating identical `(type, url)` pairs. An explicit
`featured: false` is preserved so a stale `true` does not persist across
regenerations. Unknown HAL IDs and malformed override entries are treated as
validation errors (non-zero exit status) so stale overrides cannot silently
accumulate. Run the script's tests with:

```bash
python3 -m pytest tests/test_apply_publication_overrides.py
```

## Deployment

The workflow in `.github/workflows/deploy.yml` builds and deploys the site to GitHub Pages. Pushes to `master` trigger production deployment.

Do not use the old Netlify, submodule, or manual `deploy.sh` workflow. The repository now contains the site source and deployment configuration in one place.

## Documentation

- [Migration guide](./MIGRATION.md)
- [Migration checklist](./MIGRATION_CHECKLIST.md)
- [Phase 0 summary](./PHASE_0_SUMMARY.md)
- [Contributing and development guide](./.github/CONTRIBUTING.md)
- [academic-cv repository](https://github.com/scott-love/academic-cv)
