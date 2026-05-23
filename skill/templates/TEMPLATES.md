# Template Selection Guide

## Decision Tree

```
IF "ai win story" OR "win story" OR "ai_win_story_template"
  → ai-win-story

ELSE IF "architecture" OR "system design" OR "design doc"
  → architecture-doc

ELSE IF "user guide" OR "guide doc"
  → user-guide

ELSE IF "implementation plan" OR "plan doc" OR "prd"
  → implementation-flow

ELSE IF "data" OR "pipeline" OR "ETL" OR "ingestion"
  → data-flow

ELSE IF "infrastructure" OR "network" OR "deployment" OR "VPC"
  → infra-flow

ELSE
  → page (default)
```

## Template Specs

### ai-win-story
**Trigger phrases:** "ai win story", "win story", "ai_win_story_template"
**File:** `templates/ai-win-story.html`
**Reference (single source of truth):** `reference/ai_win_story_ref_template.md`
→ Required sections, placeholders, format rules, and live example URL are all in the reference file. Do not duplicate them here.

### architecture-doc
**Trigger phrases:** "architecture", "system design", "design doc"
**File:** `templates/architecture.html`
**Reference (single source of truth):** `reference/architecture_ref_template.md`
→ Required sections, placeholders, format rules are all in the reference file. Do not duplicate them here.

### user-guide
**Trigger phrases:** "user guide", "guide doc"
**File:** `templates/user-guide.html`
**Reference (single source of truth):** `reference/user_guide_ref_template.md`
→ Required sections, placeholders, format rules are all in the reference file. Do not duplicate them here.

### prd-doc
**Trigger phrases:** "implementation plan", "plan doc", "prd"
**File:** `templates/prd.html`
**Reference (single source of truth):** `reference/prd_ref_template.md`
→ Required sections, placeholders, format rules are all in the reference file. Do not duplicate them here.

### data-flow
**Trigger phrases:** "data flow", "pipeline", "ETL", "ingestion", "data architecture"
**File:** `templates/data-flow.html`
**Reference (single source of truth):** `reference/data_flow_ref_template.md`
→ Required sections, placeholders, format rules are all in the reference file. Do not duplicate them here.

### infra-flow
**Trigger phrases:** "infrastructure", "network", "deployment", "VPC", "infra"
**File:** `templates/infra-flow.html`
**Reference (single source of truth):** `reference/infra_flow_ref_template.md`
→ Required sections, placeholders, format rules are all in the reference file. Do not duplicate them here.

### page
**Use**: General documentation, simple pages, default fallback
**Includes**: Title, overview, details, additional info
**Diagram**: Optional, not included by default

## Template Content Structure

All templates use Confluence storage format (HTML-like):
- `<h1>` for title
- `<h2>` for sections
- `<ac:structured-macro ac:name="info">` for callout boxes
- `<ac:structured-macro ac:name="panel">` for colored panels
- `{{page.diagram_placeholder}}` marks where diagram should be embedded
