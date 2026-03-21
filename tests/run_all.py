#!/usr/bin/env python3
"""
Run all Agent Kit test suites in one command.

Usage: python3 tests/run_all.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SUITES = [
    ROOT / 'tests' / 'test_kit.py',
    ROOT / 'custom' / 'hooks' / 'tests' / 'test_hooks.py',
]


def main() -> None:
    total_failed = 0
    results = []

    for suite in SUITES:
        label = suite.relative_to(ROOT)
        print(f'\n{"─" * 60}')
        print(f'Running: {label}')
        print('─' * 60)
        result = subprocess.run([sys.executable, str(suite)])
        passed = result.returncode == 0
        results.append((label, passed))
        if not passed:
            total_failed += 1

    print(f'\n{"═" * 60}')
    for label, passed in results:
        status = '✓ PASS' if passed else '✗ FAIL'
        print(f'  {status}  {label}')
    print('═' * 60)

    if total_failed:
        print(f'\n{total_failed} suite(s) failed.')
        sys.exit(1)
    print(f'\nAll {len(SUITES)} suites passed.')


if __name__ == '__main__':
    main()
