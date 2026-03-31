---
description: Regenerate README.md, CLAUDE.md, AGENTS.md to reflect current agent-kit state
category: workflow
allowed-tools: Read, Write, Bash(ls:*, find:*, cat:*)
---

# Sync Agent Kit Documentation

Regenerate README.md, CLAUDE.md, and AGENTS.md to reflect the current state of the agent-kit repository.

Run this command whenever you add or remove skills, commands, hooks, or MCP servers.

---

## Step 1: Read Current State

Run these commands in parallel to get the current repo state:

**Commands** — list all `.md` files in `global/commands/`:
```bash
ls global/commands/*.md
```

**Custom Skills** — list directories in `custom/skills/` with `SKILL.md`:
```bash
find custom/skills -name "SKILL.md" | sort
```
For each skill, read the `SKILL.md` to extract: name, description (first sentence).

**Custom Commands** — list `.md` files in `custom/commands/` (excluding README.md):
```bash
ls custom/commands/*.md 2>/dev/null
```

**Hooks** — read `custom/hooks/hooks.json`:
```bash
cat custom/hooks/hooks.json
```
Extract: name, event, description.

**MCP Servers** — read `global/settings.json`:
```bash
cat global/settings.json
```
Extract server names and packages from `mcpServers`.

**Project skills** — list `.claude/skills/` directories:
```bash
ls .claude/skills/ 2>/dev/null
```

---

## Step 2: Rewrite README.md

Rewrite `README.md` completely using data from Step 1. Follow this structure:

1. **Header** — project name and one-line description
2. **How It Works** — table: Global / Submodule / Per-project layers
3. **Quick Start** — install.py, /ak:init-project, /ak:setup-skills, /ak:setup-custom
4. **Commands table** — all commands from `global/commands/` with descriptions
5. **MCP Servers table** — from `global/settings.json`
6. **Custom Assets** — Skills table, Hooks table (name + trigger + description)
7. **Project Structure** — directory tree with current files
8. **Extending** — how to add MCP servers, commands, skills, hooks; mention /ak:sync-docs
9. **Requirements** — Node.js, Python 3, Claude Code, Git

Keep it concise. Every table must reflect actual current files.

---

## Step 3: Rewrite CLAUDE.md

Rewrite `CLAUDE.md` completely. This is the AI instruction file for developing agent-kit.

Structure:
1. One-line project description + install command
2. **Structure** — accurate directory tree (current files only)
3. **Global Commands** table — name, file, purpose
4. **Project Commands** table — name, file, purpose
5. **MCP Servers** table — from global/settings.json
6. **Custom Skills** — name + description
7. **Custom Hooks** — list of hook names
8. **Development Rules**:
   - "After adding/removing skills, commands, or hooks — run `/ak:sync-docs` immediately"
   - Edit source in `global/` or `custom/`, never in `~/.claude/` directly
   - Re-run `python3 scripts/install.py` after changing `global/`
   - Hook scripts in `custom/hooks/scripts/` must be Python 3

Keep it short — target 60-80 lines total.

---

## Step 4: Rewrite AGENTS.md

Rewrite `AGENTS.md` completely. Universal AI config for non-Claude assistants.

Structure:
1. Project overview (2 sentences)
2. Tech stack
3. Commands (install.py usage)
4. Directory structure (brief)
5. Conventions
6. **MCP Servers** table — from global/settings.json
7. **Custom Skills** — comma-separated names
8. **Do Not Modify** section

Keep it under 80 lines.

---

## Step 5: Confirm

After rewriting all 3 files, report:

- Files updated: README.md, CLAUDE.md, AGENTS.md
- Commands listed: N
- MCP servers listed: N
- Custom skills listed: N
- Custom hooks listed: N
