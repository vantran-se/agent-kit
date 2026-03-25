#!/usr/bin/env python3
"""
check-any-changed: Forbid explicit `any` types in changed TypeScript files.
PostToolUse — Write|Edit|MultiEdit
"""
import json
import os
import re
import sys

# Matches explicit any: `: any`, `: any[]`, `<any>`, `as any`
ANY_PATTERN = re.compile(r':\s*any\b|:\s*any\[\]|<any>|\bas\s+any\b')
# Allowed: jest matchers like expect.any( or .any(
ALLOWED_PATTERN = re.compile(r'expect\.any\(|\.any\(')


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    path = payload.get('tool_input', {}).get('file_path', '')
    if not path or not path.endswith(('.ts', '.tsx')):
        sys.exit(0)
    if not os.path.exists(path):
        sys.exit(0)

    with open(path) as f:
        lines = f.readlines()

    violations = []
    for i, line in enumerate(lines, 1):
        if ANY_PATTERN.search(line) and not ALLOWED_PATTERN.search(line):
            violations.append(f'  line {i}: {line.rstrip()}')

    if violations:
        print(f"WARNING: Explicit 'any' type in {path} — use proper TypeScript types:", file=sys.stderr)
        print('\n'.join(violations), file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
