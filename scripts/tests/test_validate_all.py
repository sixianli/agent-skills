from __future__ import annotations

import importlib.util
import json
import subprocess
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
    entry = {"name": "demo-skill", "skill_dir": "demo-skill"}
    (repo_root / "skills.json").write_text(
        json.dumps({"skills": [entry]}), encoding="utf-8"
    )
    subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "add", "--", "skills.json", "demo-skill"],
        cwd=repo_root,
        check=True,
    )
    return entry


def make_harness_repo(
    repo_root: Path,
    files: dict[str, str],
    *,
    harness_files: object = None,
) -> dict:
    skill_dir = repo_root / "demo-skill"
    entry = {"name": "demo-skill", "skill_dir": "demo-skill"}
    if harness_files is not None:
        entry["harness_files"] = harness_files
    tracked_paths = ["skills.json"]
    for relative_path, content in files.items():
        path = skill_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        tracked_paths.append(f"demo-skill/{relative_path}")
    (repo_root / "skills.json").write_text(
        json.dumps({"skills": [entry]}), encoding="utf-8"
    )
    subprocess.run(["git", "init", "--quiet"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "add", "--", *tracked_paths], cwd=repo_root, check=True
    )
    return entry


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

    def test_agent_name_outside_agent_section_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": (
                        "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        "## Install\n~/.codex/hooks.json\n"
                    )
                },
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn("demo-skill/SKILL.md:6:", errors[0])
            self.assertIn("~/.codex", errors[0])

    def test_agent_name_under_agent_heading_passes(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": (
                        "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        "### In Codex\n~/.codex/hooks.json\nClaude Code\n"
                    )
                },
            )
            self.assertEqual(
                validate_all.harness_wording_errors(entry, repo_root), []
            )
            outside_root = repo_root / "outside"
            outside_root.mkdir()
            outside_entry = make_harness_repo(
                outside_root,
                {
                    "SKILL.md": (
                        "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        "## Install\nClaude Code\n"
                    )
                },
            )
            errors = validate_all.harness_wording_errors(
                outside_entry, outside_root
            )
            self.assertEqual(len(errors), 1)
            self.assertIn("Claude Code", errors[0])

    def test_unregistered_script_naming_an_agent_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n",
                    "scripts/run.py": 'os.environ["CODEX_THREAD_ID"]\n',
                },
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn("demo-skill/scripts/run.py:1:", errors[0])
            self.assertIn("CODEX_THREAD_ID", errors[0])
            entry["harness_files"] = {"scripts/run.py": ["codex"]}
            self.assertEqual(
                validate_all.harness_wording_errors(entry, repo_root), []
            )

    def test_registered_file_naming_another_agent_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n",
                    "tests/e2e.py": "opencode run\n",
                },
                harness_files={"tests/e2e.py": ["codex"]},
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn("opencode", errors[0])
            self.assertIn("demo-skill/tests/e2e.py:1:", errors[0])

    def test_registered_file_that_does_not_exist_is_reported(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {"SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n"},
                harness_files={"tests/missing.py": ["codex"]},
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn("tests/missing.py", errors[0])

    def test_harness_file_registrations_must_have_valid_agents(self):
        invalid_values = (
            [],
            {"tests/e2e.py": []},
            {"tests/e2e.py": "codex"},
            {"tests/e2e.py": ["vscode"]},
        )
        for harness_files in invalid_values:
            with (
                self.subTest(harness_files=harness_files),
                tempfile.TemporaryDirectory() as root,
            ):
                repo_root = Path(root)
                entry = make_harness_repo(
                    repo_root,
                    {
                        "SKILL.md": (
                            "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        ),
                        "tests/e2e.py": "codex\n",
                    },
                    harness_files=harness_files,
                )
                errors = validate_all.harness_wording_errors(entry, repo_root)
                self.assertTrue(errors)
                self.assertIn("harness_files", errors[0])

    def test_neutral_skill_name_with_harness_prefix_is_allowed(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": (
                        "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        "codex-orchestration pstack-codex\n"
                    )
                },
            )
            self.assertEqual(
                validate_all.harness_wording_errors(entry, repo_root), []
            )

    def test_ignored_and_untracked_files_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n",
                    ".gitignore": "tests/ignored.py\n",
                },
            )
            tests_dir = repo_root / "demo-skill" / "tests"
            tests_dir.mkdir()
            (tests_dir / "ignored.py").write_text("opencode run\n", encoding="utf-8")
            (tests_dir / "untracked.py").write_text("Codex\n", encoding="utf-8")
            self.assertEqual(
                validate_all.harness_wording_errors(entry, repo_root), []
            )

    def test_binary_files_are_not_scanned(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n",
                    "tests/run.py": 'os.environ["CODEX_THREAD_ID"]\n',
                },
            )
            binary_path = repo_root / "demo-skill" / "tests" / "fixture.dat"
            binary_path.parent.mkdir(exist_ok=True)
            binary_path.write_bytes(b"\x00CODEX_THREAD_ID\xff")
            subprocess.run(
                ["git", "add", "--", "demo-skill/tests/fixture.dat"],
                cwd=repo_root,
                check=True,
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn("demo-skill/tests/run.py:1:", errors[0])

    def test_shared_agent_directory_allows_either_registered_agent(self):
        for agent in ("codex", "opencode"):
            with (
                self.subTest(agent=agent),
                tempfile.TemporaryDirectory() as root,
            ):
                repo_root = Path(root)
                entry = make_harness_repo(
                    repo_root,
                    {
                        "SKILL.md": (
                            "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        ),
                        "tests/e2e.py": ".agents/skills/demo-skill\n",
                    },
                    harness_files={"tests/e2e.py": [agent]},
                )
                self.assertEqual(
                    validate_all.harness_wording_errors(entry, repo_root), []
                )
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n",
                    "tests/e2e.py": ".agents/skills/demo-skill\n",
                },
                harness_files={"tests/e2e.py": ["claude-code"]},
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 1)
            self.assertIn(".agents/skills", errors[0])

    def test_headings_inside_code_fences_do_not_allow_agent_names(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": (
                        "---\nname: demo-skill\ndescription: Demo.\n---\n"
                        "```markdown\n### In Codex\n```\n~/.codex/hooks.json\n"
                    )
                },
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 2)
            self.assertTrue(
                any(
                    "SKILL.md:6:" in error and "Codex" in error for error in errors
                )
            )
            self.assertTrue(
                any(
                    "SKILL.md:8:" in error and "~/.codex" in error
                    for error in errors
                )
            )

    def test_frontmatter_does_not_supply_agent_section_heading(self):
        with tempfile.TemporaryDirectory() as root:
            repo_root = Path(root)
            entry = make_harness_repo(
                repo_root,
                {
                    "SKILL.md": (
                        "---\nname: demo-skill\ndescription: Demo.\n"
                        "# Codex\nexample: ~/.codex/hooks.json\n---\n"
                    )
                },
            )
            errors = validate_all.harness_wording_errors(entry, repo_root)
            self.assertEqual(len(errors), 2)
            self.assertTrue(
                any(
                    "SKILL.md:4:" in error and "Codex" in error for error in errors
                )
            )
            self.assertTrue(
                any(
                    "SKILL.md:5:" in error and "~/.codex" in error
                    for error in errors
                )
            )


if __name__ == "__main__":
    unittest.main()
