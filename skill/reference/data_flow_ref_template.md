# Data Flow — Reference (Single Source of Truth)

> This file is the single source of truth for the data-flow / ETL pipeline page type.
> - Generate HTML implementing this structure when a new data flow page is requested
> - `templates/TEMPLATES.md` and `SKILL.md` point here — they do NOT duplicate section rules
> When structure changes, update this file first, then sync the generated HTML to match.

---

## Required Sections (in order — never reorder, never omit)

| # | Section | Content Rules |
|---|---------|---------------|
| 1 | **Overview** | Pipeline name, 2-3 sentences on what it does and why it exists, owning team, schedule, owner, DAG ID |
| 2 | **Pipeline Diagram** | `{{page.diagram_placeholder}}` — Source → Transform → Load flow, goes after overview |
| 3 | **Source Tables** | Table: Table / Schema / Filter / Volume — `class="wrapped"` |
| 4 | **Transformation Steps** | Numbered `<ol>` — each step describes a discrete transformation |
| 5 | **Output Schema** | Table: Column / Type / Description / Source — `class="wrapped"` |
| 6 | **Write Specifications** | Output table, write mode, partition columns, S3 path |
| 7 | **Data Quality Checks** | Bullet list of validations run before/after write |
| 8 | **Volume & Growth** | `info` macro — approximate row counts, data size, growth rate |
| 9 | **Dependencies** | Upstream pipelines or tables this job depends on |
| 10 | **SLA & Error Handling** | `warning` macro — expected completion time, retry logic, failure alerts; use `warning` if SLA is at risk or error handling is manual |

> If content for a section isn't available, add a placeholder — **never skip a section**.
