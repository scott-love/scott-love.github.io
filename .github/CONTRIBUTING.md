# Contributing and Development Guide

## Repository and branch policy

`scott-love/scott-love.github.io` is the **only active repository** for the website. The former `scott-love/personal-site` repository is archived.

- `master` is the production branch and source of truth.
- Use a feature branch for substantial changes and open a pull request targeting `master` when review is useful.
- Small, low-risk documentation or content changes may be committed directly to `master`.
- `migrate/hugoblox` is historical migration work; do not use it for new development.

## Prerequisites

Install:

- Hugo Extended `v0.165.0` or later
- Go `1.23` or later
- Node.js compatible with the repository's npm lockfile

Verify the tools:

```bash
hugo version
go version
node --version
npm --version
```

## Local setup

From the repository root:

```bash
npm ci
hugo server -D
```

The development site is available at http://localhost:1313/.

For a production-style build:

```bash
hugo --gc --minify
```

Generated output is written to `public/`, which is intentionally ignored by Git.

## Validation

Before pushing changes:

```bash
# Validate the content migration checks, when relevant
python scripts/migrate_content_frontmatter.py --root . --check

# Build the site
hugo --gc --minify

git status
```

Also inspect any changed pages locally, especially homepage sections, publications, posts, and navigation.

## Deployment

`.github/workflows/deploy.yml` builds the site and deploys it to GitHub Pages. A push to `master` triggers the production deployment.

Monitor workflow runs in the repository's Actions tab. The live site is:

https://scott-love.github.io/

Do not add back Netlify configuration, the old self-referencing Git submodule, or the obsolete Wowchemy/Academic updater scripts.

## Content and data pipeline

Phase 1 work investigates how the `scott-love/academic-cv` repository can provide structured data for HugoBlox content. Until that pipeline is implemented, edit the site's content using the existing HugoBlox content structure and document automation changes before introducing them.

## Troubleshooting

- **Hugo command not found:** install Hugo Extended and ensure it is on `PATH`.
- **Module errors:** run `hugo mod tidy` and retry the build.
- **Missing CSS:** run `npm ci` and confirm the Hugo build completes without errors.
- **Pages deployment failure:** inspect the failed job in Actions and confirm the Pages source is GitHub Actions.
- **Unexpected generated files:** leave `public/`, `_vendor/`, `resources/_gen/`, and `node_modules/` untracked; they are generated or local directories.
