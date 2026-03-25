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

## Step 2: Read Current Settings

Read both:
- `~/.claude/settings.json` — global permissions (apply to all projects)
- `.claude/settings.json` — project-level permissions (create as `{}` if missing)

---

## Step 3: Merge MCP Permissions

For each permission in `mcpPermissions` from `global/settings.json`:

- **Skip** if already present in `~/.claude/settings.json` `permissions.allow` (already covered globally)
- **Skip** if already present in `.claude/settings.json` `permissions.allow`
- **Add** to `.claude/settings.json` only if missing from both

Never remove existing permissions. Deduplicate.

If all permissions are covered globally, skip writing `.claude/settings.json` entirely and note that global permissions already cover everything.

---

## Step 4: Report

Show a brief summary:
- Permissions added to project settings (list new ones only)
- Permissions skipped — already in global `~/.claude/settings.json`
- Permissions skipped — already in project `.claude/settings.json`
- Path updated: `.claude/settings.json` (or "no changes needed")
