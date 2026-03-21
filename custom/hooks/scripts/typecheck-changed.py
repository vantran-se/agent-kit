#!/usr/bin/env python3
"""
typecheck-changed: Run tsc --noEmit when a TypeScript file is modified.
PostToolUse — Write|Edit|MultiEdit
"""
import os
import subprocess
import sys


def main() -> None:
    path = os.environ.get('CLAUDE_TOOL_INPUT_FILE_PATH', '')
    if not path:
        sys.exit(0)

    if not path.endswith(('.ts', '.tsx')):
        sys.exit(0)

    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    if not os.path.exists(os.path.join(root, 'tsconfig.json')):
        sys.exit(0)

    print(f'Type-checking {path}...', file=sys.stderr)
    result = subprocess.run(['npx', 'tsc', '--noEmit'], cwd=root)
    if result.returncode != 0:
        print('TypeScript errors found — fix all errors above', file=sys.stderr)
        sys.exit(2)
    print('TypeScript: OK', file=sys.stderr)


if __name__ == '__main__':
    main()
