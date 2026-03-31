---
description: Sync MCP permissions from agent-kit into global ~/.claude/settings.json
category: workflow
allowed-tools: Read, Write, Bash(cat:*)
---

# Update Agent Kit Settings for This Project

Sync the latest MCP permissions from agent-kit into global `~/.claude/settings.json`.

**Note:** MCP permissions are enabled globally by default during `python3 scripts/install.py`. Run this command only if you updated agent-kit and want to sync new permissions.

---

## Step 1: Read Agent Kit Config

Read the agent-kit path and MCP permissions:
```bash
AGENT_KIT_PATH=$(cat ~/.claude/agent-kit-path 2>/dev/null)
if [ -z "$AGENT_KIT_PATH" ]; then
  echo "agent-kit path not found. Run: python3 scripts/install.py"
  exit 1
fi
```

Read `$AGENT_KIT_PATH/global/settings.json` to get `mcpPermissions` array.

---

## Step 2: Read Global Settings

Read `~/.claude/settings.json`:
```bash
cat ~/.claude/settings.json
```

Extract `permissions.allow` array.

---

## Step 3: Merge MCP Permissions

For each permission in `mcpPermissions`:

- **Skip** if already in `~/.claude/settings.json` `permissions.allow`
- **Add** to `~/.claude/settings.json` `permissions.allow` if missing

Never remove existing permissions. Deduplicate.

Write `~/.claude/settings.json` only if new permissions were added.

---

## Step 4: Report

Show brief summary:
- Permissions added to global settings (list new ones only)
- Permissions skipped — already in global `~/.claude/settings.json`
- Path updated: `~/.claude/settings.json` (or "no changes needed")
