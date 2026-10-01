# Academic Data Flow Specification

**Status:** Phase 1 design draft  
**Last updated:** October 1, 2026  
**Source repository:** `scott-love/academic-cv`  
**Website repository:** `scott-love/scott-love.github.io`  
**Production branch:** `master`

## Purpose

This document defines how canonical academic data is transformed into CV outputs and HugoBlox website content while preserving website-specific editorial decisions.

The immediate integration target is publication data. The existing `academic-cv` repository already maintains structured academic data and refreshes publications from HAL. The HugoBlox website should consume that canonical data rather than maintain a second independent publication-ingestion pipeline.

## Design principles

1. `academic-cv` owns canonical academic facts.
2. The HugoBlox website owns presentation and editorial metadata.
3. Generated content must be deterministic and reviewable.
4. A change to canonical CV data should be capable of producing a corresponding website update.
5. Website-only presentation changes must not require changes to the CV source data.
6. Automation must validate data before it reaches the production website.
7. Destructive changes should be recoverable during the initial implementation.

## Repository responsibilities

### `scott-love/academic-cv`

This repository is the current canonical source for academic data and CV generation. It currently contains:

- Structured YAML data for profile, education, employment, funding, grants, honors, languages, supervision, and teaching.
- `data/publications.json`, refreshed from HAL by `scripts/fetch_hal.py`.
- Python scripts that generate ModernCV-compatible LaTeX.
- GitHub Actions automation that builds CV PDFs and publishes releases.

The repository should eventually provide an export command that converts canonical data into a versioned, Hugo-compatible representation.

### `scott-love/scott-love.github.io`

This repository is the canonical source for the HugoBlox website and GitHub Pages deployment. It owns:

- Hugo configuration and theme integration.
- Website layouts and presentation.
- Website navigation and landing-page composition.
- Editorial metadata such as featured items, tags, images, summaries, and custom links.
- Generated Hugo content received from the academic data pipeline.
- Production deployment from `master` through GitHub Actions.

The website should not independently fetch publications from HAL.

## Current academic-cv pipeline

The current CV pipeline is:

```text
data/profile.yml
 data/*.yml
 data/publications.json
        |
        +--> scripts/generate_cv_latex.py
        |       |
        |       +--> cv/cv.tex
        |       +--> cv/cv_short.tex
        |
        +--> xelatex
                |
                +--> cv/cv.pdf
                +--> cv/cv_short.pdf
```

Publication refresh currently follows this path:

```text
HAL API
   |
   +--> scripts/fetch_hal.py
          |
          +--> data/publications.json
```

The proposed website export extends the existing pipeline:

```text
canonical academic-cv data
        |
        +--> CV generation
        |
        +--> Hugo export
                |
                +--> generated Hugo publication/profile content
```

## Current HugoBlox content model

The website uses Hugo content bundles under language-specific content roots, including:

```text
content/en/
content/fr/
```

Publications currently live under:

```text
content/en/publication/
```

Existing publication bundles contain `index.md` files with HugoBlox front matter such as:

- `title`
- `authors`
- `date`
- `publication_types`
- `publication`
- `abstract`
- `tags`
- `featured`
- `hugoblox.ids`
- `links`
- `image`

The homepage renders publication collections using HugoBlox collection blocks. New generated publication bundles must remain compatible with those blocks.

## Initial integration target: publications

Publications are the first integration target because:

- `academic-cv` already has a structured `data/publications.json` collection.
- Publication records are refreshed from HAL.
- Records include stable HAL identifiers.
- The website already renders publications as Hugo content bundles.
- Publication generation can be tested without redesigning the entire profile or homepage.

The initial exporter should generate publications first. Education, employment, teaching, supervision, and other profile content should be evaluated after the publication path is stable.

## Proposed generated output

New generated publication bundles should use the canonical HAL identifier as their directory name:

```text
content/en/publication/hal-05689674/index.md
content/en/publication/hal-05687484/index.md
content/en/publication/hal-05677734/index.md
```

