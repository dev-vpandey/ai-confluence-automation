#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DEST="$HOME/.claude/skills/confluence-automation"
MIN_PYTHON_MINOR=9

echo "=== Confluence Automation Installer ==="
echo ""

# ── Python version check ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 || command -v python || true)
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

# Patch install-time tokens in SKILL.md
# Use | as sed delimiter to avoid conflicts with path slashes
sed -i.bak "s|__INSTALL_PATH__|$REPO_DIR|g" "$SKILL_DEST/SKILL.md" && rm "$SKILL_DEST/SKILL.md.bak"
sed -i.bak "s|__DEFAULT_SPACE__|$cf_space|g" "$SKILL_DEST/SKILL.md" && rm "$SKILL_DEST/SKILL.md.bak"
sed -i.bak "s|__DEFAULT_PARENT__|${cf_parent:-}|g" "$SKILL_DEST/SKILL.md" && rm "$SKILL_DEST/SKILL.md.bak"

echo "✅ Skill installed to $SKILL_DEST"

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo "==================================="
echo "✅ Installation complete!"
echo "==================================="
echo ""
echo "Test it:"
echo "  source $REPO_DIR/venv/bin/activate"
if [ -n "$pat_token" ]; then
  echo "  source $PROFILE"
fi
echo "  python src/confluence_page.py search 'test' $cf_space"
