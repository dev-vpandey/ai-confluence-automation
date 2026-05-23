# Plan: Config-driven Confluence settings via config.yaml

## Context
Multiple source files hardcode `https://confluence.ops.expertcity.com` and operational constants (timeouts, session file path). Any environment change (staging, different org) requires editing source files. Goal: centralize mutable config in `config.yaml` with in-code defaults so existing users are unaffected.

## Decisions made
- **Mechanism**: `config.yaml` at project root (gitignored), `config.example.yaml` shipped
- **Scope**: `confluence.base_url`, `confluence.session_file`, `timeouts.create_page/search/health_check`
- **Fallback**: defaults in code — config file is opt-in, zero breaking change
- **Auth**: `CONFLUENCE_TOKEN` env var stays untouched

---

## Step 1 — Add `pyyaml` to requirements.txt
File: `requirements.txt`
Append: `pyyaml>=6.0`

---

## Step 2 — Create `src/config.py`
New file. Loads `config.yaml` from project root if present, else returns `{}`.
Exposes typed constants consumed by other modules.

```python
from pathlib import Path
import yaml

_config_path = Path(__file__).parent.parent / "config.yaml"
_raw = yaml.safe_load(_config_path.read_text()) if _config_path.exists() else {}

def _get(section: str, key: str, default):
    return _raw.get(section, {}).get(key, default)

BASE_URL = _get("confluence", "base_url", "https://confluence.ops.expertcity.com")
SESSION_FILE = Path(_get("confluence", "session_file", "~/.confluence-session")).expanduser()

TIMEOUT_HEALTH  = _get("timeouts", "health_check", 5)
TIMEOUT_SEARCH  = _get("timeouts", "search", 10)
TIMEOUT_CREATE  = _get("timeouts", "create_page", 30)
```

---

## Step 3 — Create `config.example.yaml`
New file at project root. Serves as docs + template.

```yaml
confluence:
  base_url: "https://confluence.ops.expertcity.com"
  session_file: "~/.confluence-session"

timeouts:
  health_check: 5
  search: 10
  create_page: 30
```

---

## Step 4 — Update `.gitignore`
Add `config.yaml` to `.gitignore` (keep `config.example.yaml` tracked).

---

## Step 5 — Refactor `src/confluence_page.py`
Critical file: `src/confluence_page.py`

| What | Current | Change |
|------|---------|--------|
| Line 27 | `BASE_URL = "https://..."` | Delete — import from config |
| Lines 35, 84 | `Path.home() / ".confluence-session"` | Replace with `SESSION_FILE` from config |
| Top of file | — | Add `from config import BASE_URL, SESSION_FILE` |

`attach_file.py` (line 10) and `attach_image.py` (line 11) already import `BASE_URL` from `confluence_page` — they get the fix for free once confluence_page is updated.

---

## Step 6 — Refactor `src/confluence.py`
File: `src/confluence.py`

| What | Current | Change |
|------|---------|--------|
| Line 11 | `BASE_URL = 'https://...'` | Replace with import from config |
| Line 487 | `BASE_URL = 'https://...'` in main() | Remove, use module-level constant |
| Line 53 | `timeout=5` | Replace with `TIMEOUT_HEALTH` |
| Line 258 | `timeout=30` | Replace with `TIMEOUT_CREATE` |
| Line 296 | `timeout=10` | Replace with `TIMEOUT_SEARCH` |
| Top of file | — | Add `from config import BASE_URL, TIMEOUT_HEALTH, TIMEOUT_SEARCH, TIMEOUT_CREATE` |

---

## Step 7 — Refactor `src/refresh_cookies.py`
File: `src/refresh_cookies.py`

| What | Current | Change |
|------|---------|--------|
| Line 15 | `CONFLUENCE_URL = "confluence.ops.expertcity.com"` | Derive from `BASE_URL` via `urlparse` |
| Line 83 | Hardcoded URL in AppleScript string | Replace with `BASE_URL` |
| Line 149 | Hardcoded URL in print statement | Replace with `BASE_URL` |

Import: `from config import BASE_URL` + `from urllib.parse import urlparse` to extract hostname.

---

## Files modified
- `requirements.txt` — add pyyaml
- `src/config.py` — new file
- `config.example.yaml` — new file
- `.gitignore` — add config.yaml
- `src/confluence_page.py` — import BASE_URL, SESSION_FILE from config
- `src/confluence.py` — import BASE_URL + timeouts from config
- `src/refresh_cookies.py` — import BASE_URL from config

**Not changed:** `attach_file.py`, `attach_image.py` (already inherit via confluence_page import), `convert_drawio_to_png.py` (diagram viewport/timeouts out of scope).

---

## Verification
1. `python src/confluence_page.py` with no `config.yaml` → uses defaults, no crash
2. Create `config.yaml` with different `base_url` → confirm it loads and overrides
3. `grep -r "expertcity.com" src/` → should return zero results after refactor
4. Existing `CONFLUENCE_TOKEN` auth flow unchanged — smoke test create/update page
