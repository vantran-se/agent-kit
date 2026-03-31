---
description: Install community skills from claudekit-skills submodule and update docs
category: workflow
allowed-tools: Read, Write, Edit, Bash(ls:*, npx:*, python3:*)
argument-hint: "[skill-names...]"
---

# Setup Skills for This Project

Install community skills from the local `claudekit-skills` submodule. After installation, update CLAUDE.md and AGENTS.md so AI agents know about the newly installed tools.

---

## Step 1: Locate Agent Kit

Read the agent-kit path:
```bash
AGENT_KIT_ROOT=$(cat ~/.claude/agent-kit-path 2>/dev/null)
if [ -z "$AGENT_KIT_ROOT" ]; then
  echo "agent-kit path not found. Run: python3 scripts/install.py"
  exit 1
fi
```

---

## Step 2: Check Submodule

```bash
ls "$AGENT_KIT_ROOT/skills/claudekit-skills/.claude/skills/"
```

If empty/missing:
> claudekit-skills submodule not initialized. Run first:
> ```bash
> python3 "$AGENT_KIT_ROOT/scripts/install.py" --init-submodule
> ```

---

## Step 3: Check Already Installed

```bash
npx skills list -a claude-code
```

Skip skills already in `.claude/skills/` or `~/.claude/skills/`.

---

## Step 4: Detect Stack

Read project files to understand stack:
- `package.json` → Node.js/TypeScript
- `requirements.txt` or `pyproject.toml` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `CLAUDE.md` → existing conventions

---

## Step 5: Recommend Skills

**Always install** (every project):
- `debugging`, `code-review`, `skill-creator`
- `mcp-management` (MCP server lifecycle via Gemini)
- `problem-solving`, `docs-seeker`, `mermaidjs-v11`, `sequential-thinking`

**Frontend**: `frontend-design`, `frontend-development`, `ui-styling`, `web-frameworks`

**Backend**: `backend-development`, `better-auth`, `databases`

**AI/ML**: `ai-multimodal`, `context-engineering`, `google-adk-python`

If arguments provided, install those specific skills. Otherwise, recommend based on stack.

---

## Step 6: Install Skills

For each skill to install:
```bash
npx skills add "$AGENT_KIT_ROOT/skills/claudekit-skills/.claude/skills/{skill-name}" -a claude-code -y
```

Install project-level by default. Ask user if they want global installation.

---

## Step 7: Update CLAUDE.md and AGENTS.md

**After installing**, read CLAUDE.md and AGENTS.md if they exist.

For each newly installed skill, add/update:

**In CLAUDE.md** — "Skills Available" section:
```markdown
**skill-name** — WHEN to use it (1 line description)
```

**In AGENTS.md** — "### Skills" section:
```markdown
**skill-name** — description
```

If sections don't exist, create them.

Tell user: "Updated CLAUDE.md and AGENTS.md with newly installed skills."

---

## Step 8: Summary

Report:
- Skills installed: list
- Failures (if any)
- Docs updated: CLAUDE.md, AGENTS.md
- Tip: `npx skills find <keyword>` for more skills from skills.sh
