---
description: Install custom skills, commands, and hooks from agent-kit custom/ directory
category: workflow
allowed-tools: Read, Write, Edit, Bash(ls:*, cat:*, cp:*, npx:*, mkdir:*)
argument-hint: "[asset-names...]"
---

# Install Custom Skills, Commands, and Hooks

Install custom assets from the user's agent-kit repository into the current project or globally. After installation, update CLAUDE.md and AGENTS.md.

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

Store as `AGENT_KIT_ROOT`.

---

## Step 2: Discover Available Assets

Run in parallel:

**2a. Custom Skills**:
```bash
ls "$AGENT_KIT_ROOT/custom/skills/"
```
For each directory with `SKILL.md`, read it to extract: name, description, scope (from frontmatter).

**2b. Custom Commands**:
```bash
ls "$AGENT_KIT_ROOT/custom/commands/"
```
For each `.md` file (excluding README.md), read first 5 lines for description.

**2c. Custom Hooks**:
```bash
cat "$AGENT_KIT_ROOT/custom/hooks/hooks.json"
```
Check which hooks are already in `.claude/settings.json` or `~/.claude/settings.json` — skip those.

---

## Step 3: Check Already Installed

- Skills in `~/.claude/skills/` or `.claude/skills/` → mark as installed
- Commands in `~/.claude/commands/` or `.claude/commands/` → mark as installed
- Hooks in settings.json → mark as installed

---

## Step 4: Present Options

If no custom assets found:
> No custom assets in `$AGENT_KIT_ROOT/custom/`.

Otherwise present:
```
CUSTOM SKILLS
  1. skill-name — description [scope: global/project]

CUSTOM COMMANDS
  2. /command-name — description [scope: global/project]

HOOKS
  3. hook-name — description [scope: project]

Enter numbers to install (e.g. "1 3"), "all", or "none".
```

---

## Step 5: Resolve Scope

- `scope: global` in definition → install globally
- `scope: project` → install to project
- If not set → ask user

---

## Step 6: Install

### Skill
```bash
# Project
npx skills add "$AGENT_KIT_ROOT/custom/skills/{skill-name}" -a claude-code -y
# Global
npx skills add "$AGENT_KIT_ROOT/custom/skills/{skill-name}" -a claude-code -g -y
```

### Command
```bash
# Project
mkdir -p .claude/commands
cp "$AGENT_KIT_ROOT/custom/commands/{name}.md" .claude/commands/
# Global
cp "$AGENT_KIT_ROOT/custom/commands/{name}.md" ~/.claude/commands/
```

### Hook
Merge into `.claude/settings.json` or `~/.claude/settings.json` under correct event key:
- `PreToolUse` — before tool execution
- `PostToolUse` — after tool execution
- `Stop` — when Claude stops

Hook structure:
```json
{
  "hooks": {
    "{event}": [
      {
        "matcher": "{matcher}",
        "hooks": [
          {
            "type": "command",
            "command": "{command}"
          }
        ]
      }
    ]
  }
}
```

Merge carefully — don't duplicate existing hooks.

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
- List what was installed (global/project)
- Note any failures
- Mention docs updated
- For community skills: run `/ak:setup-skills`
