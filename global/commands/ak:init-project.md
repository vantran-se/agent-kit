---
description: Per-project setup wizard — generates CLAUDE.md, AGENTS.md, configures hooks, indexes code with GitNexus
category: workflow
allowed-tools: Read, Write, Edit, Bash(python3:*, npx:*, ls:*, cat:*)
---

# Initialize AI Agent Setup for This Project

Set up AI agent configuration for the current project. Generate CLAUDE.md and AGENTS.md that **actively guide AI agents** to use available MCP servers, skills, and hooks.

---

## Step 1: Run Setup Script

Read agent-kit path and run init-project.py:

```bash
AGENT_KIT_PATH=$(cat ~/.claude/agent-kit-path 2>/dev/null)
if [ -z "$AGENT_KIT_PATH" ]; then
  echo "agent-kit path not found. Run: python3 scripts/install.py"
  exit 1
fi
python3 "$AGENT_KIT_PATH/scripts/init-project.py" --cwd . --pretty
```

Store output as `SETUP_DATA`. You get:
- `.gitignore` status
- GitNexus indexing status
- Existing files (CLAUDE.md, AGENTS.md, .claude/settings.json)
- Detected formatter
- MCP permissions from agent-kit

---

## Step 2: Check Existing Files

Using `SETUP_DATA.existing`:

- `claude_md.exists` → read content, plan to update (never overwrite blindly)
- `claude_settings.exists` → read and merge hooks/permissions later
- `agents_md.exists` → read for context

---

## Step 3: Discover Available MCP Servers & Skills

**MCP Servers**:
```bash
claude mcp list
```

**Skills installed**:
```bash
npx skills list -a claude-code
ls .claude/skills/ 2>/dev/null
ls ~/.claude/skills/ 2>/dev/null
```

From `SETUP_DATA.mcp_permissions`, map to MCP servers:
- `mcp__context7__*` → context7
- `mcp__gitnexus__*` → gitnexus (already indexed)
- `mcp__sequential-thinking__*` → sequential-thinking
- `mcp__memory__*` → memory

Note key skills: `mcp-management`, `debugging`, `code-review`, `skill-creator`, etc.

---

### MCP Servers — When to Use

**context7** — Use when:
- Working with external libraries/frameworks (React, Next.js, Prisma, Django, etc.)
- User asks about latest API features or migration guides
- You need current best practices, not outdated docs
- Debugging library-specific issues
- **Trigger:** Importing `anthropic`, `@anthropic-ai/sdk`, `prisma`, `tailwindcss`, etc.

**gitnexus** — Use when:
- Need to find where a function/class is defined
- Understanding how a feature works across the codebase
- Tracing execution flows or call chains
- Investigating bugs or finding all callers of a function
- Before modifying shared code — check blast radius with `impact()`

**sequential-thinking** — Use when:
- Architectural decisions with multiple trade-offs
- Debugging complex multi-step issues
- Planning implementation before writing code
- Tasks requiring 3+ reasoning steps
- **Trigger:** User asks "how should I...", "what's the best way to..."

**memory** — Use when:
- Learning project-specific conventions for the first time
- After making decisions that should persist across sessions
- User explicitly asks you to "remember" something
- Retrieving context from previous work sessions

---

### Skills — When to Use

#### Core Skills (Always Available)

**mcp-management** — Use when:
- Adding/removing MCP servers from config
- MCP server misbehaving or not responding
- Need to discover available MCP tools/prompts
- **Run via Gemini** to save tokens vs. running directly

**debugging** — Use when:
- Stuck on a bug after 2+ failed attempts
- Need structured debugging workflow
- Error messages are unclear or misleading
- **Trigger:** User says "this doesn't work", "why is this broken"

**code-review** — Use when:
- Before committing significant changes (10+ lines)
- After implementing a new feature
- User asks for feedback on code quality
- **Trigger:** Pre-commit, PR preparation, refactor complete

**skill-creator** — Use when:
- Creating a new skill from scratch
- Optimizing an existing skill's performance
- Running evals to test skill effectiveness
- **Trigger:** User says "create a skill for...", "automate this workflow"

**sequential-thinking** — Use when:
- Complex reasoning with multiple steps
- Architectural decisions and planning
- Breaking down ambiguous problems
- **Trigger:** "how should I approach...", "plan out..."

**problem-solving** — Use when:
- General problem-solving framework needed
- Breaking down complex issues
- Systematic analysis required

