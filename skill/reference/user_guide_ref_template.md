# User Guide — Reference (Single Source of Truth)

> This file is the single source of truth for the user-guide page type.
> - Generate HTML implementing this structure when a new user guide is requested
> - `templates/TEMPLATES.md` and `SKILL.md` point here — they do NOT duplicate section rules
> When structure changes, update this file first, then sync generated HTML to match.

---

## Required Sections (in order — never reorder, never omit)

| #  | Section                    | Content Rules |
|----|----------------------------|---------------|
| 1  | **Header Metadata**        | Audience, Last updated (YYYY-MM-DD), Version (vX.Y) — rendered as `info` panel or `class="wrapped"` table |
| 2  | **What this does**         | One sentence — what problem this solves for the user. Followed by **Does NOT cover:** line listing explicitly out-of-scope use cases |
| 3  | **Prerequisites**          | Plain bullet list (`<ul>`) — what must be true before the user can start (access, installs, credentials). Followed by "Need access? Contact: [team / link]" line |
| 4  | **Quick Start**            | Fastest path to working — 3–5 steps max as numbered `<ol>`. Must end with "Expected result: [what the user should see]" |
| 5  | **Common Tasks**           | One `<h3>Task N: [Name]</h3>` block per task. Each block must include: "When to use: [situation]" line, then numbered `<ol>` steps |
| 6  | **Limitations**            | `warning` macro — bullet list of known caps and unsupported use cases users will hit |
| 7  | **Reference**              | One `<h3>[Key concept or field]</h3>` block per term — plain-language definition, no jargon |
| 8  | **Troubleshooting**        | Table: Problem / Likely cause / Fix — `class="wrapped"`. Followed by "Still stuck? Contact: [team / Slack / ticket]" and "Feedback: [link]" lines |
| 9  | **What changed in this version** | Bullet list of changes affecting existing users and new capabilities worth knowing. Followed by "[Full release notes](link)" |

> If content for a section isn't available, add a placeholder — **never skip a section**.

---

## Confluence Rendering Notes

- Header Metadata → `<ac:structured-macro ac:name="info">` panel or `class="wrapped"` table
- Prerequisites → `<ul>` plain bullet list (not checkboxes — prerequisites are conditions to verify, not tasks to complete)
- Quick Start → `<ol>` numbered list ending with expected result paragraph
- Common Tasks → `<h3>` subsections inside Common Tasks `<h2>`, each with `<ol>` steps
- Limitations → `<ac:structured-macro ac:name="warning">` callout with `<ul>` inside
- Reference → `<h3>` per term inside Reference `<h2>`
- Troubleshooting → `class="wrapped"` HTML table
