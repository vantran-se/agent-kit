# Agent Kit

Shared AI agent setup toolkit for Claude Code. Install once globally, then bootstrap any project with a single command.

## How It Works

| Layer | What it does |
|-------|-------------|
| **Global** (`~/.claude/`) | Commands + MCP servers — installed via `python3 scripts/install.py` |
| **Submodules** (`skills/`) | Community skills from 2 sources — cloned via `--init-submodule` |
| **Per-project** (`.claude/`) | Skills, hooks — set up via `/ak:init-project`, `/ak:setup-skills`, `/ak:setup-custom` |

## Quick Start

```bash
git clone <this-repo>
cd agent-kit
python3 scripts/install.py    # installs global commands + MCP servers
python3 scripts/install.py --init-submodule  # clone skills submodules
```

Then in any project:
```
/ak:init-project    # generate CLAUDE.md, AGENTS.md, hooks, gitnexus rebuild
/ak:setup-skills    # install community skills (debugging, code-review, etc.)
/ak:setup-custom    # install custom skills, commands, and hooks from custom/
```

## Commands

| Command | Purpose |
|---------|---------|
| `/ak:init-project` | Per-project setup wizard — CLAUDE.md, AGENTS.md, hooks, gitnexus |
| `/ak:setup-skills` | Install community skills from claudekit-skills + anthropics/skills submodules |
| `/ak:setup-custom` | Install custom skills, commands, and hooks from `custom/` |
| `/ak:update` | Sync MCP permissions to global settings |
| `/ak:sync-docs` | Regenerate README, CLAUDE.md, AGENTS.md (this repo only) |

## MCP Servers

Installed globally via `global/settings.json`:

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Skills Sources

### claudekit-skills (skills/claudekit-skills/)

30+ community skills. Cloned via `--init-submodule`. Installed per-project via `/ak:setup-skills`.

Key skills: `debugging`, `code-review`, `skill-creator`, `mcp-management`, `frontend-development`, `backend-development`, `ai-multimodal`, `context-engineering`, `databases`, `devops`

### anthropics/skills (skills/anthropics-skills/)

17 official Anthropic skills. Installed per-project via `/ak:setup-skills`.

Key skills: `claude-api`, `mcp-builder`, `pdf`, `docx`, `xlsx`, `pptx`, `web-artifacts-builder`, `frontend-design`, `canvas-design`, `internal-comms`

### Custom Skills (custom/skills/)

Private project-specific skills. Add a directory with `SKILL.md` to create one.

## Custom Hooks

3 hooks in `custom/hooks/hooks.json`:

| Hook | Trigger | Description |
|------|---------|-------------|
| `check-secrets` | PreToolUse / Write\|Edit\|MultiEdit | Block writing hardcoded secrets or API keys |
| `block-dangerous-bash` | PreToolUse / Bash | Block dangerous bash commands (rm -rf, force push, DROP TABLE, etc.) |
| `gitnexus-auto-rebuild` | PostToolUse / Write\|Edit\|MultiEdit | Auto-rebuild gitnexus knowledge graph after code changes |

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
│   ├── commands/
│   │   ├── code-review.md
│   │   ├── research.md
│   │   └── validate-and-fix.md
│   └── hooks/
│       └── hooks.json               # 3 hooks (check-secrets, block-dangerous-bash, gitnexus-auto-rebuild)
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

## Extending

- **Add MCP servers**: edit `global/settings.json`, re-run `python3 scripts/install.py`
- **Add commands**: add `.md` files to `global/commands/` or `custom/commands/`
- **Add custom skills**: add a directory with `SKILL.md` to `custom/skills/`
- **Add hooks**: add entries to `custom/hooks/hooks.json`
- After any change: run `/ak:sync-docs` to keep docs in sync

## Requirements

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| **Node.js** | 18+ | MCP servers (npx), skills | `brew install node` |
| **Python** | 3.10+ | Scripts | `brew install python@3.12` |
| **Claude Code** | Latest | Main AI agent | `npm install -g @anthropic/claude-code` |
| **Git** | Latest | Submodules, version control | `brew install git` |

### Optional Tools

| Tool | Purpose | Install |
|------|---------|---------|
| **GitNexus** | Knowledge graph for codebase | `npm install -g gitnexus` |
| **npx** | Run MCP servers | Comes with Node.js/npm |

### Post-Install Setup

```bash
# 1. Install Agent Kit globally
cd agent-kit
python3 scripts/install.py

# 2. Initialize submodules (clone skills)
python3 scripts/install.py --init-submodule

# 3. Verify installation
python3 scripts/install.py --check
```

### Per-Project Setup

```bash
# In any project directory
/ak:init-project    # Generate CLAUDE.md, AGENTS.md, hooks
/ak:setup-skills    # Install skills (debugging, code-review, etc.)
/ak:setup-custom    # Install custom skills, commands, and hooks from custom/
```
