#!/usr/bin/env python3
"""
self-review: Prompt Claude to critically self-review before stopping.
Outputs a decision:block with targeted review questions.
"""
import json
import sys

REVIEW_PROMPT = """Before stopping, perform a critical self-review. Answer each question honestly:

IMPLEMENTATION COMPLETENESS
- Did you create a mock/placeholder implementation instead of real functionality?
- Are there any "Not implemented yet", TODO, or stub comments in production code?
- Does the implementation actually do what it claims, or does it return hardcoded/fake values?
- Did you implement the full solution, or just the minimum to make tests pass?
- Did you finish what you started, or leave work half-done?

CODE QUALITY
- Did you leave the code better than you found it?
- Is there duplicated logic that should be extracted?
- Are you using different patterns than the existing codebase uses?
- Is the code more complex than it needs to be?
- Is every piece of code still serving a clear purpose?

INTEGRATION & REFACTORING
- Did you just add code on top without integrating it properly with existing code?
- Does the change integrate correctly with all consumers and callers?
- Should you extract new functionality into cleaner abstractions?
- Did you leave temporary workarounds or hacks?
- Did you check for breaking changes in interfaces and exports?

CODEBASE CONSISTENCY
- Should other parts of the codebase be updated to match your improvements?
- Did you update all places that depend on what you changed?
- Are there related files that need the same changes?
- Are you following the same patterns used elsewhere in the codebase?

If all answers are satisfactory, proceed. If not, fix the issues before stopping."""

print(json.dumps({'decision': 'block', 'reason': REVIEW_PROMPT}))
sys.exit(0)