The exporter should create the complete active publication collection from `academic-cv` data rather than attempt to match each existing author/year bundle. Existing website publication bundles may be archived during the transition and can be removed after the regenerated collection has been reviewed.

A generated record should have a shape similar to:

```yaml
---
title: "Longitudinal MRI template of the baboon brain from birth to adolescence"
authors:
  - "Katherine L Bryant"
  - "Arnaud Le Troter"
date: "2026-01-01T00:00:00Z"
publication_types:
  - "article-journal"
publication: "Imaging Neuroscience"
hugoblox:
  ids:
    hal: "hal-05689674"
    doi: "10.1162/IMAG.a.1316"
links:
  - type: url
    url: "https://amu.hal.science/hal-05689674v1"
---
```

The date representation is provisional. When the source only supplies a year, the exporter must use an explicit and documented fallback rather than implying a precise publication date.

## Source-to-HugoBlox publication mapping

| `academic-cv` field | HugoBlox output | Ownership |
|---|---|---|
| `hal_id` | Bundle identity and `hugoblox.ids.hal` | Canonical |
| `docid` | Optional internal metadata | Canonical |
| `title` | `title` | Canonical |
| `authors` | `authors` | Canonical |
| `year` | Publication date/year | Canonical, transformed |
| `category` | `publication_types` mapping | Canonical, transformed |
| `journal` | `publication` | Canonical |
| `doi` | `hugoblox.ids.doi` and DOI link | Canonical |
| `hal_url` | HAL external link | Canonical |
| `conference` | Event or venue metadata | Canonical |
| `presentation_type` | Event/publication metadata | Canonical |
| `conference_start` | Event start date | Canonical |
| `conference_end` | Event end date | Canonical |
| `conference_organizer` | Event metadata | Canonical |
| `city` | Event location | Canonical |
| `country` | Event location | Canonical |
| `volume` | Bibliographic metadata | Canonical |
| `issue` | Bibliographic metadata | Canonical |
| `pages` | Bibliographic metadata | Canonical |
| `publisher` | Bibliographic metadata | Canonical |
| `series` | Bibliographic metadata | Canonical |
| `book_title` | Bibliographic metadata | Canonical |
| `editors` | Bibliographic metadata | Canonical |
| `abstract` when available | `abstract` | Canonical or reviewed |
| `source` | Bibliographic metadata | Canonical |

The exporter should omit empty values rather than emitting empty strings or null-valued front matter unless HugoBlox requires a specific field.

## Publication type mapping

The mapping from HAL/category values to HugoBlox publication types must be explicit, versioned, and tested. An initial mapping may include:

| Source category | HugoBlox type |
|---|---|
| `Journal article` | `article-journal` |
| `Conference presentation` | `paper-conference` |
| `Preprint` | `article` |
| `Book chapter` | `chapter` |
| `Other scientific contribution` | `article` or `misc`, pending review |
| Unknown category | Validation error or explicit fallback |

The final mapping should be confirmed against the HugoBlox theme behavior and the desired publication filters.

## Canonical and editorial ownership

### Generated canonical fields

The exporter should own:

- Title
- Authors
- Publication year/date
- Journal or conference
- DOI
- HAL identifier
- HAL URL
- Publication category
- Conference dates and location
- Volume, issue, and pages
- Publisher and series information
- Other bibliographic identifiers and source metadata

### Website-owned editorial fields

The website should be able to own:

- `featured`
- Tags
- Images
- Website-specific summaries
- Related projects
- Custom PDF links
- Additional external links
- Visibility decisions
- English/French presentation choices
- Display-specific metadata

The generated-content process must not overwrite editorial fields unintentionally.

## Editorial overrides

Editorial overrides should be maintained separately from generated canonical publication content and keyed by stable identifier. A proposed format is:

```yaml
hal-05689674:
  featured: true
  tags:
    - mri
    - brain
    - baboon
  image:
    filename: featured.png
    preview_only: true
  links:
    - type: pdf
      url: "https://example.org/article.pdf"
```

