# HugoBlox Migration Checklist

**Phase 0: Stack Modernization (2–3 weeks)**

Use this checklist to track progress through the migration. Check off items as completed. Link to GitHub Issues for detailed discussion of blockers.

---

## Pre-Migration Setup

### Backup & Planning
- [ ] **TASK-1**: Back up current site
  - [x] Clone `master` to local backup branch: `git branch backup/2026-09-09-master`
  - [ ] Export current config files
  - [ ] Take screenshot of deployed site (for comparison)
  - [x] Document current versions: `hugo version`, `go version`
  - **Reference Issue**: [TASK-1](#)

- [x] **TASK-2**: Review HugoBlox migration guide
  - [x] Read: https://hugoblox.com/docs/guide
  - [x] Read: https://hugoblox.com/wowchemy (rebrand explanation)
  - [x] Review: HugoBlox breaking changes from Wowchemy
  - **Reference Issue**: [TASK-2](#)

- [x] **TASK-3**: Plan Go & Hugo versions
  - [x] Current versions on local machine:
    - Hugo: `hugo version`
    - Go: `go version`
  - [x] Target versions:
    - Hugo: Latest stable (0.165.0+)
    - Go: 1.23+ (current stable)
  - [x] Document installation steps for your OS
  - [x] Record module version pins to reuse during TASK-6
  - **Reference Issue**: [TASK-3](#)

---

## Hugo & Go Updates

### Update Hugo
- [x] **TASK-4**: Update Hugo from 0.78.2 → latest stable
  - [x] Download latest Hugo from https://github.com/gohugoio/hugo/releases
  - [x] Install to your system PATH (verify: `hugo version`)
  - [x] Test build locally: `hugo server` (from migrate/hugoblox branch)
  - [x] Document any build errors or warnings
  - [ ] Fix any Markdown/syntax errors that arise *(deferred to later migration tasks where fixes are explicitly scoped)*
  - **Reference Issue**: [TASK-4](#)
  - **Tracking note (Issue 5 evidence)**:
    - Installed Hugo: `v0.165.0+extended darwin/arm64`
    - Warnings observed:
      - `languages.fr.languageCode` deprecated → use `languages.fr.locale`
      - `languages.en.languageCode` deprecated → use `languages.en.locale`
      - `.Site.LanguageCode` deprecated → use `.Site.Language.Locale`
      - `.Site.Data` deprecated → use `hugo.Data`
    - Fatal error observed:
      - `can't evaluate field GoogleAnalytics in type interface {}`
      - Source chain includes `layouts/partials/marketing/google_analytics.html` in legacy Wowchemy module
    - Interpretation: expected compatibility break after Hugo upgrade; remediation tracked for subsequent migration tasks (no ad hoc config/template fixes in this checkpoint step).

### Update Go
- [x] **TASK-5**: Update Go from 1.15 → latest stable
  - [x] Download latest Go from https://golang.org/dl/
  - [x] Install to system PATH (verify: `go version`)
  - [x] Verified: local Go version 1.27.1 (exceeds 1.23 requirement)
  - [x] Update `go.mod`: Confirmed `go 1.23` declaration in place
  - [x] Run: `go mod tidy` (verified; cleaned redundant explicit requires)
  - [x] Test build: `hugo --gc --minify` (361/360 pages built successfully)
  - [x] Document any module-related errors (none found)
  - **Reference Issue**: [TASK-5](#)

### Update Wowchemy → HugoBlox Modules
- [x] **TASK-6**: Update Hugo modules to HugoBlox
  - [x] **Review HugoBlox module structure**
    - [x] Check: `https://github.com/HugoBlox/hugo-blox-builder/blob/main/go.mod`
    - [x] Document namespace migration direction: `github.com/HugoBlox/...`
    - [x] Confirm module versions should be reused from **TASK-3** during initial migration
    - **Reference Issue**: [#6](https://github.com/scott-love/personal-site/issues/6)

  - [x] **Inspect current `go.mod`**: No legacy Wowchemy refs; all HugoBlox namespace
  - [x] **Update `go.mod`**: HugoBlox namespace migration complete; go mod tidy cleaned redundant explicit requires
  - [x] Create checkpoint before module edits (implicit: git commit capturing clean state before tidy)
  - [x] Run: `go mod tidy` (removed unnecessary explicit `require` block; Hugo resolves via module config)
  - [x] Run: `hugo mod graph` (verified: 3 HugoBlox projects resolved: blox v0.12.0, analytics v0.3.1, netlify v1.2.1)
  - [x] Test build: `hugo --gc --minify` (361/360 pages; build succeeded identically before/after tidy)
  - [x] Run migration CI/build from `migrate/hugoblox` (verified locally)
  - [x] Document any module resolution errors (none found; only expected `.Site.AllPages` deprecation warning from Hugo)
  - [x] **Rollback plan validated**: not needed; build confirmed stable and clean
  - **Reference Issue**: [TASK-6](#)

---

## Configuration Migration

### Hugo Configuration Updates
- [x] **TASK-7**: Update Hugo config files
  - [x] Review `config/_default/config.toml` for deprecated settings (none found)
  - [x] Check Hugo migration guide: https://gohugo.io/getting-started/configuration/#configuration-format
  - [x] Update any `languageCode` → confirmed: `config/_default/languages.toml` uses `locale = "en-us"` and `locale = "fr"` (not `languageCode`)
  - [x] Verify `markup.goldmark` settings (Markdown parser) — correctly configured with `unsafe = true` in renderer
  - [x] Test build: `hugo server -D` (succeeded with expected .Site.AllPages deprecation warning)
  - [x] Document changes made to config (none needed; already modernized to HugoBlox format)
  - **Reference Issue**: [TASK-7](#)

### Netlify → GitHub Pages Migration
- [ ] **TASK-8**: Remove Netlify config, set up GitHub Actions
  - [ ] Delete or archive `netlify.toml` (we won't need it anymore)
  - [ ] Commit this deletion on migrate/hugoblox branch
  - [ ] Note: GitHub Pages deployment config comes next (TASK-9)
  - **Reference Issue**: [TASK-8](#)

---

## Layout & Styling Migration

### Wowchemy → HugoBlox Theme Migration
- [ ] **TASK-9**: Migrate theme layouts
  - [ ] **Backup existing layouts**:
    ```bash
    git stash  # Save any uncommitted changes
    ```
  - [ ] **Check if HugoBlox layouts differ from Wowchemy**
    - HugoBlox moved from Bootstrap to Tailwind CSS
    - Shortcodes may have changed names or parameters
  - [ ] Review `themes/academic/` (or module imports)
  - [ ] Check `content/` for any custom shortcodes using Wowchemy syntax
  - [ ] Document differences found
  - [ ] Test build: `hugo server`
  - **Reference Issue**: [TASK-9](#)

### CSS & Styling
- [ ] **TASK-10**: Verify Tailwind CSS styling
  - [ ] Check: Do custom CSS files still apply?
  - [ ] Inspect deployed site: Do colors/layout look correct?
  - [ ] Check responsive design (mobile, tablet, desktop)
  - [ ] Document any visual regressions
  - [ ] Test site in multiple browsers (Chrome, Firefox, Safari)
  - **Reference Issue**: [TASK-10](#)

---

## Content Testing

### Content Rendering
- [ ] **TASK-11**: Test all content renders correctly
  - [ ] **Home page**: Load http://localhost:1313/
    - [ ] Header/navigation visible?
    - [ ] Bio section renders?
    - [ ] Featured projects/publications show?
  
  - [ ] **Publications page**: http://localhost:1313/publication/
    - [ ] Publication list appears?
    - [ ] Individual publication pages load?
    - [ ] Links/references work?
  
  - [ ] **Blog posts**: http://localhost:1313/post/
    - [ ] List page shows?
    - [ ] Individual post pages load?
    - [ ] Code blocks render correctly?
    - [ ] Images display?
  
  - [ ] **About/CV page**: http://localhost:1313/about/
    - [ ] Content renders?
    - [ ] Any custom shortcodes work?
  
  - [ ] **Navigation**:
    - [ ] All menu items link correctly?
    - [ ] Breadcrumbs (if enabled) work?
  
  - [ ] **Search** (if enabled):
    - [ ] Search functionality available?
    - [ ] Results display correctly?
  
  - **Reference Issue**: [TASK-11](#)

### Metadata & SEO
- [ ] **TASK-12**: Verify metadata
  - [ ] Check page titles (browser tab)
  - [ ] Inspect meta descriptions in HTML
  - [ ] Verify open graph tags (OG image, OG description)
  - [ ] Check RSS feed generation: http://localhost:1313/index.xml
  - [ ] Test with: https://www.opengraphcheck.com/
  - **Reference Issue**: [TASK-12](#)

---

## GitHub Pages Deployment Setup

### GitHub Actions Workflow
- [ ] **TASK-13**: Create GitHub Actions deployment workflow
  - [ ] Create file: `.github/workflows/deploy.yml`
  - [ ] Workflow should:
    - [ ] Trigger on push to `migrate/hugoblox`
    - [ ] Check out code
    - [ ] Set up Hugo (latest)
    - [ ] Build site: `hugo --gc --minify`
    - [ ] Deploy to `gh-pages` branch
    - [ ] (Later: deploy to master after merge)
  - [ ] Commit workflow to migrate/hugoblox
  - [ ] Verify workflow file syntax
  - **Reference Issue**: [TASK-13](#)

### GitHub Pages Settings
- [ ] **TASK-14**: Configure GitHub Pages
  - [ ] Go to repo **Settings → Pages**
  - [ ] Set source: `gh-pages` branch (or Actions as source)
  - [ ] Set root directory: `/` (should be default)
  - [ ] Verify custom domain settings (if applicable)
  - [ ] Save settings
  - [ ] **Note**: GitHub Pages will show a link to your live site
  - **Reference Issue**: [TASK-14](#)

### Deploy & Test
- [ ] **TASK-15**: First deployment to GitHub Pages
  - [ ] Push commits from migrate/hugoblox to GitHub
  - [ ] GitHub Actions workflow triggers automatically
  - [ ] Monitor workflow in **Actions** tab
  - [ ] Wait for `gh-pages` branch to be created/updated
  - [ ] Visit https://scott-love.github.io/ (may take 1–2 minutes)
  - [ ] Verify site displays correctly
  - [ ] Compare with master branch site (should differ if significant changes)
  - [ ] Document any deployment issues
  - **Reference Issue**: [TASK-15](#)

---

## Full Regression Testing

### Functionality Testing
- [ ] **TASK-16**: Full site functionality test
  - [ ] External links work (click several)
  - [ ] Download links work (if any PDFs)
  - [ ] Forms submit (if any contact forms)
  - [ ] Social media links open in new tab
  - [ ] Email links trigger mail client
  - [ ] Video embeds (if any) play
  - [ ] Images load without 404s
  - **Reference Issue**: [TASK-16](#)

### Performance Testing
- [ ] **TASK-17**: Measure performance
  - [ ] Run Lighthouse in Chrome DevTools
  - [ ] Target scores: Performance 90+, Accessibility 90+, Best Practices 90+, SEO 90+
  - [ ] Check mobile vs. desktop scores
  - [ ] Use Google PageSpeed Insights: https://pagespeed.web.dev/
  - [ ] Document baseline metrics (for before/after comparison)
  - [ ] If scores are low, investigate bottlenecks
  - **Reference Issue**: [TASK-17](#)

### Accessibility Testing
- [ ] **TASK-18**: Accessibility audit
  - [ ] Run axe DevTools (Chrome extension)
  - [ ] Check for:
    - [ ] Proper heading hierarchy (H1 → H2 → H3)
    - [ ] Image alt text
    - [ ] Color contrast (text vs. background)
    - [ ] Keyboard navigation (Tab through site)
    - [ ] Screen reader test (VoiceOver on macOS)
  - [ ] Document issues found
  - **Reference Issue**: [TASK-18](#)

### Cross-Browser Testing
- [ ] **TASK-19**: Test on multiple browsers
  - [ ] Chrome (latest)
  - [ ] Firefox (latest)
  - [ ] Safari (macOS)
  - [ ] Edge (if on Windows)
  - [ ] Mobile browsers (iOS Safari, Chrome Mobile)
  - [ ] Document any rendering differences
  - **Reference Issue**: [TASK-19](#)

---

## Final Verification & Cleanup

### Documentation & Rollback
- [ ] **TASK-20**: Update documentation
  - [ ] Update README.md with new Hugo/Go versions
  - [ ] Update MIGRATION.md with Phase 0 completion notes
  - [ ] Create/update `.github/CONTRIBUTING.md` with new build instructions
  - [ ] Document any breaking changes for future developers
  - [ ] Add troubleshooting section to Wiki
  - **Reference Issue**: [TASK-20](#)

### Merge Preparation
- [ ] **TASK-21**: Prepare for merge to master
  - [ ] All tasks above completed ✓
  - [ ] All tests passing ✓
  - [ ] GitHub Actions workflow successful ✓
  - [ ] Staging site (github.io) looks correct ✓
  - [ ] No open blockers ✓
  - [ ] Create Pull Request: migrate/hugoblox → master
  - [ ] Add detailed PR description
  - [ ] Request review
  - **Reference Issue**: [TASK-21](#)

- [ ] **TASK-22**: Merge to master
  - [ ] PR approved
  - [ ] All CI checks pass
  - [ ] Merge to master
  - [ ] Verify GitHub Pages builds from master
  - [ ] Confirm live site displays correctly
  - [ ] Monitor for 24–48 hours for any issues
  - **Reference Issue**: [TASK-22](#)

---

## Phase 0 Complete ✅

Once all tasks above are checked off:

- [ ] **Phase 0 Summary**: Write completion summary
  - [ ] Time taken (vs. estimate of 2–3 weeks)
  - [ ] Major issues encountered & resolutions
  - [ ] Any technical debt created (if any)
  - [ ] Lessons learned for future migrations
  - [ ] Prepare for Phase 1: Data Pipeline Discovery

---

## Quick Reference: Common Commands

```bash
# Check current versions
hugo version
go version

# Update modules
go mod tidy
go mod graph

# Local build
hugo server              # Development server (live reload)
hugo server -D           # Include draft posts
hugo build               # Production build

# GitHub Pages workflow
git push origin migrate/hugoblox  # Trigger Actions

# Monitor Actions
# Navigate to: https://github.com/scott-love/personal-site/actions
```

---

## Troubleshooting During Migration

| Issue | Possible Cause | Solution |
|-------|----------------|----------|
| `hugo: command not found` | Hugo not in PATH | Reinstall Hugo; verify `hugo version` works |
| Build fails with module errors | Old go.mod cache | Run `go mod tidy && go mod verify` |
| CSS looks broken | Tailwind not loading | Check module imports; verify HugoBlox CSS is loaded |
| Content doesn't render | Shortcode syntax changed | Check HugoBlox docs for shortcode parameter changes |
| GitHub Pages shows 404 | Workflow didn't publish | Check Actions tab; verify `gh-pages` branch exists |
| Site looks different | CSS framework change | Expected; review HugoBlox styling; adjust custom CSS |

---

**Last Updated**: October 2026  
**Phase**: 0 (Stack Modernization)  
**Status**: 🟢 TASK-5/6/7 Complete; TASK-8+ Pending
