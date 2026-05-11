#!/usr/bin/env python3

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HOOKS_JSON = ROOT / "custom" / "hooks" / "hooks.json"


class TestHooks(unittest.TestCase):
    def setUp(self):
        self.hooks = json.loads(HOOKS_JSON.read_text())

    def test_hooks_json_exists(self):
        self.assertTrue(HOOKS_JSON.exists())

    def test_hooks_are_valid(self):
        self.assertIsInstance(self.hooks, list)
        self.assertGreater(len(self.hooks), 0)
        for hook in self.hooks:
            self.assertRegex(hook["name"], r"^[a-z0-9-]+$")
            self.assertIn("description", hook)
            self.assertIn("hook", hook)
            self.assertIn("event", hook["hook"])
            self.assertIn("command", hook["hook"])

    def test_dangerous_bash_patterns_present(self):
        command = next(h["hook"]["command"] for h in self.hooks if h["name"] == "block-dangerous-bash")
        self.assertIn("rm", command)
        self.assertIn("DROP", command)
        self.assertIn("--force", command)

    def test_secret_patterns_present(self):
        command = next(h["hook"]["command"] for h in self.hooks if h["name"] == "check-secrets")
        for pattern in ("sk-", "AKIA", "ghp_", "PRIVATE KEY"):
            self.assertIn(pattern, command)


if __name__ == "__main__":
    unittest.main(verbosity=2)
