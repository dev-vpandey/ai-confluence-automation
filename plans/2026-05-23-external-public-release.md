# External Public Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make this project usable by anyone outside the org — supporting both Atlassian Cloud and Server/DC, with a single `install.sh` that wires up the backend + Claude Code skill end-to-end.

**Architecture:** Add an `install.sh` entry point that prompts for user-specific config (Confluence URL, default space, parent page ID, auth token), writes `config.yaml` + `skill-config.yaml`, copies skill files from the repo's `skill/` directory to `~/.claude/skills/confluence-automation/`, and patches the install path into `SKILL.md`. Python code gets cloud detection, generic auth hints, and cross-platform browser launch. Dependencies split into core vs. cookie-auth optional.

**Tech Stack:** Python 3.9+, bash, requests, pyyaml, playwright (optional, cookie-auth only)

---

## File Map

```
ai-confluence-automation/
├── install.sh                          ← NEW: single-command installer
├── requirements.txt                    ← MODIFY: remove playwright
├── requirements-cookie-auth.txt        ← NEW: playwright only
├── config.example.yaml                 ← MODIFY: URL → placeholder
├── skill-config.example.yaml           ← NEW: default_space, parent_page_id
├── skill/                              ← NEW DIR: move from ~/.claude/skills/confluence-automation/
│   ├── SKILL.md                        ← MOVE + MODIFY: remove hardcoded path/spaces/ID
│   ├── README.md                       ← MOVE + MODIFY: update clone URL, remove BI/36441229
│   ├── templates/                      ← MOVE: all HTML templates (unchanged)
│   └── reference/                      ← MOVE: all reference files (unchanged)
├── src/
│   ├── confluence_page.py              ← MODIFY: cloud detection + generic auth hint
│   └── refresh_cookies.py             ← MODIFY: cross-platform browser launch
├── refresh-auth                        ← MODIFY: cross-platform open command
├── README.md                           ← MODIFY: clone URL → GitHub, setup instructions
└── .gitignore                          ← MODIFY: add skill-config.yaml
```

---

## Task 1: Move skill files into repo

**Files:**
- Create: `skill/` (directory)
- Move from: `~/.claude/skills/confluence-automation/SKILL.md` → `skill/SKILL.md`
- Move from: `~/.claude/skills/confluence-automation/README.md` → `skill/README.md`
- Move from: `~/.claude/skills/confluence-automation/templates/` → `skill/templates/`
- Move from: `~/.claude/skills/confluence-automation/reference/` → `skill/reference/`

- [ ] **Step 1: Copy skill files into repo**

```bash
mkdir -p skill
cp ~/.claude/skills/confluence-automation/SKILL.md skill/SKILL.md
cp ~/.claude/skills/confluence-automation/README.md skill/README.md
cp -r ~/.claude/skills/confluence-automation/templates skill/templates
cp -r ~/.claude/skills/confluence-automation/reference skill/reference
```

- [ ] **Step 2: Verify structure**

```bash
find skill/ -type f | sort
```

Expected output includes: `skill/SKILL.md`, `skill/README.md`, `skill/templates/architecture.html`, `skill/reference/REFERENCE.md`, etc.

- [ ] **Step 3: Commit**

```bash
git add skill/
git commit -m "feat: move skill files into repo for distribution"
```

---

## Task 2: Split requirements.txt

**Files:**
- Modify: `requirements.txt`
- Create: `requirements-cookie-auth.txt`

- [ ] **Step 1: Update requirements.txt — remove playwright**

Replace content of `requirements.txt` with:

```
requests>=2.31.0
pyyaml>=6.0
```

- [ ] **Step 2: Create requirements-cookie-auth.txt**

```
# Install ONLY if using cookie-based auth (Atlassian Server/DC without PAT)
# Run: pip install -r requirements-cookie-auth.txt
# Then: playwright install chromium
playwright>=1.40.0
```

- [ ] **Step 3: Verify core install works without playwright**

```bash
python3 -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate
pip install -r requirements.txt
python -c "import requests, yaml; print('OK')"
deactivate
rm -rf /tmp/test-venv
```

Expected: `OK` with no playwright import errors.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt requirements-cookie-auth.txt
git commit -m "feat: split playwright into optional requirements-cookie-auth.txt"
```

---

## Task 3: Config placeholders + skill-config template

**Files:**
- Modify: `config.example.yaml`
- Create: `skill-config.example.yaml`
- Modify: `.gitignore`

- [ ] **Step 1: Update config.example.yaml URL to placeholder**

Replace `config.example.yaml` content:

```yaml
confluence:
  base_url: "https://your-confluence-instance.com"
  session_file: "~/.confluence-session"

