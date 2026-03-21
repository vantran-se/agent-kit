#!/usr/bin/env python3
"""
check-todos: Block Stop if there are incomplete TodoWrite items in the session transcript.
Receives full JSON payload on stdin.
"""
import json
import os
import sys
from typing import List, Optional


def find_latest_todos(transcript: list) -> Optional[List[dict]]:
    """Walk the transcript in reverse and return the last TodoWrite todos list."""
    for item in reversed(transcript):
        if not isinstance(item, dict):
            continue
        content = item.get('content', [])
        if isinstance(content, list):
            for block in content:
                if (
                    isinstance(block, dict)
                    and block.get('type') == 'tool_use'
                    and block.get('name') == 'TodoWrite'
                ):
                    todos = block.get('input', {}).get('todos', [])
                    if todos:
                        return todos
        # Also handle flat message structure
        if item.get('role') == 'assistant' and isinstance(content, str):
            continue
    return None


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    transcript_path = payload.get('transcript_path', '')
    if not transcript_path or not os.path.exists(transcript_path):
        sys.exit(0)

    try:
        with open(transcript_path) as f:
            transcript = json.load(f)
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    # Support both list and {"messages": [...]} formats
    if isinstance(transcript, dict):
        transcript = transcript.get('messages', [])

    todos = find_latest_todos(transcript)
    if not todos:
        sys.exit(0)

    incomplete = [t for t in todos if t.get('status') != 'completed']
    if not incomplete:
        sys.exit(0)

    items = '\n'.join(
        f'  - [{t.get("status", "pending")}] {t.get("content", "")}'
        for t in incomplete
    )
    reason = (
        f'You have {len(incomplete)} incomplete todo item(s). '
        f'Complete all tasks before stopping:\n\n{items}\n\n'
        'Use TodoWrite to mark each task as completed as you finish them.'
    )
    print(json.dumps({'decision': 'block', 'reason': reason}))
    sys.exit(0)


if __name__ == '__main__':
    main()
