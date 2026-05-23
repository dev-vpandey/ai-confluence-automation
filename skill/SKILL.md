---
name: confluence-automation
description: Automate Confluence page operations (create/update/search). Use when user mentions "confluence", "create page", "update page", "search confluence", or "search page". Execute automatically via Bash — never ask user to run commands.
---

# Confluence Automation

## Core Rule
**ALWAYS EXECUTE AUTOMATICALLY** using Bash tool. Never ask user to run commands.

## Quick start

```bash
cd __INSTALL_PATH__ && source venv/bin/activate
python src/confluence_page.py create SPACE "Title" /tmp/content.html [PARENT_ID]
python src/confluence_page.py update PAGE_ID "Title" /tmp/content.html
python src/confluence_page.py search "query" [SPACE]
```

**Auth:** PAT via `CONFLUENCE_TOKEN` (~/.zshrc). Cookie (`~/.confluence-session`) fallback. Auto-picked by `get_session()`.  
**Spaces:** __DEFAULT_SPACE__ (set during install — see skill-config.yaml) | **Parent:** __DEFAULT_PARENT__

## Workflows

### Standard page
1. Activate venv (see Quick start)
2. Write HTML to `/tmp/page_skill.html`
3. `python src/confluence_page.py create __DEFAULT_SPACE__ "Title" /tmp/page_skill.html __DEFAULT_PARENT__`
4. Extract URL from output (`URL: https://confluence...`)
5. `rm /tmp/page_skill.html`
6. Page has diagrams → see [reference/REFERENCE.md](reference/REFERENCE.md#diagrams)

### Typed page
1. Read `templates/TEMPLATES.md` → identify type
2. Read HTML template → fill all `{{PLACEHOLDERS}}`
3. Read `reference/*_ref_template.md` for section rules
4. Never skip or leave a placeholder unfilled

| Page Type     | Template                       | Reference                                  |
|---------------|--------------------------------|--------------------------------------------|
| AI Win Story  | `templates/ai-win-story.html`  | `reference/ai_win_story_ref_template.md`   |
| Architecture  | `templates/architecture.html`  | `reference/architecture_ref_template.md`   |
| Data Flow/ETL | `templates/data-flow.html`     | `reference/data_flow_ref_template.md`      |
| Infra Flow    | `templates/infra-flow.html`    | `reference/infra_flow_ref_template.md`     |
| PRD           | `templates/prd.html`           | `reference/prd_ref_template.md`            |
| User Guide    | `templates/user-guide.html`    | `reference/user_guide_ref_template.md`     |

> Structure changes: update `reference/*_ref_template.md` first, then sync HTML. Never update structure in SKILL.md or TEMPLATES.md.

## Advanced features

HTML macros, diagram attachment → [reference/REFERENCE.md](reference/REFERENCE.md)

## Response format

```
✅ Page created!
   https://your-confluence-instance.com/spaces/BI/pages/123456
```

Always extract and show URL to user.

## Execution checklist

✅ Execute via Bash  
✅ Temp files (`/tmp/page_$$.html`)  
✅ Script handles auth  
✅ Cleanup temp files  
✅ Report URL
