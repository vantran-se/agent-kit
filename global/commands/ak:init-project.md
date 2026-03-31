# Initialize AI Agent Setup for This Project

You are setting up AI agent configuration for the current project. Follow these steps carefully and sequentially.

---

## Step 1: Run Setup Script

Read the agent-kit path from `~/.claude/agent-kit-path`. Then run the setup script:

```bash
python3 {AGENT_KIT_PATH}/scripts/init-project.py --cwd .
```

This script handles all mechanical setup in one shot:
- Updates `.gitignore` with `.gitnexus/`
- Runs `npx gitnexus analyze` to index the repo (so you can use gitnexus MCP immediately)
- Scans existing files (CLAUDE.md, AGENTS.md, .claude/settings.json)
- Detects the project's formatter and generates the hook command
- Reads MCP permissions from agent-kit config

**Parse the JSON output** and use it throughout the remaining steps. Store it as `SETUP_DATA`.

If the agent-kit path file does not exist, tell the user:
> agent-kit path not found. Run `python3 scripts/install.py` from your agent-kit directory first.

Then stop.

---

## Step 2: Handle Existing Files

Using `SETUP_DATA.existing`:

- If `claude_md.exists` is true, show the user the existing content and ask: "CLAUDE.md already exists. Update it or skip?"
- If `claude_settings.exists` is true, read the content — merge later, never overwrite
- If `agents_md.exists` is true, read the content for context

---

## Step 3: Detect Project Stack

GitNexus has already indexed the repo in Step 1. Use the gitnexus MCP tool `search_code` to understand the project:

- Search for framework patterns, key dependencies, project structure
- Identify the language, framework, package manager, test runner
- Check for Docker, environment variables, CI/CD configuration

Summarize the stack in 2-3 lines.

---

## Step 4: Ask User for Missing Information

Ask in a **single message**. Skip anything already clear from Step 3:

1. **Project purpose** — What does this project do? (1-2 sentences)
2. **Stack corrections** — Anything you got wrong?
3. **Non-obvious conventions** — Anything that differs from the standard for this stack? (e.g., "we use pnpm not npm", "snake_case for files", "no default exports")
4. **Git workflow** — Branch naming, commit message format?
5. **Common gotchas** — Anything Claude commonly gets wrong in this type of project?
6. **Context7 libraries** — Which packages should context7 look up docs for?

Do NOT ask about things Claude can infer from code (standard language conventions, obvious patterns).

---

## Step 5: Generate `CLAUDE.md`

**Target: ~50-100 lines. Ruthlessly short.**

Rule of thumb for every line: *"Would removing this cause Claude to make mistakes?"* If not, cut it.

**Include only:**
- Exact commands Claude can't guess (install, dev, test, build, lint)
- Code style rules that **differ from the stack's defaults**
- Testing conventions specific to this project
- Git/PR workflow rules
- Known gotchas or non-obvious behaviors
- Environment variables required to run locally

**Never include:**
- Anything Claude can read from code
- Standard language/framework conventions Claude already knows
- Detailed API docs (use `@link` or context7 instead)
- Section headers with no unique content
- Obvious rules like "write clean code" or "follow best practices"

**Use `@path/to/file` imports** to reference related docs instead of copy-pasting:

```markdown
# [Project Name]

[1-2 sentence description]

## Commands

\`\`\`bash
[install cmd]   # install deps
[dev cmd]       # start dev server
[test cmd]      # run tests
[build cmd]     # production build
[lint/format]   # formatter command
\`\`\`

## Conventions

[ONLY rules that differ from this stack's defaults. Skip anything standard.]

## Git

[Branch naming + commit format if non-standard]

## Gotchas

[Non-obvious behaviors or common mistakes specific to this project]

## Environment

[Required env vars not in .env.example, or setup steps Claude needs to know]

## MCP Tools

- **context7** — `resolve-library-id` → `get-library-docs` for up-to-date docs on: [libraries from Step 4]
- **gitnexus** — `search_code` for semantic search across this repo and other indexed repos
- **sequential-thinking** — use for complex architectural decisions, multi-step debugging
- **memory** — store and retrieve persistent knowledge across sessions (conventions, decisions, context)
```

If any section would be empty or generic, omit it entirely.

---

## Step 6: Generate `AGENTS.md`

Write the full content — no lazy references. This file must work standalone for Cursor, Copilot, Gemini, and other AI assistants that don't have MCP.

Same rules as CLAUDE.md: only non-obvious, project-specific info. Keep it under 150 lines.

```markdown
# AI Assistant Configuration — [Project Name]

> Compatible with Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

[1-2 sentence description]

## Tech Stack

- **Language**: [language + version]
- **Framework**: [framework]
- **Key Libraries**: [list — only ones relevant to working on this project]
- **Database**: [if applicable]

## Commands

\`\`\`bash
[install cmd]
[dev cmd]
[test cmd]
[build cmd]
\`\`\`

## Conventions

[Only non-standard rules. If it's the default for this stack, omit it.]

## Directory Structure

[Only if non-standard layout — skip if conventional Next.js/Django/etc. structure]

## Git Workflow

[Branch naming + commit format if non-standard]

## Gotchas

[Non-obvious behaviors or common mistakes]

## MCP Servers (Claude Code)

- **context7** — `resolve-library-id` → `get-library-docs` for up-to-date docs on: [libraries]
- **gitnexus** — `search_code` for semantic search across this and other indexed repos
- **sequential-thinking** — use for complex architectural decisions, multi-step debugging
- **memory** — store/retrieve persistent knowledge across sessions

## Do Not Modify

[Auto-generated files, lock files, build output dirs]
```

---

## Step 7: Setup Hooks

Using `SETUP_DATA.formatter`:

If a formatter was detected, ask the user: "Set up auto-format hooks? (Recommended — runs formatter after every file edit, prevents CI failures)"

- Detected formatter: `SETUP_DATA.formatter.detected`
- Hook command ready to use: `SETUP_DATA.formatter.hook_command`

If no formatter was detected, ask the user which formatter they use.

If yes, add to `.claude/settings.json` (merge with existing):

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "[SETUP_DATA.formatter.hook_command]"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Task complete\" with title \"Claude Code\"' 2>/dev/null || notify-send 'Claude Code' 'Task complete' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

Read the `mcpPermissions` array from `SETUP_DATA.mcp_permissions` for the authoritative permission list.

---

## Step 8: Install Custom Assets

If `SETUP_DATA.agent_kit_path` is not null, run `/ak:setup-custom` to offer the user custom skills, commands, and hooks stored in the agent-kit repo.

If agent_kit_path is null, skip and note it in the summary.

---

## Step 9: Summary

Final summary using data from `SETUP_DATA`:
- Files created or updated (with paths)
- Hooks configured (formatter detected + notification)
- GitNexus status: `SETUP_DATA.gitnexus.status`
- MCP tools available (all 4: context7, gitnexus, sequential-thinking, memory)
- Custom assets installed (from Step 8, if any)
- Next: run `/ak:setup-skills` to install skills from the local claudekit-skills submodule
