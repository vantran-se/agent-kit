#!/usr/bin/env python3
"""
check-comment-replacement: Block edits that replace real code with explanatory comments.
Receives full JSON payload on stdin.
"""
import json
import re
import sys
from typing import Optional


COMMENT_PATTERNS = [
    re.compile(r'^\s*//'),          # JS/TS // comment
    re.compile(r'^\s*/\*.*\*/\s*$'),# JS/TS /* inline block */
    re.compile(r'^\s*#(?!#)'),      # Python/bash # comment (not ## markdown headers)
    re.compile(r'^\s*--'),          # SQL/Lua -- comment
    re.compile(r'^\s*\*\s'),        # Block comment continuation * text
    re.compile(r'^\s*<!--.*-->\s*$'),# HTML <!-- comment -->
]

SKIP_EXTENSIONS = {'.md', '.txt', '.rst', '.json', '.yaml', '.yml', '.toml', '.lock'}


def is_comment_line(line: str) -> bool:
    return any(p.match(line) for p in COMMENT_PATTERNS)


def non_empty_lines(text: str) -> list[str]:
    return [l for l in text.split('\n') if l.strip()]


def is_mostly_comments(text: str) -> bool:
    lines = non_empty_lines(text)
    if len(lines) < 2:
        return False
    comment_count = sum(1 for l in lines if is_comment_line(l))
    return comment_count / len(lines) >= 0.6


def has_real_code(text: str) -> bool:
    """Returns True if text contains non-comment, non-empty lines."""
    lines = non_empty_lines(text)
    return any(not is_comment_line(l) for l in lines)


def check_replacement(old_string: str, new_string: str, file_path: str) -> Optional[str]:
    # Skip non-code files
    if any(file_path.endswith(ext) for ext in SKIP_EXTENSIONS):
        return None
    # The old string must have real code (not just comments)
    if not has_real_code(old_string):
        return None
    # The new string must be mostly comments
    if not is_mostly_comments(new_string):
        return None
    return file_path or '(unknown file)'


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = payload.get('tool_name', '')
    inp = payload.get('tool_input', {})

    edits = []
    if tool == 'Edit':
        edits.append((
            inp.get('old_string', ''),
            inp.get('new_string', ''),
            inp.get('file_path', ''),
        ))
    elif tool == 'MultiEdit':
        fp = inp.get('file_path', '')
        for edit in inp.get('edits', []):
            edits.append((edit.get('old_string', ''), edit.get('new_string', ''), fp))

    violations = []
    for old, new, fp in edits:
        result = check_replacement(old, new, fp)
        if result:
            violations.append(result)

    if violations:
        files = ', '.join(violations)
        reason = (
            f'Code replaced with comments detected in: {files}\n\n'
            'Do not replace working code with explanatory comments:\n'
            '  - If code is removed, delete it completely\n'
            '  - If code should stay, keep it and add comments alongside it\n'
            '  - Use git commit messages to document why code was removed'
        )
        print(json.dumps({'decision': 'block', 'reason': reason}))

    sys.exit(0)


if __name__ == '__main__':
    main()
