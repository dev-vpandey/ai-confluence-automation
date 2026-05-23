# PRD — Reference (Single Source of Truth)

> This file is the single source of truth for the PRD page type.
> - Generate HTML implementing this structure when a PRD is requested
> - `templates/TEMPLATES.md` and `SKILL.md` point here — they do NOT duplicate section rules
> When structure changes, update this file first, then sync generated HTML to match.

---

## Required Sections (in order — never reorder, never omit)

| #  | Section               | Content Rules |
|----|-----------------------|---------------|
| 1  | **Header Metadata**   | Author, Date (YYYY-MM-DD), Status (Draft / In Review / Approved), Audience, Version — rendered as a table or info panel |
| 2  | **Version History**   | Table: Version / Date / Author / Summary of changes |
| 3  | **Stakeholders**      | Table: Role / Name / Responsibility — rows for PM Owner, Eng Lead, Exec Sponsor at minimum |
| 4  | **TL;DR**             | `info` macro — 2–3 bullets: What (one sentence), Why now (business driver), Expected outcome (metric that changes). Exec-readable, no jargon |
| 5  | **Problem**           | What is broken or missing today, who is affected and how badly. Must be specific and quantified — avoid vague statements like "users find it hard to do X" |
| 6  | **Goals**             | Numbered list — each goal specific and measurable with a success metric |
| 7  | **Non-Goals**         | Bullet list — what this initiative explicitly does NOT address, with reason / phase for each deferral |
| 8  | **Constraints**       | Bullet list covering: Budget, Legal / compliance, Tech (platform limits, existing system constraints), Timeline (hard deadline if any) |
| 9  | **Proposed Solution** | High-level approach description; link to Design Doc for implementation detail. Must include: (a) any explicit Assumptions, (b) **User Experience** subsection as numbered flow (User does X → System does Y → User sees Z), (c) **Edge Cases / Error States** subsection |
| 10 | **Alternatives Considered** | Table: Option / Rejected because |
| 11 | **Success Criteria**  | Table: Metric / Baseline / Target / By (date) / How measured — measurable and time-bound |
| 12 | **Dependencies & Risks** | Table: Item / Type (Dependency or Risk) / Owner / Mitigation |
| 13 | **Timeline**          | Table: Phase / Scope / Owner / Target date |
| 14 | **Go-to-Market / Launch** | Bullet list: Comms plan, Feature flag (yes/no + flag name), Docs needed |
| 15 | **Open Questions**    | `info` macro — checkbox list of unresolved questions, each with owner and needed-by date |
| 16 | **References**        | Bullet list of links: Design Doc, related tickets, related resources |

> If content for a section isn't available, add a placeholder — **never skip a section**.

---

## Status Values

Valid values for the Status metadata field: `Draft`, `In Review`, `Approved`

## Audience Values

Typical audiences: `Engineering`, `Data Analysts`, `Leadership` — list all that apply.

---

## Confluence Rendering Notes

- Header Metadata → render as `<ac:structured-macro ac:name="info">` panel or `class="wrapped"` table
- TL;DR → `<ac:structured-macro ac:name="info">` callout box
- Open Questions → `<ac:structured-macro ac:name="info">` callout box with checkboxes (`<ac:task-list>`)
- All data tables → `class="wrapped"` HTML tables
- User Experience flow → `<ol>` numbered list inside Proposed Solution `<h3>` subsection
- Edge Cases → `<ul>` bullet list inside Proposed Solution `<h3>` subsection
- Problem section → plain paragraphs; encourage quantified specifics over vague prose
