from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "validate_all.py"
SPEC = importlib.util.spec_from_file_location("validate_all", SCRIPT)
validate_all = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_all)

VALID_DESCRIPTION = "Run SiBlog blog commands safely."


def make_skill(frontmatter: str, body: str = "# Skill\n") -> Path:
    skill_dir = Path(tempfile.mkdtemp()) / "demo-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")
    return skill_dir


class SkillStructureTests(unittest.TestCase):
    def assert_valid(self, skill_dir: Path):
        self.assertIsNone(validate_all.skill_structure_error(skill_dir))

    def assert_invalid(self, skill_dir: Path, fragment: str):
        error = validate_all.skill_structure_error(skill_dir)
        self.assertIsNotNone(error)
        self.assertIn(fragment, error)

    def test_extra_frontmatter_keys_are_allowed(self):
        self.assert_valid(
            make_skill(
                f'name: demo-skill\ndescription: {VALID_DESCRIPTION}\n'
                'argument-hint: "[blog:header | blog:tilian]"\ncustom: value'
            )
        )

    def test_missing_skill_file(self):
        empty = Path(tempfile.mkdtemp())
        self.assert_invalid(empty, "SKILL.md")

    def test_missing_frontmatter(self):
        skill_dir = Path(tempfile.mkdtemp())
        (skill_dir / "SKILL.md").write_text("# no frontmatter\n", encoding="utf-8")
        self.assert_invalid(skill_dir, "frontmatter")

    def test_frontmatter_must_be_mapping(self):
        self.assert_invalid(make_skill("- a\n- b"), "dictionary")

    def test_name_and_description_required(self):
        self.assert_invalid(make_skill(f"description: {VALID_DESCRIPTION}"), "name")
        self.assert_invalid(make_skill("name: demo-skill"), "description")

    def test_name_must_be_hyphen_case(self):
        for name in ("Demo", "demo_skill", "-demo", "demo-", "demo--skill", "a" * 65):
            with self.subTest(name=name):
                self.assert_invalid(make_skill(f"name: {name}\ndescription: {VALID_DESCRIPTION}"), "Name")

    def test_description_rules(self):
        for description, fragment in (
            ("Use <tag> here", "angle brackets"),
            ("x" * 1025, "too long"),
            ("[TODO: fill]", "TODO"),
        ):
            with self.subTest(fragment=fragment):
                self.assert_invalid(make_skill(f'name: demo-skill\ndescription: "{description}"'), fragment)

    def test_todo_placeholder_outside_code_fence_is_rejected(self):
        frontmatter = f"name: demo-skill\ndescription: {VALID_DESCRIPTION}"
        self.assert_invalid(make_skill(frontmatter, "[TODO: write steps]\n"), "TODO")
        self.assert_valid(make_skill(frontmatter, "```text\n[TODO: write steps]\n```\n"))


if __name__ == "__main__":
    unittest.main()
