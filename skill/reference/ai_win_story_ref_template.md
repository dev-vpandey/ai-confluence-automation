# AI Win Story — Reference (Single Source of Truth)

> This file is the single source of truth for the AI win story page type.
> - `templates/ai-win-story.html` implements this structure — update the template when this changes
> - `templates/TEMPLATES.md` and `SKILL.md` point here — they do NOT duplicate section rules
> Live example: https://confluence.ops.expertcity.com/spaces/DFS/pages/1046071787

---

## Page Title Format

**Always** include the trophy emoji in the page title:

```
Data AI Win Story 🏆 — {{STORY_TITLE}}
```

Example: `Data AI Win Story 🏆 — Automated Table Certification with Source Traceability`

- The `🏆` emoji is **required** — never omit it
- Use em dash `—` between the fixed prefix and the story-specific title

---

## Required Sections (in order — never reorder, never omit)

| # | Section | Content Rules |
|---|---------|---------------|
| 1 | **Header** | Hardcoded — taken verbatim from template, never change or parameterize |
| 2 | **Opening Quote** | `<blockquote>` with a team member quote — sets the hook |
| 3 | **The Setup — What Were We Trying to Solve?** | Team, SDLC phase, bullet-list pain points before AI |
| 4 | **The Approach — How Did We Use AI?** | AI tool, workflow fit, example prompts, adoption story, "How It Works" ASCII flow in code block, optional detail table |
| 5 | **The Proof — What Changed?** | 4-column metrics table (Metric / Before / After / Delta) + `info` panel with headline number |
| 6 | **What We Learned — The Honest Take** | Exactly 4 bullets in order: ✅ worked / ⚠️ do differently / 🚫 dead ends / 💡 unexpected benefit |
| 7 | **The Playbook — How Could Another Team Repeat This?** | Numbered `<h3>Step N — Title</h3>` blocks with code macros + `warning` panel for prerequisites at end |
| 8 | **Voices from the Team** | Minimum 2 `<blockquote>` entries, each attributed to a named person with role |
| 9 | **What's Next** | Bullet list of follow-on work |
| 10 | **Footer** | `<hr/>` + hardcoded italic credit line — taken verbatim from template, never change or parameterize |

> If content for a section isn't available, add a placeholder — **never skip a section**.
