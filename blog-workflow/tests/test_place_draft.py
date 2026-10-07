from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "place_draft.py"
DRAFT_TEXT = '---\ntitle: "隔离的工具执行环境"\ndate: "2026-09-27T10:00:00+09:00"\ndraft: true\n---\n\n正文\n'


class PlaceDraftTests(unittest.TestCase):
    def test_uses_explicit_blog_root_from_an_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            blog = root / "different-blog-project"
            (blog / "content/posts").mkdir(parents=True)
            (blog / "hugo.toml").write_text('title = "Fixture Blog"\n', encoding="utf-8")
            draft = root / "draft.md"
            draft.write_text(DRAFT_TEXT, encoding="utf-8")
            working = root / "unrelated-project"
            working.mkdir()
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(draft), "content/posts/entry.md", "--blog-root", str(blog)],
                cwd=working, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((blog / "content/posts/entry.md").read_text(encoding="utf-8"), DRAFT_TEXT)

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.blog = self.tmp / "Hugo blog"
        (self.blog / "docs").mkdir(parents=True)
        (self.blog / "docs" / "post-metadata.md").write_text("# Post Metadata Guide\n", encoding="utf-8")
        (self.blog / "hugo.toml").write_text('title = "Fixture Blog"\n', encoding="utf-8")
        (self.blog / "content" / "posts" / "AI application engineering").mkdir(parents=True)
        self.draft = self.tmp / "draft.md"
        self.draft.write_text(DRAFT_TEXT, encoding="utf-8")

    def place(self, target: str, draft: Path | None = None, root: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(draft or self.draft),
                target,
                "--blog-root",
                str(root or self.blog),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_copies_draft_into_category_directory(self):
        target = "content/posts/AI application engineering/agent-tool-sandbox.md"
        result = self.place(target)
        self.assertEqual(result.returncode, 0, result.stderr)
        placed = self.blog / target
        self.assertEqual(placed.read_text(encoding="utf-8"), DRAFT_TEXT)
        self.assertIn(str(placed), result.stdout)

    def test_creates_new_subdirectory_inside_posts(self):
        target = "content/posts/AI application engineering/Agent/agent-tool-sandbox.md"
        self.assertEqual(self.place(target).returncode, 0)
        self.assertTrue((self.blog / target).is_file())

    def test_refuses_to_overwrite_existing_post(self):
        target = self.blog / "content/posts/AI application engineering/existing.md"
        target.write_text("原文章\n", encoding="utf-8")
        result = self.place("content/posts/AI application engineering/existing.md")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "原文章\n")

    def test_refuses_target_outside_posts(self):
        for target in ("content/posts/../../docs/evil.md", "docs/evil.md", "/tmp/evil.md"):
            with self.subTest(target=target):
                self.assertNotEqual(self.place(target).returncode, 0)
        self.assertFalse((self.blog / "docs" / "evil.md").exists())

    def test_refuses_non_markdown_target(self):
        self.assertNotEqual(self.place("content/posts/AI application engineering/post.txt").returncode, 0)

    def test_refuses_draft_not_marked_as_draft(self):
        published = self.tmp / "published.md"
        published.write_text(DRAFT_TEXT.replace("draft: true", "draft: false"), encoding="utf-8")
        result = self.place("content/posts/AI application engineering/p.md", draft=published)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("draft: true", result.stderr)

    def test_refuses_root_that_is_not_blog(self):
        other = self.tmp / "other"
        (other / "content" / "posts").mkdir(parents=True)
        result = self.place("content/posts/p.md", root=other)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Hugo", result.stderr)


if __name__ == "__main__":
    unittest.main()
