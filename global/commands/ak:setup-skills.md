---
description: Install community skills from claudekit-skills and anthropics/skills submodules
category: workflow
allowed-tools: Read, Write, Edit, Bash(ls:*, npx:*, python3:*)
argument-hint: "[skill-names...]"
---

# Setup Skills for This Project

Install community skills from **2 sources**:
1. **claudekit-skills** (https://github.com/mrgoonie/claudekit-skills) — 30+ community skills
2. **anthropics/skills** (https://github.com/anthropics/skills) — Official Anthropic skills

After installation, update CLAUDE.md and AGENTS.md so AI agents know about the newly installed tools.

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

## Step 2: Check Submodules

**claudekit-skills**:
```bash
ls "$AGENT_KIT_ROOT/skills/claudekit-skills/.claude/skills/"
```

If empty/missing:
> claudekit-skills submodule not initialized. Run first:
> ```bash
> python3 "$AGENT_KIT_ROOT/scripts/install.py" --init-submodule
> ```

**anthropics/skills**:
```bash
ls "$AGENT_KIT_ROOT/skills/anthropics-skills/skills/"
```

If empty/missing:
> anthropics/skills submodule not initialized. Run:
> ```bash
> git submodule update --init --recursive
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

## Step 5: Recommended Skills

### Always Install (Every Project)

**From claudekit-skills:**
- `debugging` — Structured debugging workflows
- `code-review` — Pre-commit review automation
- `skill-creator` — Create and optimize skills
- `mcp-management` — MCP server lifecycle (run via Gemini to save tokens)
- `problem-solving` — General problem-solving framework
- `docs-seeker` — Find and read documentation
- `mermaidjs-v11` — Create diagrams and flowcharts
- `sequential-thinking` — Complex reasoning and planning

**From anthropics/skills:**
- `claude-api` — Build apps with Claude API / Anthropic SDK
- `mcp-builder` — Create MCP servers for external APIs/services
- `skill-creator` — Official Anthropic skill creator
- `pdf` — Read and analyze PDF documents
- `docx` / `xlsx` / `pptx` — Work with Office documents

### Frontend Projects
**claudekit-skills:** `frontend-design`, `frontend-development`, `ui-styling`, `web-frameworks`
**anthropics/skills:** `frontend-design`, `web-artifacts-builder`, `canvas-design`, `brand-guidelines`, `theme-factory`

### Backend Projects
**claudekit-skills:** `backend-development`, `better-auth`, `databases`, `devops`
**anthropics/skills:** `mcp-builder` (for API integrations)

### AI/ML Projects
**claudekit-skills:** `ai-multimodal`, `context-engineering`, `google-adk-python`
**anthropics/skills:** `claude-api` (Anthropic SDK integration)

### Data/Analysis
**anthropics/skills:** `docx`, `xlsx`, `pdf`, `doc-coauthoring`

### Internal/Business
**anthropics/skills:** `internal-comms`, `slack-gif-creator`, `brand-guidelines`

If arguments provided, install those specific skills. Otherwise, recommend based on stack.

---

## Step 6: Install Skills

**From claudekit-skills:**
```bash
npx skills add "$AGENT_KIT_ROOT/skills/claudekit-skills/.claude/skills/{skill-name}" -a claude-code -y
```

**From anthropics/skills:**
```bash
npx skills add "$AGENT_KIT_ROOT/skills/anthropics-skills/skills/{skill-name}" -a claude-code -y
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
