# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [2.0.0] — 2026-05-23

### Added
- **`install.sh`** — single-command installer: Python version check, venv setup, optional cookie-auth deps, `config.yaml` write, `skill-config.yaml` write, shell profile PAT setup, skill install to `~/.claude/skills/confluence-automation/`
- **`skill/`** — skill files moved into repo for distribution (SKILL.md, README.md, templates/, reference/)
- **`requirements-cookie-auth.txt`** — playwright split out as optional install (Server/DC cookie auth only)
- **`skill-config.example.yaml`** — template for user-specific skill defaults (space, parent page ID)
- **`tests/`** — unit tests for cloud detection and cross-platform browser launch (7 tests)

### Changed
- **`config.example.yaml`** — `base_url` changed to `https://your-confluence-instance.com` placeholder
- **`src/confluence_page.py`** — cloud detection (`is_cloud_instance()`): `.atlassian.net` URLs enforce PAT-only, block cookie auth with clear message; auth hints genericised (no `~/.zshrc` reference)
- **`src/refresh_cookies.py`** — cross-platform browser launch via `get_open_command()` (macOS/Linux/Windows)
- **`requirements.txt`** — playwright removed from core dependencies
- **`README.md`**, **`documentation/USER-GUIDE.md`**, **`documentation/architecture/PRD.md`**, **`documentation/architecture/DESIGN-DOC.md`** — org-specific URLs, space names, and internal references replaced with generic equivalents
- **`.gitignore`** — `skill-config.yaml` added

---

## [1.3.0] — 2026-05-23

### Added
- **`src/config.py`** — new config loader; reads `config.yaml` from repo root if present, falls back to hardcoded defaults when absent. Exposes `BASE_URL`, `SESSION_FILE`, `TIMEOUT_HEALTH`, `TIMEOUT_SEARCH`, `TIMEOUT_CREATE`
- **`config.example.yaml`** — template config file (git-tracked); users copy to `config.yaml` to override defaults
- **`documentation/adr/0002-config-yaml-for-runtime-settings.md`** — ADR documenting why `config.yaml` was chosen over env vars or `python-dotenv`

### Changed
- **`src/confluence_page.py`** — `BASE_URL` and `~/.confluence-session` path now imported from `config.py`; cookie domain derived via `urlparse(BASE_URL).netloc`
- **`src/confluence.py`** — `BASE_URL`, `TIMEOUT_HEALTH`, `TIMEOUT_SEARCH`, `TIMEOUT_CREATE`, and `SESSION_FILE` imported from `config.py`; string-split hostname replaced with `urlparse`
- **`src/refresh_cookies.py`** — `CONFLUENCE_URL` constant removed; `BASE_URL` and `SESSION_FILE` imported from `config.py`; hostname derived via `urlparse`
- **`src/attach_image.py`** — cookie domain derived via `urlparse(BASE_URL).netloc` instead of hardcoded string
- **`requirements.txt`** — `pyyaml>=6.0` added
- **`.gitignore`** — `config.yaml` added (local config must not be committed)
- **`README.md`** — Configuration section added; setup step added for `cp config.example.yaml config.yaml`; directory structure updated
- **`documentation/USER-GUIDE.md`** — Configuration section added; Quick Start updated; Limitations updated; v1.3 changelog entry added

---

## [1.2.0] — 2026-05-22

### Added
- **`src/confluence_page.py`** — PAT token authentication via `CONFLUENCE_TOKEN` env var; `get_session()` prefers Bearer token over cookie session when env var is set
- **`src/confluence_page.py`** — `_auth_hint()` helper — returns auth-method-aware error message on 401 (rotates PAT hint vs. `./refresh-auth` hint based on which auth method is active)

### Changed
- **`SKILL.md`** — Auth section rewritten: PAT as primary, cookie as fallback, `get_session()` auto-selection documented; 401 error fix updated to cover both auth methods; restructured to under 100 lines per write-a-skill guidelines
- **`README.md`** — Tagline, prerequisites (Chrome removed), setup steps, auth section, and environment table updated to reflect PAT as default
- **`documentation/USER-GUIDE.md`** — Prerequisites, quick start, auth section, limitations, troubleshooting table updated; v1.2 changelog entry added
- **`documentation/architecture/DESIGN-DOC.md`** — Decision 1 rewritten (cookie → PAT+cookie fallback); problem statement, non-goals, component description, security section, error table, and rollout plan updated

