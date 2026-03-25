# Agent Kit

Shared AI agent setup toolkit for Claude Code. Install once globally, then bootstrap any project with a single command.

## How It Works

| Layer | What it does |
|-------|-------------|
| **Global** (`~/.claude/`) | Commands + user-scoped MCP servers — installed once via `python3 scripts/install.py` |
| **Per-project** (`.claude/`) | Hooks, skills, custom commands — set up per project via `/ak:init-project` |

## Quick Start

```bash
# 1. Clone and install globally (once per machine)
git clone <repo-url> ~/workspace/agent-kit
cd ~/workspace/agent-kit
python3 scripts/install.py

# 2. In any project, run the setup wizard
/ak:init-project

# 3. Optional: install skills and custom assets
/ak:setup-skills
/ak:setup-custom
```

## Global Commands

Installed to `~/.claude/commands/` and available in every project:

| Command | Purpose |
|---------|---------|
| `/ak:init-project` | Full project setup wizard — generates CLAUDE.md, AGENTS.md, hooks, GitNexus index |
| `/ak:setup-skills` | Install skills from `skills.sh` for the current stack |
| `/ak:setup-custom` | Install custom skills, commands, and hooks from `custom/` |
| `/ak:update` | Sync latest MCP permissions from agent-kit into an existing project's `.claude/settings.json` |

This repo also has a local command:

| Command | Purpose |
|---------|---------|
| `/ak:sync-docs` | Regenerate README.md, CLAUDE.md, AGENTS.md (agent-kit repo only) |

## MCP Servers

Defined in `global/settings.json`, registered as user-scoped by `install.py` (`claude mcp add --scope user`), available across all projects:

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs |
| `gitnexus` | `gitnexus@latest` | Semantic code search |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

To add a server, add it to `global/settings.json` and re-run `python3 scripts/install.py`.

## Custom Assets

### Skills (`custom/skills/`)

| Skill | Purpose |
|-------|---------|
| `docx` | Word document creation and manipulation |
| `frontend-design` | Production-grade UI with high design quality |
| `internal-comms` | Internal communications (status reports, updates, newsletters) |
| `pdf` | PDF reading, merging, splitting, OCR, and creation |
| `pptx` | PowerPoint slide deck creation and editing |
| `xlsx` | Spreadsheet reading, editing, and creation |

### Hooks (`custom/hooks/hooks.json`)

24 hooks total:

| Hook | Trigger | Description |
|------|---------|-------------|
| `auto-format-prettier` | PostToolUse | Auto-format JS/TS/JSON/CSS with Prettier |
| `auto-format-eslint` | PostToolUse | Auto-fix ESLint issues |
| `auto-format-biome` | PostToolUse | Auto-format with Biome |
| `auto-format-ruff` | PostToolUse | Auto-format Python with Ruff |
| `auto-format-gofmt` | PostToolUse | Auto-format Go with gofmt |
| `auto-format-rustfmt` | PostToolUse | Auto-format Rust with rustfmt |
| `auto-format-standardrb` | PostToolUse | Auto-format Ruby with StandardRB |
| `auto-format-rubocop` | PostToolUse | Auto-format Ruby with RuboCop |
| `notify-on-stop` | Stop | Desktop notification when task completes |
| `block-dangerous-bash` | PreToolUse | Block destructive shell commands |
| `check-secrets` | PreToolUse | Block hardcoded secrets in files |
| `prevent-test-skip` | PostToolUse | Warn on `.skip()` / `.only()` in tests |
| `file-guard` | PreToolUse | Block access to sensitive files |
| `lint-changed` | PostToolUse | Lint the changed file (Biome or ESLint) |
| `typecheck-changed` | PostToolUse | Run `tsc --noEmit` on changed TypeScript files |
| `check-any-changed` | PostToolUse | Forbid explicit `any` in TypeScript |
| `test-changed` | PostToolUse | Run tests related to the changed file |
| `check-comment-replacement` | PreToolUse | Block edits that replace code with comments |
| `check-unused-parameters` | PreToolUse | Block underscore-prefixed lazy refactoring |
| `typecheck-project` | Stop | Run `tsc --noEmit` on entire project |
| `lint-project` | Stop | Lint entire project at Stop |
| `test-project` | Stop | Run full test suite at Stop |
| `check-todos` | Stop | Block Stop if TodoWrite items are incomplete |
| `self-review` | Stop | Prompt Claude to self-review before stopping |

Hooks with complex logic use standalone Python scripts in `custom/hooks/scripts/`.

Hook input is provided as JSON via stdin. Scripts parse with `json.load(sys.stdin)`; inline bash commands use `jq`.

## Project Structure

```
agent-kit/
├── global/                          # Installed into ~/.claude/ by install.py
│   ├── commands/
│   │   ├── ak:init-project.md       # /ak:init-project — full project setup
│   │   ├── ak:setup-custom.md       # /ak:setup-custom — install from custom/
│   │   ├── ak:setup-skills.md       # /ak:setup-skills — install from skills.sh
│   │   └── ak:update.md             # /ak:update — sync MCP permissions to existing project
│   └── settings.json                # MCP server definitions (read by install.py)
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

## Extending

**Add an MCP server** — add to `global/settings.json`, then re-run `python3 scripts/install.py`:
```json
"my-server": { "command": "npx", "args": ["-y", "my-mcp-package"] }
```

**Add a global command** — create `global/commands/my-command.md`, then re-run `python3 scripts/install.py`.

**Add a custom skill** — add a directory with `SKILL.md` to `custom/skills/`.

**Add a hook** — add an entry to `custom/hooks/hooks.json`. For complex logic, add a Python script to `custom/hooks/scripts/`.

**After any change** — run `/ak:sync-docs` to update README.md, CLAUDE.md, and AGENTS.md.

## Running Tests

```bash
python3 tests/run_all.py                          # all suites
python3 tests/test_kit.py                         # integrity only (structure, schema, docs sync)
python3 custom/hooks/tests/test_hooks.py          # hook behavior only
```

## Requirements

- [Node.js](https://nodejs.org) (for `npx` MCP servers)
- [Claude Code](https://claude.ai/code)
