# Sync Agent Kit Documentation

Regenerate README.md, CLAUDE.md, and AGENTS.md to reflect the current state of the agent-kit repository.

Run this command whenever you add or remove skills, commands, hooks, or MCP servers.

## Step 1: Read Current State

Run these in parallel to get the current repo state:

**Commands** — list all `.md` files in `global/commands/` (these are the slash commands):
```bash
ls global/commands/*.md
```

**Custom Skills** — list directories in `custom/skills/` that contain a `SKILL.md`:
```bash
find custom/skills -name "SKILL.md" | sort
```
For each skill, read the `SKILL.md` to extract: name, description (first sentence only).

**Custom Commands** — list `.md` files in `custom/commands/` excluding README.md:
```bash
ls custom/commands/*.md 2>/dev/null
```

**Hooks** — read `custom/hooks/hooks.json` and extract: name, event, description, stacks.

**MCP Servers** — read `global/settings.json` for server names and packages.

**Project skills** — list `.claude/skills/` directories.

## Step 2: Rewrite README.md

Rewrite `README.md` completely using the data from Step 1. Follow this structure exactly:

1. **Header** — project name and one-line description
2. **How It Works** — two-layer table (global / per-project)
3. **Quick Start** — install.sh steps, /ak:init-project, /ak:setup-skills, /ak:setup-custom
4. **Commands table** — all commands from `global/commands/` with descriptions
5. **MCP Servers table** — from `global/settings.json`
6. **Custom Assets** — Skills table (name + description), Hooks table (name + trigger + description)
7. **Project Structure** — accurate directory tree with current files
8. **Extending** — how to add MCP servers, commands, skills, hooks; mention /ak:sync-docs
9. **Requirements** — Node.js, Claude Code

Keep it concise. Every table must reflect the actual current files.

## Step 3: Rewrite CLAUDE.md

Rewrite `CLAUDE.md` completely. This is the AI instruction file for developing agent-kit itself.

Structure:
1. One-line project description + install command
2. **Structure** — accurate directory tree (current files only)
3. **Global Commands** table — name, file, purpose
4. **MCP Servers** table — from global/settings.json
5. **Custom Skills** table — from custom/skills/
6. **Custom Hooks** — comma-separated list of hook names
7. **Development Rules** — must include:
   - "After adding/removing skills, commands, or hooks — run `/ak:sync-docs` immediately"
   - Reminder that `.claude/settings.json` has a hook that will remind automatically
   - Edit source in global/ or custom/, never in ~/.claude/ directly
   - Re-run install.sh after changing global/

Keep it short — target 60-80 lines total.

## Step 4: Rewrite AGENTS.md

Rewrite `AGENTS.md` completely. This is the universal AI config for non-Claude assistants.

Structure:
1. Project overview (2 sentences)
2. Tech stack
3. Commands (install.sh usage)
4. Directory structure (brief)
5. Conventions
6. **MCP Servers** table — from global/settings.json
7. **Custom Skills** — comma-separated names, link to README
8. **Do Not Modify** section

Keep it under 80 lines.

## Step 5: Confirm

After rewriting all 3 files, report:
- Files updated (README.md, CLAUDE.md, AGENTS.md)
- Commands listed: N
- MCP servers listed: N
- Custom skills listed: N
- Custom hooks listed: N
