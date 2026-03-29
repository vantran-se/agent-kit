#!/usr/bin/env python3
from __future__ import annotations
"""Agent Kit — Init Project Setup Script

Handles mechanical setup steps for /ak:init-project so the AI doesn't
have to check & execute each one individually. Saves tokens significantly.

Usage:
  python3 scripts/init-project.py                          # run in current dir
  python3 scripts/init-project.py --cwd /path/to/project   # specify project
  python3 scripts/init-project.py --skip-gitnexus           # skip indexing
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
  entry = ".gitnexus/"

  if gitignore.exists():
    content = gitignore.read_text()
    if entry in content:
      return {"updated": False, "already_had_gitnexus": True}
    # Append with newline separator
    separator = "" if content.endswith("\n") else "\n"
    gitignore.write_text(f"{content}{separator}\n# GitNexus index\n{entry}\n")
    return {"updated": True, "already_had_gitnexus": False}

  # No .gitignore — create one
  gitignore.write_text(f"# GitNexus index\n{entry}\n")
  return {"updated": True, "already_had_gitnexus": False}


# ── Step 2: GitNexus Analyze ──────────────────────────────────────────────────

def run_gitnexus(project: Path, skip: bool) -> dict:
  """Run gitnexus analyze if project is a git repo."""
  is_git = (project / ".git").is_dir()

  if not is_git:
    return {"is_git_repo": False, "status": "skipped", "message": "not a git repo"}

  if skip:
    return {"is_git_repo": True, "status": "skipped", "message": "--skip-gitnexus flag"}

  if not shutil.which("npx"):
    return {"is_git_repo": True, "status": "error", "message": "npx not found"}

  code, stdout, stderr = run_cmd(["npx", "-y", "gitnexus", "analyze"], cwd=project)
  if code == 0:
    return {"is_git_repo": True, "status": "indexed"}
  return {"is_git_repo": True, "status": "error", "message": stderr or stdout}


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


# ── Step 4: Detect Formatter ──────────────────────────────────────────────────

HOOK_TPL = (
  'FILE=$(jq -r \'.tool_input.file_path // empty\'); '
  '[ -n "$FILE" ] && {cmd} 2>/dev/null || true'
)

FORMATTER_MAP = [
  # (config files to check, formatter name, hook command)
  (
    [".prettierrc", ".prettierrc.json", ".prettierrc.yaml", ".prettierrc.yml",
     ".prettierrc.js", ".prettierrc.cjs", ".prettierrc.mjs", "prettier.config.js",
     "prettier.config.cjs", "prettier.config.mjs"],
    "prettier",
    'npx prettier --write "$FILE"',
  ),
  (
    ["biome.json", "biome.jsonc"],
    "biome",
    'npx biome format --write "$FILE"',
  ),
  (
    [".eslintrc", ".eslintrc.json", ".eslintrc.js", ".eslintrc.cjs",
     ".eslintrc.yml", ".eslintrc.yaml", "eslint.config.js", "eslint.config.cjs",
     "eslint.config.mjs"],
    "eslint",
    'npx eslint --fix "$FILE"',
  ),
  (
    ["ruff.toml", ".ruff.toml"],
    "ruff",
    'ruff format "$FILE"',
  ),
  (
    ["pyproject.toml"],  # check for [tool.black] inside
    "black",
    'black "$FILE"',
  ),
  (
    ["go.mod"],
    "gofmt",
    'gofmt -w "$FILE"',
  ),
  (
    ["Cargo.toml"],
    "rustfmt",
    'rustfmt "$FILE"',
  ),
  (
    [".rubocop.yml", ".rubocop.yaml"],
    "rubocop",
    'bundle exec rubocop --autocorrect "$FILE"',
  ),
  (
    [".standard.yml"],
    "standardrb",
    'bundle exec standardrb --fix "$FILE"',
  ),
]


def detect_formatter(project: Path) -> dict:
  """Detect project formatter by checking config file existence."""
  for config_files, name, cmd in FORMATTER_MAP:
    for cfg in config_files:
      if (project / cfg).exists():
        # Special case: pyproject.toml might not have [tool.black]
        if name == "black" and cfg == "pyproject.toml":
          content = read_text_file(project / cfg) or ""
          # Check for ruff first (higher priority)
          if "[tool.ruff" in content:
            continue
          if "[tool.black" not in content:
            continue
        hook_command = HOOK_TPL.format(cmd=cmd)
        return {"detected": name, "hook_command": hook_command}

  # Fallback: check package.json for formatter hints
  pkg = load_json_file(project / "package.json")
  if pkg:
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    if "prettier" in deps:
      hook_command = HOOK_TPL.format(cmd='npx prettier --write "$FILE"')
      return {"detected": "prettier", "hook_command": hook_command}
    if "@biomejs/biome" in deps:
      hook_command = HOOK_TPL.format(cmd='npx biome format --write "$FILE"')
      return {"detected": "biome", "hook_command": hook_command}
    if "eslint" in deps:
      hook_command = HOOK_TPL.format(cmd='npx eslint --fix "$FILE"')
      return {"detected": "eslint", "hook_command": hook_command}

  return {"detected": None, "hook_command": None}


# ── Step 5: Agent Kit Path & MCP Permissions ──────────────────────────────────

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
    help="Skip gitnexus analyze"
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

  # 2. GitNexus analyze (run early so AI can use MCP immediately)
  result["gitnexus"] = run_gitnexus(project, skip=args.skip_gitnexus)

  # 3. Scan existing setup files
  result["existing"] = scan_existing(project)

  # 4. Detect formatter
  result["formatter"] = detect_formatter(project)

  # 5. Agent Kit path & MCP permissions
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
  if gi["already_had_gitnexus"]:
    print("  ✓ .gitignore already has .gitnexus/")
  elif gi["updated"]:
    print("  + .gitignore updated with .gitnexus/")

  # GitNexus
  gn = data["gitnexus"]
  status_icon = {"indexed": "✓", "skipped": "—", "error": "✗"}
  print(f"  {status_icon.get(gn['status'], '?')} gitnexus: {gn['status']}", end="")
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

  # Formatter
  print()
  fmt = data["formatter"]
  if fmt["detected"]:
    print(f"  ✓ Formatter detected: {fmt['detected']}")
  else:
    print("  — No formatter detected")

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
