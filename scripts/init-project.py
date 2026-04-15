#!/usr/bin/env python3
from __future__ import annotations
"""Agent Kit — Init Project Setup Script

Handles mechanical setup steps for /ak:init-project so the AI doesn't
have to check & execute each one individually. Saves tokens significantly.

Usage:
  python3 scripts/init-project.py                          # run in current dir
  python3 scripts/init-project.py --cwd /path/to/project   # specify project
  python3 scripts/init-project.py --skip-gitnexus           # skip gitnexus rebuild
  python3 scripts/init-project.py --pretty                  # human-readable output
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.resolve()


# ── Utilities ─────────────────────────────────────────────────────────────────

def load_json_file(path: Path) -> dict | None:
  """Load JSON file, return None if missing or invalid."""
  try:
    return json.loads(path.read_text())
  except Exception:
    return None


def read_text_file(path: Path) -> str | None:
  """Read text file, return None if missing."""
  try:
    return path.read_text()
  except Exception:
    return None


def run_cmd(cmd: list[str], cwd: Path | None = None,
            timeout: int = 120) -> tuple[int, str, str]:
  """Run command, return (returncode, stdout, stderr)."""
  try:
    result = subprocess.run(
      cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()
  except FileNotFoundError:
    return -1, "", f"command not found: {cmd[0]}"
  except subprocess.TimeoutExpired:
    return -2, "", f"timeout after {timeout}s"


# ── Step 1: Update .gitignore ─────────────────────────────────────────────────

def update_gitignore(project: Path) -> dict:
  """Add .gitnexus/ to .gitignore if not already present."""
  gitignore = project / ".gitignore"
  entries = [(".gitnexus/", "# GitNexus output")]

  if gitignore.exists():
    content = gitignore.read_text()
    updated = False
    for entry, comment in entries:
      if entry not in content:
        separator = "" if content.endswith("\n") else "\n"
        content = f"{content}{separator}\n{comment}\n{entry}"
        updated = True
    if updated:
      gitignore.write_text(content + "\n")
    return {"updated": updated, "already_had_entries": not updated}

  # No .gitignore — create one
  lines = ["# GitNexus output", ".gitnexus/"]
  gitignore.write_text("\n".join(lines) + "\n")
  return {"updated": True, "already_had_entries": False}


# ── Step 2: GitNexus Rebuild ──────────────────────────────────────────────────

def run_gitnexus_rebuild(project: Path, skip: bool) -> dict:
  """Run gitnexus analyze if gitnexus is available and project has code."""
  # Check if .gitnexus/ already exists (gitnexus was run before)
  gitnexus_dir_exists = (project / ".gitnexus").exists()

  if not gitnexus_dir_exists:
    return {"status": "skipped", "message": ".gitnexus/ not found — run 'npx gitnexus analyze' first"}

  if skip:
    return {"status": "skipped", "message": "--skip-gitnexus flag"}

  # Try to rebuild using gitnexus CLI
  code, stdout, stderr = run_cmd(
    ["npx", "gitnexus", "analyze"],
    cwd=project
  )
  if code == 0:
    return {"status": "rebuilt"}
  return {"status": "error", "message": stderr or stdout}


# ── Step 3: Scan Existing Setup ───────────────────────────────────────────────

def scan_existing(project: Path) -> dict:
  """Check which config files already exist and read their content."""
  result = {}

  # CLAUDE.md
  claude_md = project / "CLAUDE.md"
  if claude_md.exists():
    result["claude_md"] = {"exists": True, "content": read_text_file(claude_md)}
  else:
    result["claude_md"] = {"exists": False}

  # AGENTS.md
  agents_md = project / "AGENTS.md"
  if agents_md.exists():
    result["agents_md"] = {"exists": True, "content": read_text_file(agents_md)}
  else:
    result["agents_md"] = {"exists": False}

  # .claude/settings.json
  settings = project / ".claude" / "settings.json"
  if settings.exists():
    result["claude_settings"] = {"exists": True, "content": load_json_file(settings)}
  else:
    result["claude_settings"] = {"exists": False}

  return result


# ── Step 4: Agent Kit Path & MCP Permissions ──────────────────────────────────

def read_agent_kit_info() -> dict:
  """Read agent-kit path and MCP permissions from global config."""
  ak_path_file = Path.home() / ".claude" / "agent-kit-path"
  ak_path = read_text_file(ak_path_file)
  ak_path = ak_path.strip() if ak_path else None

  mcp_permissions = []
  if ak_path:
    settings_file = Path(ak_path) / "global" / "settings.json"
    settings = load_json_file(settings_file)
    if settings:
      mcp_permissions = settings.get("mcpPermissions", [])

  return {
    "agent_kit_path": ak_path,
    "mcp_permissions": mcp_permissions,
  }


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
  parser = argparse.ArgumentParser(
    description="Agent Kit — Init Project Setup Script"
  )
  parser.add_argument(
    "--cwd", type=str, default=".",
    help="Project directory (default: current dir)"
  )
  parser.add_argument(
    "--skip-gitnexus", action="store_true",
    help="Skip gitnexus rebuild"
  )
  parser.add_argument(
    "--pretty", action="store_true",
    help="Human-readable output instead of JSON"
  )
  args = parser.parse_args()

  project = Path(args.cwd).resolve()
  if not project.is_dir():
    print(json.dumps({"error": f"directory not found: {project}"}))
    sys.exit(1)

  # Run all steps in order
  result = {}

  # 1. Update .gitignore (before gitnexus so .gitnexus/ is ignored)
  result["gitignore"] = update_gitignore(project)

  # 2. GitNexus rebuild (run early so AI can use graph immediately)
  result["gitnexus"] = run_gitnexus_rebuild(project, skip=args.skip_gitnexus)

  # 3. Scan existing setup files
  result["existing"] = scan_existing(project)

  # 4. Agent Kit path & MCP permissions
  ak_info = read_agent_kit_info()
  result["agent_kit_path"] = ak_info["agent_kit_path"]
  result["mcp_permissions"] = ak_info["mcp_permissions"]

  # Output
  if args.pretty:
    print_pretty(result)
  else:
    print(json.dumps(result, indent=2, ensure_ascii=False))


def print_pretty(data: dict):
  """Print human-readable summary."""
  divider = "━" * 44

  print("Agent Kit — Init Project Setup")
  print(divider)

  # Gitignore
  gi = data["gitignore"]
  if gi.get("already_had_entries"):
    print("  ✓ .gitignore already has .gitnexus/")
  elif gi.get("updated"):
    print("  + .gitignore updated with .gitnexus/")

  # GitNexus
  gn = data["gitnexus"]
  status_icon = {"rebuilt": "✓", "skipped": "—", "error": "✗"}
  print(f"  {status_icon.get(gn.get('status', '?'), '?')} gitnexus: {gn.get('status', 'unknown')}", end="")
  if "message" in gn:
    print(f" ({gn['message']})", end="")
  print()

  # Existing files
  pretty_names = {
    "claude_md": "CLAUDE.md",
    "agents_md": "AGENTS.md",
    "claude_settings": ".claude/settings.json",
  }
  print()
  print("  Existing files:")
  for key in ["claude_md", "agents_md", "claude_settings"]:
    info = data["existing"][key]
    name = pretty_names[key]
    icon = "✓" if info["exists"] else "—"
    print(f"    {icon} {name}")

  # Agent Kit
  print()
  if data["agent_kit_path"]:
    print(f"  ✓ Agent Kit: {data['agent_kit_path']}")
    print(f"    MCP permissions: {len(data['mcp_permissions'])}")
  else:
    print("  — Agent Kit path not found")

  print()
  print(divider)


if __name__ == "__main__":
  main()
