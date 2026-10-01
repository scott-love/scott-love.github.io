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

## Deployment

The workflow in `.github/workflows/deploy.yml` builds and deploys the site to GitHub Pages. Pushes to `master` trigger production deployment.

Do not use the old Netlify, submodule, or manual `deploy.sh` workflow. The repository now contains the site source and deployment configuration in one place.

## Documentation

- [Migration guide](./MIGRATION.md)
- [Migration checklist](./MIGRATION_CHECKLIST.md)
- [Phase 0 summary](./PHASE_0_SUMMARY.md)
- [Contributing and development guide](./.github/CONTRIBUTING.md)
- [academic-cv repository](https://github.com/scott-love/academic-cv)
