#!/usr/bin/env python3
"""
Test suite for all hook scripts in custom/hooks/scripts/.
Run: python3 test_hooks.py
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from typing import Dict, Optional, Tuple

SCRIPTS_DIR = Path(__file__).parent.parent / 'scripts'
PYTHON = sys.executable


def run_script(script: str, stdin_data: Optional[str] = None, env: Optional[Dict] = None) -> Tuple[int, str, str]:
    """Run a hook script, return (exit_code, stdout, stderr)."""
    full_env = {**os.environ, **(env or {})}
    result = subprocess.run(
        [PYTHON, str(SCRIPTS_DIR / script)],
        input=stdin_data,
        capture_output=True,
        text=True,
        env=full_env,
    )
    return result.returncode, result.stdout, result.stderr


def payload(tool_name: str, **tool_input) -> str:
    return json.dumps({'tool_name': tool_name, 'tool_input': tool_input})


# ─────────────────────────────────────────────────────────────────────────────
class TestFileGuard(unittest.TestCase):

    def _run(self, tool_name, env=None, **kwargs):
        return run_script('file-guard.py', stdin_data=payload(tool_name, **kwargs), env=env)

    def test_allows_normal_file(self):
        rc, out, _ = self._run('Read', file_path='/src/app.ts')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_blocks_dotenv(self):
        rc, out, _ = self._run('Read', file_path='/project/.env')
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_blocks_dotenv_local(self):
        rc, out, _ = self._run('Write', file_path='.env.local')
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_blocks_private_key(self):
        rc, out, _ = self._run('Read', file_path='/home/user/.ssh/id_rsa')
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_blocks_pem(self):
        rc, out, _ = self._run('Edit', file_path='server.pem')
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_blocks_bash_pipeline_cat_env(self):
        rc, out, _ = self._run('Bash', command='find . -name .env | xargs cat')
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_allows_bash_safe_command(self):
        rc, out, _ = self._run('Bash', command='npm run build')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_skips_unknown_tool(self):
        rc, out, _ = run_script('file-guard.py', stdin_data=payload('ListFiles'))
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_claudeignore(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, '.claudeignore').write_text('secrets/*\n')
            rc, out, _ = self._run(
                'Read',
                file_path='secrets/config.json',
                env={'CLAUDE_PROJECT_DIR': tmpdir},
            )
            data = json.loads(out)
            self.assertEqual(data['decision'], 'block')


# ─────────────────────────────────────────────────────────────────────────────
class TestCheckAnyChanged(unittest.TestCase):

    def _run(self, file_path, content=''):
        with tempfile.NamedTemporaryFile(suffix='.ts', mode='w', delete=False) as f:
            f.write(content)
            fname = f.name
        try:
            rc, out, err = run_script('check-any-changed.py', env={'CLAUDE_TOOL_INPUT_FILE_PATH': fname})
        finally:
            os.unlink(fname)
        return rc, out, err

    def test_skips_non_ts_file(self):
        rc, _, _ = run_script('check-any-changed.py', env={'CLAUDE_TOOL_INPUT_FILE_PATH': 'app.js'})
        self.assertEqual(rc, 0)

    def test_passes_clean_ts(self):
        rc, _, _ = self._run('app.ts', 'const x: string = "hello";\n')
        self.assertEqual(rc, 0)

    def test_blocks_any_type(self):
        rc, _, err = self._run('app.ts', 'function foo(x: any): any { return x; }\n')
        self.assertEqual(rc, 2)
        self.assertIn('any', err)

    def test_blocks_any_array(self):
        rc, _, err = self._run('app.ts', 'const items: any[] = [];\n')
        self.assertEqual(rc, 2)

    def test_allows_expect_any(self):
        rc, _, _ = self._run('app.ts', 'expect(fn).toBeCalledWith(expect.any(String));\n')
        self.assertEqual(rc, 0)

    def test_blocks_as_any(self):
        rc, _, err = self._run('app.ts', 'const x = foo as any;\n')
        self.assertEqual(rc, 2)


# ─────────────────────────────────────────────────────────────────────────────
class TestCheckCommentReplacement(unittest.TestCase):

    def _run(self, old_string, new_string, file_path='app.ts'):
        data = payload('Edit', old_string=old_string, new_string=new_string, file_path=file_path)
        return run_script('check-comment-replacement.py', stdin_data=data)

    def test_allows_normal_edit(self):
        rc, out, _ = self._run('const x = 1;', 'const x = 2;')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_blocks_code_replaced_with_comments(self):
        old = textwrap.dedent('''\
            function processData(items) {
                items.forEach(item => item.validate());
                return items.filter(i => i.active);
            }
        ''')
        new = textwrap.dedent('''\
            // processData function removed
            // was iterating and filtering items
            // TODO: re-implement later
        ''')
        rc, out, _ = self._run(old, new)
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_allows_adding_comments_alongside_code(self):
        old = 'function foo() { return 1; }'
        new = '// returns one\nfunction foo() { return 1; }'
        rc, out, _ = self._run(old, new)
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_allows_editing_markdown(self):
        rc, out, _ = self._run('old text', '# new header\n## subheader', file_path='README.md')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_skips_empty_old_string(self):
        rc, out, _ = self._run('', '// new comment\n// another\n')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_multiedit(self):
        data = json.dumps({
            'tool_name': 'MultiEdit',
            'tool_input': {
                'file_path': 'app.ts',
                'edits': [
                    {
                        'old_string': 'function real() { doStuff(); }',
                        'new_string': '// function real removed\n// did stuff before',
                    }
                ],
            },
        })
        rc, out, _ = run_script('check-comment-replacement.py', stdin_data=data)
        data_out = json.loads(out)
        self.assertEqual(data_out['decision'], 'block')


# ─────────────────────────────────────────────────────────────────────────────
class TestCheckUnusedParameters(unittest.TestCase):

    def _run(self, new_string, file_path='app.ts'):
        data = payload('Edit', new_string=new_string, old_string='', file_path=file_path)
        return run_script('check-unused-parameters.py', stdin_data=data)

    def test_allows_normal_function(self):
        rc, out, _ = self._run('function foo(bar: string): string { return bar; }')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_blocks_underscore_param(self):
        rc, out, _ = self._run('function foo(_bar: string): void { doSomething(); }')
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_blocks_arrow_underscore(self):
        rc, out, _ = self._run('const fn = (_x: number) => 42;')
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')

    def test_skips_non_code_file(self):
        rc, out, _ = self._run('function foo(_bar) {}', file_path='notes.md')
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_allows_dunder_methods(self):
        # Python dunder methods should not be flagged (allowlist)
        rc, out, _ = self._run('def __init__(self, value):\n    self.value = value', file_path='app.py')
        self.assertEqual(rc, 0)


# ─────────────────────────────────────────────────────────────────────────────
class TestCheckTodos(unittest.TestCase):

    def _make_transcript(self, todos: list) -> str:
        transcript = [
            {
                'role': 'assistant',
                'content': [
                    {
                        'type': 'tool_use',
                        'name': 'TodoWrite',
                        'input': {'todos': todos},
                    }
                ],
            }
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(transcript, f)
            return f.name

    def test_skips_no_transcript(self):
        rc, out, _ = run_script('check-todos.py', stdin_data=json.dumps({}))
        self.assertEqual(rc, 0)
        self.assertEqual(out.strip(), '')

    def test_passes_all_completed(self):
        path = self._make_transcript([
            {'content': 'Task A', 'status': 'completed', 'activeForm': 'Doing A'},
            {'content': 'Task B', 'status': 'completed', 'activeForm': 'Doing B'},
        ])
        try:
            rc, out, _ = run_script('check-todos.py', stdin_data=json.dumps({'transcript_path': path}))
            self.assertEqual(rc, 0)
            self.assertEqual(out.strip(), '')
        finally:
            os.unlink(path)

    def test_blocks_incomplete_todos(self):
        path = self._make_transcript([
            {'content': 'Task A', 'status': 'completed', 'activeForm': 'Doing A'},
            {'content': 'Task B', 'status': 'pending', 'activeForm': 'Doing B'},
            {'content': 'Task C', 'status': 'in_progress', 'activeForm': 'Doing C'},
        ])
        try:
            rc, out, _ = run_script('check-todos.py', stdin_data=json.dumps({'transcript_path': path}))
            data = json.loads(out)
            self.assertEqual(data['decision'], 'block')
            self.assertIn('Task B', data['reason'])
            self.assertIn('Task C', data['reason'])
            self.assertNotIn('Task A', data['reason'])
        finally:
            os.unlink(path)

    def test_skips_missing_transcript_file(self):
        rc, out, _ = run_script('check-todos.py', stdin_data=json.dumps({'transcript_path': '/nonexistent/path.json'}))
        self.assertEqual(rc, 0)


# ─────────────────────────────────────────────────────────────────────────────
class TestSelfReview(unittest.TestCase):

    def test_always_blocks(self):
        rc, out, _ = run_script('self-review.py')
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data['decision'], 'block')
        self.assertIn('self-review', data['reason'].lower())

    def test_covers_all_review_areas(self):
        _, out, _ = run_script('self-review.py')
        reason = json.loads(out)['reason']
        for keyword in ['IMPLEMENTATION', 'CODE QUALITY', 'INTEGRATION', 'CONSISTENCY']:
            self.assertIn(keyword, reason)


# ─────────────────────────────────────────────────────────────────────────────
class TestTypecheckChanged(unittest.TestCase):

    def test_skips_non_ts_file(self):
        rc, _, _ = run_script('typecheck-changed.py', env={'CLAUDE_TOOL_INPUT_FILE_PATH': 'app.py'})
        self.assertEqual(rc, 0)

    def test_skips_no_tsconfig(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc, _, _ = run_script(
                'typecheck-changed.py',
                env={
                    'CLAUDE_TOOL_INPUT_FILE_PATH': 'app.ts',
                    'CLAUDE_PROJECT_DIR': tmpdir,
                },
            )
            self.assertEqual(rc, 0)


# ─────────────────────────────────────────────────────────────────────────────
class TestTypecheckProject(unittest.TestCase):

    def test_skips_no_tsconfig(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc, _, _ = run_script('typecheck-project.py', env={'CLAUDE_PROJECT_DIR': tmpdir})
            self.assertEqual(rc, 0)


# ─────────────────────────────────────────────────────────────────────────────
class TestLintChanged(unittest.TestCase):

    def test_skips_non_supported_ext(self):
        rc, _, _ = run_script('lint-changed.py', env={'CLAUDE_TOOL_INPUT_FILE_PATH': 'main.py'})
        self.assertEqual(rc, 0)

    def test_skips_no_linter_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc, _, _ = run_script(
                'lint-changed.py',
                env={
                    'CLAUDE_TOOL_INPUT_FILE_PATH': 'app.ts',
                    'CLAUDE_PROJECT_DIR': tmpdir,
                },
            )
            self.assertEqual(rc, 0)


# ─────────────────────────────────────────────────────────────────────────────
class TestLintProject(unittest.TestCase):

    def test_skips_no_linter_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc, _, err = run_script('lint-project.py', env={'CLAUDE_PROJECT_DIR': tmpdir})
            self.assertEqual(rc, 0)
            self.assertIn('skipping', err)


# ─────────────────────────────────────────────────────────────────────────────
class TestTestChanged(unittest.TestCase):

    def test_skips_non_source_file(self):
        rc, _, _ = run_script('test-changed.py', env={'CLAUDE_TOOL_INPUT_FILE_PATH': 'README.md'})
        self.assertEqual(rc, 0)

    def test_skips_test_file_itself(self):
        rc, _, _ = run_script('test-changed.py', env={'CLAUDE_TOOL_INPUT_FILE_PATH': 'app.test.ts'})
        self.assertEqual(rc, 0)

    def test_warns_no_test_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / 'utils.ts'
            src.write_text('export const add = (a: number, b: number) => a + b;\n')
            rc, _, err = run_script(
                'test-changed.py',
                env={
                    'CLAUDE_TOOL_INPUT_FILE_PATH': str(src),
                    'CLAUDE_PROJECT_DIR': tmpdir,
                },
            )
            self.assertEqual(rc, 0)
            self.assertIn('No test file', err)

    def test_runs_test_file_when_found(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / 'utils.ts'
            test = Path(tmpdir) / 'utils.test.ts'
            src.write_text('export const x = 1;\n')
            # Write a passing fake test (just exit 0)
            test.write_text('// test\n')
            # Create package.json with vitest
            pkg = {'scripts': {'test': 'exit 0'}, 'devDependencies': {'vitest': '^1.0.0'}}
            Path(tmpdir, 'package.json').write_text(json.dumps(pkg))
            # We can't actually run vitest without install, just verify it finds the test
            rc, _, err = run_script(
                'test-changed.py',
                env={
                    'CLAUDE_TOOL_INPUT_FILE_PATH': str(src),
                    'CLAUDE_PROJECT_DIR': tmpdir,
                },
            )
            self.assertIn('utils.test.ts', err)


# ─────────────────────────────────────────────────────────────────────────────
class TestTestProject(unittest.TestCase):

    def test_skips_no_package_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            rc, _, _ = run_script('test-project.py', env={'CLAUDE_PROJECT_DIR': tmpdir})
            self.assertEqual(rc, 0)

    def test_skips_no_test_script(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'package.json').write_text(json.dumps({'scripts': {'build': 'tsc'}}))
            rc, _, err = run_script('test-project.py', env={'CLAUDE_PROJECT_DIR': tmpdir})
            self.assertEqual(rc, 0)
            self.assertIn('No test script', err)

    def test_detects_package_managers(self):
        """Verify pnpm-lock.yaml triggers pnpm detection (command may fail if pnpm not installed)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, 'package.json').write_text(json.dumps({'scripts': {'test': 'exit 0'}}))
            Path(tmpdir, 'pnpm-lock.yaml').write_text('')
            rc, _, err = run_script('test-project.py', env={'CLAUDE_PROJECT_DIR': tmpdir})
            # Any exit code is acceptable — pnpm may not be installed in test env.
            # What matters is the script runs without Python exceptions.
            self.assertNotIn('Traceback', err)


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
