# Hybrid PAT + Cookie Authentication

The project's cookie-based auth works but expires every ~24h and requires browser interaction to refresh. Replacing it entirely would break existing users who haven't set up a PAT yet. Instead, auth resolution checks `CONFLUENCE_TOKEN` env var first; if absent, falls back to `~/.confluence-session`. This lets PAT adopters get persistent auth while keeping cookie users unaffected.

## Considered Options

**Full PAT replacement** — delete cookie logic, require `CONFLUENCE_TOKEN`. Cleaner, but a breaking change for any user or CI job not yet holding a PAT.

**Hybrid fallback (chosen)** — PAT when env var is set, cookies otherwise. Zero breakage; users migrate at their own pace.

## Consequences

- `attach_file.py` and `attach_image.py` define their own auth locally and are not covered by this change. PAT is not supported for attachment operations until those files are updated.
- If `CONFLUENCE_TOKEN` is set but invalid, the script hard-fails with a rotation hint. It does not silently retry with cookies — a set-but-broken token is always a signal to fix the token, not fall through to stale cookies.
- For Atlassian Cloud instances (`.atlassian.net` URLs), cookie auth is not available — the script detects the URL and enforces PAT-only with a clear error message. Cookie fallback remains available for Server/DC users only.
