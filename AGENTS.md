# AI Assistant Configuration — Agent Kit

> Compatible with Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

Agent Kit is a shared AI agent setup toolkit for Claude Code. Install once globally with `python3 scripts/install.py`, then bootstrap any project using `/ak:init-project`.

## Tech Stack

- **Language**: Python 3 (scripts), Markdown (commands/skills)
- **Runtime**: Node.js 18+ (MCP servers via npx)
- **Tool**: Claude Code

## Commands

```bash
python3 scripts/install.py              # install global commands + MCP servers
python3 scripts/install.py --init-submodule  # clone skills submodules
python3 tests/run_all.py                # run all test suites
python3 tests/test_kit.py               # integrity tests only
```

## Directory Structure

```
global/commands/          # slash commands installed to ~/.claude/commands/
global/settings.json      # MCP server definitions
custom/commands/          # 3 custom commands (code-review, research, validate-and-fix)
custom/hooks/hooks.json   # 3 security hooks (check-secrets, block-dangerous-bash, gitnexus-auto-rebuild)
skills/
  claudekit-skills/       # Git submodule — 30+ community skills
  anthropics-skills/      # Git submodule — 17 official Anthropic skills
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
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Skills

**Community Skills** (30+ from claudekit-skills): `debugging`, `code-review`, `skill-creator`, `mcp-management`, `frontend-development`, `backend-development`, `ai-multimodal`, `context-engineering`, `databases`, `devops`

**Anthropic Official Skills** (17 from anthropics/skills): `claude-api`, `mcp-builder`, `pdf`, `docx`, `xlsx`, `pptx`, `web-artifacts-builder`, `frontend-design`, `canvas-design`, `internal-comms`

**Custom Skills** (from custom/skills/): Project-specific skills defined with `SKILL.md`

Installed per-project via `/ak:setup-skills` with user selection.

## Do Not Modify

- `~/.claude/commands/` — managed by `install.py`
- `~/.claude/settings.json` — managed by `install.py`
- Any `.gitnexus/` directories — auto-generated GitNexus knowledge graph
- `skills/claudekit-skills/` and `skills/anthropics-skills/` — git submodules
