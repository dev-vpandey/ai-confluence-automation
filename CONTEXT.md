# Confluence Automation

Python CLI and Claude Code skill for creating, updating, searching, and reading pages on the GoTo on-prem Confluence instance without manual browser interaction.

## Language

### Authentication

**PAT (Personal Access Token)**:
A long-lived token issued by Confluence Server used as a `Bearer` credential. Set via `export CONFLUENCE_TOKEN=<token>` in shell profile; rotated by updating that value and re-sourcing.
_Avoid_: API key, API token, access key

**Cookie Auth**:
Session-based authentication using three browser cookies (`JSESSIONID`, `seraph.confluence`, `confluence.browse.space.cookie`) stored in `~/.confluence-session`. Expires ~24h; refreshed via `./refresh-auth`.
_Avoid_: session token, browser auth

**Auth Resolution**:
The precedence rule: check `CONFLUENCE_TOKEN` env var first; if absent, fall back to `~/.confluence-session`. Applied at session creation, not per-request.
_Avoid_: auth priority, auth fallback chain

**Session**:
A `requests.Session` object holding auth context (either a `Bearer` header or a cookie jar). Created once per CLI invocation, reused across all HTTP calls in that run.
_Avoid_: connection, client

### Pages & Content

**Page**:
A Confluence wiki page with a title, HTML body (storage format), version number, and a space key. Identified by numeric page ID.
_Avoid_: document, article

**Space**:
A Confluence workspace identified by a short key (e.g. `DAT`, `ENG`). Groups related pages.
_Avoid_: project, namespace

**Storage Format**:
Confluence's internal HTML dialect used in the REST API. Similar to XHTML but with Confluence-specific macros. The CLI accepts plain HTML files and posts them as storage format.
_Avoid_: confluence HTML, page HTML

### Operations

**Refresh**:
The act of obtaining new valid cookies via `./refresh-auth`. Involves browser interaction (guided or manual). Only relevant when using Cookie Auth.
_Avoid_: re-authenticate, re-login, token refresh (which applies to PAT rotation, not cookie refresh)

**Rotation**:
Replacing an expired or revoked PAT with a new one in the shell profile and re-sourcing. Distinct from Refresh, which applies to cookies.
_Avoid_: refresh (use only for cookies)

---

## Example Dialogue

> **Dev:** "My create command is failing with a 401."
>
> **Domain expert:** "Are you on PAT or Cookie Auth?"
>
> **Dev:** "I have `CONFLUENCE_TOKEN` set."
>
> **Domain expert:** "Then your PAT has expired. Rotate it — update `CONFLUENCE_TOKEN` in `~/.zshrc`, re-source, and retry. Don't run `./refresh-auth`; that's for Cookie Auth."
>
> **Dev:** "What if I unset the token entirely?"
>
> **Domain expert:** "Auth Resolution falls back to `~/.confluence-session`. If that file's missing or stale, run `./refresh-auth` to refresh your cookies."

---

## Flagged Ambiguities

**"token"** is overloaded in this codebase: it appears in the context of both the PAT (`CONFLUENCE_TOKEN`) and cookie values (the JSESSIONID string is sometimes called "the token"). Prefer **PAT** when referring to the env-var credential and **cookie** or **JSESSIONID** when referring to session values.