**docs-seeker** — Use when:
- Need to find documentation quickly
- Looking for API references or guides
- **Trigger:** "how do I...", "what's the way to..."

**mermaidjs-v11** — Use when:
- Need to create diagrams or flowcharts
- Visualizing system architecture
- **Trigger:** "draw a diagram...", "show the flow..."

#### Anthropic Official Skills

**claude-api** — Use when:
- Building apps with Claude API or Anthropic SDK
- Code imports `anthropic`, `@anthropic-ai/sdk`, `claude_agent_sdk`
- **Trigger:** Working with Claude API, Agent SDK

**mcp-builder** — Use when:
- Building MCP servers to integrate external APIs/services
- Creating FastMCP servers in Python
- **Trigger:** "create an MCP server...", "integrate with..."

**pdf** — Use when:
- Reading or analyzing PDF documents
- Extracting information from PDFs
- **Trigger:** User uploads PDF, "read this PDF..."

**docx** — Use when:
- Creating or editing Word documents
- Working with .docx files programmatically

**xlsx** — Use when:
- Creating or editing Excel spreadsheets
- Working with .xlsx files programmatically

**pptx** — Use when:
- Creating or editing PowerPoint presentations
- Working with .pptx files programmatically

**doc-coauthoring** — Use when:
- Collaborative document writing
- Iterative document improvement

**web-artifacts-builder** — Use when:
- Building interactive web artifacts
- Creating React components for artifacts
- **Trigger:** "build a web app...", "create an interactive..."

**webapp-testing** — Use when:
- Testing web applications
- Browser automation and testing

**canvas-design** — Use when:
- Designing canvas-based visualizations
- Working with HTML5 canvas or design tools

**frontend-design** — Use when:
- UI/UX design work
- Creating visually appealing interfaces
- **Trigger:** "make it look nice...", "design a..."

**brand-guidelines** — Use when:
- Ensuring brand consistency
- Following corporate identity guidelines

**theme-factory** — Use when:
- Creating or applying themes
- Styling variations for components

**internal-comms** — Use when:
- Internal team communications
- Drafting announcements, updates

**slack-gif-creator** — Use when:
- Creating animated GIFs for Slack
- Fun/engaging team communications

#### Specialized Skills (Stack-Specific)

**frontend-development** — Use when:
- Building frontend features
- React, Vue, Angular development
- **Trigger:** Working on UI components

**backend-development** — Use when:
- Building backend services
- API development, database work

**ai-multimodal** — Use when:
- Working with AI/ML features
- Multimodal inputs (images, text)

**context-engineering** — Use when:
- Optimizing context window usage
- Managing long conversations

**better-auth** — Use when:
- Implementing authentication
- Working with Better-Auth library

**databases** — Use when:
- Database schema design
- Query optimization

**devops** — Use when:
- CI/CD pipelines
- Infrastructure automation
- **Trigger:** Docker, Kubernetes, GitHub Actions

**google-adk-python** — Use when:
- Working with Google ADK
- Python agent development

**code-search** — Use when:
- Searching codebases
- Finding definitions and references

---

## Step 4: Analyze Project Stack

Use gitnexus MCP `search_code`:
- Search key files: `package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`
- Find entry points, routing, database models, API handlers
- Identify test structure, CI/CD config

Summarize stack in 2-3 lines.

---

## Step 5: Ask User for Missing Information

Ask in a **single message**. Skip what's clear from Step 4:

1. **Project purpose** — What does this project do?
2. **Stack corrections** — Anything wrong?
3. **Non-obvious conventions** — Team-specific rules
4. **Git workflow** — Branch naming, commit format
5. **Common gotchas** — What AI agents mess up
6. **Context7 libraries** — Which packages need docs lookup?

---

## Step 6: Generate CLAUDE.md

**Goal:** Actively instruct Claude to use available tools. Under 100 lines.

