# Custom Commands

Place your custom slash commands here as `.md` files.

These are commands NOT in `global/commands/` — they are optional or project-type-specific commands you may want to install selectively.

## Structure

```
custom/commands/
└── my-command.md
```

## File Format

```markdown
---
description: One-line description shown in /help
scope: global   # or: project
---

# My Command

[Full prompt content for this command]
```

## `scope` field

- `global` — offer to install to `~/.claude/commands/` (available in all projects)
- `project` — offer to install to `.claude/commands/` in the current project only
- omitted — `/setup-custom` will ask the user each time

## Installation

Run `/setup-custom` — it will discover commands here and ask which to install.
