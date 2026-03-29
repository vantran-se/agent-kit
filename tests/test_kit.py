#!/usr/bin/env python3
"""
Agent Kit integrity tests — verify the kit is coherent after any update.

Run: python3 tests/test_kit.py
Or:  python3 -m pytest tests/ -v
"""
import ast
import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
HOOKS_JSON = ROOT / 'custom' / 'hooks' / 'hooks.json'
SCRIPTS_DIR = ROOT / 'custom' / 'hooks' / 'scripts'
GLOBAL_SETTINGS = ROOT / 'global' / 'settings.json'
GLOBAL_COMMANDS_DIR = ROOT / 'global' / 'commands'
CUSTOM_SKILLS_DIR = ROOT / 'custom' / 'skills'
README = ROOT / 'README.md'
CLAUDE_MD = ROOT / 'CLAUDE.md'
AGENTS_MD = ROOT / 'AGENTS.md'
INSTALL_PY = ROOT / 'scripts' / 'install.py'


# ─────────────────────────────────────────────────────────────────────────────
class TestHooksJson(unittest.TestCase):
    """hooks.json schema, field completeness, and script references."""

    def setUp(self):
        with open(HOOKS_JSON) as f:
            self.hooks = json.load(f)

    def test_is_a_list(self):
        self.assertIsInstance(self.hooks, list)

    def test_not_empty(self):
        self.assertGreater(len(self.hooks), 0)

    def test_required_fields_present(self):
        required = {'name', 'description', 'stacks', 'scope', 'hook'}
        for h in self.hooks:
            missing = required - set(h.keys())
            self.assertFalse(missing, f"Hook '{h.get('name', '?')}' missing fields: {missing}")

    def test_hook_field_has_event_and_command(self):
        for h in self.hooks:
            hook = h['hook']
            self.assertIn('event', hook, f"Hook '{h['name']}' missing event")
            self.assertIn('command', hook, f"Hook '{h['name']}' missing command")

    def test_valid_events(self):
        valid = {'PreToolUse', 'PostToolUse', 'Stop', 'SubagentStop', 'SessionStart', 'UserPromptSubmit'}
        for h in self.hooks:
            event = h['hook']['event']
            self.assertIn(event, valid, f"Hook '{h['name']}' has unknown event: {event}")

    def test_valid_scopes(self):
        for h in self.hooks:
            self.assertIn(h['scope'], ('global', 'project'),
                          f"Hook '{h['name']}' has invalid scope: {h['scope']}")

    def test_no_duplicate_names(self):
        names = [h['name'] for h in self.hooks]
        duplicates = {n for n in names if names.count(n) > 1}
        self.assertFalse(duplicates, f"Duplicate hook names: {duplicates}")

    def test_script_references_point_to_existing_files(self):
        """Commands referencing custom/hooks/scripts/*.py must point to existing files."""
        script_pattern = re.compile(r'custom/hooks/scripts/([^"\')\s]+\.py)')
        for h in self.hooks:
            cmd = h['hook']['command']
            for match in script_pattern.finditer(cmd):
                script_path = SCRIPTS_DIR / Path(match.group(1)).name
                self.assertTrue(
                    script_path.exists(),
                    f"Hook '{h['name']}' references missing script: {match.group(1)}"
                )

    def test_stacks_is_list(self):
        for h in self.hooks:
            self.assertIsInstance(h['stacks'], list,
                                  f"Hook '{h['name']}' stacks must be a list")

    def test_names_are_kebab_case(self):
        pattern = re.compile(r'^[a-z0-9-]+$')
        for h in self.hooks:
            self.assertRegex(h['name'], pattern,
                             f"Hook name '{h['name']}' should be kebab-case")

    def test_descriptions_are_non_empty(self):
        for h in self.hooks:
            self.assertTrue(h['description'].strip(),
                            f"Hook '{h['name']}' has empty description")


# ─────────────────────────────────────────────────────────────────────────────
class TestHookScripts(unittest.TestCase):
    """custom/hooks/scripts/ — hooks use inline bash commands, no Python scripts."""

    def test_scripts_directory_exists(self):
        self.assertTrue(SCRIPTS_DIR.exists())

    def test_no_python_scripts(self):
        """All hooks use inline bash commands — no standalone scripts needed."""
        scripts = list(SCRIPTS_DIR.glob('*.py'))
        self.assertEqual(scripts, [],
                         f"Unexpected Python scripts found: {[s.name for s in scripts]}")

    def test_no_shell_scripts_exist(self):
        sh_files = list(SCRIPTS_DIR.glob('*.sh'))
        self.assertEqual(sh_files, [],
                         f"Shell scripts found (not allowed): {[f.name for f in sh_files]}")


