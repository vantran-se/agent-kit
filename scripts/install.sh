#!/usr/bin/env bash
# Agent Kit — Global Installer
# Installs global Claude Code commands and MCP servers into ~/.claude/
#
# Usage:
#   ./scripts/install.sh              # Full global install
#   ./scripts/install.sh --check      # Check current status only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GLOBAL_DIR="$REPO_ROOT/global"
CLAUDE_DIR="$HOME/.claude"
CLAUDE_COMMANDS_DIR="$CLAUDE_DIR/commands"
CLAUDE_SETTINGS="$CLAUDE_DIR/settings.json"

# ── Parse args ───────────────────────────────────────────────────────────────
CHECK_ONLY=false
for arg in "$@"; do
  case $arg in
    --check) CHECK_ONLY=true ;;
  esac
done

echo "Agent Kit — Global Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Source : $REPO_ROOT"
echo "  Target : $CLAUDE_DIR"
[[ "$CHECK_ONLY" == true ]] && echo "  Mode   : check only (no writes)"
echo ""

# ── Pre-flight ───────────────────────────────────────────────────────────────
if ! command -v node &> /dev/null; then
  echo "ERROR: node not found. Install Node.js from https://nodejs.org"
  exit 1
fi

if ! command -v npx &> /dev/null; then
  echo "ERROR: npx not found. Install Node.js from https://nodejs.org"
  exit 1
fi

if [[ "$CHECK_ONLY" == true ]]; then
  echo "--- Agent Kit path ($CLAUDE_DIR/agent-kit-path) ---"
  if [[ -f "$CLAUDE_DIR/agent-kit-path" ]]; then
    echo "  ✓ $(cat "$CLAUDE_DIR/agent-kit-path")"
  else
    echo "  ✗ not saved"
  fi

  echo ""
  echo "--- Global commands ($CLAUDE_COMMANDS_DIR) ---"
  for cmd_file in "$GLOBAL_DIR/commands/"*.md; do
    [[ -f "$cmd_file" ]] || continue
    cmd_name="$(basename "$cmd_file")"
    dest="$CLAUDE_COMMANDS_DIR/$cmd_name"
    if [[ -f "$dest" ]]; then
      echo "  ✓ /$(basename "$cmd_file" .md) — installed"
    else
      echo "  ✗ /$(basename "$cmd_file" .md) — NOT installed"
    fi
  done

  echo ""
  echo "--- Global MCP servers ($CLAUDE_SETTINGS) ---"
  if [[ -f "$CLAUDE_SETTINGS" ]]; then
    for key in context7 gitnexus sequential-thinking memory; do
      if node -e "const s=require('$CLAUDE_SETTINGS'); process.exit(s.mcpServers && s.mcpServers['$key'] ? 0 : 1)" 2>/dev/null; then
        echo "  ✓ $key — configured"
      else
        echo "  ✗ $key — NOT configured"
      fi
    done
  else
    echo "  ✗ settings.json not found"
  fi
  exit 0
fi

# ── 0. Save agent-kit path ───────────────────────────────────────────────────
mkdir -p "$CLAUDE_DIR"
echo "$REPO_ROOT" > "$CLAUDE_DIR/agent-kit-path"
echo "[0/3] Saved agent-kit path → $CLAUDE_DIR/agent-kit-path"

# ── 1. Install global commands ───────────────────────────────────────────────
echo ""
echo "[1/3] Installing global Claude Code commands..."
mkdir -p "$CLAUDE_COMMANDS_DIR"

# Remove old unprefixed command names left over from before the ak: rename
for old_name in init-project.md setup-skills.md setup-custom.md; do
  old_path="$CLAUDE_COMMANDS_DIR/$old_name"
  if [[ -f "$old_path" ]]; then
    rm "$old_path"
    echo "  - removed old command: /$old_name (replaced by ak: prefix)"
  fi
done

installed=0
for cmd_file in "$GLOBAL_DIR/commands/"*.md; do
  [[ -f "$cmd_file" ]] || continue
  cmd_name="$(basename "$cmd_file")"
  dest="$CLAUDE_COMMANDS_DIR/$cmd_name"
  cp "$cmd_file" "$dest"
  echo "  + /$(basename "$cmd_file" .md)"
  ((installed++))
done

echo "  $installed command(s) installed to $CLAUDE_COMMANDS_DIR"

# ── 2. Merge global MCP servers ──────────────────────────────────────────────
echo ""
echo "[2/3] Configuring global MCP servers..."

node -e "
const fs = require('fs');
const settingsPath = '$CLAUDE_SETTINGS';
const sourcePath = '$GLOBAL_DIR/settings.json';

let current = {};
try { current = JSON.parse(fs.readFileSync(settingsPath, 'utf8')); } catch {}

const source = JSON.parse(fs.readFileSync(sourcePath, 'utf8'));
if (!current.mcpServers) current.mcpServers = {};

let added = 0, skipped = 0;
for (const [name, config] of Object.entries(source.mcpServers || {})) {
  if (!current.mcpServers[name]) {
    current.mcpServers[name] = config;
    console.log('  + ' + name);
    added++;
  } else {
    console.log('  = ' + name + ' (already configured, skipped)');
    skipped++;
  }
}

fs.mkdirSync(require('path').dirname(settingsPath), { recursive: true });
fs.writeFileSync(settingsPath, JSON.stringify(current, null, 2) + '\n');
console.log('  ' + added + ' server(s) added, ' + skipped + ' skipped');
"

# ── 3. Verify custom/ directory ──────────────────────────────────────────────
echo ""
echo "[3/3] Custom assets directory..."
CUSTOM_DIR="$REPO_ROOT/custom"
skill_count=$(find "$CUSTOM_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
cmd_count=$(find "$CUSTOM_DIR/commands" -name "*.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
hook_count=$(node -e "try { const h=require('$CUSTOM_DIR/hooks/hooks.json'); console.log(h.length); } catch { console.log(0); }" 2>/dev/null)
echo "  skills:   $skill_count"
echo "  commands: $cmd_count"
echo "  hooks:    $hook_count"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Done! Global setup complete."
echo ""
echo "Available commands (in any project):"
for cmd_file in "$GLOBAL_DIR/commands/"*.md; do
  [[ -f "$cmd_file" ]] || continue
  echo "  /$(basename "$cmd_file" .md)"
done
echo ""
echo "Next: open any project in Claude Code and run /ak:init-project"
echo "      /ak:setup-custom  to install custom skills, commands, and hooks"
echo "      /ak:setup-skills  to install skills from skills.sh"
