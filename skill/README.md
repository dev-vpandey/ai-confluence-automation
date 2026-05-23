# Confluence Automation Skill

Automate Confluence page creation, updates, and searches via Claude Code.

---

## Setup

**1. Clone the backend project:**
```bash
git clone https://github.com/dev-vpandey/ai-confluence-automation.git
```

Follow the project's own README for venv setup, dependencies, and authentication.

**2. Install and authenticate:**
```bash
cd ai-confluence-automation && ./install.sh
```

**3. Verify:**
```bash
source venv/bin/activate
python src/confluence_page.py search "test" BI
```

The skill file at `~/.claude/skills/confluence-automation/SKILL.md` is loaded by Claude Code automatically — no additional configuration needed.

---

## Usage

Trigger phrases: `"confluence"`, `"create page"`, `"update page"`, `"search confluence"`

| Operation | Example request |
|-----------|----------------|
| Create | "Create a Confluence page for the Delta Lake architecture" |
| Update | "Update the API docs page in BI space" |
| Search | "Find all architecture pages in BI space" |

Configure defaults via install.sh (written to skill-config.yaml).

---

## Authentication

Cookie-based (not API token). Cookies last ~12–24 hours. The skill auto-checks age and prompts refresh when needed.

```bash
./refresh-auth --guided    # Chrome + step-by-step
./refresh-auth --manual    # Direct input
```

---

## File Structure

```
~/.claude/skills/confluence-automation/
├── SKILL.md                   # Loaded by Claude Code
├── README.md                  # This file
└── templates/
    ├── TEMPLATES.md           # Template selection logic
    └── diagram-workflow.md    # Diagram review/embed flow
```

For script internals, commands, macros, and troubleshooting see the [project repo](https://github.com/dev-vpandey/ai-confluence-automation).

---

## Related Skills

`drawio-diagram` — generate a diagram and embed it directly into a Confluence page.
