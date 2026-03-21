#!/usr/bin/env python3
"""
test-project: Run the full test suite at Stop.
Stop
"""
import json
import os
import subprocess
import sys


def detect_package_manager(root: str) -> str:
    if os.path.exists(os.path.join(root, 'pnpm-lock.yaml')):
        return 'pnpm'
    if os.path.exists(os.path.join(root, 'yarn.lock')):
        return 'yarn'
    return 'npm'


def main() -> None:
    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    pkg_path = os.path.join(root, 'package.json')

    if not os.path.exists(pkg_path):
        sys.exit(0)

    with open(pkg_path) as f:
        pkg = json.load(f)

    if 'test' not in pkg.get('scripts', {}):
        print('No test script in package.json, skipping', file=sys.stderr)
        sys.exit(0)

    pm = detect_package_manager(root)
    print('Running project test suite...', file=sys.stderr)
    try:
        result = subprocess.run([pm, 'test'], cwd=root)
    except FileNotFoundError:
        print(f"'{pm}' not found — skipping test suite", file=sys.stderr)
        sys.exit(0)
    if result.returncode != 0:
        print('Test suite FAILED — fix all failing tests above', file=sys.stderr)
        sys.exit(2)
    print('Tests: OK', file=sys.stderr)


if __name__ == '__main__':
    main()
