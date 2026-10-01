# Copilot Space Instructions — scott-love/scott-love.github.io

## Purpose

This Space supports modernization and ongoing development of Scott Love’s HugoBlox website, with a focus on maintaining a reliable data pipeline from canonical academic records to website content.

---

## Repository and Branch Truth

- **Primary active repository:** `scott-love/scott-love.github.io`
- **Archived repository (do not use for new work):** `scott-love/personal-site`
- **Production branch / source of truth:** `master`
- **Deployment target:** GitHub Pages via GitHub Actions
- **Deployment workflow:** `.github/workflows/deploy.yml`

Assume all new work targets `master` directly or via PRs into `master`.

---

## Current Program Status

- **Phase 0 (HugoBlox migration):** Complete and deployed.
- **Phase 1 (Data Pipeline Discovery):** Publications path implemented (HAL-based publication bundles + editorial override system); broader pipeline design documented.
- **Phase 2 (Implementation backlog):** Defined; execution in progress/planned (automation from `academic-cv` to reviewable website PRs with CI safety gates).

---

## Data Ownership and System Boundaries

### Canonical academic data source
- Repository: `scott-love/academic-cv`
- Canonical bibliographic/publication facts originate there.

### Website presentation source
- Repository: `scott-love/scott-love.github.io`
- Website-specific editorial/presentation data lives here.

### Ownership rule
- `academic-cv` owns canonical facts (title, authors, venue, identifiers, etc.).
- Website repo owns editorial fields (e.g., featured flags, tags, images, curated links, display-oriented abstract text where applicable).

Do not move website editorial ownership into `academic-cv` unless explicitly decided in a future architecture change.

---

## Publications Model (Current)

Active publication bundles use HAL-based identifiers under:

- `content/en/publication/hal-*/index.md`

Legacy pre-migration bundles are retained only for reference under:

- `content/en/publication_archive_pre_hal_migration/`

Archive content must remain excluded from active rendering/build outputs.

---

## Editorial Override System (Current)

Override files and tooling in website repo:

- `data/publication_overrides.yml`
- `scripts/apply_publication_overrides.py`
- `tests/test_apply_publication_overrides.py`

Expected behavior:

1. Canonical publication content is generated from `academic-cv`.
2. Website editorial overrides are applied afterward.
3. Only editorial allowlist fields are overridden (not canonical bibliographic fields).
4. Unknown HAL IDs and malformed override entries should fail validation.
5. `--check` mode is used for validation/reporting in CI and local checks.
6. Override application should be idempotent.

---

## Tooling Standards

Python tooling in this repository uses `uv`.

Use:

- `uv sync --dev`
- `uv run python scripts/apply_publication_overrides.py --check`
- `uv run python scripts/apply_publication_overrides.py --overrides data/publication_overrides.yml --content-dir content/en/publication`
- `uv run pytest -q`

Site build commands:

- `npm ci`
- `hugo server -D` (local dev)
- `hugo --gc --minify` (production-style validation)

---

## Phase 2 Direction (Implementation Guidance)

Target path: **academic-cv change → generated publication artifact or equivalent handoff → reviewable PR in website repo → CI validation → merge to master**.

Key requirements for implementation:

1. Deterministic generated output.
2. Clear diff visibility (added/updated/removed HAL IDs).
3. CI gates for:
   - override validation/idempotence
   - tests
   - Hugo build
4. Guardrails around destructive removals.
5. Operational docs: approval policy, rollback, refresh cadence.

---

## Copilot Behavior Requirements in This Space

1. Prefer repository-grounded answers over generic advice.
2. Preserve established architecture decisions unless user asks to revisit them.
3. For docs/process changes, keep terminology consistent with:
   - `master` as production branch
   - single active repo model
   - `academic-cv` canonical data ownership
4. When proposing changes, include concrete file paths and command examples.
5. Avoid introducing alternate pipelines unless explicitly requested.

---

## Token and Response Efficiency Guidance

When assisting in this Space, **minimize token usage when possible** while preserving accuracy:

1. Default to concise answers.
2. Use bullet points and short checklists over long prose.
3. Provide diffs or targeted snippets instead of repeating full files unless asked.
4. Avoid re-explaining already agreed decisions.
5. If a task is repetitive (e.g., issue templates), provide compact reusable patterns.
6. For large outputs, offer:
   - a short summary first
   - full expanded content only on request

Be brief-by-default, detailed-on-demand.

---

## Preferred Output Style for Repo Changes

- If asked for file edits, provide either:
  - a minimal unified diff, or
  - complete replacement content when explicitly requested.
- Keep commit messages short and action-oriented.
- Keep issue titles prefixed with `[Phase 2]` for Phase 2 tracking work.

---

## Safety and Validation

Before recommending merge/deploy steps, verify:

- commands align with current repo tooling (`uv`, Hugo, npm),
- paths exist and match current structure,
- proposed automation does not bypass review/CI safeguards.

If uncertain, state uncertainty explicitly and suggest the smallest safe validation step.
### When Working on a Task
1. **Read the full issue** before starting
2. **Check the checklist** in the issue description
3. **Follow the exact branch**: `migrate/hugoblox`
4. **Commit with clear messages**:
   ```bash
   git add <files>
   git commit -m "chore: TASK-X - Brief description"
   git push origin migrate/hugoblox
   ```
