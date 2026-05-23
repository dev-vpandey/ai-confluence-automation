# Confluence Automation: User Guide

**Audience:** Engineers, Data/BI Analysts, Product Managers
**Last updated:** 2026-05-23
**Version:** v1.3

---

## What this does

Lets you create, update, and search Confluence pages by describing what you want in plain English. No browser, no macro syntax, no manual copy-paste.

**Does NOT cover:** Multi-user setups, OAuth auth, Slack-triggered operations.

---

## Repositories

╔══════════════════════════════════════╦══════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║ Repo                                 ║ Link                                                                                                     ║
╠══════════════════════════════════════╬══════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║ Repo                                 ║ https://github.com/dev-vpandey/ai-confluence-automation                                                  ║
╚══════════════════════════════════════╩══════════════════════════════════════════════════════════════════════════════════════════════════════════╝

---

## Prerequisites

- [ ] Python 3.9+ installed
- [ ] Access to your Confluence instance (must be able to log in)
- [ ] `CONFLUENCE_TOKEN` set in your shell profile (generate via Confluence profile → Personal Access Tokens)
- [ ] Claude Code/Github copilot CLI installed with the `confluence-automation` skill loaded
- [ ] Backend repo cloned locally

---

## Configuration

When it starts, the backend looks for `config.yaml` at the repo root. If the file isn't there, it falls back to defaults — you don't need to create it unless you're changing something.

```bash
cp config.example.yaml config.yaml
```

Then edit what you need:

```yaml
confluence:
  base_url: "https://your-confluence-instance.com"
  session_file: "~/.confluence-session"

timeouts:
  health_check: 5
  search: 10
  create_page: 30
```

`config.yaml` is gitignored — your local values won't end up in commits. Don't edit `config.example.yaml`; that's the template everyone else copies from.

The only settings you'd actually touch: `base_url` if you're on a different Confluence instance, the timeout values if things are timing out on a slow connection, or `session_file` if you want cookies stored somewhere else. `CONFLUENCE_TOKEN` stays in your shell profile — auth isn't configured here.

---

## Quick Start

1. Clone and run the installer:
   ```bash
   git clone https://github.com/dev-vpandey/ai-confluence-automation.git
   cd ai-confluence-automation
   ./install.sh
   ```
   The installer sets up the venv, writes `config.yaml`, installs the skill, and adds `CONFLUENCE_TOKEN` to your shell profile.

2. Open Claude Code and describe what you want:
   ```
   Create a Confluence page in the ENG space about our new ETL pipeline
   ```

Expected result: Claude executes automatically and returns a URL like:
```
✅ Page created!
   https://your-confluence-instance.com/spaces/ENG/pages/123456
```

---

## How it works

![How It Works](architecture/diagrams/how-it-works.png)

The `confluence-automation` skill is the **only interface** you need. It selects the right HTML template, fills in the content, calls the backend, and returns the URL. You never touch HTML or run Python directly.

---

## Common Tasks

### Create a new page

Tell Claude what type of page you need and the space:

```
Create an architecture page in ENG space for our new data ingestion service
```

```
Create an AI win story in ENG space — we reduced ETL runtime by 60% using Claude
```

```
Create a user guide in ENG space for the new metrics dashboard, put it under parent page 99999
```

Claude selects the matching typed template, fills all sections, and creates the page.

**Supported page types:**

╔═════════════════╦══════════════════════════════════════════════════════╗
║ Page Type       ║ Trigger phrases                                      ║
╠═════════════════╬══════════════════════════════════════════════════════╣
║ AI Win Story    ║ "ai win story", "win story"                          ║
║ Architecture    ║ "architecture", "system design"                      ║
║ Data Flow / ETL ║ "data flow", "etl", "pipeline"                       ║
║ Infra Flow      ║ "infra flow", "infrastructure"                       ║
║ PRD             ║ "prd", "product requirements"                        ║
║ User Guide      ║ "user guide", "how to", "guide"                      ║
╚═════════════════╩══════════════════════════════════════════════════════╝

### Update an existing page

```
Update page 1050411658 — change the overview section to reflect the new schema
```