### Removed
- **Prerequisites** — Google Chrome no longer required for initial setup; cookie extraction via Chrome is now fallback-only

---

## [1.1.0] — 2026-05-11

### Added
- **`confluence-automation` skill** — 6 new typed HTML page templates: `ai-win-story.html`, `architecture.html`, `data-flow.html`, `infra-flow.html`, `prd.html`, `user-guide.html`
- **`confluence-automation` skill** — 7 reference files as single sources of truth for each page type (`reference/ai_win_story_ref_template.md`, `architecture_ref_template.md`, `data_flow_ref_template.md`, `implementation_flow_ref_template.md`, `infra_flow_ref_template.md`, `user_guide_ref_template.md`, `prd_ref_template.md`); each defines required sections, placeholders, and format rules
- **`confluence-automation` skill** — `templates/TEMPLATES.md` decision tree mapping page types to template + reference files
- **`confluence-automation` skill** — `templates/diagram-workflow.md` Generate → Review → Embed workflow for draw.io + Confluence
- **`confluence-automation` skill** — `README.md` setup guide (clone instructions, trigger phrases, auth overview)
- **`documentation/`** — Structured docs hierarchy replacing flat `docs/`: `USER-GUIDE.md`, `architecture/DESIGN-DOC.md`, `architecture/PRD.md`, architecture diagrams (`confluence-architecture`, `how-it-works` in `.drawio` + `.png`)
- **`confluence-automation-product-brief.md`** — AI Win Story for the skill; published to Confluence `/spaces/DFS/pages/1046071787`

### Changed
- **`SKILL.md`** — Full rewrite: consolidated commands, templates table for all 6 page types, typed-page workflow, execution checklist; authoritative update rule added
- **`templates/ai-win-story.html`** — Section 4 includes `{{OPTIONAL_DETAIL_TABLE}}` placeholder; section count formalised to 10
- **`templates/TEMPLATES.md`** — Per-type spec content removed; entries now point to `reference/*_ref_template.md` only
- **`requirements.txt`** — Removed unused `pyyaml>=6.0`
- **`.gitignore`** — Renamed `implementation_plan/` → `implementation_planner/`; added `auth_change_token_impl/`; removed `CHANGELOG.md` exclusion

### Fixed
- **`src/attach_file.py`** — Added `X-Atlassian-Token: nocheck` header (Confluence rejects multipart POST without it); wrapped file open in context manager to prevent resource leaks on repeated calls
- **`refresh-auth`** — Replaced hardcoded `~/bitbucket/...` path with `$(dirname "${BASH_SOURCE[0]}")` — works from any clone location
- **`cf`** — Corrected Python invocation from `python confluence.py` → `python src/confluence.py`

### Removed
- **`docs/`** — Flat docs directory (AUTH_GUIDE, AUTO_REFRESH_GUIDE, DEV_GUIDE, DIAGRAM_WORKFLOW, MACROS_REFERENCE, TROUBLESHOOTING, USER_GUIDE + all diagrams) replaced by `documentation/`
- **`QUICK_REFERENCE.md`** — Content folded into `documentation/USER-GUIDE.md`

---

## [1.0.0] — 2026-04-01

### Added
- Initial release: `src/confluence.py`, `src/confluence_page.py`, `src/attach_file.py`, `src/attach_image.py`, `src/convert_drawio_to_png.py`, `src/refresh_cookies.py`
- `cf` CLI wrapper and `refresh-auth` auth helper scripts
- `docs/` documentation directory
- `requirements.txt`

---

[2.0.0]: https://github.com/dev-vpandey/ai-confluence-automation/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/dev-vpandey/ai-confluence-automation/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/dev-vpandey/ai-confluence-automation/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/dev-vpandey/ai-confluence-automation/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/dev-vpandey/ai-confluence-automation/releases/tag/v1.0.0
