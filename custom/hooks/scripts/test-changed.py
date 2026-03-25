#!/usr/bin/env python3
"""
test-changed: Find and run tests related to the changed source file.
PostToolUse — Write|Edit|MultiEdit
"""
import json
import os
import subprocess
import sys
from typing import List, Optional

SOURCE_EXTS = {'.ts', '.tsx', '.js', '.jsx', '.mjs'}


def detect_runner(root: str) -> List[str]:
    pkg = os.path.join(root, 'package.json')
    if not os.path.exists(pkg):
        return ['npm', 'test', '--']
    with open(pkg) as f:
        content = json.load(f)
    deps = {**content.get('dependencies', {}), **content.get('devDependencies', {})}
    if 'vitest' in deps:
        return ['npx', 'vitest', 'run']
    if 'jest' in deps:
        return ['npx', 'jest']
    return ['npm', 'test', '--']


def find_test_file(path: str) -> Optional[str]:
    base, ext = os.path.splitext(path)
    dirname = os.path.dirname(path)
    basename = os.path.basename(base)
    candidates = [
        f'{base}.test{ext}',
        f'{base}.spec{ext}',
        os.path.join(dirname, '__tests__', f'{basename}.test{ext}'),
        os.path.join(dirname, '__tests__', f'{basename}.spec{ext}'),
    ]
    return next((c for c in candidates if os.path.exists(c)), None)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    path = payload.get('tool_input', {}).get('file_path', '')
    if not path:
        sys.exit(0)

    _, ext = os.path.splitext(path)
    if ext.lower() not in SOURCE_EXTS:
        sys.exit(0)

    # Skip if the file itself is a test
    base = os.path.basename(path)
    if '.test.' in base or '.spec.' in base:
        sys.exit(0)

    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    test_file = find_test_file(path)

    if not test_file:
        print(f'No test file found for {path} — consider creating {os.path.splitext(path)[0]}.test{ext}', file=sys.stderr)
        sys.exit(0)

    runner = detect_runner(root)
    print(f'Running tests for {path}: {test_file}', file=sys.stderr)
    try:
        result = subprocess.run([*runner, test_file], cwd=root)
    except FileNotFoundError:
        print(f"Test runner '{runner[0]}' not found — skipping", file=sys.stderr)
        sys.exit(0)
    if result.returncode != 0:
        print(f'Tests FAILED for {path}', file=sys.stderr)
        sys.exit(2)
    print('Tests: OK', file=sys.stderr)


if __name__ == '__main__':
    main()
