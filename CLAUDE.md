# Agent Kit

Shared AI agent setup toolkit. Run `./scripts/install.sh` once per machine — then `/init-project`, `/setup-skills`, `/setup-custom`, `/sync-docs` are available in every project.

## Structure

```
agent-kit/
├── global/                          # Installed into ~/.claude/ by install.sh
│   ├── commands/
│   │   ├── init-project.md          # /init-project — full project setup
│   │   ├── setup-skills.md          # /setup-skills — install from skills.sh
│   │   └── setup-custom.md          # /setup-custom — install from custom/
│   └── settings.json                # MCP server definitions (4 servers)
├── custom/                          # User-managed private assets
│   ├── skills/                      # 6 skills (docx, frontend-design, internal-comms, pdf, pptx, xlsx)
│   ├── commands/                    # Optional private slash commands
│   └── hooks/
│       ├── hooks.json               # 22 hook definitions
│       ├── scripts/                 # Standalone Python 3 hook scripts (12 files)
│       └── tests/                   # Hook test suite (test_hooks.py)
├── tests/
│   ├── run_all.py                   # Run all test suites: python3 tests/run_all.py
│   └── test_kit.py                  # Project integrity tests (structure, schema, docs sync)
├── scripts/
│   └── install.sh                   # Global installer
└── .claude/
    ├── settings.json                # MCP config + doc-sync hook
    ├── commands/
    │   └── sync-docs.md             # /sync-docs — regenerate docs (this repo only)
    └── skills/
        └── skill-creator/           # Meta-skill: create & evaluate skills
```

## Global Commands (installed to ~/.claude/commands/)

| Command | File | Purpose |
|---------|------|---------|
| `/init-project` | `global/commands/init-project.md` | Per-project setup wizard |
| `/setup-skills` | `global/commands/setup-skills.md` | Install skills from skills.sh |
| `/setup-custom` | `global/commands/setup-custom.md` | Install from custom/ |

## Project Commands (this repo only, .claude/commands/)

| Command | File | Purpose |
|---------|------|---------|
| `/sync-docs` | `.claude/commands/sync-docs.md` | Regenerate README, CLAUDE.md, AGENTS.md |

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

22 hooks: `auto-format-prettier`, `auto-format-eslint`, `auto-format-biome`, `auto-format-ruff`, `auto-format-gofmt`, `auto-format-rustfmt`, `notify-on-stop`, `block-dangerous-bash`, `check-secrets`, `prevent-test-skip`, `file-guard`, `lint-changed`, `typecheck-changed`, `check-any-changed`, `test-changed`, `check-comment-replacement`, `check-unused-parameters`, `typecheck-project`, `lint-project`, `test-project`, `check-todos`, `self-review`

Hooks with complex logic have standalone scripts in `custom/hooks/scripts/` (Python 3 only — no `.sh` files).

## Running Tests

```bash
python3 tests/run_all.py                          # all suites
python3 tests/test_kit.py                         # integrity only (structure, schema, docs sync)
python3 custom/hooks/tests/test_hooks.py          # hook behavior only
```

## Development Rules

**After adding/removing skills, commands, or hooks — run `/sync-docs` immediately.**

This repo has a hook in `.claude/settings.json` that reminds you automatically whenever you edit files in `global/` or `custom/`.

- Edit source in `global/commands/` or `custom/` — never edit `~/.claude/commands/` directly
- Re-run `./scripts/install.sh` after changing `global/` to deploy globally
- Custom skills from [anthropics/skills](https://github.com/anthropics/skills) go in `custom/skills/`
- Hook scripts in `custom/hooks/scripts/` must be Python 3 — no shell scripts
- The `skill-creator` skill in `.claude/skills/` is for developing and evaluating new skills
