# Install Custom Skills, Commands, and Hooks

You are installing custom assets from the user's agent-kit repository into the current project or globally.

## Step 1: Locate Agent Kit

Read the agent-kit path from `~/.claude/agent-kit-path`.

If the file does not exist, tell the user:
> agent-kit path not found. Run `python3 scripts/install.py` from your agent-kit directory first.

Then stop.

Store the path as AGENT_KIT_ROOT for the rest of this command.

## Step 2: Discover Available Assets

Run these three operations in parallel:

**2a. Custom Skills** — list directories in `{AGENT_KIT_ROOT}/custom/skills/` (each directory with a `SKILL.md` is a skill):
```bash
ls {AGENT_KIT_ROOT}/custom/skills/
```

For each skill directory found, read its `SKILL.md` to extract: name, description, scope (from frontmatter).

**2b. Custom Commands** — list `.md` files in `{AGENT_KIT_ROOT}/custom/commands/` (excluding README.md):
```bash
ls {AGENT_KIT_ROOT}/custom/commands/
```

For each `.md` file, read first 5 lines to extract: description from frontmatter or first heading.

**2c. Custom Hooks** — read `{AGENT_KIT_ROOT}/custom/hooks/hooks.json`:
```bash
cat {AGENT_KIT_ROOT}/custom/hooks/hooks.json
```

Also check which hooks are already configured in `.claude/settings.json` (project) and `~/.claude/settings.json` (global) — skip those.

## Step 3: Check Already Installed

Before presenting options, check what is already installed:

- Skills already in `~/.claude/skills/` or `.claude/skills/` → mark as installed
- Commands already in `~/.claude/commands/` or `.claude/commands/` → mark as installed
- Hooks already in `~/.claude/settings.json` or `.claude/settings.json` → mark as installed

## Step 4: Present Options to User

If all three categories are empty (no custom assets found), tell the user:
> No custom assets found in `{AGENT_KIT_ROOT}/custom/`. Add skills, commands, or hooks there to make them available here.

Otherwise, present a single message with all available assets grouped by category. Mark already-installed items with `[installed]`.

Example format:
```
CUSTOM SKILLS
  1. skill-name — description [scope: global/project]
  2. another-skill — description

CUSTOM COMMANDS
  3. /command-name — description [scope: global/project]
  4. /other-command — description

HOOKS
  5. auto-format-prettier — Auto-format JS/TS with Prettier after every edit [scope: project]
  6. notify-on-stop — Desktop notification when Claude finishes [scope: global]
  7. block-dangerous-bash — Warn before dangerous commands [scope: global] [installed]

Enter numbers to install (e.g. "1 3 5"), "all", or "none".
For items without a fixed scope, you'll be asked: global or project.
```

Wait for the user's response.

## Step 5: Resolve Scope for Each Selected Item

For each selected item:
- If it has `scope: global` in its definition → install globally
- If it has `scope: project` → install to current project
- If scope is not set → ask the user: "Install [name] globally (all projects) or for this project only?"

## Step 6: Install Selected Assets

### Installing a Skill

```bash
# Project-level
npx skills add {AGENT_KIT_ROOT}/custom/skills/{skill-name} -a claude-code -y

# Global
npx skills add {AGENT_KIT_ROOT}/custom/skills/{skill-name} -a claude-code -g -y
```

### Installing a Command

```bash
# Project-level
mkdir -p .claude/commands
cp {AGENT_KIT_ROOT}/custom/commands/{command-name}.md .claude/commands/

# Global
cp {AGENT_KIT_ROOT}/custom/commands/{command-name}.md ~/.claude/commands/
```

### Installing a Hook

Read the hook definition from `hooks.json` and merge it into the appropriate `settings.json`.

**Project-level** → `.claude/settings.json`
**Global** → `~/.claude/settings.json`

The merge logic — add under the correct event key (`PostToolUse`, `PreToolUse`, `Stop`):

```json
{
  "hooks": {
    "{event}": [
      {
        "matcher": "{matcher}",   // omit if event is Stop
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

Merge carefully — do not duplicate hooks already present with the same command.

## Step 7: Summary

After all installs:
- List what was installed and where (global / project)
- Note any failures with the error
- Tip: add new skills to `{AGENT_KIT_ROOT}/custom/skills/`, commands to `custom/commands/`, hooks to `custom/hooks/hooks.json`
