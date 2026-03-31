# AI Assistant Configuration — Agent Kit

> Compatible with Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

Agent Kit is a shared AI agent setup toolkit for Claude Code. Install once globally with `python3 scripts/install.py`, clone skills submodule, then bootstrap any project using `/ak:init-project`.

## Tech Stack

- **Language**: Python 3 (scripts), Markdown (commands/skills)
- **Runtime**: Node.js 18+ (MCP servers via npx)
- **Tool**: Claude Code

## Commands

```bash
python3 scripts/install.py              # install global commands + MCP servers
python3 scripts/install.py --init-submodule  # clone claudekit-skills submodule
python3 tests/run_all.py                # run all test suites
python3 tests/test_kit.py               # integrity tests only
```

## Directory Structure

```
global/commands/          # slash commands installed to ~/.claude/commands/
global/settings.json      # MCP server definitions
custom/skills/            # 1 private skill (internal-comms)
custom/hooks/hooks.json   # 2 security hooks (check-secrets, block-dangerous-bash)
skills/claudekit-skills/  # Git submodule — 30+ community skills
.claude/commands/         # repo-local commands (ak:sync-docs)
.claude/skills/           # repo-local skills (skill-creator)
scripts/init-project.py
scripts/install.py
tests/
```

## Conventions

- Edit in `global/` or `custom/` — never edit `~/.claude/` directly
- Hook scripts must be Python 3 — no shell scripts in `custom/hooks/scripts/`
- After adding/removing skills, commands, or hooks: run `/ak:sync-docs`
- Re-run `python3 scripts/install.py` after any change to `global/`

## MCP Servers

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs |
| `gitnexus` | `gitnexus@latest` | Semantic code search |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Skills

**Private** (`custom/skills/`): `internal-comms` — installed per project via `/ak:setup-custom`.

**Community** (30+): `skills/claudekit-skills/.claude/skills/` — cloned via `--init-submodule`, installed per-project via `/ak:setup-skills`. Includes `mcp-management`, `debugging`, `code-review`, `skill-creator`, and more.

## Do Not Modify

- `~/.claude/commands/` — managed by `install.py`
- `~/.claude/settings.json` — managed by `install.py`
- Any `.gitnexus/` directories — auto-generated index
- `skills/claudekit-skills/` — git submodule, update via `git submodule update`
