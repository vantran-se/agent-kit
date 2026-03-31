# Agent Kit

Shared AI agent setup toolkit. Run `python3 scripts/install.py` once per machine — then `/ak:init-project`, `/ak:setup-skills`, `/ak:setup-custom`, `/ak:update`, `/ak:sync-docs` are available in every project.

## Structure

```
agent-kit/
├── global/                          # Installed into ~/.claude/ by install.py
│   ├── commands/
│   │   ├── ak:init-project.md
│   │   ├── ak:setup-custom.md
│   │   ├── ak:setup-skills.md
│   │   └── ak:update.md
│   └── settings.json                # MCP server definitions (4 servers) + mcpPermissions
├── custom/
│   ├── skills/
│   │   └── internal-comms/
│   ├── commands/
│   └── hooks/
│       └── hooks.json               # 1 active hook (check-secrets)
├── skills/
│   └── claudekit-skills/            # Git submodule — 30+ community skills
├── tests/
│   ├── run_all.py
│   ├── test_init_project_script.py
│   └── test_kit.py
├── scripts/
│   ├── init-project.py
│   └── install.py
└── .claude/
    ├── settings.json
    ├── commands/
    │   └── ak:sync-docs.md
    └── skills/
        └── skill-creator/
```

## Global Commands (installed to ~/.claude/commands/)

| Command | File | Purpose |
|---------|------|---------|
| `/ak:init-project` | `global/commands/ak:init-project.md` | Per-project setup wizard |
| `/ak:setup-skills` | `global/commands/ak:setup-skills.md` | Install skills from submodule + skills.sh |
| `/ak:setup-custom` | `global/commands/ak:setup-custom.md` | Install from custom/ + submodule skills |
| `/ak:update` | `global/commands/ak:update.md` | Sync MCP permissions to existing project |

## Project Commands (this repo only)

| Command | File | Purpose |
|---------|------|---------|
| `/ak:sync-docs` | `.claude/commands/ak:sync-docs.md` | Regenerate README, CLAUDE.md, AGENTS.md |

## MCP Servers (global/settings.json)

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs |
| `gitnexus` | `gitnexus@latest` | Semantic code search |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Custom Skills (custom/skills/)

`internal-comms` — private skill for internal communications.

Community skills (30+) in `skills/claudekit-skills/.claude/skills/` — installed per-project via `/ak:setup-custom`.

## Custom Hooks (custom/hooks/hooks.json)

1 active hook: `check-secrets`

Hook input: JSON via stdin — use `jq -r '.tool_input.field_name'`.

## Development Rules

**After adding/removing skills, commands, or hooks — run `/ak:sync-docs` immediately.**

- Edit source in `global/commands/` or `custom/` — never edit `~/.claude/` directly
- Re-run `python3 scripts/install.py` after changing `global/` to deploy globally
- Hook scripts in `custom/hooks/scripts/` must be Python 3 — no shell scripts
- The `skill-creator` skill in `.claude/skills/` is for developing and evaluating new skills

**Before implementing any Claude Code feature** — use the `claude-code-guide` subagent to verify the correct API/behavior first.
