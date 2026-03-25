# Custom Skills

Skills stored here are offered to the user during `/ak:setup-custom` and `/ak:init-project`.

Run `/ak:setup-custom` in any project to install them globally (`~/.claude/skills/`) or per-project (`.claude/skills/`).

---

## Available Skills

### docx
Word document creation, reading, and editing (.docx). Supports headings, TOC, tables, page numbers, letterheads, tracked changes, find-and-replace, and image insertion.
- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/docx)
- Extra files: `scripts/`

### frontend-design
Create distinctive, production-grade frontend interfaces — web components, pages, landing pages, dashboards, React components, HTML/CSS layouts. Avoids generic AI aesthetics.
- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design)

### internal-comms
Write internal communications: status reports, leadership updates, company newsletters, FAQs, incident reports, project updates.
- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/internal-comms)
- Extra files: `examples/`

### pdf
Everything PDF: read/extract text and tables, merge, split, rotate, watermark, create, fill forms, encrypt/decrypt, extract images, OCR scanned PDFs.
- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pdf)
- Extra files: `forms.md`, `reference.md`, `scripts/`

### pptx
PowerPoint files end-to-end: create slide decks, read/extract content, edit existing presentations, combine/split files, work with templates and speaker notes.
- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/pptx)
- Extra files: `editing.md`, `pptxgenjs.md`, `scripts/`

### xlsx
Spreadsheet files (.xlsx, .xlsm, .csv, .tsv): create from scratch, open/read/edit, add columns, compute formulas, format, chart, clean messy data, convert formats.
- Source: [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/xlsx)
- Extra files: `scripts/`

---

## Adding a New Skill

Each skill is a directory containing at minimum a `SKILL.md`:

```
custom/skills/
└── my-skill/
    └── SKILL.md
```

### SKILL.md frontmatter

```markdown
---
name: my-skill
description: One-line description (used by Claude to decide when to trigger this skill)
scope: global   # or: project (omit to ask user each time)
---

# My Skill

[Full skill content — instructions, context, workflow steps]
```

### `scope` field

| Value | Installs to |
|-------|-------------|
| `global` | `~/.claude/skills/` — available in all projects |
| `project` | `.claude/skills/` — current project only |
| *(omitted)* | `/ak:setup-custom` asks the user each time |
