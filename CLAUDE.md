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
│   └── settings.json                # MCP server definitions (3 servers) + mcpPermissions
├── custom/
│   ├── commands/
│   │   ├── code-review.md
│   │   ├── research.md
│   │   └── validate-and-fix.md
│   ├── hooks/
│   │   └── hooks.json               # 3 active hooks
│   └── skills/
├── skills/
│   ├── claudekit-skills/            # Git submodule — 30+ community skills
│   └── anthropics-skills/           # Git submodule — 17 official Anthropic skills
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
| `/ak:setup-skills` | `global/commands/ak:setup-skills.md` | Install from claudekit-skills + anthropics/skills |
| `/ak:setup-custom` | `global/commands/ak:setup-custom.md` | Install custom skills/commands/hooks from custom/ |
| `/ak:update` | `global/commands/ak:update.md` | Sync MCP permissions to global settings |

## Project Commands (this repo only)

| Command | File | Purpose |
|---------|------|---------|
| `/ak:sync-docs` | `.claude/commands/ak:sync-docs.md` | Regenerate README, CLAUDE.md, AGENTS.md |

## MCP Servers (global/settings.json)

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

**Note:** GitNexus was replaced with **graphify** — a knowledge graph tool that creates `graphify-out/` for semantic code navigation.

## Custom Commands (custom/commands/)

| Command | Purpose |
|---------|---------|
| `code-review` | Multi-aspect code review using parallel code-review-expert agents |
| `research` | Deep research with parallel subagents and automatic citations |
| `validate-and-fix` | Run quality checks and automatically fix issues |

## Custom Skills (custom/skills/)

Private project-specific skills. Add a directory with `SKILL.md` to create one.

## Custom Hooks (custom/hooks/hooks.json)

3 active hooks:
- `check-secrets` — Block writing hardcoded secrets/API keys
- `block-dangerous-bash` — Block dangerous bash commands (rm -rf, force push, DROP TABLE, etc.)
- `graphify-auto-rebuild` — Auto-rebuild graphify knowledge graph after code changes (PostToolUse hook)

Hook input: JSON via stdin — use `jq -r '.tool_input.field_name'`.

## Development Rules

**After adding/removing skills, commands, or hooks — run `/ak:sync-docs` immediately.**

- Edit source in `global/commands/` or `custom/` — never edit `~/.claude/` directly
- Re-run `python3 scripts/install.py` after changing `global/` to deploy globally
- Hook scripts in `custom/hooks/scripts/` must be Python 3 — no shell scripts
- The `skill-creator` skill in `.claude/skills/` is for developing and evaluating new skills

**Before implementing any Claude Code feature** — use the `claude-code-guide` subagent to verify the correct API/behavior first.

## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, the `graphify-auto-rebuild` hook automatically rebuilds the graph
- Manual rebuild: `python3 -c "from graphify.watch import _rebuild_code; from pathlib import Path; _rebuild_code(Path('.'))"`