The final location of this file is an open design decision. It may live in the website repository, the academic-cv repository, or a dedicated generated-content configuration area. The preferred initial location is the website repository because these values describe website presentation rather than academic facts.

The transformation precedence is:

```text
canonical academic-cv record
        |
        +--> normalization and Hugo mapping
                |
                +--> website editorial overrides
                        |
                        +--> generated Hugo bundle
```

## Existing publication content during regeneration

The first regeneration should not require record-by-record matching. The planned transition is:

1. Preserve the existing publication bundles in Git history.
2. Move the current active publication bundles to a clearly named archive location or archive commit.
3. Generate a fresh active publication collection from `academic-cv/data/publications.json`.
4. Review the generated site and compare the output with the previous deployed site.
5. Restore selected editorial assets through the override mechanism if needed.
6. Remove the temporary archive only after the regenerated collection is accepted.

The archive is a safety mechanism, not a permanent second publication collection. Archived content must not be rendered as active Hugo content.

## Stable identifier rules

1. Use `hal_id` as the primary publication identifier whenever available.
2. Normalize HAL identifiers to lowercase.
3. Treat HAL version suffixes as versions of one canonical record where appropriate.
4. Use DOI as a secondary identifier.
5. Use title/author/year matching only for diagnostics, not automatic identity assignment.
6. Do not use an author/year slug as the canonical identity for new generated records.
7. Records without a stable identifier require explicit review or an approved fallback identifier.

Suggested identity precedence:

```text
hal_id
  -> DOI
    -> explicit manually approved fallback
      -> validation failure
```

## Record lifecycle behavior

| Situation | Required behavior |
|---|---|
| New canonical record | Generate a new Hugo bundle |
| Existing canonical record changed | Regenerate deterministically and show a diff |
| Existing record no longer present in source data | Archive or report during initial implementation; do not silently lose it |
| Website-only editorial record | Preserve only if explicitly configured as website-owned |
| Duplicate HAL ID | Validation error |
| Missing title | Validation error |
| Missing identifier | Validation error or explicit review path |
| Missing year/date | Validation warning or documented fallback |
| Missing optional bibliographic field | Omit the field |

Although the long-term system may permit automatic deletion of generated records, the first implementation should retain an archive or generated diff so that an unexpected source change is recoverable.

## Validation requirements

The exporter should validate before writing production content. At minimum, it should check:

- Input JSON is valid.
- Each record is an object.
- Every record has a non-empty title.
- Every record has a stable identifier or an explicit approved fallback.
- Stable identifiers are unique.
- Authors are represented consistently.
- Years and dates are parseable.
- Publication categories are known or explicitly handled.
- DOI values are normalized where present.
- URLs are syntactically valid where present.
- Generated front matter parses successfully.
- Output paths are safe and deterministic.
- Editorial overrides reference valid records or are reported as orphaned overrides.

Validation should produce actionable errors and warnings and should return a non-zero exit status for blocking errors.

## Proposed exporter interface

The first implementation may add the following to `academic-cv`:

```text
scripts/generate_hugo_content.py
scripts/validate_publications.py
templates/hugo/publication.md
schemas/publication.schema.json
```

A provisional command-line interface is:

```bash
uv run python scripts/generate_hugo_content.py \
  --input data/publications.json \
  --output build/hugo
```

The exporter should initially write to a temporary output directory. It should not directly mutate the website repository until the output format and tests are stable.

## Testing strategy

The exporter should use fixtures covering at least:

- Journal article with DOI
- Journal article without DOI
- Conference presentation
- Poster
- Preprint
- Record with missing optional conference fields
- Record with many authors
- Duplicate stable identifier
- Missing required field
- Unknown publication category
- Editorial override application
- Orphaned editorial override

Tests should inspect both parsed data and generated file paths. At least one test should perform a Hugo build using representative generated content once the exporter is integrated with the website repository.

## Cross-repository integration options

### Option A: generated-content pull request

```text
academic-cv change
        |
        +--> academic-cv workflow
                |
                +--> generate Hugo content
                        |
                        +--> open PR in scott-love/scott-love.github.io
                                |
                                +--> Hugo validation
                                        |
                                        +--> merge to master
                                                |
                                                +--> GitHub Pages deployment
```