timeouts:
  health_check: 5
  search: 10
  create_page: 30
```

- [ ] **Step 2: Create skill-config.example.yaml**

```yaml
# Skill defaults — copied to skill-config.yaml by install.sh
# Edit these values to match your Confluence setup.
skill:
  default_space: "YOUR_SPACE_KEY"
  default_parent_page_id: ""   # optional: numeric ID of parent page
```

- [ ] **Step 3: Add skill-config.yaml to .gitignore**

Add to `.gitignore`:

```
# Skill user config (local, not committed)
skill-config.yaml
```

- [ ] **Step 4: Commit**

```bash
git add config.example.yaml skill-config.example.yaml .gitignore
git commit -m "feat: add skill-config template and generic config placeholder"
```

---

## Task 4: Cloud detection + generic auth hint in confluence_page.py

**Files:**
- Modify: `src/confluence_page.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_confluence_page.py`:

```python
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Patch BASE_URL before importing
import unittest.mock as mock

def test_cloud_url_detected():
    with mock.patch.dict(os.environ, {'CONFLUENCE_TOKEN': 'test-token'}):
        with mock.patch('config.BASE_URL', 'https://myorg.atlassian.net/wiki'):
            import importlib
            import confluence_page
            importlib.reload(confluence_page)
            assert confluence_page.is_cloud_instance() is True

def test_server_url_not_cloud():
    with mock.patch('config.BASE_URL', 'https://confluence.mycompany.com'):
        import importlib
        import confluence_page
        importlib.reload(confluence_page)
        assert confluence_page.is_cloud_instance() is False

def test_cloud_blocks_cookie_auth():
    with mock.patch('config.BASE_URL', 'https://myorg.atlassian.net/wiki'):
        import importlib
        import confluence_page
        importlib.reload(confluence_page)
        with pytest.raises(SystemExit):
            confluence_page.load_cookies()

def test_auth_hint_generic():
    with mock.patch.dict(os.environ, {}, clear=True):
        import importlib
        import confluence_page
        importlib.reload(confluence_page)
        hint = confluence_page._auth_hint()
        assert '~/.zshrc' not in hint
        assert 'shell profile' in hint
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd /path/to/ai-confluence-automation
source venv/bin/activate
pip install pytest
pytest tests/test_confluence_page.py -v
```

Expected: 4 failures — `is_cloud_instance` not defined, `_auth_hint` still has `~/.zshrc`.

- [ ] **Step 3: Add `is_cloud_instance()` function to confluence_page.py**

Add after imports block (after `from config import BASE_URL, SESSION_FILE`):

```python
def is_cloud_instance() -> bool:
    return ".atlassian.net" in BASE_URL
```

- [ ] **Step 4: Update `load_cookies()` to block on Cloud**

Replace the start of `load_cookies()`:

```python
def load_cookies():
    """Load cookies from ~/.confluence-session"""
    if is_cloud_instance():
        print("❌ Cloud Confluence detected (atlassian.net).")
        print("   Cookie auth is not supported for Atlassian Cloud.")
        print("   Set CONFLUENCE_TOKEN in your shell profile and re-source it.")
        sys.exit(1)

    session_file = SESSION_FILE
    # ... rest of existing function unchanged ...
```

- [ ] **Step 5: Update `_auth_hint()` to remove ~/.zshrc reference**

Replace `_auth_hint()`:

```python
def _auth_hint():
    if os.environ.get('CONFLUENCE_TOKEN'):
        return (
            "   PAT invalid or expired.\n"
            "   Rotate CONFLUENCE_TOKEN in your shell profile and re-source it."
        )
    if is_cloud_instance():
        return (
            "   Atlassian Cloud requires a PAT.\n"
            "   Set CONFLUENCE_TOKEN in your shell profile and re-source it."
        )
    return (
        "   Your cookies have expired or are invalid.\n"
        "   Run: ./refresh-auth guided"
    )
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
pytest tests/test_confluence_page.py -v
```

Expected: 4 passing.

- [ ] **Step 7: Commit**

```bash
git add src/confluence_page.py tests/test_confluence_page.py
git commit -m "feat: cloud detection, PAT enforcement for atlassian.net, generic auth hint"
```

---

## Task 5: Cross-platform browser launch

**Files:**
- Modify: `refresh-auth`
- Modify: `src/refresh_cookies.py`

- [ ] **Step 1: Write failing test for cross-platform open**

Add to `tests/test_refresh_cookies.py`:

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import unittest.mock as mock

def test_open_command_macos():
    with mock.patch('platform.system', return_value='Darwin'):
        import importlib
        import refresh_cookies
        importlib.reload(refresh_cookies)
        assert refresh_cookies.get_open_command() == 'open'

def test_open_command_linux():
    with mock.patch('platform.system', return_value='Linux'):
        import importlib
        import refresh_cookies
        importlib.reload(refresh_cookies)
        assert refresh_cookies.get_open_command() == 'xdg-open'

def test_open_command_windows():
    with mock.patch('platform.system', return_value='Windows'):
        import importlib
        import refresh_cookies
        importlib.reload(refresh_cookies)
        assert refresh_cookies.get_open_command() == 'start'
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_refresh_cookies.py -v
```

