#!/usr/bin/env python3
"""
lint-changed: Run Biome or ESLint on the changed file after every edit.
PostToolUse — Write|Edit|MultiEdit
"""
import glob
import os
import subprocess
import sys
from typing import List

SUPPORTED_EXTS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.css', '.scss', '.vue', '.svelte'}


def run(cmd: List[str], cwd: str) -> int:
    result = subprocess.run(cmd, cwd=cwd, capture_output=False)
    return result.returncode


def main() -> None:
    path = os.environ.get('CLAUDE_TOOL_INPUT_FILE_PATH', '')
    if not path:
        sys.exit(0)

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED_EXTS:
        sys.exit(0)

    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

    # Prefer Biome
    has_biome_config = os.path.exists(os.path.join(root, 'biome.json')) or \
                       os.path.exists(os.path.join(root, 'biome.jsonc'))
    if has_biome_config:
        print(f'Running Biome on {path}...', file=sys.stderr)
        rc = run(['npx', 'biome', 'check', path], cwd=root)
        if rc != 0:
            print(f'Biome check failed for {path}', file=sys.stderr)
            sys.exit(2)
        print('Biome: OK', file=sys.stderr)
        sys.exit(0)

    # Fall back to ESLint
    eslint_configs = (
        glob.glob(os.path.join(root, '.eslintrc*')) +
        glob.glob(os.path.join(root, 'eslint.config.*'))
    )
    if eslint_configs:
        print(f'Running ESLint on {path}...', file=sys.stderr)
        rc = run(['npx', 'eslint', path], cwd=root)
        if rc != 0:
            print(f'ESLint check failed for {path}', file=sys.stderr)
            sys.exit(2)
        print('ESLint: OK', file=sys.stderr)


if __name__ == '__main__':
    main()
