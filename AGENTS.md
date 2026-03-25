# AI Assistant Configuration — Agent Kit

> Compatible with Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

Agent Kit is a shared toolkit for bootstrapping AI agent configuration across multiple projects. Install once globally via `python3 scripts/install.py`, then use `/ak:init-project` in any project.

## Tech Stack

- **Languages**: Markdown, JSON, Python 3 (hook scripts), Bash (installer)
- **Runtime**: Node.js / npx (for MCP servers and skills CLI)
- **Target**: Claude Code CLI

## Commands

```bash
python3 scripts/install.py          # Install globally (once per machine)
python3 scripts/install.py --check  # Verify installation status
```

## Directory Structure

```
global/commands/        Source of truth for slash commands (deployed to ~/.claude/commands/)
global/settings.json    MCP server definitions (read by install.py, registered via claude mcp add)
custom/skills/          Private skills offered during /ak:setup-custom
custom/commands/        Private slash commands offered during /ak:setup-custom
custom/hooks/           Hook definitions (hooks.json) and scripts (scripts/*.py)
scripts/                Installer and utilities
.claude/                Settings and skills for agent-kit development only
```

## Conventions

- Always edit source in `global/` or `custom/` — never in `~/.claude/` directly
- Re-run `install.py` after changing `global/` to deploy
- Run `/ak:sync-docs` after adding skills, commands, or hooks
- Hook scripts must be Python 3 — place in `custom/hooks/scripts/*.py`
- Hook input arrives as JSON via stdin — parse with `json.load(sys.stdin)` or `jq`; never use `$CLAUDE_TOOL_INPUT_*` env vars
- MCP servers are defined in `global/settings.json` — `install.py` registers them via `claude mcp add --scope user`
- Templates/prompts are plain Markdown — file content is the prompt sent to Claude

## MCP Servers (defined in global/settings.json)

| Server | Purpose |
|--------|---------|
| `context7` | Up-to-date library docs — `resolve-library-id` → `get-library-docs` |
| `gitnexus` | Semantic code search — `search_code` |
| `sequential-thinking` | Structured reasoning for complex decisions |
| `memory` | Persistent knowledge graph across sessions |

## Custom Skills Available

`docx`, `frontend-design`, `internal-comms`, `pdf`, `pptx`, `xlsx` — see README.md for details.

## Do Not Modify

- `~/.claude/commands/` — managed by `install.py`, always edit source in `global/commands/`
- `custom/skills/*/LICENSE.txt` — third-party licenses
- `.claude/skills/skill-creator/` — do not edit, sourced from anthropics/skills
