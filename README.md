# Agent Kit

Shared AI agent setup toolkit for Claude Code. Install once globally, then bootstrap any project with a single command.

## How It Works

| Layer | What it does |
|-------|-------------|
| **Global** (`~/.claude/`) | Commands + MCP servers + claudekit-skills plugin — installed once via `python3 scripts/install.py` |
| **Per-project** (`.claude/`) | Hooks, custom skills, commands — set up per project via `/ak:init-project` |

## Quick Start

```bash
git clone <this-repo>
python3 scripts/install.py        # installs global commands, MCP servers, claudekit-skills plugin
```

Then in any project:
```
/ak:init-project    # generate CLAUDE.md, AGENTS.md, hooks, GitNexus index
/ak:setup-custom    # install custom skills, commands, hooks from this repo
/ak:setup-skills    # install additional skills from the skills.sh registry
```

## Commands

| Command | Purpose |
|---------|---------|
| `/ak:init-project` | Per-project setup wizard — CLAUDE.md, AGENTS.md, hooks, GitNexus |
| `/ak:setup-skills` | Install additional skills from the skills.sh registry |
| `/ak:setup-custom` | Install custom skills, commands, and hooks from `custom/` |
| `/ak:update` | Sync MCP permissions to an existing project |
| `/ak:sync-docs` | Regenerate README, CLAUDE.md, AGENTS.md (this repo only) |

## MCP Servers

Installed globally via `global/settings.json`:

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs |
| `gitnexus` | `gitnexus@latest` | Semantic code search |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Skills

### Community Skills (claudekit-skills)

Installed globally via `install.py` (`claude plugin marketplace add mrgoonie/claudekit-skills` + 12 plugin bundles). Covers frontend, backend, AI/ML, devops, databases, debugging, testing, and more — **activated automatically** by Claude based on task context, no syntax needed.

### Custom Skills (custom/skills/)

1 private skill installed per project via `/ak:setup-custom`:

| Skill | Description |
|-------|-------------|
| `internal-comms` | Internal communications — status reports, leadership updates, newsletters, incident reports |

## Custom Hooks

2 hooks in `custom/hooks/hooks.json` — installed per project via `/ak:setup-custom`:

| Hook | Trigger | Description |
|------|---------|-------------|
| `block-dangerous-bash` | PreToolUse / Bash | Block dangerous commands (rm -rf, force push, DROP TABLE, kill -9) |
| `check-secrets` | PreToolUse / Write\|Edit\|MultiEdit | Block writing hardcoded secrets or API keys |

## Project Structure

```
agent-kit/
├── global/                          # Installed into ~/.claude/ by install.py
│   ├── commands/
│   │   ├── ak:init-project.md
│   │   ├── ak:setup-custom.md
│   │   ├── ak:setup-skills.md
│   │   └── ak:update.md
│   └── settings.json                # MCP server definitions + mcpPermissions
├── custom/                          # User-managed private assets
│   ├── skills/
│   │   └── internal-comms/          # Private skill
│   ├── commands/                    # Optional private slash commands
│   └── hooks/
│       ├── hooks.json               # 2 hook definitions
│       └── scripts/                 # Python 3 hook scripts (if any)
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

## Extending

- **Add MCP servers**: edit `global/settings.json`, re-run `python3 scripts/install.py`
- **Add commands**: add `.md` files to `global/commands/` or `custom/commands/`
- **Add custom skills**: add a directory with `SKILL.md` to `custom/skills/`
- **Add hooks**: add entries to `custom/hooks/hooks.json`
- After any change: run `/ak:sync-docs` to keep docs in sync

## Requirements

- Node.js 18+
- Claude Code
