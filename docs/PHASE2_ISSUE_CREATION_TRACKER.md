# Phase 2 Issue Creation Tracker

Milestone target: **Phase 2 - Data Pipeline Implementation**  
Repository: `scott-love/scott-love.github.io`  
Mode: use existing labels only (skip missing labels)

## Prep
- [ ] Create milestone `Phase 2 - Data Pipeline Implementation` (UI)
- [ ] Confirm available labels in repo (apply only existing)

---

## Wave 1 — Foundations

- [ ] **Issue #__** [Phase 2] Freeze Hugo exporter schema v1 in academic-cv  
  Suggested labels: `phase-2`, `pipeline`, `academic-cv`, `priority:high`

- [ ] **Issue #__** [Phase 2] Enforce deterministic publication export output  
  Suggested labels: `phase-2`, `pipeline`, `academic-cv`, `validation`, `priority:high`  
  Depends on: schema v1 issue

- [ ] **Issue #__** [Phase 2] Finalize and test publication type mapping  
  Suggested labels: `phase-2`, `pipeline`, `academic-cv`, `validation`, `priority:high`  
  Depends on: schema v1 issue

- [ ] **Issue #__** [Phase 2] Define and test date precision/fallback policy  
  Suggested labels: `phase-2`, `pipeline`, `academic-cv`, `validation`, `priority:high`  
  Depends on: schema v1 issue

---

## Wave 2 — Cross-repo PR path

- [ ] **Issue #__** [Phase 2] Emit website publication artifact from academic-cv CI  
  Suggested labels: `phase-2`, `ci`, `automation`, `academic-cv`, `priority:high`  
  Depends on: schema + determinism + type mapping + date policy

- [ ] **Issue #__** [Phase 2] Add manual import-publication-artifact workflow in website repo  
  Suggested labels: `phase-2`, `website-integration`, `ci`, `automation`, `priority:high`  
  Depends on: artifact issue

- [ ] **Issue #__** [Phase 2] Auto-generate publication diff summary for PRs  
  Suggested labels: `phase-2`, `website-integration`, `automation`, `priority:medium`  
  Depends on: import workflow issue

---

## Wave 3 — Safety gates

- [ ] **Issue #__** [Phase 2] Add override validation + idempotence CI gate  
  Suggested labels: `phase-2`, `validation`, `ci`, `website-integration`, `priority:high`  
  Depends on: import workflow issue

- [ ] **Issue #__** [Phase 2] Add pytest + Hugo build CI gate for generated-content PRs  
  Suggested labels: `phase-2`, `validation`, `ci`, `website-integration`, `priority:high`  
  Depends on: import workflow issue

- [ ] **Issue #__** [Phase 2] Add destructive-change guardrail for publication removals  
  Suggested labels: `phase-2`, `validation`, `ci`, `ops`, `priority:high`  
  Depends on: import workflow + diff summary issues

---

## Wave 4 — Operations & governance

- [ ] **Issue #__** [Phase 2] Document review/approval policy for generated content  
  Suggested labels: `phase-2`, `docs`, `ops`, `priority:medium`  
  Depends on: import workflow + override gate + build gate

- [ ] **Issue #__** [Phase 2] Add rollback runbook for publication pipeline failures  
  Suggested labels: `phase-2`, `docs`, `ops`, `priority:high`  
  Depends on: import workflow + override gate + build gate + guardrail

- [ ] **Issue #__** [Phase 2] Decide and document refresh cadence/triggers  
  Suggested labels: `phase-2`, `ops`, `docs`, `priority:medium`  
  Depends on: import workflow + override gate + build gate

---

## Master issue

- [ ] **Issue #__** [Phase 2] Master tracker — academic-cv → website publication automation
- [ ] Link all 13 issues in checklist format
- [ ] Assign milestone to master + all child issues

---

## Milestone Definition of Done

- [ ] Manual run can generate/import publication updates and open a PR to `master`
- [ ] PR includes added/updated/removed HAL summary
- [ ] CI gates enforce overrides/tests/Hugo build
- [ ] Removal guardrail is active
- [ ] Approval + rollback + cadence docs are published