Expected: `get_open_command` not defined.

- [ ] **Step 3: Add `get_open_command()` to refresh_cookies.py**

Add after imports:

```python
import platform

def get_open_command() -> str:
    system = platform.system()
    if system == 'Darwin':
        return 'open'
    elif system == 'Linux':
        return 'xdg-open'
    else:
        return 'start'
```

- [ ] **Step 4: Replace hardcoded `open` in refresh_cookies.py**

Find any `subprocess.run(['open', ...]` or `subprocess.run(["open", ...]` and replace:

```python
# Before
subprocess.run(['open', base_url], check=False)

# After
subprocess.run([get_open_command(), base_url], check=False)
```

- [ ] **Step 5: Update refresh-auth shell script**

Find the `open` call in `refresh-auth` and replace with OS-aware version:

```bash
# Detect OS and open browser
case "$(uname -s)" in
  Darwin)  open "$CONFLUENCE_URL" ;;
  Linux)   xdg-open "$CONFLUENCE_URL" 2>/dev/null || echo "Open $CONFLUENCE_URL in your browser" ;;
  MINGW*|CYGWIN*|MSYS*) start "$CONFLUENCE_URL" ;;
  *)       echo "Open $CONFLUENCE_URL in your browser" ;;
esac
```

- [ ] **Step 6: Run tests — verify they pass**

```bash
pytest tests/test_refresh_cookies.py -v
```

Expected: 3 passing.

- [ ] **Step 7: Commit**

```bash
git add src/refresh_cookies.py refresh-auth tests/test_refresh_cookies.py
git commit -m "feat: cross-platform browser launch (macOS/Linux/Windows)"
```

---

## Task 6: Update README + skill/README URLs and references

**Files:**
- Modify: `README.md`
- Modify: `skill/README.md`
- Modify: `skill/SKILL.md`

- [ ] **Step 1: Update README.md clone URL**

Replace:
```
git clone ssh://git@bitbucket.ops.expertcity.com:7999/dat/ai-data-confluence-automation.git
cd ai-data-confluence-automation
```

With:
```
git clone https://github.com/dev-vpandey/ai-confluence-automation.git
cd ai-confluence-automation
```

- [ ] **Step 2: Update README.md setup section**

Replace the manual "Add your PAT token to ~/.zshrc" step with:

```
# 5. Run the installer (handles config, skill install, auth setup)
./install.sh
```

Remove old step 4 (cp config.example.yaml) and step 5 (echo to ~/.zshrc) — install.sh handles both.

- [ ] **Step 3: Update skill/README.md**

Replace:
```
git clone https://bitbucket.ops.expertcity.com/projects/DAT/repos/ai-data-confluence-automation
```

With:
```
git clone https://github.com/dev-vpandey/ai-confluence-automation.git
cd ai-confluence-automation
./install.sh
```

Remove `Default space: BI` and `Default parent page: 36441229` — these come from `skill-config.yaml` now.

- [ ] **Step 4: Update skill/SKILL.md**

Replace hardcoded path:
```
cd ~/Documents/git_work/ai-data-confluence-automation && source venv/bin/activate
```

With a token that `install.sh` patches at install time:
```
cd __INSTALL_PATH__ && source venv/bin/activate
```

Replace hardcoded spaces `BI`, `TECH`, `SOA` with note:
```
**Spaces:** see skill-config.yaml (set during install)
```

Replace hardcoded parent ID `36441229` with:
```
**Parent page:** see skill-config.yaml (set during install)
```

- [ ] **Step 5: Commit**

```bash
git add README.md skill/README.md skill/SKILL.md
git commit -m "docs: update URLs to GitHub, remove org-specific defaults"
```

