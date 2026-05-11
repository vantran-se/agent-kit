# Agent Kit

Shared AI agent setup toolkit for Claude Code. Install it once per machine, then bootstrap target projects with consistent commands, MCP servers, skills, hooks, and assistant guidance.

## How It Works

| Layer | Source | Installed / used by |
|-------|--------|---------------------|
| Global | `global/commands/`, `global/settings.json` | `python3 scripts/install.py` installs commands and MCP permissions globally |
| Submodule | `skills/claudekit-skills/`, `skills/anthropics-skills/` | `/ak:setup-skills` installs selected community or official skills into target projects |
| Custom | `custom/commands/`, `custom/hooks/`, `custom/skills/` | `/ak:setup-custom` installs selected reusable assets into target projects |
| Repo-local | `.claude/commands/`, `.claude/skills/`, `.claude/settings.json` | Maintenance tooling for this repository |
| Visual docs | `docs/raw/`, `docs/` | JSON sources rendered into reader-friendly HTML documentation |

## Quick Start

```bash
git clone <this-repo>
cd agent-kit
python3 scripts/install.py
python3 scripts/install.py --init-submodule
python3 scripts/install.py --check
```

Then in any target project:

```text
/ak:init-project
/ak:setup-skills
/ak:setup-custom
```

## Commands

### Global Commands

Installed into `~/.claude/commands/` by `python3 scripts/install.py`.

| Command | Source file | Purpose |
|---------|-------------|---------|
| `/ak:init-project` | `global/commands/ak:init-project.md` | Per-project setup wizard for assistant docs, hooks, MCP permissions, and GitNexus guidance |
| `/ak:setup-custom` | `global/commands/ak:setup-custom.md` | Install custom skills, commands, and hooks from `custom/` |
| `/ak:setup-skills` | `global/commands/ak:setup-skills.md` | Install community and official Anthropic skills from submodules |
| `/ak:update` | `global/commands/ak:update.md` | Sync Agent Kit MCP permissions into global `~/.claude/settings.json` |

### Repo-local Commands

Available only in this repository through `.claude/commands/`.

| Command | Source file | Purpose |
|---------|-------------|---------|
| `/ak:sync-docs` | `.claude/commands/ak:sync-docs.md` | Regenerate `README.md`, `CLAUDE.md`, and `AGENTS.md` after assets change |
| `/create-command` | `.claude/commands/create-command.md` | Create a Claude Code slash command with frontmatter and tool permissions |
| `/create-subagent` | `.claude/commands/create-subagent.md` | Create a specialized domain-expert subagent |

### Custom Commands

Installed selectively from `custom/commands/` by `/ak:setup-custom`.

| Command | Source file | Purpose |
|---------|-------------|---------|
| `/code-review` | `custom/commands/code-review.md` | Multi-aspect code review using parallel code-review-expert agents |
| `/research` | `custom/commands/research.md` | Deep research with parallel subagents and automatic citations |
| `/validate-and-fix` | `custom/commands/validate-and-fix.md` | Run quality checks and automatically fix issues using concurrent agents |

## MCP Servers

