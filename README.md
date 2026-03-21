# Agent Kit

Shared AI agent setup toolkit for Claude Code. Install once globally, then bootstrap any project with a single command.

## How It Works

Two-layer setup:

| Layer | Command | When | Where |
|-------|---------|------|-------|
| **Global** | `./scripts/install.sh` | Once per machine | `~/.claude/` |
| **Per-project** | `/init-project` | Once per project | project root |

---

## Quick Start

### 1. Global install (once per machine)

```bash
git clone git@github.com:vantran-se/agent-kit.git ~/workspace/agent-kit
cd ~/workspace/agent-kit
./scripts/install.sh
```

Installs:
- 3 slash commands → `~/.claude/commands/`
- 4 MCP servers → `~/.claude/settings.json`
- Saves agent-kit path → `~/.claude/agent-kit-path`

Verify:
```bash
./scripts/install.sh --check
```

### 2. Initialize a project

Open any project in Claude Code:

```
/init-project
```

Generates: `CLAUDE.md`, `AGENTS.md`, auto-format hooks, indexes with GitNexus, offers custom assets.

### 3. Install skills (optional)

```
/setup-skills    # discover & install from skills.sh
/setup-custom    # install from custom/ in this repo
```

---

## Commands

| Command | What it does |
|---------|-------------|
| `/init-project` | Full project setup — detects stack, generates CLAUDE.md + AGENTS.md, configures hooks, indexes with GitNexus, offers custom assets |
| `/setup-skills` | Search skills.sh for stack-relevant skills, pick and install |
| `/setup-custom` | Install custom skills, commands, and hooks from this repo |

---

## MCP Servers (global, no API key required)

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp` | Up-to-date library docs — `resolve-library-id` → `get-library-docs` |
| `gitnexus` | `gitnexus@latest` | Semantic code search across indexed repos |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Better reasoning for complex/multi-step problems |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge graph across sessions |

---

## Custom Assets

Assets in `custom/` are offered during `/setup-custom` and `/init-project`. Install globally or per-project.

### Skills (`custom/skills/`)

| Skill | Description |
|-------|-------------|
| `docx` | Create/read/edit Word documents (.docx) |
| `frontend-design` | Production-grade UI — React, landing pages, dashboards |
| `internal-comms` | Status reports, newsletters, incident reports |
| `pdf` | Read/merge/split/OCR PDF files |
| `pptx` | Create/edit PowerPoint presentations |
| `xlsx` | Create/read/edit spreadsheets (.xlsx, .csv) |

### Hooks (`custom/hooks/hooks.json`)

22 hooks total. Install per-project or globally via `/setup-custom`.

#### Auto-format (project scope)

| Hook | Trigger | Stacks |
|------|---------|--------|
| `auto-format-prettier` | PostToolUse | TS, JS, Next.js, React, Vue, Svelte |
| `auto-format-eslint` | PostToolUse | TS, JS, Next.js, React |
| `auto-format-biome` | PostToolUse | TS, JS, Next.js, React |
| `auto-format-ruff` | PostToolUse | Python, FastAPI, Django, Flask |
| `auto-format-gofmt` | PostToolUse | Go |
| `auto-format-rustfmt` | PostToolUse | Rust |

#### Safety (global scope)

| Hook | Trigger | Description |
|------|---------|-------------|
| `block-dangerous-bash` | PreToolUse | Block `rm -rf`, `DROP TABLE`, force push, `kill -9` |
| `check-secrets` | PreToolUse | Block hardcoded API keys and private keys |
| `file-guard` | PreToolUse | Block access to `.env`, private keys, `.claudeignore` patterns |
| `check-comment-replacement` | PreToolUse | Block replacing real code with comments |
| `check-unused-parameters` | PreToolUse | Block underscore-prefixed parameters |

#### Code quality (project scope)

| Hook | Trigger | Description |
|------|---------|-------------|
| `lint-changed` | PostToolUse | Run Biome or ESLint on the changed file |
| `typecheck-changed` | PostToolUse | Run `tsc --noEmit` on TypeScript changes |
| `check-any-changed` | PostToolUse | Forbid explicit `any` types in TypeScript |
| `test-changed` | PostToolUse | Find and run tests for the changed file |
| `prevent-test-skip` | PostToolUse | Warn on `.skip()` / `.only()` in test files |

#### Project-wide checks at Stop (project scope)

| Hook | Trigger | Description |
|------|---------|-------------|
| `typecheck-project` | Stop | `tsc --noEmit` on entire project |
| `lint-project` | Stop | Biome or ESLint on entire project |
| `test-project` | Stop | Run full test suite |

#### Session quality (global scope)

| Hook | Trigger | Description |
|------|---------|-------------|
| `check-todos` | Stop | Block if incomplete TodoWrite items exist |
| `self-review` | Stop | Prompt self-review before stopping |
| `notify-on-stop` | Stop | Desktop notification with project name |

> All hooks in `custom/hooks/scripts/` are standalone Python 3 scripts.

---

## Project Structure

```
agent-kit/
├── global/                          # Installed into ~/.claude/ by install.sh
│   ├── commands/
│   │   ├── init-project.md          # /init-project
│   │   ├── setup-skills.md          # /setup-skills
│   │   └── setup-custom.md          # /setup-custom
│   └── settings.json                # MCP server definitions
├── custom/                          # User-managed private assets
│   ├── skills/                      # 6 skills (docx, frontend-design, internal-comms, pdf, pptx, xlsx)
│   ├── commands/                    # Optional private slash commands
│   └── hooks/
│       ├── hooks.json               # 22 hook definitions
│       ├── scripts/                 # Standalone Python 3 hook scripts (12 files)
│       └── tests/                   # Hook test suite — run: python3 tests/test_hooks.py
│           ├── file-guard.py
│           ├── lint-changed.py
│           ├── typecheck-changed.py
│           ├── check-any-changed.py
│           ├── test-changed.py
│           ├── typecheck-project.py
│           ├── lint-project.py
│           ├── test-project.py
│           ├── check-comment-replacement.py
│           ├── check-unused-parameters.py
│           ├── check-todos.py
│           └── self-review.py
├── tests/
│   ├── run_all.py                   # Run all tests: python3 tests/run_all.py
│   └── test_kit.py                  # Project integrity tests
├── scripts/
│   └── install.sh                   # Global installer
└── .claude/
    ├── settings.json                # MCP config + doc-sync reminder hook
    ├── commands/
    │   └── sync-docs.md             # /sync-docs (agent-kit only)
    └── skills/
        └── skill-creator/           # Meta-skill: create & evaluate new skills
```

---

## Extending

### Add a new MCP server
1. Add to `global/settings.json`
2. Run `./scripts/install.sh`

### Add a new global command
1. Create `global/commands/my-command.md`
2. Run `./scripts/install.sh`

### Add a custom skill
1. Create `custom/skills/my-skill/SKILL.md`
2. Available via `/setup-custom` immediately

### Add a hook
1. Add entry to `custom/hooks/hooks.json`
2. For complex logic, add a Python script to `custom/hooks/scripts/` and reference it via `python3 "$(cat ~/.claude/agent-kit-path)/custom/hooks/scripts/your-script.py"`
3. Available via `/setup-custom` immediately

### Update docs after any change

Run `/sync-docs` — available when working inside agent-kit (`.claude/commands/sync-docs.md`).

---

## Requirements

- [Node.js](https://nodejs.org) — for `npx` (runs MCP servers and skills CLI)
- [Python 3.7+](https://python.org) — for hook scripts in `custom/hooks/scripts/`
- [Claude Code](https://claude.ai/code) CLI
