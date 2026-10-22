from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "validate_all.py"
SPEC = importlib.util.spec_from_file_location("validate_all", SCRIPT)
validate_all = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_all)

VALID_DESCRIPTION = "Run Hugo blog commands safely."


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


HARNESS_ONLY_SNIPPETS = (
    ("Run ${CLAUDE_SKILL_DIR}/scripts/build.py.", "CLAUDE_SKILL_DIR"),
    ("Read CODEX_SKILL_DIR/references/notes.md.", "CODEX_SKILL_DIR"),
    ("Set allow_implicit_invocation: true.", "allow_implicit_invocation"),
    ("Set disable-model-invocation: true.", "disable-model-invocation"),
    ("Use the Skill tool to load it.", "Skill tool"),
)


def make_repo_skill(repo_root: Path, body_line: str, reference_line: str) -> dict:
    skill_dir = repo_root / "demo-skill"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Demo skill.\n---\n\n```text\n"
        f"{body_line}\n```\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "note.md").write_text(
        f"# Notes\n\n{reference_line}\n", encoding="utf-8"
    )
    return {"name": "demo-skill", "skill_dir": "demo-skill"}


class HarnessWordingTests(unittest.TestCase):
    def test_harness_only_text_is_rejected(self):
        for line, fragment in HARNESS_ONLY_SNIPPETS:
            with (
                self.subTest(fragment=fragment),
                tempfile.TemporaryDirectory() as root,
            ):
                repo_root = Path(root)
                entry = make_repo_skill(repo_root, line, line)
                errors = validate_all.harness_wording_errors(entry, repo_root)
                self.assertEqual(len(errors), 2)
                self.assertTrue(errors[0].startswith("demo-skill/SKILL.md:7: "))
                self.assertIn(f"harness-only text '{fragment}'", errors[0])
                self.assertTrue(
                    errors[0].endswith(
                        "; write it so any agent can follow it, or mark the skill "
                        'with "harness" in skills.json'
                    )
                )
                self.assertTrue(
                    errors[1].startswith("demo-skill/references/note.md:3: ")
                )
                self.assertIn(f"harness-only text '{fragment}'", errors[1])

    def test_harness_specific_skill_is_exempt(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_repo_skill(
                repo_root,
                HARNESS_ONLY_SNIPPETS[0][0],
                HARNESS_ONLY_SNIPPETS[1][0],
            )
            entry["harness"] = "claude-code"
            self.assertEqual(validate_all.harness_wording_errors(entry, repo_root), [])

    def test_unknown_harness_value_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_repo_skill(
                repo_root,
                HARNESS_ONLY_SNIPPETS[0][0],
                HARNESS_ONLY_SNIPPETS[1][0],
            )
            entry["harness"] = "vscode"
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn("vscode", errors[0])


if __name__ == "__main__":
    unittest.main()
