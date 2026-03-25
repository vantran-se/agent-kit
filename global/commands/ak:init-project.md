# Initialize AI Agent Setup for This Project

You are setting up AI agent configuration for the current project. Follow these steps carefully and sequentially.

---

## Step 1: Check Existing Setup

Before anything else:
- If `CLAUDE.md` already exists, read it and ask: "CLAUDE.md already exists. Update it or skip?"
- If `.claude/settings.json` already exists, read it — merge later, never overwrite
- If `AGENTS.md` already exists, read it

---

## Step 2: Detect Project Stack

Read these files to understand the project:

- `package.json` → Node.js/TypeScript, identify framework (Next.js, Express, NestJS, Vite, etc.)
- `requirements.txt`, `pyproject.toml`, `setup.py` → Python (FastAPI, Django, Flask, ruff/black for formatting)
- `go.mod` → Go (gofmt)
- `Cargo.toml` → Rust (rustfmt)
- `pom.xml`, `build.gradle` → Java/Kotlin
- `.env.example` → required environment variables
- `docker-compose.yml`, `Dockerfile` → infrastructure
- `README.md` → project description
- `.eslintrc*`, `.prettierrc*`, `biome.json` → formatter/linter config
- `jest.config*`, `vitest.config*`, `pytest.ini` → test runner config

Summarize the stack in 2-3 lines.

---

## Step 3: Ask User for Missing Information

Ask in a **single message**. Skip anything already clear from the files:

1. **Project purpose** — What does this project do? (1-2 sentences)
2. **Stack corrections** — Anything you got wrong?
3. **Non-obvious conventions** — Anything that differs from the standard for this stack? (e.g., "we use pnpm not npm", "snake_case for files", "no default exports")
4. **Git workflow** — Branch naming, commit message format?
5. **Common gotchas** — Anything Claude commonly gets wrong in this type of project?
6. **Context7 libraries** — Which packages should context7 look up docs for?

Do NOT ask about things Claude can infer from code (standard language conventions, obvious patterns).

---

## Step 4: Generate `CLAUDE.md`

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

- **context7** — `resolve-library-id` → `get-library-docs` for up-to-date docs on: [libraries from Step 3]
- **gitnexus** — `search_code` for semantic search across this repo and other indexed repos
- **sequential-thinking** — use for complex architectural decisions, multi-step debugging
- **memory** — store and retrieve persistent knowledge across sessions (conventions, decisions, context)
```

If any section would be empty or generic, omit it entirely.

---

## Step 5: Generate `AGENTS.md`

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

## Step 6: Setup Hooks

Ask the user: "Set up auto-format hooks? (Recommended — runs formatter after every file edit, prevents CI failures)"

If yes, detect the formatter. Hook input arrives as JSON on stdin — extract `tool_input.file_path` using `jq`:
- TypeScript/JS with Prettier → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && npx prettier --write "$FILE" 2>/dev/null || true`
- TypeScript/JS with ESLint → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && npx eslint --fix "$FILE" 2>/dev/null || true`
- TypeScript/JS with Biome → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && npx biome format --write "$FILE" 2>/dev/null || true`
- Python with Ruff → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && ruff format "$FILE" 2>/dev/null || true`
- Python with Black → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && black "$FILE" 2>/dev/null || true`
- Go → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && gofmt -w "$FILE" 2>/dev/null || true`
- Rust → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && rustfmt "$FILE" 2>/dev/null || true`
- Ruby with StandardRB → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && bundle exec standardrb --fix "$FILE" 2>/dev/null || true`
- Ruby with RuboCop → `FILE=$(jq -r '.tool_input.file_path // empty'); [ -n "$FILE" ] && bundle exec rubocop --autocorrect "$FILE" 2>/dev/null || true`

Add to `.claude/settings.json` (merge with existing):

```json
{
  "permissions": {
    "allow": [
      "mcp__context7__*",
      "mcp__gitnexus__*",
      "mcp__sequential-thinking__*",
      "mcp__memory__*"
    ]
  },
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "[formatter command]"
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

The MCP permissions allow all tools from the 4 standard servers without prompting. The Stop hook sends a desktop notification — works on macOS (osascript) and Linux (notify-send), silently skips if neither is available.

Read the `mcpPermissions` array from `~/.claude/agent-kit-path` → `global/settings.json` to get the authoritative list. If the file is not found, use the defaults above.

---

## Step 7: Update `.gitignore`

Check if `.gitnexus/` is already in `.gitignore`. If not, append:

```
# GitNexus index
.gitnexus/
```

---

## Step 8: GitNexus — Analyze Project

Check that `.git/` exists. If not, warn and skip.

If it is a git repo, run immediately:

```bash
npx gitnexus analyze
```

This indexes the repo so the `gitnexus` MCP tool can search it semantically.

---

## Step 9: Install Custom Assets

Read the agent-kit path from `~/.claude/agent-kit-path` (a single line containing the path, e.g. `/Users/you/workspace/agent-kit`).

If the file does not exist, skip this step and note it in the summary.

If it exists, run `/ak:setup-custom` to offer the user custom skills, commands, and hooks stored in the agent-kit repo.

## Step 10: Summary

Final summary:
- Files created or updated (with paths)
- Hooks configured (formatter detected + notification)
- GitNexus status (indexed / skipped / failed)
- MCP tools available (all 4: context7, gitnexus, sequential-thinking, memory)
- Custom assets installed (from Step 9, if any)
- Next: run `/ak:setup-skills` to install skills from skills.sh for this stack