This is the recommended first integration model. It keeps repositories separate while ensuring that canonical CV changes can produce reviewable website changes.

### Option B: published versioned data artifact

`academic-cv` could publish a versioned JSON or archive artifact, and the website workflow could consume a selected version. This provides a clean dependency boundary but adds artifact versioning and update-management work.

### Option C: unified repository

```text
canonical academic data change
        |
        +--> generate CV outputs
        +--> generate Hugo content
        +--> build Hugo website
        +--> deploy website
```

A unified repository may ultimately be the most convenient design because every canonical CV update can produce an atomic website update. It should be reconsidered after the exporter, override model, and validation rules are proven.

## Initial recommendation

Proceed with Option A for the first implementation while keeping repository consolidation open.

This provides:

- Reuse of the existing HAL and CV data pipeline.
- Independent website editorial control.
- Reviewable generated changes.
- A straightforward rollback path.
- A practical basis for deciding whether a monorepo is worthwhile.

The repository merge decision should be revisited after a successful publication export and at least one complete end-to-end update.

## Staged implementation plan

### Phase 1: discovery and design

- [x] Identify `academic-cv` as the canonical academic data source.
- [x] Identify `data/publications.json` as the initial publication source.
- [x] Define stable identifier and regeneration strategy.
- [x] Define canonical versus editorial ownership.
- [x] Define validation and lifecycle requirements.
- [ ] Review and approve this specification.

### Phase 2: exporter implementation

- [ ] Add publication schema and validation.
- [ ] Add deterministic Hugo publication exporter.
- [ ] Add fixtures and tests.
- [ ] Add publication type mapping.
- [ ] Add output and validation documentation.

### Phase 3: website integration

- [ ] Add website editorial override storage.
- [ ] Archive the existing active publication bundles.
- [ ] Generate the new `hal-*` publication collection.
- [ ] Build and inspect the website locally and in Actions.
- [ ] Review links, dates, authors, publication filters, and layout.
- [ ] Remove the temporary archive after acceptance.

### Phase 4: cross-repository automation

- [ ] Define how the exporter output is transferred between repositories.
- [ ] Add a reviewable pull-request workflow.
- [ ] Add status reporting and failure handling.
- [ ] Reassess whether a unified repository is preferable.

## Open decisions

1. Should generated content be committed to the website repository or consumed as a versioned artifact?
2. Where should website editorial overrides live?
3. Should generated content include English only initially, or generate English and French structures together?
4. What date fallback should be used when HAL exposes only a year?
5. Which source categories should map to `article`, `misc`, or custom HugoBlox publication types?
6. Should abstracts be added to `publications.json` before website export?
7. Should the website retain selected PDFs and images through overrides, or should those assets move into a separate website media area?
8. After the first end-to-end publication update, should the two repositories be merged?

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| HAL schema changes | Validate source records and pin/test expected fields |
| Generated content overwrites editorial work | Keep overrides separate and apply them after canonical mapping |
| Source records disappear unexpectedly | Archive or report removals during initial implementation |
| Publication type mapping is incorrect | Version the mapping and test representative records |
| Website build fails after regeneration | Run Hugo validation before merging generated output |
| Cross-repository automation becomes difficult to maintain | Begin with reviewable PRs and explicit artifacts |
| Repository merge creates excessive coupling | Delay consolidation until the data flow is proven |

## Acceptance criteria for the first implementation

The initial publication integration is successful when:

- Every valid source record generates one deterministic Hugo publication bundle.
- Generated bundle names use stable canonical identifiers.
- The website builds successfully with the regenerated collection.
- Publication lists and featured collections render correctly.
- DOI and HAL links are preserved where available.
- Website-specific editorial overrides survive regeneration.
- Validation catches duplicate or malformed records.
- Removed source records produce a visible report or archive action.
- A canonical data change can produce a reviewable website change.
- The process is documented well enough to repeat locally and in CI.
