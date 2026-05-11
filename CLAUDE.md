# Agent Kit

Shared AI agent setup toolkit for Claude Code. Run `python3 scripts/install.py` once per machine, then use `/ak:init-project`, `/ak:setup-skills`, `/ak:setup-custom`, and `/ak:update` in target projects.

## Structure

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
│   │   ├── code-review.md
│   │   ├── research.md
│   │   └── validate-and-fix.md
│   ├── hooks/
│   │   ├── hooks.json
│   │   ├── scripts/
│   │   └── tests/test_hooks.py
│   └── skills/html-doc-coauthoring/
├── skills/
│   ├── claudekit-skills/
│   └── anthropics-skills/
├── .claude/
│   ├── commands/
│   │   ├── ak:sync-docs.md
│   │   ├── create-command.md
│   │   └── create-subagent.md
│   ├── settings.json
│   └── skills/skill-creator/
├── docs/
│   ├── raw/agent-kit-project-documentation.json
│   └── agent-kit-project-documentation.html
├── scripts/
│   ├── init-project.py
│   └── install.py
└── tests/
```

## Global Commands

| Command | File | Purpose |
|---------|------|---------|
| `/ak:init-project` | `global/commands/ak:init-project.md` | Per-project setup wizard for assistant docs, hooks, MCP permissions, and GitNexus guidance |
| `/ak:setup-custom` | `global/commands/ak:setup-custom.md` | Install custom skills, commands, and hooks from `custom/` |
| `/ak:setup-skills` | `global/commands/ak:setup-skills.md` | Install community and Anthropic skills from submodules |
| `/ak:update` | `global/commands/ak:update.md` | Sync MCP permissions to global `~/.claude/settings.json` |

## Project Commands

| Command | File | Purpose |
|---------|------|---------|
| `/ak:sync-docs` | `.claude/commands/ak:sync-docs.md` | Regenerate `README.md`, `CLAUDE.md`, and `AGENTS.md` |
| `/create-command` | `.claude/commands/create-command.md` | Create a Claude Code slash command |
| `/create-subagent` | `.claude/commands/create-subagent.md` | Create a domain-expert subagent |

## MCP Servers

| Server | Package | Purpose |
|--------|---------|---------|
| `context7` | `@upstash/context7-mcp@latest` | Up-to-date library docs |
| `sequential-thinking` | `@modelcontextprotocol/server-sequential-thinking` | Complex reasoning |
| `memory` | `@modelcontextprotocol/server-memory` | Persistent knowledge |

## Custom Commands

| Command | Purpose |
|---------|---------|
| `code-review` | Multi-aspect code review using parallel code-review-expert agents |
| `research` | Deep research with parallel subagents and automatic citations |
| `validate-and-fix` | Run quality checks and automatically fix issues using concurrent agents |

## Custom Skills

| Skill | Description |
|-------|-------------|
| `html-doc-coauthoring` | Co-author substantial documentation and produce reader-friendly HTML with visual structure, charts, cards, tables, flow blocks, timelines, and concise prose. |

## Repo-local Skills

| Skill | Description |
|-------|-------------|
| `skill-creator` | Create, modify, evaluate, and optimize AI skills. |

## Custom Hooks

3 active hooks:
- `block-dangerous-bash` — Block dangerous bash commands, destructive deletes, force push, hard reset, database destruction, `kill`, and unsafe permissions
- `check-secrets` — Block writing hardcoded secrets, API keys, tokens, or private keys
- `gitnexus-auto-rebuild` — Auto-rebuild GitNexus knowledge graph after code changes

## Development Rules

**After adding/removing skills, commands, hooks, or MCP servers — run `/ak:sync-docs` immediately.**

- Edit source in `global/` or `custom/`; never edit `~/.claude/` directly
- Re-run `python3 scripts/install.py` after changing `global/`
- Install selected custom assets into projects with `/ak:setup-custom`
- Hook scripts in `custom/hooks/scripts/` must be Python 3; no shell scripts
- Do not edit `skills/claudekit-skills/` or `skills/anthropics-skills/`; they are Git submodules
- Keep visual docs source in `docs/raw/` and generated HTML in `docs/`
- Run `python3 tests/run_all.py` after documentation or toolkit changes

## GitNexus

This project may contain a `.gitnexus/` knowledge graph. Do not modify `.gitnexus/` manually; rebuild with `npx gitnexus analyze` if needed.