# ─────────────────────────────────────────────────────────────────────────────
class TestGlobalSettings(unittest.TestCase):
    """global/settings.json — MCP server definitions."""

    def setUp(self):
        with open(GLOBAL_SETTINGS) as f:
            self.settings = json.load(f)

    def test_has_mcp_servers(self):
        self.assertIn('mcpServers', self.settings)

    def test_expected_servers_present(self):
        expected = {'context7', 'gitnexus', 'sequential-thinking', 'memory'}
        actual = set(self.settings['mcpServers'].keys())
        self.assertEqual(expected, actual, f"MCP servers mismatch. Expected: {expected}, Got: {actual}")

    def test_each_server_has_command_and_args(self):
        for name, server in self.settings['mcpServers'].items():
            self.assertIn('command', server, f"Server '{name}' missing command")
            self.assertIn('args', server, f"Server '{name}' missing args")
            self.assertIsInstance(server['args'], list,
                                  f"Server '{name}' args must be a list")

    def test_servers_use_npx(self):
        for name, server in self.settings['mcpServers'].items():
            self.assertEqual(server['command'], 'npx',
                             f"Server '{name}' should use npx")


# ─────────────────────────────────────────────────────────────────────────────
class TestSkills(unittest.TestCase):
    """custom/skills/ — each skill has valid SKILL.md with required frontmatter."""

    EXPECTED_SKILLS = {'internal-comms'}

    def setUp(self):
        self.skill_dirs = [
            d for d in CUSTOM_SKILLS_DIR.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

    def test_expected_skills_present(self):
        names = {d.name for d in self.skill_dirs}
        self.assertEqual(names, self.EXPECTED_SKILLS,
                         f"Skills mismatch. Expected: {self.EXPECTED_SKILLS}, Got: {names}")

    def test_each_skill_has_skill_md(self):
        for skill_dir in self.skill_dirs:
            skill_md = skill_dir / 'SKILL.md'
            self.assertTrue(skill_md.exists(),
                            f"Skill '{skill_dir.name}' missing SKILL.md")

    def test_skill_md_has_frontmatter(self):
        for skill_dir in self.skill_dirs:
            content = (skill_dir / 'SKILL.md').read_text()
            self.assertTrue(content.startswith('---'),
                            f"Skill '{skill_dir.name}' SKILL.md missing YAML frontmatter")

    def test_skill_md_has_name_field(self):
        for skill_dir in self.skill_dirs:
            content = (skill_dir / 'SKILL.md').read_text()
            self.assertIn('name:', content,
                          f"Skill '{skill_dir.name}' SKILL.md missing 'name:' field")

    def test_skill_md_has_description_field(self):
        for skill_dir in self.skill_dirs:
            content = (skill_dir / 'SKILL.md').read_text()
            self.assertIn('description:', content,
                          f"Skill '{skill_dir.name}' SKILL.md missing 'description:' field")

    def test_each_skill_has_license(self):
        for skill_dir in self.skill_dirs:
            license_file = skill_dir / 'LICENSE.txt'
            self.assertTrue(license_file.exists(),
                            f"Skill '{skill_dir.name}' missing LICENSE.txt")


# ─────────────────────────────────────────────────────────────────────────────
class TestGlobalCommands(unittest.TestCase):
    """global/commands/ — command files exist, are non-empty, and have titles."""

    EXPECTED_COMMANDS = {
        'ak:init-project.md',
        'ak:setup-skills.md',
        'ak:setup-custom.md',
        'ak:update.md',
    }

    def test_command_files_exist(self):
        actual = {f.name for f in GLOBAL_COMMANDS_DIR.glob('*.md')}
        self.assertEqual(actual, self.EXPECTED_COMMANDS,
                         f"Commands mismatch. Expected: {self.EXPECTED_COMMANDS}, Got: {actual}")

    def test_commands_are_non_empty(self):
        for cmd_file in GLOBAL_COMMANDS_DIR.glob('*.md'):
            content = cmd_file.read_text().strip()
            self.assertTrue(len(content) > 100,
                            f"{cmd_file.name} is suspiciously short ({len(content)} chars)")

    def test_commands_have_h1_title(self):
        for cmd_file in GLOBAL_COMMANDS_DIR.glob('*.md'):
            content = cmd_file.read_text()
            self.assertRegex(content, r'^# .+',
                             f"{cmd_file.name} missing H1 title")


# ─────────────────────────────────────────────────────────────────────────────
class TestDocumentationSync(unittest.TestCase):
    """README.md and CLAUDE.md counts must match the actual project state."""

    def setUp(self):
        with open(HOOKS_JSON) as f:
            self.hooks = json.load(f)
        self.readme = README.read_text()
        self.claude_md = CLAUDE_MD.read_text()
        self.agents_md = AGENTS_MD.read_text()

    def test_hook_count_in_claude_md(self):
        actual = len(self.hooks)
        pattern = re.compile(rf'\b{actual}\b hooks')
        self.assertRegex(self.claude_md, pattern,
                         f"CLAUDE.md should mention '{actual} hooks' (actual count: {actual})")

    def test_hook_count_in_readme(self):
        actual = len(self.hooks)
        pattern = re.compile(rf'\b{actual}\b hooks')
        self.assertRegex(self.readme, pattern,
                         f"README.md should mention '{actual} hooks' (actual count: {actual})")

    def test_mcp_server_count_in_readme(self):
        with open(GLOBAL_SETTINGS) as f:
            settings = json.load(f)
        server_names = list(settings['mcpServers'].keys())
        for name in server_names:
            self.assertIn(name, self.readme,
                          f"README.md missing MCP server: {name}")

    def test_all_skills_mentioned_in_readme(self):
        skill_names = [d.name for d in CUSTOM_SKILLS_DIR.iterdir()
                       if d.is_dir() and not d.name.startswith('.')]
        for name in skill_names:
            self.assertIn(name, self.readme,
                          f"README.md missing skill: {name}")

    def test_all_skills_mentioned_in_agents_md(self):
        skill_names = [d.name for d in CUSTOM_SKILLS_DIR.iterdir()
                       if d.is_dir() and not d.name.startswith('.')]
        for name in skill_names:
            self.assertIn(name, self.agents_md,
                          f"AGENTS.md missing skill: {name}")

    def test_sync_docs_rule_in_claude_md(self):
        self.assertIn('/ak:sync-docs', self.claude_md,
                      "CLAUDE.md must mention /ak:sync-docs rule")

    def test_hook_names_in_claude_md(self):
        """All hook names must appear in CLAUDE.md hooks list."""
        for h in self.hooks:
            self.assertIn(h['name'], self.claude_md,
                          f"CLAUDE.md hooks list missing: {h['name']}")


# ─────────────────────────────────────────────────────────────────────────────
class TestInstallScript(unittest.TestCase):
    """scripts/install.py — exists and contains key install targets."""

    def test_install_py_exists(self):
        self.assertTrue(INSTALL_PY.exists(), "scripts/install.py not found")

    def test_install_py_is_valid_python(self):
        source = INSTALL_PY.read_text()
        try:
            ast.parse(source)
        except SyntaxError as e:
            self.fail(f"install.py has syntax error: {e}")

    def test_saves_agent_kit_path(self):
        content = INSTALL_PY.read_text()
        self.assertIn('agent-kit-path', content,
                      "install.py must save agent-kit-path")

    def test_installs_global_commands(self):
        content = INSTALL_PY.read_text()
        self.assertTrue(
            '~/.claude/commands' in content or 'CLAUDE_COMMANDS_DIR' in content,
            "install.py must reference ~/.claude/commands or CLAUDE_COMMANDS_DIR"
        )

    def test_registers_mcp_servers(self):
        content = INSTALL_PY.read_text()
        self.assertIn('mcpServers', content,
                      "install.py must configure mcpServers")

    def test_supports_check_flag(self):
        content = INSTALL_PY.read_text()
        self.assertIn('--check', content,
                      "install.py must support --check flag")

    def test_installs_claudekit_plugin(self):
        content = INSTALL_PY.read_text()
        self.assertIn('mrgoonie/claudekit-skills', content,
                      "install.py must install mrgoonie/claudekit-skills plugin")


# ─────────────────────────────────────────────────────────────────────────────
class TestProjectStructure(unittest.TestCase):
    """Critical files and directories exist where expected."""

    def test_required_directories_exist(self):
        dirs = [
            ROOT / 'global' / 'commands',
            ROOT / 'global',
            ROOT / 'custom' / 'skills',
            ROOT / 'custom' / 'hooks' / 'scripts',
            ROOT / 'scripts',
            ROOT / '.claude' / 'commands',
            ROOT / '.claude' / 'skills',
            ROOT / 'tests',
        ]
        for d in dirs:
            self.assertTrue(d.exists(), f"Directory missing: {d.relative_to(ROOT)}")

    def test_required_files_exist(self):
        files = [
            ROOT / 'README.md',
            ROOT / 'CLAUDE.md',
            ROOT / 'AGENTS.md',
            ROOT / 'scripts' / 'install.py',
            ROOT / 'global' / 'settings.json',
            ROOT / 'custom' / 'hooks' / 'hooks.json',
            ROOT / '.claude' / 'settings.json',
            ROOT / '.claude' / 'commands' / 'ak:sync-docs.md',
        ]
        for f in files:
            self.assertTrue(f.exists(), f"File missing: {f.relative_to(ROOT)}")

    def test_no_stray_sh_files_in_scripts(self):
        sh_files = list((ROOT / 'custom' / 'hooks' / 'scripts').glob('*.sh'))
        self.assertEqual(sh_files, [],
                         f"Unexpected .sh files in scripts/: {[f.name for f in sh_files]}")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