Defined in `global/settings.json`.

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp@latest` | Up-to-date library documentation |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Structured reasoning for complex tasks |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge storage |

Permissions installed globally:

```text
mcp__context7__*
mcp__sequential-thinking__*
mcp__memory__*
```

## Custom Assets

### Skills

| Skill | Source | Description |
|-------|--------|-------------|
| `html-doc-coauthoring` | `custom/skills/html-doc-coauthoring/` | Co-author substantial documentation and generate reader-friendly HTML with markdown, cards, metrics, tables, callouts, images, cloud topology diagrams, flows, timelines, charts, steps, code, checklists, resources, and details blocks |

### Repo-local Skills

| Skill | Source | Description |
|-------|--------|-------------|
| `html-doc-coauthoring` | `.claude/skills/html-doc-coauthoring/` | Repo-local installed copy of the HTML documentation co-authoring skill |
| `skill-creator` | `.claude/skills/skill-creator/` | Create, modify, evaluate, and optimize AI skills |

### Hooks

3 hooks are defined in `custom/hooks/hooks.json`.

| Hook | Trigger | Description |
|------|---------|-------------|
| `block-dangerous-bash` | `PreToolUse` / `Bash` | Block dangerous bash commands such as destructive deletes, force push, hard reset, database destruction, `kill`, and unsafe permissions |
| `check-secrets` | `PreToolUse` / `Write\|Edit\|MultiEdit` | Block writes that appear to contain hardcoded secrets, API keys, tokens, or private keys |
| `gitnexus-auto-rebuild` | `PostToolUse` / `Write\|Edit\|MultiEdit` | Rebuild the GitNexus knowledge graph after code changes |

## Project Structure

```text
agent-kit/
├── global/
│   ├── commands/
│   │   ├── ak:init-project.md
│   │   ├── ak:setup-custom.md
│   │   ├── ak:setup-skills.md
│   │   └── ak:update.md
│   └── settings.json
├── custom/
│   ├── commands/
│   │   ├── README.md
│   │   ├── code-review.md
│   │   ├── research.md
│   │   └── validate-and-fix.md
│   ├── hooks/
│   │   ├── hooks.json
│   │   ├── scripts/
│   │   └── tests/test_hooks.py
│   └── skills/html-doc-coauthoring/
│       ├── SKILL.md
│       ├── LICENSE.txt
│       ├── references/html-doc-guide.md
│       └── scripts/build_html_doc.py
├── skills/
│   ├── claudekit-skills/
│   └── anthropics-skills/
├── .claude/
│   ├── commands/
│   │   ├── ak:sync-docs.md
│   │   ├── create-command.md
│   │   └── create-subagent.md
│   ├── settings.json
│   └── skills/
│       ├── html-doc-coauthoring/
│       └── skill-creator/
├── docs/
│   ├── raw/
│   │   ├── agent-kit-project-documentation.json
│   │   └── sample-components-documentation.json
│   ├── agent-kit-project-documentation.html
│   └── sample-components-documentation.html
├── scripts/
│   ├── init-project.py
│   └── install.py
├── tests/
│   ├── run_all.py
│   ├── test_init_project_script.py
│   └── test_kit.py
├── AGENTS.md
├── CLAUDE.md
└── README.md
```

## Extending Agent Kit

| Change | Source of truth | Follow-up |
|--------|-----------------|-----------|
| Add or update global commands | `global/commands/*.md` | Run `/ak:sync-docs`, then `python3 scripts/install.py` |
| Add or update MCP servers or permissions | `global/settings.json` | Run `/ak:sync-docs`, then `python3 scripts/install.py` or `/ak:update` |
| Add custom commands | `custom/commands/*.md` | Run `/ak:sync-docs`, then `/ak:setup-custom` in target projects |
| Add custom skills | `custom/skills/<name>/SKILL.md` | Run `/ak:sync-docs`, then `/ak:setup-custom` in target projects |
| Add custom hooks | `custom/hooks/hooks.json` | Run `/ak:sync-docs`, then `/ak:setup-custom` in target projects |
| Update visual docs | `docs/raw/*.json` | Regenerate the matching file in `docs/*.html` |

Do not edit `~/.claude/` directly. It is managed by the installer and setup commands.

## Requirements

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | Installer, init script, HTML doc generation, hook tests, and repository test suites |
| Node.js | 18+ | MCP servers through `npx`, GitNexus, and related tooling |
| Claude Code | Latest | Slash command and assistant configuration runtime |
| Git | Latest | Repository cloning, submodules, and version control |
| GitNexus | Optional | Knowledge graph generation for target projects |

## Testing

```bash
python3 tests/run_all.py
python3 tests/test_kit.py
python3 tests/test_init_project_script.py
python3 custom/hooks/tests/test_hooks.py
```

## Visual Documentation

| Document | Source |
|----------|--------|
| `docs/agent-kit-project-documentation.html` | `docs/raw/agent-kit-project-documentation.json` |
| `docs/sample-components-documentation.html` | `docs/raw/sample-components-documentation.json` |

Regenerate all visual docs:

```bash
for file in docs/raw/*.json; do python3 custom/skills/html-doc-coauthoring/scripts/build_html_doc.py "$file"; done
```
