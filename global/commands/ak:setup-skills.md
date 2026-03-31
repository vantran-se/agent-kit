# Setup Skills for This Project

You are helping the user discover and install AI agent skills from the local claudekit-skills submodule and https://skills.sh into the current project.

## Step 1: Check Submodule Skills

First, check if the claudekit-skills submodule is initialized:

```bash
ls {AGENT_KIT_ROOT}/skills/claudekit-skills/plugins/
```

If the directory doesn't exist or is empty, tell the user:
> claudekit-skills submodule not initialized. Run this first:
> ```bash
> python3 {AGENT_KIT_ROOT}/scripts/install.py --init-submodule
> ```

If submodule exists, list available plugin bundles with their skills.

## Step 2: Check Already-Installed Skills

Run to see what's already installed (skip recommending these):

```bash
npx skills list -a claude-code
```

## Step 3: Detect Project Stack

Read the following files if they exist:
- `package.json` — framework, key dependencies
- `requirements.txt`, `pyproject.toml` — Python stack
- `go.mod`, `Cargo.toml` — Go / Rust
- `CLAUDE.md`, `AGENTS.md` — already-documented stack info (prefer this if available)

Summarize the stack in 1-2 lines.

## Step 4: Install from Submodule (Recommended)

Based on the detected stack, recommend skills from `{AGENT_KIT_ROOT}/skills/claudekit-skills/plugins/{bundle}/skills/`:

**Always install** (every project):
- `debugging` — Systematic debugging frameworks
- `code-review` — Code review automation
- `skill-creator` — Create and test new skills
- `mcp-management` — MCP server lifecycle management via Gemini
- `problem-solving` — Advanced thinking techniques
- `docs-seeker` — Documentation discovery
- `mermaidjs-v11` — Diagram generation
- `sequential-thinking` — Complex reasoning

**Frontend projects**:
- `frontend-design`, `frontend-development`, `ui-styling`, `web-frameworks`

**Backend projects**:
- `backend-development`, `better-auth`, `databases`

**AI/ML projects**:
- `ai-multimodal`, `context-engineering`, `google-adk-python`

Install selected skills:

```bash
npx skills add {AGENT_KIT_ROOT}/skills/claudekit-skills/plugins/{bundle-name}/skills/{skill-name} -a claude-code -y
```

## Step 5: Search Additional Skills (Optional)

For skills not in the submodule, run `npx skills find <keyword>` to discover more from skills.sh.

Present any additional findings and ask if the user wants to install them.

## Step 6: Summary

After all installs:
- List successfully installed skills
- Note any failures with the error
- Submodule location: `{AGENT_KIT_ROOT}/skills/claudekit-skills/plugins/`
- Tip: run `python3 {AGENT_KIT_ROOT}/scripts/install.py --init-submodule` to initialize submodule
- Tip: run `npx skills find <keyword>` anytime to discover more skills from skills.sh
