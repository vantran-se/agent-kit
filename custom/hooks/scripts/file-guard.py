#!/usr/bin/env python3
"""
file-guard: Block access to sensitive files based on hardcoded patterns + .claudeignore.
PreToolUse — Read|Edit|MultiEdit|Write|Bash
"""
import json
import os
import re
import sys
from typing import Optional

SENSITIVE_PATTERNS = [
    r'(^|/)\.env$',
    r'(^|/)\.env\.',
    r'(^|/)id_rsa$',
    r'(^|/)id_ed25519$',
    r'(^|/)id_ecdsa$',
    r'\.pem$',
    r'\.key$',
    r'\.p12$',
    r'\.pfx$',
    r'(^|/)credentials\.json$',
    r'(^|/)secrets\.(json|yaml|yml)$',
    r'\.aws/credentials$',
    r'(^|/)\.netrc$',
]


def block(reason: str) -> None:
    print(json.dumps({'decision': 'block', 'reason': reason}))
    sys.exit(0)


def is_sensitive(path: str) -> bool:
    return any(re.search(p, path, re.IGNORECASE) for p in SENSITIVE_PATTERNS)


def check_claudeignore(path: str, root: str) -> Optional[str]:
    ignore_file = os.path.join(root, '.claudeignore')
    if not os.path.exists(ignore_file):
        return None
    with open(ignore_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            pattern = re.escape(line).replace(r'\*', '.*').replace(r'\?', '.')
            if re.search(pattern, path):
                return line
    return None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = payload.get('tool_name', '')
    inp = payload.get('tool_input', {})
    root = os.environ.get('CLAUDE_PROJECT_DIR', os.getcwd())

    if tool == 'Bash':
        cmd = inp.get('command', '')
        if re.search(r'find.*\.env.*xargs.*cat|cat\s+.*\.env\b', cmd, re.IGNORECASE):
            block('Access denied: command reads a sensitive .env file via pipeline.')
        return

    if tool not in ('Read', 'Edit', 'MultiEdit', 'Write'):
        sys.exit(0)

    path = inp.get('file_path', '')
    if not path:
        sys.exit(0)

    if is_sensitive(path):
        block(f'Access denied: "{path}" matches a sensitive file pattern. Use environment variables or a secrets manager instead.')

    matched = check_claudeignore(path, root)
    if matched:
        block(f'Access denied: "{path}" is protected by .claudeignore pattern: {matched}')


if __name__ == '__main__':
    main()
