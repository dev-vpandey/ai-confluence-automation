# PAT Token Authentication — Implementation Plan

## Context

Cookie auth expires ~24h and requires browser interaction to refresh. Adding PAT (Personal Access Token) support lets users set `CONFLUENCE_TOKEN` in their shell profile for persistent, rotatable auth. Cookie auth is preserved as a fallback for users who don't have a PAT configured.

**Auth resolution order:** `CONFLUENCE_TOKEN` env var → `~/.confluence-session` cookie file

---

## Decisions

╔══════════════════════════════════════╦═══════════════════════════════════════════════════════╗
║ Decision                             ║ Choice                                                ║
╠══════════════════════════════════════╬═══════════════════════════════════════════════════════╣
║ Env var name                         ║ CONFLUENCE_TOKEN                                      ║
║ Auth header format                   ║ Authorization: Bearer <token>                         ║
║ Token set but invalid (401)          ║ Hard fail — PAT rotation hint, no cookie fallback     ║
║ Token absent                         ║ Cookie auth (existing flow, unchanged)                ║
║ Scope                                ║ confluence_page.py only                               ║
║ confluence.py (legacy OOP layer)     ║ No changes — not in scope                             ║
║ attach_file.py / attach_image.py     ║ No changes — PAT not supported for attachments        ║
╚══════════════════════════════════════╩═══════════════════════════════════════════════════════╝

---

## File Modified

**`src/confluence_page.py`** — only file touched.

---

## Changes

### 1. Add `_auth_hint()` helper (after `create_session()`, ~line 111)

Returns the correct 401 error message depending on which auth method was active:

```python
def _auth_hint():
    if os.environ.get('CONFLUENCE_TOKEN'):
        return (
            "   PAT invalid or expired.\n"
            "   Rotate CONFLUENCE_TOKEN in ~/.zshrc and run: source ~/.zshrc"
        )
    return (
        "   Your cookies have expired or are invalid.\n"
        "   Run: ./refresh-auth"
    )
```

### 2. Add `get_session()` function (after `_auth_hint()`)

Single entry point for auth resolution — PAT branch skips cookie loading and age check entirely:

```python
def get_session():
    token = os.environ.get('CONFLUENCE_TOKEN')
    if token:
        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {token}'})
        return session
    cookies = load_cookies()
    return create_session(cookies)
```

### 3. Replace `load_cookies()` + `create_session()` call pairs (4 locations)

| Function       | Lines   | Before                                      | After                  |
|----------------|---------|---------------------------------------------|------------------------|
| `create_page`  | 120–121 | `cookies = load_cookies()`                  | `session = get_session()` |
|                |         | `session = create_session(cookies)`         | _(remove)_             |
| `update_page`  | 183–184 | same pattern                                | `session = get_session()` |
| `read_page`    | 253–254 | same pattern                                | `session = get_session()` |
| `search_pages` | 305–306 | same pattern                                | `session = get_session()` |

### 4. Update 401 error messages (3 locations)

In `create_page()` (line 165), `update_page()` (line 230), `read_page()` (line 289):

```python
# Before
print("   Your cookies have expired or are invalid.")
print("   Run: ./refresh-auth")

# After
print(_auth_hint())
```

---

## What Does NOT Change

- `load_cookies()` — untouched, still used by cookie fallback path
- `create_session()` — untouched
- `check_cookie_age()` — untouched; naturally skipped when PAT active
- `confluence.py` — legacy layer, no PAT support
- `attach_file.py`, `attach_image.py` — define their own auth locally; PAT not supported there

---

## Verification

| Scenario | Steps | Expected |
|---|---|---|
| PAT valid | `export CONFLUENCE_TOKEN=<valid>` → `python src/confluence_page.py read <ID>` | Succeeds, no `~/.confluence-session` needed |
| Cookie fallback | `unset CONFLUENCE_TOKEN` → same command | Uses `~/.confluence-session` as before |
| PAT invalid | `export CONFLUENCE_TOKEN=bad` → any command | Prints PAT rotation hint, exits 1 |
| Cookie expired | `unset CONFLUENCE_TOKEN`, corrupt session file → any command | Prints cookie refresh hint, exits 1 |
| No auth at all | `unset CONFLUENCE_TOKEN`, delete session file → any command | `load_cookies()` prints "No cookies found. Run: ./refresh-auth" |
