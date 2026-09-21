"""Source integrity and persisted forward-trial document contracts.

These tests do not emulate the model or prove implicit skill selection.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
REPO = PACKAGE.parent


class SourceContracts(unittest.TestCase):
    def test_complete_upstream_snapshot_matches_lock(self):
        lock = json.loads((PACKAGE / 'upstream-lock.json').read_text())
        source = PACKAGE / 'upstream'
        actual = {
            str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in source.rglob('*') if p.is_file()
        }
        self.assertEqual(actual, lock['files'])

    def test_interview_and_licenses_are_unmodified_upstream(self):
        source = PACKAGE / 'upstream'
        self.assertEqual(
            (REPO / 'grill-me/references/grilling.md').read_bytes(),
            (source / 'skills/productivity/grilling/SKILL.md').read_bytes(),
        )
        for name in ('grill-me', 'grill-with-docs'):
            self.assertEqual((REPO / name / 'LICENSE').read_bytes(),
                             (source / 'LICENSE').read_bytes())

    def test_packaged_runtime_references_resolve(self):
        for name in ('grill-me', 'grill-with-docs'):
            root = REPO / name
            for file in root.rglob('*.md'):
                for relative in re.findall(r'\]\(([^)]+\.md)\)', file.read_text()):
                    if not relative.startswith(('https://', 'http://')):
                        target = (file.parent / relative).resolve()
                        self.assertTrue(target.is_relative_to(root))
                        self.assertTrue(target.is_file(), f'{file}: {relative}')


class CapturedDocumentContracts(unittest.TestCase):
    def test_live_capture_is_strictly_valid(self):
        # Empty governed directories are runtime scaffolding, not tracked files.
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / 'project'
            shutil.copytree(PACKAGE / 'tests/captured-project', project)
            for relative in ('docs/adr', 'docs/execution/specs', 'docs/execution/plans',
                             'docs/archive/specs', 'docs/archive/plans',
                             'docs/archive/runbooks', 'docs/runbooks'):
                (project / relative).mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                [sys.executable, str(REPO / 'document-governance/scripts/validate_docs.py'),
                 str(project), '--strict', '--format=json'],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json.loads(result.stdout)['ok'])

    def test_supersession_keeps_original_decision_body(self):
        seed = (PACKAGE / 'tests/seed-adr.md').read_text()
        captured = (PACKAGE / 'tests/captured-project/docs/adr/0001-storage.md').read_text()
        self.assertEqual(seed.split('---', 2)[2], captured.split('---', 2)[2])


if __name__ == '__main__':
    unittest.main()
