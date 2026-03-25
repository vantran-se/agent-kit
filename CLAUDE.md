# Agent Kit

Shared AI agent setup toolkit. Run `python3 scripts/install.py` once per machine — then `/ak:init-project`, `/ak:setup-skills`, `/ak:setup-custom`, `/ak:update`, `/ak:sync-docs` are available in every project.

## Structure

```
agent-kit/
├── global/                          # Installed into ~/.claude/ by install.py
│   ├── commands/
│   │   ├── ak:init-project.md       # /ak:init-project — full project setup
│   │   ├── ak:setup-custom.md       # /ak:setup-custom — install from custom/
│   │   ├── ak:setup-skills.md       # /ak:setup-skills — install from skills.sh
│   │   └── ak:update.md             # /ak:update — sync MCP permissions to existing project
│   └── settings.json                # MCP server definitions (4 servers) + mcpPermissions
├── custom/                          # User-managed private assets
│   ├── skills/                      # 6 skills (docx, frontend-design, internal-comms, pdf, pptx, xlsx)
│   ├── commands/                    # Optional private slash commands
│   └── hooks/
│       ├── hooks.json               # 24 hook definitions
│       ├── scripts/                 # Standalone Python 3 hook scripts (12 files)
│       └── tests/                   # Hook test suite (test_hooks.py)
├── tests/
│   ├── run_all.py                   # Run all test suites: python3 tests/run_all.py
│   └── test_kit.py                  # Project integrity tests (structure, schema, docs sync)
├── scripts/
│   └── install.py                   # Global installer
└── .claude/
    ├── settings.json                # MCP config + doc-sync hook
    ├── commands/
    │   └── ak:sync-docs.md          # /ak:sync-docs — regenerate docs (this repo only)
    └── skills/
        └── skill-creator/           # Meta-skill: create & evaluate skills
```

## Global Commands (installed to ~/.claude/commands/)

| Command | File | Purpose |
|---------|------|---------|
| `/ak:init-project` | `global/commands/ak:init-project.md` | Per-project setup wizard |
| `/ak:setup-skills` | `global/commands/ak:setup-skills.md` | Install skills from skills.sh |
| `/ak:setup-custom` | `global/commands/ak:setup-custom.md` | Install from custom/ |
| `/ak:update` | `global/commands/ak:update.md` | Sync MCP permissions to existing project |

## Project Commands (this repo only, .claude/commands/)

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

| Skill | Purpose |
|-------|---------|
| `docx` | Word documents |
| `frontend-design` | Production UI |
| `internal-comms` | Internal communications |
| `pdf` | PDF manipulation |
| `pptx` | PowerPoint files |
| `xlsx` | Spreadsheets |

## Custom Hooks (custom/hooks/hooks.json)

24 hooks: `auto-format-prettier`, `auto-format-eslint`, `auto-format-biome`, `auto-format-ruff`, `auto-format-gofmt`, `auto-format-rustfmt`, `auto-format-standardrb`, `auto-format-rubocop`, `notify-on-stop`, `block-dangerous-bash`, `check-secrets`, `prevent-test-skip`, `file-guard`, `lint-changed`, `typecheck-changed`, `check-any-changed`, `test-changed`, `check-comment-replacement`, `check-unused-parameters`, `typecheck-project`, `lint-project`, `test-project`, `check-todos`, `self-review`

Hooks with complex logic have standalone scripts in `custom/hooks/scripts/` (Python 3 only — no `.sh` files).

**Hook input format**: JSON via stdin. Python scripts use `json.load(sys.stdin)`; inline bash commands use `jq -r '.tool_input.field_name'`. Never use `$CLAUDE_TOOL_INPUT_*` env vars — they do not exist.

## Running Tests

```bash
python3 tests/run_all.py                          # all suites
python3 tests/test_kit.py                         # integrity only (structure, schema, docs sync)
python3 custom/hooks/tests/test_hooks.py          # hook behavior only
```

## Development Rules

**After adding/removing skills, commands, or hooks — run `/ak:sync-docs` immediately.**

This repo has a hook in `.claude/settings.json` that reminds you automatically whenever you edit files in `global/` or `custom/`.

- Edit source in `global/commands/` or `custom/` — never edit `~/.claude/commands/` directly
- Re-run `python3 scripts/install.py` after changing `global/` to deploy globally
- Custom skills from [anthropics/skills](https://github.com/anthropics/skills) go in `custom/skills/`
- Hook scripts in `custom/hooks/scripts/` must be Python 3 — no shell scripts
- The `skill-creator` skill in `.claude/skills/` is for developing and evaluating new skills

**Before implementing any Claude Code feature** — use the `claude-code-guide` subagent to verify the correct API/behavior first:

```
Agent(claude-code-guide): verify [feature] — e.g. correct hook input format, MCP scope flags, permission rule syntax
```

Claude Code evolves fast. Never assume — always check docs before writing hooks, MCP config, permissions, or settings.