---

## Task 7: Create install.sh

**Files:**
- Create: `install.sh`

- [ ] **Step 1: Create install.sh**

```bash
#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DEST="$HOME/.claude/skills/confluence-automation"
MIN_PYTHON_MINOR=9

echo "=== Confluence Automation Installer ==="
echo ""

# ── Python version check ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
  echo "❌ Python 3 not found. Install Python 3.9+ and retry."
  exit 1
fi

PY_MINOR=$("$PYTHON" -c "import sys; print(sys.version_info.minor)")
PY_MAJOR=$("$PYTHON" -c "import sys; print(sys.version_info.major)")

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt "$MIN_PYTHON_MINOR" ]; }; then
  echo "❌ Python 3.$MIN_PYTHON_MINOR+ required. Found: $("$PYTHON" --version)"
  exit 1
fi
echo "✅ Python $("$PYTHON" --version)"

# ── Virtual environment ───────────────────────────────────────────────────────
if [ ! -d "$REPO_DIR/venv" ]; then
  echo "Creating virtual environment..."
  "$PYTHON" -m venv "$REPO_DIR/venv"
fi

source "$REPO_DIR/venv/bin/activate"
pip install --quiet -r "$REPO_DIR/requirements.txt"
echo "✅ Core dependencies installed"

# ── Cookie auth (optional) ────────────────────────────────────────────────────
echo ""
read -rp "Use Server/DC cookie auth fallback? Requires Playwright (~150MB). [y/N]: " cookie_auth
if [[ "$cookie_auth" =~ ^[Yy]$ ]]; then
  pip install --quiet -r "$REPO_DIR/requirements-cookie-auth.txt"
  playwright install chromium
  echo "✅ Cookie auth dependencies installed"
fi

# ── Confluence config ─────────────────────────────────────────────────────────
echo ""
echo "=== Confluence Config ==="
read -rp "Confluence base URL (e.g. https://myorg.atlassian.net/wiki): " cf_url
read -rp "Default space key (e.g. ENG): " cf_space
read -rp "Default parent page ID (optional, press Enter to skip): " cf_parent

# Write config.yaml
cat > "$REPO_DIR/config.yaml" <<EOF
confluence:
  base_url: "$cf_url"
  session_file: "~/.confluence-session"

timeouts:
  health_check: 5
  search: 10
  create_page: 30
EOF
echo "✅ config.yaml written"

# Write skill-config.yaml
cat > "$REPO_DIR/skill-config.yaml" <<EOF
skill:
  default_space: "$cf_space"
  default_parent_page_id: "$cf_parent"
EOF
echo "✅ skill-config.yaml written"

# ── PAT token setup ───────────────────────────────────────────────────────────
echo ""
echo "=== Authentication ==="
echo "Generate a PAT in Confluence: Profile → Personal Access Tokens → create with read/write."
read -rp "Paste your PAT token (leave blank to skip): " pat_token

if [ -n "$pat_token" ]; then
  # Detect shell profile
  case "$SHELL" in
    */zsh)   PROFILE="$HOME/.zshrc" ;;
    */bash)
      if [ -f "$HOME/.bash_profile" ]; then
        PROFILE="$HOME/.bash_profile"
      else
        PROFILE="$HOME/.bashrc"
      fi
      ;;
    */fish)  PROFILE="$HOME/.config/fish/config.fish" ;;
    *)       PROFILE="$HOME/.profile" ;;
  esac

  if grep -q "CONFLUENCE_TOKEN" "$PROFILE" 2>/dev/null; then
    echo "⚠️  CONFLUENCE_TOKEN already in $PROFILE — update it manually if needed."
  else
    echo "export CONFLUENCE_TOKEN=$pat_token" >> "$PROFILE"
    echo "✅ CONFLUENCE_TOKEN added to $PROFILE"
    echo "   Run: source $PROFILE"
  fi
fi

# ── Install skill ─────────────────────────────────────────────────────────────
echo ""
echo "=== Installing Claude Code Skill ==="
mkdir -p "$SKILL_DEST"
cp -r "$REPO_DIR/skill/." "$SKILL_DEST/"

# Patch install path into SKILL.md
sed -i.bak "s|__INSTALL_PATH__|$REPO_DIR|g" "$SKILL_DEST/SKILL.md" && rm "$SKILL_DEST/SKILL.md.bak"

# Patch default space into SKILL.md
sed -i.bak "s|__DEFAULT_SPACE__|$cf_space|g" "$SKILL_DEST/SKILL.md" && rm "$SKILL_DEST/SKILL.md.bak"

# Patch parent page ID into SKILL.md (empty string if not provided)
sed -i.bak "s|__DEFAULT_PARENT__|$cf_parent|g" "$SKILL_DEST/SKILL.md" && rm "$SKILL_DEST/SKILL.md.bak"

echo "✅ Skill installed to $SKILL_DEST"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "==================================="
echo "✅ Installation complete!"
echo "==================================="
echo ""
echo "Test it:"
echo "  source $REPO_DIR/venv/bin/activate"
echo "  python src/confluence_page.py search 'test' $cf_space"
echo ""
if [ -n "$pat_token" ]; then
  echo "  Run: source $PROFILE   (to load CONFLUENCE_TOKEN)"
fi
```

