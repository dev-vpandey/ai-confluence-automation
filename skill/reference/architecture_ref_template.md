# Architecture / Design Doc — Reference (Single Source of Truth)

> This file is the single source of truth for the architecture / design doc page type.
> - Generate HTML implementing this structure when a new architecture or design doc is requested
> - `templates/TEMPLATES.md` and `SKILL.md` point here — they do NOT duplicate section rules
> When structure changes, update this file first, then sync generated HTML to match.

---

## Required Sections (in order — never reorder, never omit)

| #  | Section                  | Content Rules |
|----|--------------------------|---------------|
| 1  | **Header Metadata**      | Author, Date (YYYY-MM-DD), Status (Draft / In Review / Approved), Audience, PRD link, Reviewers, Approved by (Name + Date) — rendered as `info` panel or `class="wrapped"` table |
| 2  | **Version History**      | Table: Version / Date / Author / Summary of changes |
| 3  | **Problem**              | One paragraph — what doesn't work today and why it matters technically |
| 4  | **Goal**                 | One sentence — what this design achieves |
| 5  | **Non-Goals**            | Bullet list — what is explicitly out of scope |
| 6  | **Architecture**         | High-level diagram or ASCII flow (`{{page.diagram_placeholder}}` if complex). Must include: **Deployment** (K8s / Lambda / on-prem / etc.), **Data flow** (sync / async / event-driven), **External dependencies** list. Followed by **Components** subsection: `<h3>Components</h3>` — one paragraph max per component describing what it does, what it owns, what it calls |
| 7  | **Proposed Solution**    | Explain the solution in plain terms before diving into implementation detail. Must include: (a) 1–2 paragraphs on the mechanism and why it fits, (b) ownership boundaries (who owns what), (c) a numbered **end-to-end flow** subsection (`<h3>`) showing exactly how a request/event moves through the system, (d) a **Why this approach** subsection (`<h3>`) with bullet points covering what makes this option the right fit |
| 8  | **Key Decisions**        | One `<h3>` block per non-obvious decision. Each block must include: options considered (bullet list with pros/cons), chosen option, and 1–2 sentence reason |
| 9  | **Data Model**           | Only if schema changes — show before/after or new schema as code block (SQL or equivalent). If no schema changes, add placeholder noting N/A |
| 9  | **API / Interface Changes** | Endpoint, function signature, or CLI flag changes. Before/after if modifying existing. If none, add placeholder |
| 10 | **Security & Access**    | Bullet list covering: Auth mechanism, PII / sensitive data (yes/no + what), Threat surface changes (yes/no + what) |
| 11 | **Observability**        | 3 bullets max per sub-item: Metrics (what to instrument), Logs (key events to log), Alerts (thresholds / on-call implications) |
| 12 | **Performance Envelope** | Bullet list: Expected throughput (req/s, events/day, etc.), Latency SLO (p99 target), Scale ceiling (max before re-design needed) |
| 13 | **Testing Strategy**     | Bullet list: Unit (what is unit-tested), Integration (what systems tested together), Load / stress (yes/no + tool + threshold), Rollout gate (criteria to proceed phase 1 → 2) |
| 14 | **Error Handling**       | Table: Scenario / Behavior — `class="wrapped"` |
| 15 | **Rollout Plan**         | Bullet list: Phase 1 (what, who, when); Rollback (how to revert) — wrap rollback in `warning` macro |
| 16 | **Open Questions**       | `info` macro — checkbox list, each with owner and needed-by date |
| 17 | **References**           | Bullet list of links: PRD, related ADRs, related tickets, related resources |

> If content for a section isn't available, add a placeholder — **never skip a section**.

---

## Status Values

Valid values for the Status metadata field: `Draft`, `In Review`, `Approved`

---

## Confluence Rendering Notes

- Header Metadata → `<ac:structured-macro ac:name="info">` panel or `class="wrapped"` table
- Architecture diagram → `{{page.diagram_placeholder}}` inside Architecture section
- Proposed Solution → `<h3>` subsections for "End-to-end flow" (numbered `<ol>`) and "Why this approach" (bullet `<ul>`) inside the Proposed Solution `<h2>` block
- Key Decisions → `<h3>` subsections inside the Key Decisions `<h2>` block
- Components → `<h3>Components</h3>` subsection inside Architecture `<h2>` block
- Error Handling → `class="wrapped"` HTML table
- Rollback step → `<ac:structured-macro ac:name="warning">` callout
- Open Questions → `<ac:structured-macro ac:name="info">` with `<ac:task-list>` checkboxes
- Code blocks (SQL, API signatures) → `<ac:structured-macro ac:name="code">` blocks
