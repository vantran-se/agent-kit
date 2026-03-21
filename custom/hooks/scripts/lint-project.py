#!/usr/bin/env python3
"""
lint-project: Run Biome or ESLint on the entire project at Stop.
Stop
"""
import glob
import os
import subprocess
import sys


def main() -> None:
    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

    # Prefer Biome
    has_biome = os.path.exists(os.path.join(root, 'biome.json')) or \
                os.path.exists(os.path.join(root, 'biome.jsonc'))
    if has_biome:
        print('Running project-wide Biome validation...', file=sys.stderr)
        result = subprocess.run(['npx', 'biome', 'check', root], cwd=root)
        if result.returncode != 0:
            print('Biome validation FAILED', file=sys.stderr)
            sys.exit(2)
        print('Biome: OK', file=sys.stderr)
        return

    # Fall back to ESLint
    eslint_configs = (
        glob.glob(os.path.join(root, '.eslintrc*')) +
        glob.glob(os.path.join(root, 'eslint.config.*'))
    )
    if eslint_configs:
        print('Running project-wide ESLint validation...', file=sys.stderr)
        result = subprocess.run(
            ['npx', 'eslint', root, '--ext', '.ts,.tsx,.js,.jsx'],
            cwd=root,
        )
        if result.returncode != 0:
            print('ESLint validation FAILED', file=sys.stderr)
            sys.exit(2)
        print('ESLint: OK', file=sys.stderr)
        return

    print('No linter configured (biome.json / .eslintrc not found), skipping', file=sys.stderr)


if __name__ == '__main__':
    main()