- [ ] **Step 2: Make install.sh executable**

```bash
chmod +x install.sh
```

- [ ] **Step 3: Smoke test install.sh (dry run with mock inputs)**

```bash
# Test Python version check triggers correctly on old python
python3 -c "
import subprocess, sys
result = subprocess.run(['bash', '-c', 'source install.sh'], 
  input=b'https://test.atlassian.net/wiki\nENG\n\n\n', 
  capture_output=True, text=True, cwd='.')
print(result.stdout[-500:])
print(result.stderr[-200:] if result.stderr else '')
"
```

Expected: installer prompts appear, config.yaml written, skill copied.

- [ ] **Step 4: Verify config.yaml written correctly**

```bash
cat config.yaml
```

Expected: `base_url` matches what was entered.

- [ ] **Step 5: Verify skill installed**

```bash
ls ~/.claude/skills/confluence-automation/
grep "__INSTALL_PATH__" ~/.claude/skills/confluence-automation/SKILL.md && echo "FAIL: token not patched" || echo "OK: path patched"
```

Expected: `OK: path patched`.

- [ ] **Step 6: Commit**

```bash
git add install.sh
git commit -m "feat: add install.sh — single-command setup for external users"
```

---

## Task 8: Final wiring — SKILL.md tokens + skill-config.yaml reading

**Files:**
- Modify: `skill/SKILL.md` (add `__INSTALL_PATH__`, `__DEFAULT_SPACE__`, `__DEFAULT_PARENT__` tokens)
- Modify: `skill/README.md` (verify clean)

- [ ] **Step 1: Verify all three tokens exist in skill/SKILL.md**

```bash
grep -n "__INSTALL_PATH__\|__DEFAULT_SPACE__\|__DEFAULT_PARENT__" skill/SKILL.md
```

Expected: 3 matches (one per token). If any missing, add them at the correct location in SKILL.md (path in `cd` command, space in Spaces section, parent in parent page section).

- [ ] **Step 2: Run install.sh end-to-end and verify patched SKILL.md**

```bash
./install.sh
# Enter: https://yourorg.atlassian.net/wiki, ENG, 12345, (blank PAT)
grep "__INSTALL_PATH__\|__DEFAULT_SPACE__\|__DEFAULT_PARENT__" ~/.claude/skills/confluence-automation/SKILL.md && echo "FAIL: unpatched tokens remain" || echo "OK: all tokens patched"
```

Expected: `OK: all tokens patched`.

- [ ] **Step 3: Run full integration smoke test**

```bash
source venv/bin/activate
export CONFLUENCE_TOKEN=<a-real-pat>
python src/confluence_page.py search "test"
```

Expected: results or "no pages found" — not an auth error.

- [ ] **Step 4: Final commit**

```bash
git add skill/SKILL.md skill/README.md
git commit -m "feat: add install-time tokens to SKILL.md for path/space/parent patching"
```

---

## Self-Review

**Spec coverage check:**

| Agreed decision | Task covering it |
|---|---|
| Cloud + Server/DC both | Task 4 (detection), Task 7 (install prompt) |
| install.sh packages skill + backend | Task 7 |
| skill-config.yaml for spaces/parent ID | Task 3, Task 7, Task 8 |
| Cloud → PAT enforcement | Task 4 |
| Templates unchanged | (no task needed) |
| Cross-platform browser launch | Task 5 |
| GitHub URLs | Task 6 |
| Shell detection for CONFLUENCE_TOKEN | Task 7 |
| requirements split (core/cookie) | Task 2 |
| Python 3.9+ check | Task 7 |
| config.example.yaml placeholder | Task 3 |
| Skill files moved into repo | Task 1 |

All 12 items covered. No gaps.
