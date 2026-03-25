# Update Agent Kit Settings for This Project

Sync the latest MCP permissions and other settings from agent-kit into this project's `.claude/settings.json`.

Run this in any project that was previously set up with `/ak:init-project` to pick up new MCP servers, permissions, or other changes.

---

## Step 1: Read Agent Kit Config

Read the agent-kit path:
```bash
cat ~/.claude/agent-kit-path
```

If not found, stop and tell the user to run `python3 scripts/install.py` first.

Read `<agent-kit-path>/global/settings.json` to get the current `mcpPermissions` array.

---

## Step 2: Read Current Project Settings

Read `.claude/settings.json` if it exists, otherwise start with `{}`.

---

## Step 3: Merge MCP Permissions

Merge the `mcpPermissions` from `global/settings.json` into `.claude/settings.json` under `permissions.allow`.

- Add any permissions from the agent-kit list that are not already present
- Never remove existing permissions
- Deduplicate

Example result:
```json
{
  "permissions": {
    "allow": [
      "mcp__context7__*",
      "mcp__gitnexus__*",
      "mcp__sequential-thinking__*",
      "mcp__memory__*"
    ]
  }
}
```

Write the merged result back to `.claude/settings.json`.

---

## Step 4: Report

Show a brief summary:
- Permissions added (list new ones only)
- Permissions already present (skipped)
- Path updated: `.claude/settings.json`
