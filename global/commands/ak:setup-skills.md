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

## Step 4: Detect Stack & Recommend Skills

Read project files to understand stack:
- `package.json` → Node.js/TypeScript
- `requirements.txt` or `pyproject.toml` → Python
- `go.mod` → Go
- `Cargo.toml` → Rust
- `CLAUDE.md` → existing conventions

### Skill Categories

Skills are organized into **3 categories**:

#### List 1: Generic Skills (Core — recommended for ALL projects)

These skills are useful regardless of tech stack:

| Skill | When to Use |
|-------|-------------|
| `debugging` | Bug, test failure, unexpected behavior — systematic 4-phase debugging |
| `code-review` | Pre-commit/PR review — 6 aspects: architecture, security, performance, testing, docs |
| `skill-creator` | Tạo/evaluate skills mới |
| `sequential-thinking` | Complex reasoning, architectural planning |
| `problem-solving` | Creative problem-solving frameworks (inversion, pattern recognition) |
| `docs-seeker` | Search docs via llms.txt, GitHub via Repomix |
| `mermaidjs-v11` | Diagrams: flowcharts, sequence, architecture, ERD |
| `doc-coauthoring` | Collaborative document writing |

#### List 2: Stack-Specific Skills (auto-suggest based on detected stack)

| Stack | Skills |
|-------|--------|
| **Node.js/TypeScript** | `backend-development`, `frontend-development`, `frontend-design`, `ui-styling`, `web-frameworks`, `web-testing`, `better-auth`, `databases` |
| **Python** | `backend-development`, `databases`, `ai-multimodal`, `google-adk-python`, `media-processing`, `pdf`, `docx`, `xlsx` |
| **Go** | `backend-development`, `devops`, `databases` |
| **Rust** | `backend-development`, `devops` |
| **Frontend-heavy** | `frontend-design`, `frontend-development`, `ui-styling`, `webapp-testing`, `threejs`, `aesthetic`, `canvas-design` |
| **Backend-heavy** | `backend-development`, `databases`, `devops`, `better-auth`, `payment-integration`, `mcp-builder` |
| **AI/ML** | `claude-api`, `ai-multimodal`, `context-engineering`, `google-adk-python` |

#### List 3: Nice-to-Have Skills (optional, less frequently used)

| Skill | Purpose |
|-------|---------|
| `mcp-management` | Discover/analyze/execute MCP tools — tích hợp Gemini CLI (chỉ cần nếu dùng MCP servers) |
| `shopify` | Shopify apps, checkout extensions, Liquid themes |
| `payment-integration` | Stripe, SePay (VietQR), Polar, Paddle, Creem.io |
| `repomix` | Package codebase thành 1 file AI-friendly |
| `chrome-devtools` | Browser automation với Puppeteer |
| `theme-factory` | Generate design themes |
| `brand-guidelines` | Brand consistency |
| `canvas-design` | Canvas-based visual designs |
| `internal-comms` | Team communication tools |
| `slack-gif-creator` | Create GIFs for Slack |
| `algorithmic-art` | Generative art |
| `web-artifacts-builder` | Build interactive web apps trong artifact |

---

## Step 5: Ask User to Select Skills (REQUIRED — DO NOT SKIP)

**CRITICAL: You MUST ask user before installing any skills. Never install automatically.**

Present recommendations using `AskUserQuestion` with **checkboxes** for better UX:

### Step 5.1: Generic Skills (Checkbox List)

Present generic skills as a **multi-select checklist**:

> "**List 1: Generic Skills (Core)** — recommended for ALL projects:
>
> Select skills to install (multi-select):
> - [ ] `debugging` — Bug, test failure, unexpected behavior
> - [ ] `code-review` — Pre-commit/PR review
> - [ ] `skill-creator` — Create/evaluate new skills
> - [ ] `sequential-thinking` — Complex reasoning, architectural planning
> - [ ] `problem-solving` — Creative problem-solving frameworks
> - [ ] `docs-seeker` — Search docs via llms.txt, GitHub
> - [ ] `mermaidjs-v11` — Diagrams: flowcharts, sequence, architecture
> - [ ] `doc-coauthoring` — Collaborative document writing
>
> Press Enter to skip all."

### Step 5.2: Stack-Specific Skills (Checkbox List)

Present stack-specific skills as a **multi-select checklist**:

> "**List 2: Stack-Specific Skills** — detected stack: **[Stack Name]**
>
> Select skills to install (multi-select):
> - [ ] `backend-development`
> - [ ] `frontend-development`
> - [ ] `databases`
> - [ ] [other stack-specific skills]
>
> Press Enter to skip."

### Step 5.3: Nice-to-Have Skills (Checkbox List)

> "**List 3: Nice-to-Have Skills** (optional):
>
> Select any skills you want (multi-select):
> - [ ] `mcp-management` — MCP server management (chỉ cần nếu dùng MCP servers)
> - [ ] `shopify`
> - [ ] `payment-integration`
> - [ ] `repomix`
> - [ ] `chrome-devtools`
> - [ ] `theme-factory`
> - [ ] `brand-guidelines`
> - [ ] `canvas-design`
> - [ ] `internal-comms`
> - [ ] `slack-gif-creator`
> - [ ] `algorithmic-art`
> - [ ] `doc-coauthoring`
> - [ ] `web-artifacts-builder`
>
> Press Enter to skip."

**If arguments provided** (`ak:setup-skills debugging code-review`), still confirm:
> "You requested: debugging, code-review. Install these now? (y/n)"

**DO NOT proceed to Step 6 until user explicitly confirms.**

---

## Step 6: Install Selected Skills

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
