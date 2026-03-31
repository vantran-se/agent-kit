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

## ⚠️ CRITICAL RULE: ALWAYS ASK USER FIRST

**You MUST ask user and get explicit confirmation before installing any skills.**

- AI suggests skills based on stack detection
- User decides which skills to install
- **NEVER install automatically** — always wait for user confirmation
- Even if user passes arguments, still confirm: "Install these? (y/n)"

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

## Step 5: Detect Stack & Recommend Skills

Read project files to understand stack:
- `package.json` → Node.js/TypeScript
- `requirements.txt` or `pyproject.toml` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `CLAUDE.md` → existing conventions

Based on detected stack, prepare recommendations:

**Core Skills** (recommend for all projects):
- `debugging`, `code-review`, `skill-creator`, `mcp-management`
- `sequential-thinking`, `problem-solving`

**Frontend**: `frontend-design`, `frontend-development`, `web-artifacts-builder`, `canvas-design`
**Backend**: `backend-development`, `databases`, `mcp-builder`
**AI/ML**: `claude-api`, `ai-multimodal`, `context-engineering`
**Data/Docs**: `pdf`, `docx`, `xlsx`, `doc-coauthoring`

---

## Step 6: Ask User to Select Skills (REQUIRED — DO NOT SKIP)

**CRITICAL: You MUST ask user before installing any skills. Never install automatically.**

Present recommendations and **wait for user confirmation**:

> "Based on your project stack, here are recommended skills:
>
> **Core** (recommended for all):
> - debugging, code-review, skill-creator, mcp-management, sequential-thinking
>
> **For your stack** [adjust based on detection]:
> - [stack-specific skills]
>
> **Available from claudekit-skills**: [list 10-15 popular]
> **Available from anthropics/skills**: [list 10-15 popular]
>
> Which skills would you like to install?
> - Type skill names separated by space, or
> - Type 'all-core' for core skills only, or
> - Type 'all-recommended' for core + stack-specific, or
> - Press Enter to skip
>
> ⚠️ I will not install anything until you confirm."

**If arguments provided** (`ak:setup-skills debugging code-review`), still confirm:
> "You requested: debugging, code-review. Install these now? (y/n)"

**DO NOT proceed to Step 7 until user explicitly confirms.**

---

## Step 7: Install Selected Skills

For each selected skill:

**Check source:**
- If from claudekit-skills: `"$AGENT_KIT_ROOT/skills/claudekit-skills/.claude/skills/{skill-name}"`
- If from anthropics/skills: `"$AGENT_KIT_ROOT/skills/anthropics-skills/skills/{skill-name}"`

**Install:**
```bash
npx skills add "{source_path}" -a claude-code -y
```

Track which skills were successfully installed vs failed.

Ask: "Install globally (~/.claude/skills/) or project-only (.claude/skills/)?" Default: project-only.

---

## Step 8: Update CLAUDE.md and AGENTS.md

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

## Step 9: Summary

Report:
- Skills installed: list
- Failures (if any)
- Docs updated: CLAUDE.md, AGENTS.md
- Tip: `npx skills find <keyword>` for more skills from skills.sh
