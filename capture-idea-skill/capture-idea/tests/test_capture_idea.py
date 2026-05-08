"""capture_idea.py 确定性逻辑测试。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_script = Path(__file__).resolve().parent.parent / "scripts" / "capture_idea.py"
_spec = importlib.util.spec_from_file_location("capture_idea", _script)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["capture_idea"] = _mod
_spec.loader.exec_module(_mod)

find_target_project_root = getattr(_mod, "find_target_project_root", None)
slugify = _mod.slugify
normalize_quotes = _mod.normalize_quotes
render_idea_markdown = _mod.render_idea_markdown
ensure_index_file = _mod.ensure_index_file
resolve_unique_path = _mod.resolve_unique_path
append_index_row = _mod.append_index_row
IdeaCapture = _mod.IdeaCapture
INDEX_HEADER = _mod.INDEX_HEADER


# ---------------------------------------------------------------------------
# target project root
# ---------------------------------------------------------------------------

class TestFindTargetProjectRoot:
    def test_find_target_project_root_from_nested_git_directory(self, tmp_path):
        project_root = tmp_path / "workspace" / "demo-project"
        nested_dir = project_root / "src" / "feature"
        (project_root / ".git").mkdir(parents=True)
        nested_dir.mkdir(parents=True)

        assert find_target_project_root is not None
        assert find_target_project_root(nested_dir) == project_root

    def test_find_target_project_root_falls_back_to_start_when_git_missing(self, tmp_path):
        start = tmp_path / "notes" / "scratch"
        start.mkdir(parents=True)

        assert find_target_project_root is not None
        assert find_target_project_root(start) == start.resolve()


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------

class TestSlugify:
    def test_basic_english(self):
        assert slugify("Eval First RAG Tuning") == "eval-first-rag-tuning"

    def test_max_words(self):
        assert slugify("one two three four five six seven") == "one-two-three-four-five"

    def test_punctuation_stripped(self):
        assert slugify("Hello, World! How's it?") == "hello-world-how-s-it"

    def test_chinese_characters(self):
        result = slugify("认知分层模型设计")
        assert result  # should produce a non-empty slug
        assert " " not in result
        assert all(c.isalnum() or c == "-" or ord(c) > 127 for c in result)

    def test_mixed_chinese_english(self):
        result = slugify("profile 分层设计 v2")
        assert "profile" in result
        assert "-" in result

    def test_empty_string(self):
        assert slugify("") == "untitled-idea"

    def test_only_punctuation(self):
        assert slugify("!!!???...") == "untitled-idea"


# ---------------------------------------------------------------------------
# normalize_quotes
# ---------------------------------------------------------------------------

class TestNormalizeQuotes:
    def test_keeps_up_to_three(self):
        assert len(normalize_quotes(["a", "b", "c", "d"])) == 3

    def test_filters_empty(self):
        assert normalize_quotes(["a", "", "  ", "b"]) == ["a", "b"]

    def test_preserves_order(self):
        assert normalize_quotes(["first", "second"]) == ["first", "second"]


# ---------------------------------------------------------------------------
# resolve_unique_path
# ---------------------------------------------------------------------------

class TestResolveUniquePath:
    def test_no_collision(self, tmp_path):
        p = resolve_unique_path(tmp_path, "2026-04-14-test")
        assert p.name == "2026-04-14-test.md"

    def test_collision_increments(self, tmp_path):
        (tmp_path / "2026-04-14-test.md").touch()
        p = resolve_unique_path(tmp_path, "2026-04-14-test")
        assert p.name == "2026-04-14-test-2.md"

    def test_multiple_collisions(self, tmp_path):
        (tmp_path / "2026-04-14-test.md").touch()
        (tmp_path / "2026-04-14-test-2.md").touch()
        p = resolve_unique_path(tmp_path, "2026-04-14-test")
        assert p.name == "2026-04-14-test-3.md"


# ---------------------------------------------------------------------------
# ensure_index_file
# ---------------------------------------------------------------------------

class TestEnsureIndexFile:
    def test_creates_new_index(self, tmp_path):
        index = ensure_index_file(tmp_path)
        assert index.exists()
        content = index.read_text()
        assert "| Date |" in content

    def test_preserves_existing_rows(self, tmp_path):
        index_path = tmp_path / "INDEX.md"
        existing = INDEX_HEADER + "| 2026-01-01 | proj | Title | captured | [T](t.md) |\n"
        index_path.write_text(existing)
        ensure_index_file(tmp_path)
        assert "2026-01-01" in index_path.read_text()


# ---------------------------------------------------------------------------
# append_index_row
# ---------------------------------------------------------------------------

class TestAppendIndexRow:
    def test_appends_new_row(self, tmp_path):
        index_path = tmp_path / "INDEX.md"
        index_path.write_text(INDEX_HEADER)
        result = append_index_row(
            index_path, today="2026-04-14", project="test",
            title="Test Idea", status="captured",
            relative_link="ideas/2026-04-14-test.md",
        )
        assert result is True
        assert "Test Idea" in index_path.read_text()

    def test_prevents_duplicate(self, tmp_path):
        index_path = tmp_path / "INDEX.md"
        index_path.write_text(INDEX_HEADER + "| ... | [X](ideas/2026-04-14-test.md) |\n")
        result = append_index_row(
            index_path, today="2026-04-14", project="test",
            title="Test", status="captured",
            relative_link="ideas/2026-04-14-test.md",
        )
        assert result is False


# ---------------------------------------------------------------------------
# render_idea_markdown
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    def test_contains_all_sections(self):
        capture = IdeaCapture(
            title="Test Idea", project="proj",
            core_ideas="- idea 1", thought_trajectory="- started here",
            quotes=["quote one", "quote two"], open_questions="- q1",
        )
        md = render_idea_markdown(capture, "2026-04-14")
        assert "# Test Idea" in md
        assert "## Core Ideas" in md
        assert "## Thought Trajectory" in md
        assert "## Verbatim Quotes" in md
        assert '> "quote one"' in md
        assert "## Open Questions" in md

    def test_empty_open_questions_gets_default(self):
        capture = IdeaCapture(
            title="T", project="p", core_ideas="c",
            thought_trajectory="t", quotes=["a", "b"],
            open_questions="",
        )
        md = render_idea_markdown(capture, "2026-04-14")
        assert "None at the moment" in md