```
Update the "Delta Lake Architecture" page in ENG space with this new content: [paste content]
```

If you don't know the page ID, ask Claude to search first:

```
Search for "Delta Lake Architecture" in ENG space
```

### Search for pages

```
Search Confluence for "ETL pipeline" in the ENG space
```

```
Find pages about "authentication" in ENG space
```

Returns up to 10 matching pages with titles and URLs.

### Attach a diagram

If your page needs a draw.io diagram:

1. Export the `.drawio` file to PNG yourself (draw.io → File → Export as → PNG)
2. Tell Claude:
   ```
   Attach diagram.png to page 1050411658
   ```

Claude calls `attach_image.py` and the image appears embedded in the page.

---

## Authentication

**Primary: PAT token**
Set `CONFLUENCE_TOKEN` in your shell profile once. No daily refresh.

```bash
export CONFLUENCE_TOKEN=your_pat_token   # add to your shell profile (~/.zshrc, ~/.bashrc, etc.)
source <your-shell-profile>
```

Generate a PAT: Confluence profile → Personal Access Tokens → create with read/write permissions.

**Fallback: Cookie session**
If `CONFLUENCE_TOKEN` isn't set, the tool falls back to cookies automatically. Cookies expire around every 24 hours, so you'll see a `401` when they do.

```bash
./refresh-auth --guided     # opens Chrome + walks you through
./refresh-auth --manual     # fastest if DevTools already open
```

---

## Limitations

- Page titles must be unique within a space
- `read` command (fetch raw page HTML) is CLI-only, not exposed in the skill
- Targets the URL set in `config.yaml` (configured during `./install.sh`)
- Diagrams require manual PNG export before attachment
- Cookie session (fallback only) expires ~24 hours; PAT tokens last until you revoke them

---

## Troubleshooting

╔══════════════════════════════════════╦═════════════════════════════════════╦══════════════════════════════════════════════╗
║ Problem                              ║ Likely cause                        ║ Fix                                          ║
╠══════════════════════════════════════╬═════════════════════════════════════╬══════════════════════════════════════════════╣
║ 401 Unauthorized                     ║ Token revoked/expired, or cookies stale ║ PAT: rotate CONFLUENCE_TOKEN in your shell profile. Cookie: ./refresh-auth --guided ║
║ 400 Bad Request                      ║ Invalid XHTML in content            ║ Check for unescaped `&` or broken tags       ║
║ 403 Forbidden                        ║ No write permission to that space   ║ Verify your Confluence space permissions     ║
║ 404 Not Found                        ║ Wrong page ID or space key          ║ Search for the page first to get correct ID  ║
║ 409 Conflict                         ║ Page edited by someone else         ║ Script auto-retries with latest version      ║
║ "No cookies found"                   ║ No CONFLUENCE_TOKEN set and no cookie session ║ Set CONFLUENCE_TOKEN in your shell profile or run ./refresh-auth ║
║ "venv not found" on cf / refresh-auth║ Not running from repo root          ║ cd to repo root first                        ║
╚══════════════════════════════════════╩═════════════════════════════════════╩══════════════════════════════════════════════╝

---

## What changed in v1.3

- Runtime config via `config.yaml`. Copy `config.example.yaml`, change `base_url` if needed, and that's it. No file means defaults, so nothing breaks for existing setups.

## What changed in v1.2

- PAT token auth via `CONFLUENCE_TOKEN` in `~/.zshrc`. Set it once, no daily refresh.
- Cookie session still works as fallback when `CONFLUENCE_TOKEN` isn't set

## What changed in v1.1

- Portable paths: scripts work from any clone location (no hardcoded `~/bitbucket/...`)
- Attach fix: `attach_file.py` no longer leaks file handles; multipart upload fixed
- 6 typed page templates: AI Win Story, Architecture, Data Flow, Infra Flow, PRD, User Guide
- Reference specs: each template has a companion `.md` spec defining required sections

[Full changelog](../../CHANGELOG.md)

---

## References

- [Design Doc](./architecture/DESIGN-DOC.md)
- [PRD](./architecture/PRD.md)
- [GitHub repo](https://github.com/dev-vpandey/ai-confluence-automation)
