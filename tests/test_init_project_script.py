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

    def test_creates_gitignore_with_graphify(self):
        data = self.run_script()
        gitignore = self.tmp_dir / '.gitignore'

        self.assertTrue(gitignore.exists())
        self.assertIn('graphify-out/', gitignore.read_text())
        self.assertTrue(data['gitignore']['updated'])
        self.assertFalse(data['gitignore']['already_had_entries'])

    def test_updates_existing_gitignore(self):
        gitignore = self.tmp_dir / '.gitignore'
        gitignore.write_text("node_modules/\n")

        data = self.run_script()

        content = gitignore.read_text()
        self.assertIn('node_modules/', content)
        self.assertIn('graphify-out/', content)
        self.assertTrue(data['gitignore']['updated'])

    def test_recognizes_existing_graphify_in_gitignore(self):
        gitignore = self.tmp_dir / '.gitignore'
        gitignore.write_text("graphify-out/\n")

        data = self.run_script()
        self.assertFalse(data['gitignore']['updated'])
        self.assertTrue(data['gitignore']['already_had_entries'])

    def test_scans_existing_setup_files(self):
        # Create some files
        (self.tmp_dir / 'CLAUDE.md').write_text("test claude txt")
        (self.tmp_dir / '.claude').mkdir()
        (self.tmp_dir / '.claude' / 'settings.json').write_text('{"foo": "bar"}')

        data = self.run_script()

        ext = data['existing']
        self.assertTrue(ext['claude_md']['exists'])
        self.assertEqual(ext['claude_md']['content'], "test claude txt")

        self.assertFalse(ext['agents_md']['exists'])

        self.assertTrue(ext['claude_settings']['exists'])
        self.assertEqual(ext['claude_settings']['content'], {"foo": "bar"})


if __name__ == '__main__':
    unittest.main()