5. **Update the issue** with results/blockers
6. **Don't skip testing** - each task has expected outputs

### Key Files in This Space
- **`MIGRATION.md`**: Complete migration guide (in `migrate/hugoblox` branch)
- **`MIGRATION_CHECKLIST.md`**: Step-by-step Phase 0 checklist
- **`.github/copilot-space-instructions.md`**: This file
- **`config/_default/config.toml`**: Hugo configuration (needs updates)
- **`go.mod` / `go.sum`**: Go module definitions (will be updated)

---

## Phase 0 Structure

### Planning Phase (TASK-1 to TASK-3)
- Backup current state and document baseline
- Review breaking changes in HugoBlox/Hugo
- Plan target versions and installation steps

### Update Phase (TASK-4 to TASK-6)
- Install Hugo 0.165.0+
- Install Go 1.23+
- Migrate Wowchemy → HugoBlox modules in `go.mod`

### Configuration Phase (TASK-7 to TASK-9)
- Update Hugo config for 0.78 → 0.165 breaking changes
- Remove Netlify config
- Migrate layouts from Wowchemy to HugoBlox

### Testing Phase (TASK-10 to TASK-19)
- Verify CSS/styling (Tailwind CSS)
- Test all content rendering
- Test metadata and SEO
- Performance testing
- Accessibility audit
- Cross-browser testing

### Deployment Phase (TASK-13 to TASK-15)
- Create GitHub Actions workflow (`.github/workflows/deploy.yml`)
- Configure GitHub Pages in repo settings
- Deploy to staging and test live site

### Finalization (TASK-20 to TASK-22)
- Update documentation
- Prepare PR for merge
- Merge `migrate/hugoblox` → `master`

---

## Common Tasks for Copilot

### "Help me with TASK-X"
I will:
1. Fetch the GitHub issue
2. Review the checklist and expected outputs
3. Guide you through each step
4. Ensure commits go to `migrate/hugoblox`
5. Document results in the issue

### "What commits should I make for TASK-X?"
I will provide:
- Exact commit messages
- Files to stage (`git add`)
- Push command (`git push origin migrate/hugoblox`)
- How to verify the commit was successful

### "I'm blocked on TASK-X"
I will:
1. Ask for the specific error/blocker
2. Check GitHub issue for known issues
3. Suggest troubleshooting steps
4. Help document the blocker in the issue

### "Is TASK-X complete?"
I will:
1. Check the GitHub issue checklist
2. Verify all acceptance criteria met
3. Confirm test results match expected outputs
4. Mark as ready for next task or identify gaps

---

## Important Notes for Copilot

### About Environment Management
- **Do NOT use `uv`** for Phase 0 (Python env manager not needed)
- Hugo is a Go binary (just install via release)
- Go modules managed by `go.mod`/`go.sum` (not Python)
- If Phase 1 adds Python automation, we can introduce `uv` then

### About Testing
- **Local testing**: `hugo server` on `migrate/hugoblox`
- **Do NOT expect perfect results** until all tasks complete
- **CSS/shortcode errors** are expected until TASK-9
- **Module errors** expected until TASK-6
- Document all errors for tracking

### About Rollback
- If critical blocker: reset to `backup/2026-09-09-master` (local only)
- If deployment issues: live site stays on `master` (protected)
- Always test locally before GitHub Actions deployment

### About Commits
- **Commit frequently**: After each logical change
- **Keep commits atomic**: One concern per commit
- **Don't mix TASK concerns**: If fixing CSS + config, make separate commits
- **Use TASK numbers**: `chore: TASK-6 - Migrate Wowchemy to HugoBlox`

---

## When to Escalate (Document in Issue)

1. **Module not found**: Specific package name/version issue
2. **Build fails consistently**: After `go mod tidy` + `hugo server`
3. **Rendering broken for >5% of content**: Indicates layout migration issue
4. **Performance regression**: Lighthouse scores drop >20 points
5. **Accessibility blocker**: Can't keyboard navigate or use screen reader

---

## Success Indicators

✅ Phase 0 is complete when:
1. All 22 tasks show completed checklists
2. `hugo server` builds without errors on `migrate/hugoblox`
3. Local site renders correctly (all pages visible)
4. GitHub Actions workflow runs successfully
5. Staging site (GitHub Pages) displays correctly
6. No open blockers in issue comments
7. PR approved and ready to merge
8. Live site ready to switch to `migrate/hugoblox` → `master`

---

## Quick Reference: Branch Commands

```bash
# Ensure you're on the migration branch
git branch  # Should show: * migrate/hugoblox

# If on master, switch to migration branch
git checkout migrate/hugoblox

# Push changes to migration branch
git push origin migrate/hugoblox

# View commits on migration branch
git log --oneline migrate/hugoblox

# Compare with master
git diff master..migrate/hugoblox
```

---

## Questions for Copilot?

Ask me about:
- **"What does TASK-X do?"** → I'll explain and link to the issue
- **"How do I commit TASK-X changes?"** → I'll give exact git commands
- **"Is the site ready to merge?"** → I'll check all issue statuses
- **"What's the next task?"** → I'll review dependencies and recommend next steps
- **"Where did we leave off?"** → I'll check recent issue comments and commits

---

**Last Updated**: 2026-09-10  
**Branch**: `migrate/hugoblox`  
**Epic Issue**: https://github.com/scott-love/personal-site/issues/1