```markdown
# [Project Name]

[1-2 sentence description]

## Quick Start

\`\`\`bash
[install cmd]   # install deps
[dev cmd]       # start dev server
[test cmd]      # run tests
[build cmd]     # production build
[lint/format]   # formatter
\`\`\`

## Conventions

[ONLY rules that differ from stack defaults]

## Git Workflow

[Branch naming + commit format]

## Environment

[Required env vars, local setup steps]

## MCP Tools — USE THESE

**context7** — Use `resolve-library-id` → `get-library-docs` when:
- Working with [libraries] — APIs change frequently
- User asks about latest features or migration guides
- You're unsure about current best practices

**gitnexus** — Use `search_code` when:
- Need to find where something is defined
- Need to understand how a feature works across the codebase
- Investigating bugs or tracing execution flows

**sequential-thinking** — Use when:
- Making architectural decisions
- Debugging complex multi-step issues
- Planning implementation before coding

**memory** — Use to:
- Store project conventions after learning them
- Remember decisions across sessions
- Retrieve context from previous work

## Skills Available

[For each installed skill, add 1 line on WHEN to use it:]

**mcp-management** — Use when adding/removing MCP servers, or when MCP server acts up (run via Gemini to save tokens)
**debugging** — Use when stuck on a bug — follow its structured workflow
**code-review** — Use before committing significant changes

## Gotchas

[Non-obvious behaviors, common mistakes]
```

**Rules:**
- Every line: "Would removing this cause Claude to make mistakes?"
- Use `@path/to/file` for related docs instead of copy-paste
- For each MCP/skill, specify **WHEN** to use it

---

## Step 7: Generate AGENTS.md

Universal config for ALL AI assistants (Cursor, Copilot, Gemini). Under 150 lines.

```markdown
# AI Assistant Configuration — [Project Name]

> For Claude Code, Cursor, GitHub Copilot, Gemini CLI, and other AI assistants.

## Project Overview

[1-2 sentences]

## Tech Stack

- **Language**: [name + version]
- **Framework**: [name]
- **Key Libraries**: [relevant ones only]

## Commands

\`\`\`bash
[install]
[dev]
[test]
[build]
\`\`\`

## Conventions

[Only non-standard rules]

## Git Workflow

[If non-standard]

## Gotchas

[Non-obvious behaviors]

## Tools Available (Claude Code)

### MCP Servers

**context7** — Fetch up-to-date docs for [libraries]. Use when APIs change frequently or user asks about latest features.

**gitnexus** — Semantic code search across this repo. Use to find definitions, trace flows, understand existing code.

**sequential-thinking** — Complex reasoning, architectural planning, multi-step debugging.

**memory** — Persistent knowledge across sessions.

### Skills

**mcp-management** — MCP server lifecycle via Gemini (saves tokens vs running directly)
**debugging** — Structured debugging workflows
**code-review** — Pre-commit review automation

## Do Not Modify

[Auto-generated files, lock files, build dirs]
```

**Rules:**
- Standalone — no MCP-specific syntax other assistants can't use
- Include skills/MCP info so any AI knows what's available

---

## Step 8: Configure Hooks

Using `SETUP_DATA.formatter`:

If formatter detected, ask: "Set up auto-format hooks? (Recommended)"

If yes, merge into `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{
          "type": "command",
          "command": "[SETUP_DATA.formatter.hook_command]"
        }]
      }
    ],
    "Stop": [
      {
        "hooks": [{
          "type": "command",
          "command": "osascript -e 'display notification \"Task complete\" with title \"Claude Code\"' 2>/dev/null || notify-send 'Claude Code' 'Task complete' 2>/dev/null || true"
        }]
      }
    ]
  }
}
```

Merge carefully — don't duplicate existing hooks.

---

## Step 9: Install Custom Assets

If `SETUP_DATA.agent_kit_path` exists, run `/ak:setup-custom`.

---

## Step 10: Install Submodule Skills

Ask user: "Install community skills from claudekit-skills submodule? (Recommended: debugging, code-review, mcp-management)"

If yes, run `/ak:setup-skills`.

---

## Step 11: Update Docs After Setup

After `/ak:setup-custom` and `/ak:setup-skills` complete:

**Re-read CLAUDE.md and AGENTS.md** — update "Skills Available" sections with what was actually installed.

Tell user: "CLAUDE.md and AGENTS.md updated with installed skills."

---

## Step 12: Summary

Report:
- Files created/updated: CLAUDE.md, AGENTS.md, .claude/settings.json (hooks)
- GitNexus: `SETUP_DATA.gitnexus.status`
- MCP servers enabled: list from permissions
- Skills installed: list
- Hooks configured: formatter + notification
- **Important:** Tell user to use these MCP servers and skills when working on this project:
  - MCP: context7, gitnexus, sequential-thinking, memory
  - Skills: debugging, code-review, mcp-management, skill-creator, etc.
