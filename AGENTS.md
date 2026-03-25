# AI Assistant Configuration — Agent Kit

> Compatible with Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

Agent Kit is a shared toolkit for bootstrapping AI agent configuration across multiple projects. Install once globally via `./scripts/install.sh`, then use `/ak:init-project` in any project.

## Tech Stack

- **Languages**: Markdown, JSON, Python 3 (hook scripts), Bash (installer)
- **Runtime**: Node.js / npx (for MCP servers and skills CLI)
- **Target**: Claude Code CLI

## Commands

```bash
./scripts/install.sh          # Install globally (once per machine)
./scripts/install.sh --check  # Verify installation status
```

## Directory Structure

```
global/commands/        Source of truth for slash commands (deployed to ~/.claude/commands/)
global/settings.json    MCP server definitions (merged into ~/.claude/settings.json)
custom/skills/          Private skills offered during /ak:setup-custom
custom/commands/        Private slash commands offered during /ak:setup-custom
custom/hooks/           Hook definitions (hooks.json) and scripts (scripts/*.py)
scripts/                Installer and utilities
.claude/                Settings and skills for agent-kit development only
```

## Conventions

- Always edit source in `global/` or `custom/` — never in `~/.claude/` directly
- Re-run `install.sh` after changing `global/` to deploy
- Run `/ak:sync-docs` after adding skills, commands, or hooks
- Hook scripts must be Python 3 — place in `custom/hooks/scripts/*.py`
- Templates/prompts are plain Markdown — file content is the prompt sent to Claude

## MCP Servers (installed globally by install.sh)

| Server | Purpose |
|--------|---------|
| `context7` | Up-to-date library docs — `resolve-library-id` → `get-library-docs` |
| `gitnexus` | Semantic code search — `search_code` |
| `sequential-thinking` | Structured reasoning for complex decisions |
| `memory` | Persistent knowledge graph across sessions |

## Custom Skills Available

`docx`, `frontend-design`, `internal-comms`, `pdf`, `pptx`, `xlsx` — see README.md for details.

## Do Not Modify

- `~/.claude/commands/` — managed by `install.sh`, always edit source in `global/commands/`
- `custom/skills/*/LICENSE.txt` — third-party licenses
- `.claude/skills/skill-creator/` — do not edit, sourced from anthropics/skills
