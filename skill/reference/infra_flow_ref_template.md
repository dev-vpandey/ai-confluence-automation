# Infra Flow — Reference (Single Source of Truth)

> This file is the single source of truth for the infra-flow / infrastructure page type.
> - Generate HTML implementing this structure when a new infra page is requested
> - `templates/TEMPLATES.md` and `SKILL.md` point here — they do NOT duplicate section rules
> When structure changes, update this file first, then sync the generated HTML to match.

---

## Required Sections (in order — never reorder, never omit)

| # | Section | Content Rules |
|---|---------|---------------|
| 1 | **Overview** | Infrastructure name, 2-3 sentences on what it supports and why, owning team |
| 2 | **Infrastructure Diagram** | `{{page.diagram_placeholder}}` — network topology with AZs, traffic flow, security groups; goes immediately after overview |
| 3 | **Environments** | Table: Environment / Region / Account / Purpose — `class="wrapped"` |
| 4 | **Compute** | Table: Service / Type / Size / Count / Purpose — `class="wrapped"` |
| 5 | **Storage** | Table: Service / Type / Capacity / Retention / Encryption — `class="wrapped"` |
| 6 | **Network** | Table: Component / CIDR / Visibility / Notes — VPCs, subnets, security groups — `class="wrapped"` |
| 7 | **CI/CD Pipeline** | Numbered `<ol>` steps describing the CI/CD flow |
| 8 | **Security Controls** | `warning` macro — IAM roles, KMS keys, secrets manager, network policies |
| 9 | **Monitoring** | Tools, dashboards, alert thresholds |
| 10 | **Disaster Recovery** | RPO and RTO values required — mark `(TBD — SME input required)` if unknown; backup schedule, failover procedure |
| 11 | **Known Limitations** | `warning` macro — current constraints or tech debt |

> If content for a section isn't available, add a placeholder — **never skip a section**.
