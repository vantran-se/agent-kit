#!/usr/bin/env python3
"""
typecheck-project: Run tsc --noEmit on the entire project at Stop.
Stop
"""
import os
import subprocess
import sys


def main() -> None:
    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())
    if not os.path.exists(os.path.join(root, 'tsconfig.json')):
        sys.exit(0)

    print('Running project-wide TypeScript validation...', file=sys.stderr)
    result = subprocess.run(['npx', 'tsc', '--noEmit'], cwd=root)
    if result.returncode != 0:
        print('TypeScript validation FAILED — fix all errors above before stopping', file=sys.stderr)
        sys.exit(2)
    print('TypeScript: OK', file=sys.stderr)


if __name__ == '__main__':
    main()
