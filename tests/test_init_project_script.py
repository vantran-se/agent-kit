#!/usr/bin/env python3
"""
Test the scripts/init-project.py script.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
INIT_PROJECT_PY = ROOT / 'scripts' / 'init-project.py'


class TestInitProjectScript(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir))

    def run_script(self, *args) -> dict:
        cmd = [sys.executable, str(INIT_PROJECT_PY), '--cwd', str(self.tmp_dir)] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    def test_creates_gitignore_with_gitnexus(self):
        data = self.run_script('--skip-gitnexus')
        gitignore = self.tmp_dir / '.gitignore'
        
        self.assertTrue(gitignore.exists())
        self.assertIn('.gitnexus/', gitignore.read_text())
        self.assertTrue(data['gitignore']['updated'])
        self.assertFalse(data['gitignore']['already_had_gitnexus'])

    def test_updates_existing_gitignore(self):
        gitignore = self.tmp_dir / '.gitignore'
        gitignore.write_text("node_modules/\n")
        
        data = self.run_script('--skip-gitnexus')
        
        content = gitignore.read_text()
        self.assertIn('node_modules/', content)
        self.assertIn('.gitnexus/', content)
        self.assertTrue(data['gitignore']['updated'])

    def test_recognizes_existing_gitnexus_in_gitignore(self):
        gitignore = self.tmp_dir / '.gitignore'
        gitignore.write_text(".gitnexus/\n")
        
        data = self.run_script('--skip-gitnexus')
        self.assertFalse(data['gitignore']['updated'])
        self.assertTrue(data['gitignore']['already_had_gitnexus'])

    def test_scans_existing_setup_files(self):
        # Create some files
        (self.tmp_dir / 'CLAUDE.md').write_text("test claude txt")
        (self.tmp_dir / '.claude').mkdir()
        (self.tmp_dir / '.claude' / 'settings.json').write_text('{"foo": "bar"}')
        
        data = self.run_script('--skip-gitnexus')
        
        ext = data['existing']
        self.assertTrue(ext['claude_md']['exists'])
        self.assertEqual(ext['claude_md']['content'], "test claude txt")
        
        self.assertFalse(ext['agents_md']['exists'])
        
        self.assertTrue(ext['claude_settings']['exists'])
        self.assertEqual(ext['claude_settings']['content'], {"foo": "bar"})

    def test_detects_formatter_prettier(self):
        (self.tmp_dir / '.prettierrc').write_text("{}")
        
        data = self.run_script('--skip-gitnexus')
        
        self.assertEqual(data['formatter']['detected'], "prettier")
        self.assertIn("prettier", data['formatter']['hook_command'])

    def test_detects_formatter_ruff(self):
        (self.tmp_dir / 'ruff.toml').write_text("")
        
        data = self.run_script('--skip-gitnexus')
        
        self.assertEqual(data['formatter']['detected'], "ruff")
        self.assertIn("ruff format", data['formatter']['hook_command'])

    def test_detects_formatter_from_package_json(self):
        (self.tmp_dir / 'package.json').write_text('{"devDependencies": {"eslint": "^8.0.0"}}')
        
        data = self.run_script('--skip-gitnexus')
        
        self.assertEqual(data['formatter']['detected'], "eslint")
        self.assertIn("eslint --fix", data['formatter']['hook_command'])

    def test_no_formatter_detected(self):
        data = self.run_script('--skip-gitnexus')
        self.assertIsNone(data['formatter']['detected'])
        self.assertIsNone(data['formatter']['hook_command'])

    def test_gitnexus_skipped_when_not_git_repo(self):
        data = self.run_script('--skip-gitnexus')
        self.assertFalse(data['gitnexus']['is_git_repo'])


if __name__ == '__main__':
    unittest.main()
