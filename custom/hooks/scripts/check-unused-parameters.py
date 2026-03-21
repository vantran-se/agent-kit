#!/usr/bin/env python3
"""
check-unused-parameters: Detect lazy refactoring where parameters are prefixed with _
instead of being properly removed.
Receives full JSON payload on stdin.
"""
import json
import re
import sys


CODE_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.py', '.go', '.rs', '.java', '.kt'}

# Patterns that indicate underscore-prefixed params in function signatures
PATTERNS = [
    re.compile(r'function\s+\w*\s*\([^)]*\b_\w+[^)]*\)'),   # function foo(_bar)
    re.compile(r'\([^)]*\b_\w+[^)]*\)\s*=>'),                # (_bar) =>
    re.compile(r'\b_\w+\s*=>'),                               # _bar =>
    re.compile(r'constructor\s*\([^)]*\b_\w+[^)]*\)'),        # constructor(_bar)
    re.compile(r'(?:async\s+)?(?:static\s+)?(?:public\s+|private\s+|protected\s+)?\w+\s*\([^)]*\b_\w+[^)]*\)', re.MULTILINE),
]

# Allow common legitimate underscore patterns
ALLOWLIST = re.compile(r'\b__(init|str|repr|len|eq|hash|new|del|enter|exit|call|iter|next)__\b')


def has_underscore_params(text: str) -> list[str]:
    if ALLOWLIST.search(text):
        return []
    matches = []
    for pattern in PATTERNS:
        for m in pattern.finditer(text):
            snippet = m.group(0).strip()[:120]
            matches.append(snippet)
    return matches


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = payload.get('tool_name', '')
    inp = payload.get('tool_input', {})
    fp = inp.get('file_path', '')

    if not any(fp.endswith(ext) for ext in CODE_EXTENSIONS):
        sys.exit(0)

    new_strings = []
    if tool == 'Edit':
        ns = inp.get('new_string', '')
        if ns:
            new_strings.append(ns)
    elif tool == 'MultiEdit':
        for edit in inp.get('edits', []):
            ns = edit.get('new_string', '')
            if ns:
                new_strings.append(ns)

    violations = []
    for text in new_strings:
        violations.extend(has_underscore_params(text))

    if violations:
        examples = '\n'.join(f'  {v}' for v in violations[:5])
        reason = (
            f'Underscore-prefixed parameter(s) detected in {fp}:\n{examples}\n\n'
            'Prefixing with _ is a convention for "intentionally unused" but signals incomplete refactoring.\n'
            '  - Remove the parameter entirely from the function signature\n'
            '  - Update all call sites to not pass that argument\n'
            '  - If the parameter is needed, give it a meaningful name'
        )
        print(json.dumps({'decision': 'block', 'reason': reason}))

    sys.exit(0)


if __name__ == '__main__':
    main()
