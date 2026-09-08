"""Observable resource resolution and decision-log behavior."""
import csv
import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('shoshin_validation', ROOT / 'scripts/validate-skills.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
VALIDATOR = Path(os.environ.get('CODEX_SKILL_VALIDATOR', str(Path.home() / '.codex/skills/.system/skill-creator/scripts/quick_validate.py')))
QUICK = module.load_validator(VALIDATOR)


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def skill(self, folder, body='', name=None):
        path = self.root / folder
        path.mkdir()
        (path / 'SKILL.md').write_text(f'---\nname: {name or folder}\ndescription: A concrete useful task\n---\n{body}\n')
        return path

    def errors(self, external=None):
        return module.validate(self.root, QUICK, external)

    def test_resources_and_sections(self):
        a = self.skill('alpha', '[method](references/method.md#naïve-method)')
        (a / 'references').mkdir()
        target = a / 'references/method.md'
        target.write_text('# naïve-method\n')
        self.assertEqual(self.errors(), [])
        target.write_text('# Renamed\n')
        self.assertTrue(any('missing section' in e for e in self.errors()))
        target.unlink()
        self.assertTrue(any('missing resource' in e for e in self.errors()))

    def test_dependency_can_be_discovered_elsewhere(self):
        self.skill('alpha', '[beta](../beta/SKILL.md)')
        self.assertTrue(any('missing skill dependency beta' in e for e in self.errors()))
        with tempfile.TemporaryDirectory() as d:
            beta = Path(d) / 'unrelated-location'
            beta.mkdir()
            (beta / 'SKILL.md').write_text('---\nname: beta\ndescription: External capability\n---\n# Beta\n')
            self.assertEqual(self.errors([beta]), [])

    def test_duplicate_names_and_directory_mismatch(self):
        self.skill('alpha')
        self.skill('beta', name='alpha')
        errors = self.errors()
        self.assertTrue(any('Duplicate skill name' in e for e in errors))
        self.assertTrue(any('name does not match' in e for e in errors))

    def test_owner_escape_and_absolute_reference(self):
        self.skill('alpha', '[outside](../../anything.md)\n[local](/machine/only.md)')
        self.assertTrue(self.errors())

    def test_fenced_examples_are_not_dependencies(self):
        self.skill('alpha', '```md\n[x](missing.md)\n```\n[external](https://example.com/docs)')
        self.assertEqual(self.errors(), [])

    def test_symlink_cannot_escape_owner(self):
        a = self.skill('alpha', '[outside](leak.md)')
        (self.root / 'outside.md').write_text('# Outside\n')
        (a / 'leak.md').symlink_to(self.root / 'outside.md')
        self.assertTrue(any('escapes owner' in e for e in self.errors()))

    def test_reference_style_links_are_checked(self):
        a = self.skill('alpha', '[method][guide]\n\n[guide]: missing.md')
        self.assertTrue(any('missing resource' in e for e in self.errors()))
        (a / 'missing.md').write_text('# Valid\n')
        self.assertEqual(self.errors(), [])
        (a / 'SKILL.md').write_text('---\nname: alpha\ndescription: A concrete task\n---\n[method][unknown]\n')
        self.assertTrue(any('undefined reference' in e for e in self.errors()))

    def test_excluded_dependency_cannot_be_restored_by_discovery(self):
        self.skill("alpha", "[review](../arena/SKILL.md)")
        self.assertTrue(any("excluded skill dependency" in e for e in self.errors()))

    def test_deferred_skill_is_not_a_runtime_entry(self):
        self.skill("arena")
        self.assertTrue(any("excluded or deferred" in e for e in self.errors()))

    def test_invalid_frontmatter_is_reported(self):
        a = self.skill('alpha')
        (a / 'SKILL.md').write_text('no frontmatter')
        self.assertTrue(any('frontmatter' in e for e in self.errors()))


class LogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'sub' / 'decisions.tsv'
        self.script = ROOT / 'skills/show-me-your-work/scripts/log.sh'

    def run_log(self, *cells):
        return subprocess.run(['bash', str(self.script), str(self.path), *cells], capture_output=True, text=True, check=False)

    def test_first_write_and_append(self):
        self.assertEqual(self.run_log('p1', 'choice ✓', 'reason', 'artifact.txt', 'verified').returncode, 0)
        self.assertEqual(self.run_log('p2', 'correct the previous row', 'new evidence', 'other.txt', 'open').returncode, 0)
        rows = list(csv.reader(self.path.read_text().splitlines(), delimiter='\t'))
        self.assertEqual(rows[0], ['ts', 'phase', 'decision', 'why', 'evidence', 'result'])
        self.assertEqual(rows[1][1:], ['p1', 'choice ✓', 'reason', 'artifact.txt', 'verified'])
        self.assertEqual(rows[2][1:], ['p2', 'correct the previous row', 'new evidence', 'other.txt', 'open'])
        self.assertRegex(rows[1][0], r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

    def test_controls_and_formula_prefixes(self):
        self.assertEqual(self.run_log('=1', '+1', '-1', '@SUM(1)', '\t =1\nnext\rline').returncode, 0)
        rows = list(csv.reader(self.path.read_text().splitlines(), delimiter='\t'))
        self.assertEqual(rows[1][1:], ["'=1", "'+1", "'-1", "'@SUM(1)", "'  =1 next line"])

    def test_bad_arguments_do_not_create_file(self):
        self.assertNotEqual(self.run_log('only-one').returncode, 0)
        self.assertFalse(self.path.exists())

    def test_invalid_existing_header_is_not_modified(self):
        self.path.parent.mkdir()
        self.path.write_text('user data\n')
        self.assertNotEqual(self.run_log('a', 'b', 'c', 'd', 'e').returncode, 0)
        self.assertEqual(self.path.read_text(), 'user data\n')

    def test_empty_file_gets_header(self):
        self.path.parent.mkdir()
        self.path.touch()
        self.assertEqual(self.run_log('a', 'b', 'c', 'd', 'e').returncode, 0)
        self.assertEqual(len(self.path.read_text().splitlines()), 2)

    def test_quotes_round_trip(self):
        self.assertEqual(self.run_log('phase', '"quoted"', '"', 'a"b', 'done').returncode, 0)
        rows = list(csv.reader(self.path.read_text().splitlines(), delimiter='\t'))
        self.assertEqual(rows[1][1:], ['phase', '"quoted"', '"', 'a"b', 'done'])

    def test_missing_final_newline_keeps_rows_separate(self):
        self.path.parent.mkdir()
        self.path.write_text('ts\tphase\tdecision\twhy\tevidence\tresult')
        self.assertEqual(self.run_log('a', 'b', 'c', 'd', 'e').returncode, 0)
        rows = list(csv.reader(self.path.read_text().splitlines(), delimiter='\t'))
        self.assertEqual(rows[0], ['ts', 'phase', 'decision', 'why', 'evidence', 'result'])
        self.assertEqual(rows[1][1:], ['a', 'b', 'c', 'd', 'e'])

    def test_write_failure_is_visible(self):
        self.path.mkdir(parents=True)
        self.assertNotEqual(self.run_log('a', 'b', 'c', 'd', 'e').returncode, 0)


if __name__ == '__main__':
    unittest.main()
