#!/usr/bin/env python3
"""Agent Kit — Global Installer
Installs global Claude Code commands and registers user-scoped MCP servers.

Usage:
  python3 scripts/install.py          # Full global install
  python3 scripts/install.py --check  # Check current status only
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()
GLOBAL_DIR = REPO_ROOT / "global"
CUSTOM_DIR = REPO_ROOT / "custom"
CLAUDE_DIR = Path.home() / ".claude"
CLAUDE_COMMANDS_DIR = CLAUDE_DIR / "commands"
CLAUDE_SETTINGS = CLAUDE_DIR / "settings.json"
AGENT_KIT_PATH_FILE = CLAUDE_DIR / "agent-kit-path"

CHECK_ONLY = "--check" in sys.argv

DIVIDER = "━" * 44

OLD_COMMAND_NAMES = ["init-project.md", "setup-skills.md", "setup-custom.md"]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def claude_available() -> bool:
    return shutil.which("claude") is not None


# ── Header ────────────────────────────────────────────────────────────────────

print("Agent Kit — Global Installer")
print(DIVIDER)
print(f"  Source : {REPO_ROOT}")
print(f"  Target : {CLAUDE_DIR}")
if CHECK_ONLY:
    print("  Mode   : check only (no writes)")
print()

# ── Pre-flight ────────────────────────────────────────────────────────────────

if not shutil.which("node"):
    print("ERROR: node not found. Install Node.js from https://nodejs.org")
    sys.exit(1)

# ── Check mode ────────────────────────────────────────────────────────────────

if CHECK_ONLY:
    print(f"--- Agent Kit path ({AGENT_KIT_PATH_FILE}) ---")
    if AGENT_KIT_PATH_FILE.exists():
        print(f"  ✓ {AGENT_KIT_PATH_FILE.read_text().strip()}")
    else:
        print("  ✗ not saved")

    print()
    print(f"--- Global commands ({CLAUDE_COMMANDS_DIR}) ---")
    for src in sorted((GLOBAL_DIR / "commands").glob("*.md")):
        dest = CLAUDE_COMMANDS_DIR / src.name
        mark = "✓" if dest.exists() else "✗"
        status = "installed" if dest.exists() else "NOT installed"
        print(f"  {mark} /{src.stem} — {status}")

    print()
    print("--- User-scoped MCP servers (~/.claude.json) ---")
    if not claude_available():
        print("  ✗ claude CLI not found — run install.py after installing Claude Code")
    else:
        settings = load_json(GLOBAL_DIR / "settings.json")
        for name in settings.get("mcpServers", {}):
            result = run(["claude", "mcp", "get", name])
            if "user" in result.stdout or "local" in result.stdout:
                print(f"  ✓ {name} — configured")
            else:
                print(f"  ✗ {name} — NOT configured (run install.py to add)")

    sys.exit(0)

# ── 0. Save agent-kit path ────────────────────────────────────────────────────

CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
AGENT_KIT_PATH_FILE.write_text(str(REPO_ROOT) + "\n")
print(f"[0/4] Saved agent-kit path → {AGENT_KIT_PATH_FILE}")

# ── 1. Install global commands ────────────────────────────────────────────────

print()
print("[1/4] Installing global Claude Code commands...")
CLAUDE_COMMANDS_DIR.mkdir(parents=True, exist_ok=True)

for old_name in OLD_COMMAND_NAMES:
    old_path = CLAUDE_COMMANDS_DIR / old_name
    if old_path.exists():
        old_path.unlink()
        print(f"  - removed old command: /{old_path.stem} (replaced by ak: prefix)")

installed = 0
for src in sorted((GLOBAL_DIR / "commands").glob("*.md")):
    dest = CLAUDE_COMMANDS_DIR / src.name
    shutil.copy2(src, dest)
    print(f"  + /{src.stem}")
    installed += 1

print(f"  {installed} command(s) installed to {CLAUDE_COMMANDS_DIR}")

# ── 2. Register user-scoped MCP servers ───────────────────────────────────────

print()
print("[2/4] Registering user-scoped MCP servers...")

if not claude_available():
    print("  ✗ claude CLI not found — skipping MCP setup")
    print("    Install Claude Code first, then re-run this script")
else:
    settings = load_json(GLOBAL_DIR / "settings.json")
    added = skipped = 0
    for name, cfg in settings.get("mcpServers", {}).items():
        cmd_parts = [cfg["command"]] + cfg.get("args", [])
        result = run(["claude", "mcp", "add", "--scope", "user", "--transport", "stdio",
                      name, "--", *cmd_parts])
        if result.returncode == 0:
            print(f"  + {name}")
            added += 1
        else:
            print(f"  = {name} (already registered, skipped)")
            skipped += 1
    print(f"  {added} server(s) added, {skipped} skipped")

# ── 3. Merge MCP permissions into ~/.claude/settings.json ─────────────────────

print()
print("[3/4] Merging MCP permissions into ~/.claude/settings.json...")

source = load_json(GLOBAL_DIR / "settings.json")
incoming = source.get("mcpPermissions", [])

if not incoming:
    print("  (no mcpPermissions defined)")
else:
    current = load_json(CLAUDE_SETTINGS)
    current.setdefault("permissions", {}).setdefault("allow", [])
    allow = current["permissions"]["allow"]

    added = skipped = 0
    for perm in incoming:
        if perm not in allow:
            allow.append(perm)
            print(f"  + {perm}")
            added += 1
        else:
            skipped += 1

    save_json(CLAUDE_SETTINGS, current)
    print(f"  {added} permission(s) added, {skipped} already present")

# ── 4. Register claudekit-skills marketplace ─────────────────────────────────

CLAUDEKIT_MARKETPLACE = "mrgoonie/claudekit-skills"

print()
print("[4/5] Registering claudekit-skills marketplace...")

if not claude_available():
    print("  ✗ claude CLI not found — skipping marketplace setup")
else:
    result = run(["claude", "plugin", "marketplace", "add", CLAUDEKIT_MARKETPLACE])
    if result.returncode == 0:
        print(f"  + marketplace registered: {CLAUDEKIT_MARKETPLACE}")
    else:
        err = result.stderr.strip() or result.stdout.strip()
        if "already" in err.lower() or "exist" in err.lower():
            print(f"  = marketplace already configured: {CLAUDEKIT_MARKETPLACE}")
        else:
            print(f"  ! marketplace add failed: {err}")
    print("  → plugins will be installed per-project via /ak:setup-custom")

# ── 5. Verify custom/ directory ───────────────────────────────────────────────

print()
print("[5/5] Custom assets directory...")

skill_count = len(list((CUSTOM_DIR / "skills").rglob("SKILL.md")))
cmd_count = len([f for f in (CUSTOM_DIR / "commands").glob("*.md")
                 if f.name != "README.md"])
hooks_file = CUSTOM_DIR / "hooks" / "hooks.json"
hook_count = len(load_json(hooks_file)) if hooks_file.exists() else 0

print(f"  skills:   {skill_count}")
print(f"  commands: {cmd_count}")
print(f"  hooks:    {hook_count}")

# ── Done ──────────────────────────────────────────────────────────────────────

print()
print(DIVIDER)
print("Done! Global setup complete.")
print()
print("Available commands (in any project):")
for src in sorted((GLOBAL_DIR / "commands").glob("*.md")):
    print(f"  /{src.stem}")
print()
print("Next: open any project in Claude Code and run /ak:init-project")
print("      /ak:setup-custom  to install custom skills, commands, and hooks")
print("      /ak:setup-skills  to install additional skills from the skills.sh registry")
print()
print("Note: mrgoonie/claudekit-skills (34 community skills) installed globally — available in all projects.")
