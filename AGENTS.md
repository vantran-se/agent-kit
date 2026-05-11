# AI Assistant Configuration — Agent Kit

> Compatible with Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

Agent Kit is a shared AI agent setup toolkit for Claude Code. Install it once globally, then bootstrap target projects with `/ak:init-project`, `/ak:setup-skills`, and `/ak:setup-custom`.

## Tech Stack

- **Language**: Python 3 scripts, Markdown commands/skills, JSON settings/docs
- **Runtime**: Node.js 18+ for MCP servers and optional GitNexus workflows
- **Primary tool**: Claude Code

## Commands

```bash
python3 scripts/install.py                   # install global commands + MCP servers
python3 scripts/install.py --init-submodule  # initialize skills submodules
python3 scripts/install.py --check           # check install status
python3 tests/run_all.py                     # run all test suites
python3 tests/test_kit.py                    # integrity tests only
python3 tests/test_init_project_script.py    # init-project tests only
python3 custom/hooks/tests/test_hooks.py     # hook tests only
```

## Directory Structure

```text
global/commands/          # 4 slash commands installed to ~/.claude/commands/
global/settings.json      # MCP server definitions + mcpPermissions
custom/commands/          # code-review, research, validate-and-fix
custom/hooks/hooks.json   # 3 hooks: block-dangerous-bash, check-secrets, gitnexus-auto-rebuild
custom/skills/            # custom skills: html-doc-coauthoring
skills/                   # Git submodules: claudekit-skills, anthropics-skills
.claude/commands/         # repo-local commands: ak:sync-docs, create-command, create-subagent
.claude/skills/           # repo-local skills: skill-creator
docs/raw/                 # editable visual documentation JSON
docs/                     # generated visual documentation HTML
scripts/                  # install.py, init-project.py
tests/                    # repository test suites
```

## Conventions

- Edit source in `global/` or `custom/`; never edit `~/.claude/` directly
- After adding/removing skills, commands, hooks, or MCP servers: run `/ak:sync-docs`
- Re-run `python3 scripts/install.py` after changing `global/`
- Hook scripts in `custom/hooks/scripts/` must be Python 3; no shell scripts
- Keep HTML doc source in `docs/raw/` and generated files in `docs/`
- Do not edit `skills/claudekit-skills/` or `skills/anthropics-skills/`; they are Git submodules

## MCP Servers

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp@latest` | Up-to-date library docs |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Skills

- **Community Skills**: installed from `skills/claudekit-skills/` with `/ak:setup-skills`
- **Anthropic Official Skills**: installed from `skills/anthropics-skills/` with `/ak:setup-skills`
- **Custom Skills**: `html-doc-coauthoring`
- **Repo-local Skills**: `skill-creator`

## Custom Assets

- **Custom commands**: `code-review`, `research`, `validate-and-fix`
- **Custom hooks**: `block-dangerous-bash`, `check-secrets`, `gitnexus-auto-rebuild`
- **Visual docs**: `docs/agent-kit-project-documentation.html` from `docs/raw/agent-kit-project-documentation.json`

## Do Not Modify

- `~/.claude/commands/` — managed by `scripts/install.py`
- `~/.claude/settings.json` — managed by `scripts/install.py` and `/ak:update`
- Any `.gitnexus/` directories — auto-generated GitNexus knowledge graph
- `skills/claudekit-skills/` and `skills/anthropics-skills/` — Git submodules
