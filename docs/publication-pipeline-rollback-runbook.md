# Publication Pipeline Rollback Runbook

**Scope:** Publication refreshes and generated-content PRs for `scott-love/scott-love.github.io`  
**Applies to:** publication import workflow, override application, and generated Hugo bundles

## When to use this runbook

Use this runbook when a publication refresh causes:
- incorrect or missing publication content
- broken Hugo builds
- bad overrides or unexpected editorial changes
- source data regressions from `academic-cv`
- exporter bugs in generated publication artifacts
- website integration failures during import or validation

## Primary rollback method

Preferred rollback is a revert of the offending merge or commit on `master`.

### If the bad change is already merged
1. Identify the offending commit or merge commit.
2. Create a revert commit on `master`.
3. Push the revert.
4. Wait for GitHub Pages deployment to complete.
5. Verify the live site.

### If the bad change is only in an open PR
1. Close or update the PR.
2. Remove or replace the bad content in the branch.
3. Re-run validation checks.
4. Re-open the PR only when the issue is fixed.

## Post-rollback verification

After rollback:
- Confirm the GitHub Pages workflow succeeded.
- Confirm the homepage loads.
- Confirm publication listings render.
- Confirm the affected publication bundles look correct.
- Confirm override-sensitive fields such as featured flags, tags, images, and links are still intact.

## Failure playbooks

### 1. Source data regression
Symptoms:
- wrong publications imported
- expected records missing
- unexpected removals

Actions:
- compare the imported artifact with the last known good source run
- verify `academic-cv` source data
- regenerate the artifact from the corrected source
- re-run import workflow

### 2. Exporter bug
Symptoms:
- malformed generated front matter
- wrong HAL mapping
- incorrect bundle naming
- bad dates or links

Actions:
- fix exporter logic in `academic-cv`
- regenerate the artifact
- re-import into the website repo
- verify with Hugo build and tests

### 3. Website integration failure
Symptoms:
- import workflow fails
- override application fails
- Hugo build fails after import

Actions:
- inspect workflow logs
- fix website-side content or workflow logic
- re-run the import workflow
- validate with build and tests

## Recovery checklist
- [ ] Identify the failure source
- [ ] Revert or correct the bad change
- [ ] Re-run validation
- [ ] Confirm Pages deployment
- [ ] Verify live site