# Diagram Workflow

## Flow: Generate → Review → Embed

### 1. Generate
```
Skill(skill="drawio-diagram", args="[type] for [topic]")
```
Creates: `/tmp/[name].drawio`

### 2. User Review
Tell user:
```
📊 Diagram: /tmp/[name].drawio
Open: app.diagrams.net (drag & drop) OR VS Code (Draw.io extension)
Reply 'approved' when ready
```

### 3. Wait
STOP. User reviews, edits, saves → says "approved"/"looks good"/"proceed"

### 4. Embed
```
create_page_with_diagram "SPACE" "Title" "content" "/tmp/diagram.drawio"
```

## Rules
- NEVER skip user review
- ALWAYS wait for explicit approval
- Professional quality only (see drawio skill for standards)
