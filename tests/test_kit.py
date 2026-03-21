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
INSTALL_SH = ROOT / 'scripts' / 'install.sh'


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
class TestHookScripts(unittest.TestCase):
    """All Python scripts in custom/hooks/scripts/ are valid and well-formed."""

    def setUp(self):
        self.scripts = list(SCRIPTS_DIR.glob('*.py'))

    def test_scripts_directory_exists(self):
        self.assertTrue(SCRIPTS_DIR.exists())

    def test_expected_script_count(self):
        self.assertEqual(len(self.scripts), 12,
                         f"Expected 12 hook scripts, found {len(self.scripts)}: {[s.name for s in self.scripts]}")

    def test_all_scripts_are_valid_python(self):
        for script in self.scripts:
            with open(script) as f:
                source = f.read()
            try:
                ast.parse(source)
            except SyntaxError as e:
                self.fail(f"{script.name} has syntax error: {e}")

    def test_all_scripts_have_shebang(self):
        for script in self.scripts:
            first_line = script.read_text().split('\n')[0]
            self.assertTrue(first_line.startswith('#!/usr/bin/env python3'),
                            f"{script.name} missing shebang line")

    def test_all_scripts_have_main_guard(self):
        # Scripts with non-trivial logic require a main guard.
        # Simple top-level scripts (e.g. self-review.py) are exempt.
        exempt = {'self-review.py'}
        for script in self.scripts:
            if script.name in exempt:
                continue
            content = script.read_text()
            self.assertIn("if __name__ == '__main__':", content,
                          f"{script.name} missing main guard")

    def test_all_scripts_have_docstring(self):
        for script in self.scripts:
            content = script.read_text()
            self.assertIn('"""', content,
                          f"{script.name} missing docstring")

    def test_no_shell_scripts_exist(self):
        sh_files = list(SCRIPTS_DIR.glob('*.sh'))
        self.assertEqual(sh_files, [],
                         f"Shell scripts found (should be Python only): {[f.name for f in sh_files]}")

    def test_expected_scripts_exist(self):
        expected = [
            'file-guard.py', 'lint-changed.py', 'typecheck-changed.py',
            'check-any-changed.py', 'test-changed.py', 'check-comment-replacement.py',
            'check-unused-parameters.py', 'typecheck-project.py', 'lint-project.py',
            'test-project.py', 'check-todos.py', 'self-review.py',
        ]
        for name in expected:
            self.assertTrue((SCRIPTS_DIR / name).exists(), f"Missing script: {name}")

    def test_no_python_310_only_syntax(self):
        """Ensure scripts use Optional/List from typing, not X | Y union syntax."""
        union_pattern = re.compile(r'\bdef \w+\([^)]*\) -> \w+ \| \w+')
        param_union = re.compile(r':\s+\w+\s+\|\s+\w+')
        for script in self.scripts:
            content = script.read_text()
            # Allow 'X | Y' only if typing imports are present for compat
            if union_pattern.search(content) or param_union.search(content):
                self.assertIn('from typing import', content,
                              f"{script.name} uses X|Y union syntax without typing import (Python 3.10+ only)")


# ─────────────────────────────────────────────────────────────────────────────
class TestSkills(unittest.TestCase):
    """custom/skills/ — each skill has valid SKILL.md with required frontmatter."""

    EXPECTED_SKILLS = {'docx', 'frontend-design', 'internal-comms', 'pdf', 'pptx', 'xlsx'}

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

    EXPECTED_COMMANDS = {'init-project.md', 'setup-skills.md', 'setup-custom.md'}

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
        self.assertIn('/sync-docs', self.claude_md,
                      "CLAUDE.md must mention /sync-docs rule")

    def test_python_requirement_in_readme(self):
        self.assertIn('Python', self.readme,
                      "README.md must mention Python requirement (for hook scripts)")

    def test_script_count_in_claude_md(self):
        actual = len(list(SCRIPTS_DIR.glob('*.py')))
        self.assertIn(str(actual), self.claude_md,
                      f"CLAUDE.md should mention script count ({actual} files)")

    def test_hook_names_in_claude_md(self):
        """All hook names must appear in CLAUDE.md hooks list."""
        for h in self.hooks:
            self.assertIn(h['name'], self.claude_md,
                          f"CLAUDE.md hooks list missing: {h['name']}")


# ─────────────────────────────────────────────────────────────────────────────
class TestInstallScript(unittest.TestCase):
    """scripts/install.sh — exists, is executable, and contains key install targets."""

    def test_install_sh_exists(self):
        self.assertTrue(INSTALL_SH.exists())

    def test_install_sh_is_executable(self):
        self.assertTrue(os.access(INSTALL_SH, os.X_OK),
                        "install.sh is not executable")

    def test_install_sh_is_valid_bash(self):
        result = subprocess.run(['bash', '-n', str(INSTALL_SH)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0,
                         f"install.sh has syntax errors: {result.stderr}")

    def test_installs_agent_kit_path(self):
        content = INSTALL_SH.read_text()
        self.assertIn('agent-kit-path', content,
                      "install.sh must save agent-kit-path")

    def test_installs_global_commands(self):
        content = INSTALL_SH.read_text()
        # install.sh uses a variable for the path, check the variable assignment
        self.assertTrue(
            '~/.claude/commands' in content or 'CLAUDE_COMMANDS_DIR' in content,
            "install.sh must reference ~/.claude/commands or a variable for it"
        )

    def test_installs_mcp_servers(self):
        content = INSTALL_SH.read_text()
        self.assertIn('mcpServers', content,
                      "install.sh must configure mcpServers")

    def test_supports_check_flag(self):
        content = INSTALL_SH.read_text()
        self.assertIn('--check', content,
                      "install.sh must support --check flag")


# ─────────────────────────────────────────────────────────────────────────────
class TestProjectStructure(unittest.TestCase):
    """Critical files and directories exist where expected."""

    def test_required_directories_exist(self):
        dirs = [
            ROOT / 'global' / 'commands',
            ROOT / 'global',
            ROOT / 'custom' / 'skills',
            ROOT / 'custom' / 'hooks' / 'scripts',
            ROOT / 'custom' / 'hooks' / 'tests',
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
            ROOT / 'scripts' / 'install.sh',
            ROOT / 'global' / 'settings.json',
            ROOT / 'custom' / 'hooks' / 'hooks.json',
            ROOT / '.claude' / 'settings.json',
            ROOT / '.claude' / 'commands' / 'sync-docs.md',
        ]
        for f in files:
            self.assertTrue(f.exists(), f"File missing: {f.relative_to(ROOT)}")

    def test_no_stray_sh_files_in_scripts(self):
        sh_files = list((ROOT / 'custom' / 'hooks' / 'scripts').glob('*.sh'))
        self.assertEqual(sh_files, [],
                         f"Unexpected .sh files in scripts/: {[f.name for f in sh_files]}")

    def test_test_files_in_correct_location(self):
        self.assertTrue((ROOT / 'custom' / 'hooks' / 'tests' / 'test_hooks.py').exists())
        self.assertTrue((ROOT / 'tests' / 'test_kit.py').exists())
        # test_hooks.py must NOT be in scripts/
        self.assertFalse((ROOT / 'custom' / 'hooks' / 'scripts' / 'test_hooks.py').exists(),
                         "test_hooks.py should not be in scripts/ directory")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
