from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "validate_docs.py"
RUNBOOK = SKILL_ROOT / "scripts" / "runbook.py"
EXCLUSION_FILE = "docs/.governance-exclude"
PINNED_PERMALINK = (
    "https://example.com/team/project/blob/"
    "0123456789abcdef0123456789abcdef01234567/docs/adr/0001-old.md"
)
REQUIRED_DIRS = [
    "docs/adr",
    "docs/execution/specs",
    "docs/runbooks",
]


class ValidateDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.sandbox = Path(self.temporary_directory.name)
        self.root = self.sandbox / "project"
        for relative in REQUIRED_DIRS:
            (self.root / relative).mkdir(parents=True, exist_ok=True)

    def write_document(
        self,
        relative: str,
        body: str,
        *,
        status: str = "active",
        document_type: str | None = None,
        decision_status: str | None = None,
        supersedes: str = "",
        superseded_by: str = "",
        extra_fields: dict[str, str] | None = None,
    ) -> Path:
        fields = [
            "---",
            f"status: {status}",
        ]
        if document_type is not None:
            fields.append(f"document_type: {document_type}")
        if decision_status is not None:
            fields.append(f"decision_status: {decision_status}")
        if extra_fields:
            fields.extend(f'{key}: "{value}"' for key, value in extra_fields.items())
        fields.extend(
            [
                f'supersedes: "{supersedes}"',
                f'superseded_by: "{superseded_by}"',
                'date: "2026-07-19"',
                "---",
                "",
                body,
                "",
            ]
        )
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(fields), encoding="utf-8")
        return path

    def run_validator(
        self, *, strict: bool = True
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        command = [
            sys.executable,
            str(VALIDATOR),
            str(self.root),
            "--format=json",
        ]
        if strict:
            command.append("--strict")
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        payload = json.loads(result.stdout)
        return result, payload

    def write_active_runbook(
        self, relative: str = "docs/runbooks/active-runbook.md"
    ) -> Path:
        (self.root / "runbook-source.txt").write_text(
            "authoritative\n", encoding="utf-8"
        )
        template = (
            SKILL_ROOT / "assets/templates/runbook-template.md"
        ).read_text(encoding="utf-8")
        content = template.replace("YYYY-MM-DD", "2026-07-19")
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_strict_mode_promotes_every_soft_rule(self) -> None:
        self.write_document(
            "docs/archive/specs/old.md",
            "# Old spec",
            status="superseded",
            document_type="spec",
        )
        self.write_document(
            "docs/adr/0001-missing-decision-status.md",
            "# ADR without decision status",
        )
        self.write_document(
            "docs/execution/plans/no-source.md",
            "# Plan without source spec",
            document_type="plan",
        )
        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["warnings"], [])
        rendered = "\n".join(payload["errors"])
        self.assertIn("archive document is not marked archived", rendered)
        self.assertIn("ADR should include decision_status", rendered)
        self.assertIn("plan should link to its source spec", rendered)

    def test_source_paths_cannot_escape_or_fall_back_to_project_root(self) -> None:
        outside = self.sandbox / "outside.md"
        outside.write_text("outside", encoding="utf-8")
        (self.root / "README.md").write_text("root only", encoding="utf-8")
        self.write_document(
            "docs/prd-v0.1.md",
            "\n".join(
                [
                    "# Links",
                    "",
                    "- [SOURCE: ../outside.md]",
                    f"- [SOURCE: {outside}]",
                    "- [SOURCE: README.md]",
                ]
            ),
            document_type="prd",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("must not contain '..' traversal", rendered)
        self.assertIn("must be repository-relative", rendered)
        self.assertIn("missing SOURCE target README.md", rendered)

    def test_closed_spec_reference_resolves_through_archive_mapping(self) -> None:
        self.write_document(
            "docs/archive/specs/closed.md",
            "# Closed spec",
            status="archived",
            document_type="spec",
        )
        self.write_document(
            "docs/prd-v0.1.md",
            "# Links\n\n- [SOURCE: docs/execution/specs/closed.md]",
            document_type="prd",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["errors"], [])

    def test_proposed_replacement_does_not_supersede_old_adr_early(self) -> None:
        self.write_document(
            "docs/adr/0001-existing.md",
            "# Current ADR",
            document_type="adr",
            decision_status="accepted",
        )
        self.write_document(
            "docs/adr/0002-proposed.md",
            "# Proposed ADR",
            document_type="adr",
            decision_status="proposed",
            supersedes="docs/adr/0001-existing.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0)
        self.assertTrue(payload["ok"])

    def test_replacement_links_deleted_adr_by_pinned_permalink(self) -> None:
        self.write_document(
            "docs/adr/0002-new.md",
            "# New decision",
            document_type="adr",
            decision_status="accepted",
            supersedes=PINNED_PERMALINK,
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["warnings"], [])

    def test_adr_does_not_need_superseded_by_field(self) -> None:
        path = self.root / "docs/adr/0001-only.md"
        path.write_text(
            '---\nstatus: active\ndocument_type: adr\ndecision_status: accepted\nsupersedes: ""\ndate: "2026-07-19"\n---\n\n# Only decision\n',
            encoding="utf-8",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)

    def test_accepted_replacement_requires_old_adr_to_be_deleted(self) -> None:
        self.write_document(
            "docs/adr/0001-old.md",
            "# Old decision",
            document_type="adr",
            decision_status="accepted",
        )
        self.write_document(
            "docs/adr/0002-new.md",
            "# New decision",
            document_type="adr",
            decision_status="accepted",
            supersedes="docs/adr/0001-old.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "supersedes target docs/adr/0001-old.md still exists",
            "\n".join(payload["errors"]),
        )

    def test_supersedes_local_path_to_deleted_adr_needs_permalink(self) -> None:
        self.write_document(
            "docs/adr/0002-new.md",
            "# New decision",
            document_type="adr",
            decision_status="accepted",
            supersedes="docs/adr/0001-gone.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "local path to a file that no longer exists",
            "\n".join(payload["errors"]),
        )

    def test_supersedes_branch_link_is_not_pinned(self) -> None:
        self.write_document(
            "docs/adr/0002-new.md",
            "# New decision",
            document_type="adr",
            decision_status="accepted",
            supersedes="https://example.com/team/project/blob/main/docs/adr/0001-old.md",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("pinned to a commit", "\n".join(payload["errors"]))

    def test_superseded_adr_kept_in_place_must_be_deleted(self) -> None:
        self.write_document(
            "docs/adr/0001-old.md",
            "# Old decision",
            status="superseded",
            document_type="adr",
            decision_status="superseded",
        )

        strict_result, strict_payload = self.run_validator(strict=True)
        migration_result, migration_payload = self.run_validator(strict=False)

        self.assertEqual(strict_result.returncode, 1)
        self.assertIn(
            "superseded ADR must be deleted", "\n".join(strict_payload["errors"])
        )
        self.assertEqual(migration_result.returncode, 0)
        self.assertIn(
            "superseded ADR must be deleted",
            "\n".join(migration_payload["warnings"]),
        )

    def test_adr_must_not_set_superseded_by(self) -> None:
        self.write_document(
            "docs/adr/0001-old.md",
            "# Old decision",
            document_type="adr",
            decision_status="accepted",
            superseded_by=PINNED_PERMALINK,
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "ADR must not set superseded_by", "\n".join(payload["errors"])
        )

    def test_archived_adr_must_be_deleted(self) -> None:
        self.write_document(
            "docs/archive/adr/0001-old.md",
            "# Old decision",
            status="archived",
            document_type="adr",
            decision_status="accepted",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn("ADRs are not archived", "\n".join(payload["errors"]))

    def test_covers_and_verified_at_are_accepted_when_well_formed(self) -> None:
        (self.root / "src/app").mkdir(parents=True)
        (self.root / "src/app/main.py").write_text("x = 1\n", encoding="utf-8")
        self.write_document(
            "docs/architecture-v0.1.md",
            "# Current shape",
            document_type="architecture",
            extra_fields={
                "covers": "src/app/**/*.py, src/app",
                "verified_at": "0123abc",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["warnings"], [])

    def test_malformed_tracking_fields_are_reported(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src/main.py").write_text("x = 1\n", encoding="utf-8")
        self.write_document(
            "docs/architecture-v0.1.md",
            "# Current shape",
            document_type="architecture",
            extra_fields={
                "covers": "../outside, https://example.com/x, src/missing/**",
                "verified_at": "main",
                "implementation": "done",
            },
        )
        self.write_document(
            "docs/runbooks/no-commit.md",
            "# Runbook",
            extra_fields={"covers": "src/main.py"},
        )

        result, payload = self.run_validator(strict=True)

        rendered = "\n".join(payload["errors"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("covers entry '../outside' must not contain '..'", rendered)
        self.assertIn("covers entry 'https://example.com/x' must be a repository path", rendered)
        self.assertIn("covers entry 'src/missing/**' matches no file", rendered)
        self.assertIn("verified_at must be a commit hash", rendered)
        self.assertIn("invalid implementation 'done'", rendered)
        self.assertIn("no-commit.md: covers requires verified_at", rendered)

    def test_reference_to_missing_path_blocks_strict_validation(self) -> None:
        (self.root / "scripts").mkdir()
        (self.root / "scripts/build.sh").write_text("echo\n", encoding="utf-8")
        self.write_document(
            "docs/architecture-v0.1.md",
            "# Shape\n\nBuild with `scripts/build.sh` and deploy with `scripts/deploy.sh`.",
            document_type="architecture",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("references path `scripts/deploy.sh`", rendered)
        self.assertNotIn("scripts/build.sh", rendered)

    def test_references_that_exist_or_are_not_repository_paths_pass(self) -> None:
        (self.root / "packages/web/src").mkdir(parents=True)
        (self.root / "packages/web/src/app.ts").write_text(
            "export function renderPage() { return runPolicy.inbox && API_TOKEN_NAME }\n",
            encoding="utf-8",
        )
        (self.root / "package.json").write_text(
            json.dumps({"scripts": {"check:docs": "true"}}), encoding="utf-8"
        )
        self.write_document(
            "docs/architecture-v0.1.md",
            "# Shape\n\n- `packages/web/src/app.ts:12` and `src/app.ts` (relative to the package)\n- `renderPage()`, `runPolicy.inbox`, `API_TOKEN_NAME`\n- `npm run check:docs`\n- `application/json`, `owner/repo`, `~/.config/tool`, `/etc/hosts`\n- `https://example.com/a/b.ts`, `docs/<topic>.md`, `e.g.`, `Node.js`\n\n```bash\nnpm run check:docs\n```",
            document_type="architecture",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["warnings"], [])

    def test_stale_symbols_commands_and_config_keys_are_reported(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src/app.ts").write_text(
            "export function renderPage() { return runPolicy.inbox }\n",
            encoding="utf-8",
        )
        (self.root / "package.json").write_text(
            json.dumps({"scripts": {"check": "true"}}), encoding="utf-8"
        )
        self.write_document(
            "docs/runbooks/operate.md",
            "# Operate\n\n- `renderLegacyPage()` and `runPolicy.thinkInbox`\n- `OLD_SECRET_NAME`\n- `npm run check:removed`\n\n```bash\nnode src/removed.mjs --dry-run\n```",
            document_type="runbook",
        )

        _result, payload = self.run_validator(strict=True)

        rendered = "\n".join(payload["errors"])
        self.assertIn("references symbol `renderLegacyPage`", rendered)
        self.assertIn("references config key `runPolicy.thinkInbox`", rendered)
        self.assertIn("references config key `OLD_SECRET_NAME`", rendered)
        self.assertIn("references package script `check:removed`", rendered)
        self.assertIn("references path `src/removed.mjs`", rendered)

    def test_in_progress_design_reports_missing_references_as_warnings(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src/app.ts").write_text("export {}\n", encoding="utf-8")
        self.write_document(
            "docs/adr/0003-new-inbox.md",
            "# New inbox\n\nThe inbox lives in `src/inbox.ts`.",
            document_type="adr",
            decision_status="accepted",
            extra_fields={"implementation": "in_progress"},
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertIn("references path `src/inbox.ts`", "\n".join(payload["warnings"]))

    def test_specs_ideas_backlog_and_archives_are_not_reference_checked(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src/app.ts").write_text("export {}\n", encoding="utf-8")
        body = "# Future\n\nWill add `src/future.ts`."
        self.write_document(
            "docs/execution/specs/2026-07-19-future-design.md",
            body,
            document_type="spec",
        )
        self.write_document(
            "docs/archive/specs/2026-07-01-old-design.md",
            body,
            status="archived",
            document_type="spec",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)

    def test_references_ignore_file_and_git_ignored_paths_are_skipped(self) -> None:
        (self.root / "src").mkdir()
        (self.root / "src/app.ts").write_text("export {}\n", encoding="utf-8")
        (self.root / "src/util.js").write_text("export {}\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("dist/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        (self.root / "docs/.governance-references-ignore").write_text(
            "src/vendor/*\n", encoding="utf-8"
        )
        self.write_document(
            "docs/architecture-v0.1.md",
            "# Shape\n\nBuild output `dist/app.js`; upstream copy `src/vendor/lib.ts`.",
            document_type="architecture",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)

    def test_structured_idea_and_backlog_are_strictly_valid(self) -> None:
        idea_path = "docs/ideas/IDEA-20260719-001-useful-thought.md"
        backlog_path = "docs/backlog/BL-20260719-001-evaluate-thought.md"
        self.write_document(
            idea_path,
            "# Useful thought",
            document_type="idea",
            extra_fields={
                "record_id": "IDEA-20260719-001",
                "record_state": "promoted",
                "updated": "2026-07-19",
                "promoted_to": backlog_path,
            },
        )
        self.write_document(
            backlog_path,
            f"# Evaluate thought\n\n- [SOURCE: {idea_path}]",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-001",
                "record_state": "in_progress",
                "updated": "2026-07-19",
                "priority": "high",
                "item_type": "evaluation",
                "source_idea": idea_path,
                "review_after": "",
                "promoted_to": "",
                "result": "",
                "reason": "",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_backlog_header_priority_and_item_type_follow_template_contract(self) -> None:
        self.write_document(
            "docs/backlog/BL-20260719-003-invalid-contract.md",
            "# Invalid contract",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-003",
                "record_state": "open",
                "updated": "2026-07-19",
                "priority": "medium",
                "item_type": "",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["warnings"], [])
        rendered = "\n".join(payload["errors"])
        self.assertIn("missing Backlog frontmatter fields", rendered)
        self.assertIn("invalid Backlog priority 'medium'", rendered)
        self.assertIn("Backlog item_type must be non-empty", rendered)

    def test_backlog_contract_violations_are_migration_warnings_normally(self) -> None:
        self.write_document(
            "docs/backlog/BL-20260719-004-migration-warning.md",
            "# Migration warning",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-004",
                "record_state": "open",
                "updated": "2026-07-19",
            },
        )

        result, payload = self.run_validator(strict=False)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])
        rendered = "\n".join(payload["warnings"])
        self.assertIn("missing Backlog frontmatter fields", rendered)
        self.assertIn("invalid Backlog priority ''", rendered)
        self.assertIn("Backlog item_type must be non-empty", rendered)

    def test_record_id_state_and_path_invariants_fail_strict_mode(self) -> None:
        self.write_document(
            "docs/ideas/wrong-name.md",
            "# Broken Idea",
            document_type="backlog",
            extra_fields={
                "record_id": "BAD-1",
                "record_state": "captured",
                "updated": "not-a-date",
                "promoted_to": "",
            },
        )
        self.write_document(
            "docs/backlog/BL-20260719-002-missing-target.md",
            "# Missing target",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-002",
                "record_state": "converted",
                "updated": "2026-07-19",
                "promoted_to": "",
            },
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("conflicts with record path kind", rendered)
        self.assertIn("invalid record_id", rendered)
        self.assertIn("invalid record_state", rendered)
        self.assertIn("must set promoted_to", rendered)
        self.assertIn("updated must be YYYY-MM-DD", rendered)

    def test_duplicate_record_ids_and_terminal_evidence_are_rejected(self) -> None:
        common = {
            "record_id": "BL-20260719-001",
            "record_state": "done",
            "updated": "2026-07-19",
            "promoted_to": "",
            "result": "",
            "reason": "",
        }
        self.write_document(
            "docs/backlog/BL-20260719-001-first.md",
            "# First",
            document_type="backlog",
            extra_fields=common,
        )
        self.write_document(
            "docs/backlog/BL-20260719-001-second.md",
            "# Second",
            document_type="backlog",
            extra_fields=common,
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("duplicate record_id", rendered)
        self.assertIn("done Backlog requires result", rendered)

    def test_codex_lessons_is_a_distinct_governed_document(self) -> None:
        self.write_document(
            "docs/lessons.md",
            "# Agent Lessons\n\n## Repeated mistake\n\n- Prevention rule: verify first.",
            document_type="lessons",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_legacy_runbook_is_warning_normally_and_error_in_strict_mode(self) -> None:
        self.write_document(
            "docs/runbooks/legacy.md",
            "# Legacy\n\n## Procedure\n\n1. Old step.",
            document_type="runbook",
        )

        normal_result, normal_payload = self.run_validator(strict=False)
        strict_result, strict_payload = self.run_validator(strict=True)

        self.assertEqual(normal_result.returncode, 0, normal_payload)
        self.assertTrue(normal_payload["warnings"])
        rendered_warnings = "\n".join(normal_payload["warnings"])
        self.assertIn("missing execution_risk", rendered_warnings)
        self.assertIn("missing required section: Scope", rendered_warnings)
        self.assertEqual(strict_result.returncode, 1)
        self.assertEqual(strict_payload["warnings"], [])

    def test_invalid_execution_risk_always_errors(self) -> None:
        path = self.write_active_runbook()
        valid_text = path.read_text(encoding="utf-8")
        path.write_text(
            valid_text.replace("execution_risk: critical", "execution_risk: unsafe"),
            encoding="utf-8",
        )
        result, payload = self.run_validator(strict=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid execution_risk", "\n".join(payload["errors"]))

    def test_active_runbook_is_not_compared_with_its_sources(self) -> None:
        self.write_active_runbook()
        (self.root / "runbook-source.txt").write_text("drift\n", encoding="utf-8")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_legacy_seal_field_and_contract_block_are_ignored(self) -> None:
        path = self.write_active_runbook()
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace(
                "execution_risk: critical",
                'execution_risk: critical\ncontract_sha256: "sha256:' + "0" * 64 + '"',
            ).replace(
                "# Runbook Title",
                "# Runbook Title\n\n<!-- runbook-contract:\n- missing/path.sh\n-->",
            ),
            encoding="utf-8",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_archived_runbook_with_legacy_seal_field_stays_valid(self) -> None:
        archived = self.write_document(
            "docs/archive/runbooks/legacy.md",
            "# Archived Runbook\n\nHistorical content.",
            status="archived",
            document_type="runbook",
            extra_fields={
                "execution_risk": "critical",
                "contract_sha256": "sha256:" + "a" * 64,
                "archive_reason": "Historical retirement",
            },
        )
        self.assertTrue(archived.is_file())

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_legacy_active_runbook_source_resolves_to_unique_archive(self) -> None:
        self.write_document(
            "docs/archive/runbooks/old-runbook.md",
            "# Archived",
            status="archived",
            document_type="runbook",
            extra_fields={"archive_reason": "Legacy history"},
        )
        self.write_document(
            "docs/prd-v0.1.md",
            "# Product\n\n[SOURCE: docs/runbooks/old-runbook.md]",
            document_type="prd",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)

    def test_legacy_runbook_source_requires_one_unambiguous_dated_archive(self) -> None:
        for archive_date in ("2026-07-18",):
            self.write_document(
                f"docs/archive/runbooks/{archive_date}-old-runbook.md",
                "# Archived",
                status="archived",
                document_type="runbook",
                extra_fields={"archive_reason": "Historical retirement"},
            )
        self.write_document(
            "docs/prd-v0.1.md",
            "# Product\n\n[SOURCE: docs/runbooks/old-runbook.md]",
            document_type="prd",
        )

        unique_result, unique_payload = self.run_validator(strict=True)
        self.assertEqual(unique_result.returncode, 0, unique_payload)

        self.write_document(
            "docs/archive/runbooks/2026-07-19-old-runbook.md",
            "# Another archive",
            status="archived",
            document_type="runbook",
            extra_fields={"archive_reason": "Historical retirement"},
        )
        ambiguous_result, ambiguous_payload = self.run_validator(strict=True)

        self.assertEqual(ambiguous_result.returncode, 1)
        self.assertIn(
            "ambiguous archived Runbook SOURCE target",
            "\n".join(ambiguous_payload["errors"]),
        )

    def test_archive_source_compatibility_rejects_symlink_escape(self) -> None:
        outside = self.sandbox / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        archive = self.root / "docs/archive/runbooks/old-runbook.md"
        archive.parent.mkdir(parents=True, exist_ok=True)
        archive.symlink_to(outside)
        self.write_document(
            "docs/prd-v0.1.md",
            "# Product\n\n[SOURCE: docs/runbooks/old-runbook.md]",
            document_type="prd",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "missing SOURCE target",
            "\n".join(payload["errors"]),
        )

    def test_bundled_templates_form_a_strictly_valid_project(self) -> None:
        templates = SKILL_ROOT / "assets" / "templates"
        destinations = {
            "prd-template.md": "docs/prd-v0.1.md",
            "architecture-template.md": "docs/architecture-v0.1.md",
            "adr-template.md": "docs/adr/0001-decision.md",
            "spec-template.md": "docs/execution/specs/2026-07-19-topic-design.md",
            "runbook-template.md": "docs/runbooks/topic-runbook.md",
            "idea-note-template.md": "docs/ideas/IDEA-20260719-a2b3c4-idea.md",
            "backlog-item-template.md": "docs/backlog/BL-20260719-a2b3c4-item.md",
            "lessons-template.md": "docs/lessons.md",
        }
        for source_name, destination_name in destinations.items():
            content = (templates / source_name).read_text(encoding="utf-8")
            content = (
                content.replace("IDEA-YYYYMMDD-xxxxxx", "IDEA-20260719-a2b3c4")
                .replace("BL-YYYYMMDD-xxxxxx", "BL-20260719-a2b3c4")
                .replace("IDEA-YYYYMMDD-NNN", "IDEA-20260719-a2b3c4")
                .replace("BL-YYYYMMDD-NNN", "BL-20260719-a2b3c4")
                .replace("vX.Y", "v0.1")
                .replace("NNNN-short-title", "0001-decision")
                .replace("YYYY-MM-DD", "2026-07-19")
                .replace("<project>", "demo")
            )
            destination = self.root / destination_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")

        checked = subprocess.run(
            [
                sys.executable,
                str(RUNBOOK),
                "check",
                str(self.root),
                "docs/runbooks/topic-runbook.md",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(checked.returncode, 0, checked.stderr)

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def write_raw(self, relative: str, content: str | bytes) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def idea_fields(self, record_id: str, **overrides: str) -> dict[str, str]:
        fields = {
            "record_id": record_id,
            "record_state": "captured",
            "updated": "2026-07-19",
            "promoted_to": "",
        }
        fields.update(overrides)
        return fields

    def test_utf8_bom_frontmatter_is_recognized(self) -> None:
        self.write_raw(
            "docs/prd-v0.1.md",
            "\ufeff---\nstatus: active\ndocument_type: prd\nsupersedes: \"\"\n"
            "superseded_by: \"\"\ndate: \"2026-07-19\"\n---\n\n# Product\n",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)

    def test_unmaintained_todo_and_index_are_notices_not_strict_errors(self) -> None:
        self.write_raw("docs/TODO.md", "- [ ] add pagination\n")
        self.write_raw("docs/ideas/INDEX.md", "# Ideas\n")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        notices = "\n".join(payload["warnings"])
        self.assertIn("docs/TODO.md: not maintained by document-governance", notices)
        self.assertIn("docs/ideas/INDEX.md: not maintained by document-governance", notices)

    def test_non_utf8_file_reports_error_and_keeps_json(self) -> None:
        self.write_raw("docs/prd-v0.1.md", b"---\nstatus: active\n---\n\xff\xfe bad\n")

        result, payload = self.run_validator(strict=False)

        self.assertEqual(result.returncode, 1)
        self.assertIn("not valid UTF-8", "\n".join(payload["errors"]))

    def test_broken_and_looping_symlinks_are_errors(self) -> None:
        (self.root / "docs/broken.md").symlink_to(self.root / "docs/nowhere.md")
        loop = self.root / "docs/loop.md"
        loop.symlink_to(loop)

        result, payload = self.run_validator(strict=False)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("docs/broken.md: symbolic link does not resolve", rendered)
        self.assertIn("docs/loop.md: symbolic link does not resolve", rendered)

    def test_date_must_be_iso_format(self) -> None:
        self.write_raw(
            "docs/prd-v0.1.md",
            "---\nstatus: active\ndocument_type: prd\nsupersedes: \"\"\n"
            "superseded_by: \"\"\ndate: \"July 19\"\n---\n\n# Product\n",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "date must be YYYY-MM-DD, found 'July 19'", "\n".join(payload["errors"])
        )
        _, relaxed = self.run_validator(strict=False)
        self.assertIn("date must be YYYY-MM-DD", "\n".join(relaxed["warnings"]))

    def test_empty_required_fields_are_missing(self) -> None:
        self.write_raw(
            "docs/archive/specs/old.md",
            "---\nstatus:\ndocument_type: spec\nsupersedes: \"\"\n"
            "superseded_by: \"\"\ndate: \"\"\n---\n\n# Old\n",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "docs/archive/specs/old.md: missing frontmatter fields: date, status",
            "\n".join(payload["errors"]),
        )

    def test_unfilled_template_placeholders_are_reported(self) -> None:
        self.write_document("docs/adr/NNNN-real.md", "# Real", decision_status="accepted")
        self.write_document(
            "docs/prd-v0.1.md",
            "# Product\n"
            "- [SOURCE: docs/architecture-vX.Y.md#section]\n"
            "- [SOURCE: docs/adr/NNNN-real.md]\n"
            "- [SOURCE: docs/<missing>.md]\n"
            "- [SOURCE: docs/gone.md]",
            document_type="prd",
        )
        self.write_document(
            "docs/ideas/IDEA-20260719-001-x.md",
            "# Idea",
            document_type="idea",
            extra_fields=self.idea_fields("IDEA-20260719-001", updated="YYYY-MM-DD"),
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn(
            "unfilled template placeholder in SOURCE target docs/architecture-vX.Y.md",
            rendered,
        )
        self.assertIn(
            "unfilled template placeholder in SOURCE target docs/<missing>.md",
            rendered,
        )
        self.assertNotIn("NNNN-real", rendered)
        self.assertIn("missing SOURCE target docs/gone.md", rendered)
        self.assertIn("unfilled template placeholder in updated", rendered)
        _, relaxed = self.run_validator(strict=False)
        self.assertIn(
            "unfilled template placeholder in SOURCE target",
            "\n".join(relaxed["warnings"]),
        )

    def test_non_record_markdown_in_ideas_names_record_rule(self) -> None:
        self.write_raw("docs/ideas/README.md", "# Ideas\n")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "every Markdown file in docs/ideas/ is a record; move non-record notes elsewhere",
            "\n".join(payload["errors"]),
        )

    def test_typed_root_documents_must_live_at_their_paths(self) -> None:
        self.write_document("docs/notes/lessons.md", "# Lessons", document_type="lessons")
        self.write_document("docs/notes/product.md", "# Product", document_type="prd")
        self.write_document(
            "docs/architecture.md", "# Arch", document_type="architecture"
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn(
            "docs/notes/lessons.md: document_type 'lessons' requires path docs/lessons.md",
            rendered,
        )
        self.assertIn(
            "docs/notes/product.md: document_type 'prd' requires path docs/prd-v<version>.md",
            rendered,
        )
        self.assertIn(
            "docs/architecture.md: document_type 'architecture' requires path "
            "docs/architecture-v<version>.md",
            rendered,
        )

    def test_project_without_plan_directories_is_valid(self) -> None:
        self.write_document("docs/prd-v0.1.md", "# Product", document_type="prd")
        self.assertFalse((self.root / "docs/execution/plans").exists())
        self.assertFalse((self.root / "docs/archive").exists())

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_legacy_plans_stay_valid_active_and_archived(self) -> None:
        self.write_document("docs/execution/specs/s.md", "# Spec", document_type="spec")
        self.write_document(
            "docs/execution/plans/open.md",
            "# Plan\n\n- [SOURCE: docs/execution/specs/s.md]",
            document_type="plan",
        )
        self.write_document(
            "docs/archive/plans/closed.md",
            "# Plan\n\n- [SOURCE: docs/execution/specs/s.md]",
            status="archived",
            document_type="plan",
        )

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertTrue(payload["ok"])

    def test_plan_source_spec_requires_heading_or_spec_source(self) -> None:
        self.write_document("docs/execution/specs/s.md", "# Spec", document_type="spec")
        self.write_document("docs/prd-v0.1.md", "# Product", document_type="prd")
        self.write_document(
            "docs/execution/plans/mention.md",
            "# Plan\n\nWe have no Source Spec yet.\n\n- [SOURCE: docs/prd-v0.1.md]",
            document_type="plan",
        )
        self.write_document(
            "docs/execution/plans/heading.md",
            "# Plan\n\n## Source Spec\n\nTBD",
            document_type="plan",
        )
        self.write_document(
            "docs/execution/plans/linked.md",
            "# Plan\n\n- [SOURCE: docs/execution/specs/s.md]",
            document_type="plan",
        )

        _, payload = self.run_validator(strict=True)

        rendered = "\n".join(payload["errors"])
        self.assertIn("plans/mention.md: plan should link to its source spec", rendered)
        self.assertNotIn("plans/heading.md", rendered)
        self.assertNotIn("plans/linked.md", rendered)

    def test_runbook_archive_fallback_preserves_subpath(self) -> None:
        self.write_document(
            "docs/archive/runbooks/other/2026-07-18-deploy.md",
            "# Other",
            status="archived",
            document_type="runbook",
            extra_fields={"archive_reason": "Retired"},
        )
        self.write_document(
            "docs/archive/runbooks/ops/2026-07-18-deploy.md",
            "# Ops",
            status="archived",
            document_type="runbook",
            extra_fields={"archive_reason": "Retired"},
        )
        self.write_document(
            "docs/prd-v0.1.md",
            "# Product\n\n- [SOURCE: docs/runbooks/ops/deploy.md]\n"
            "- [SOURCE: docs/runbooks/web/deploy.md]",
            document_type="prd",
        )

        _, payload = self.run_validator(strict=True)

        rendered = "\n".join(payload["errors"])
        self.assertNotIn("runbooks/ops/deploy.md", rendered)
        self.assertIn("missing SOURCE target docs/runbooks/web/deploy.md", rendered)

    def test_both_record_id_formats_are_accepted(self) -> None:
        self.write_document(
            "docs/ideas/IDEA-20260719-a2b3c4-new.md",
            "# New",
            document_type="idea",
            extra_fields=self.idea_fields("IDEA-20260719-a2b3c4"),
        )
        self.write_document(
            "docs/ideas/IDEA-20260719-001-legacy.md",
            "# Legacy",
            document_type="idea",
            extra_fields=self.idea_fields("IDEA-20260719-001"),
        )
        self.write_document(
            "docs/ideas/IDEA-20260719-a0b3c4-bad.md",
            "# Bad alphabet",
            document_type="idea",
            extra_fields=self.idea_fields("IDEA-20260719-a0b3c4"),
        )

        _, payload = self.run_validator(strict=True)

        rendered = "\n".join(payload["errors"])
        self.assertEqual(
            [line for line in payload["errors"] if "invalid record_id" in line],
            ["docs/ideas/IDEA-20260719-a0b3c4-bad.md: invalid record_id 'IDEA-20260719-a0b3c4'"],
            rendered,
        )

    def test_archived_records_and_archive_link_mapping(self) -> None:
        self.write_document(
            "docs/archive/specs/s.md", "# Spec", status="archived", document_type="spec"
        )
        idea = "docs/ideas/IDEA-20260719-001-thought.md"
        self.write_document(
            "docs/archive/ideas/IDEA-20260719-001-thought.md",
            "# Thought",
            status="archived",
            document_type="idea",
            extra_fields=self.idea_fields(
                "IDEA-20260719-001",
                record_state="promoted",
                promoted_to="docs/execution/specs/s.md",
            ),
        )
        self.write_document(
            "docs/archive/backlog/BL-20260719-001-item.md",
            f"# Item\n\n- [SOURCE: {idea}]",
            status="archived",
            document_type="backlog",
            extra_fields={
                "record_id": "BL-20260719-001",
                "record_state": "done",
                "updated": "2026-07-19",
                "priority": "normal",
                "item_type": "task",
                "source_idea": idea,
                "review_after": "",
                "promoted_to": "",
                "result": "Shipped",
                "reason": "",
            },
        )

        result, payload = self.run_validator(strict=True)
        self.assertEqual(result.returncode, 0, payload)

        self.write_document(
            "docs/archive/ideas/IDEA-20260719-002-open.md",
            "# Open",
            status="archived",
            document_type="idea",
            extra_fields=self.idea_fields("IDEA-20260719-002"),
        )
        self.write_document(
            "docs/ideas/IDEA-20260719-001-dup.md",
            "# Dup",
            document_type="idea",
            extra_fields=self.idea_fields("IDEA-20260719-001"),
        )
        result, payload = self.run_validator(strict=True)
        rendered = "\n".join(payload["errors"])
        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "IDEA-20260719-002-open.md: archived record must have a terminal record_state",
            rendered,
        )
        self.assertIn("duplicate record_id 'IDEA-20260719-001'", rendered)
    def test_unfilled_record_template_outside_templates_reports_placeholder(self) -> None:
        templates = SKILL_ROOT / "assets" / "templates"
        for name, dest in (
            ("idea-note-template.md", "docs/ideas/IDEA-20260719-a2b3c4-idea.md"),
            ("backlog-item-template.md", "docs/backlog/BL-20260719-a2b3c4-item.md"),
            ("spec-template.md", "docs/execution/specs/s.md"),
        ):
            self.write_raw(dest, (templates / name).read_text(encoding="utf-8"))

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("unfilled template placeholder in record_id", rendered)
        self.assertIn("unfilled template placeholder in SOURCE target", rendered)


    def write_exclusions(self, *lines: str) -> None:
        self.write_raw(EXCLUSION_FILE, "\n".join(lines) + "\n")

    def test_excluded_directory_is_not_validated(self) -> None:
        self.write_raw("docs/ocr-eval/report.md", "# Report without frontmatter\n")
        self.write_raw("docs/ocr-eval/runs/run.md", "# Run without frontmatter\n")
        self.write_exclusions("docs/ocr-eval")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)
        self.assertEqual(payload["errors"], [])

    def test_exclusion_file_ignores_blank_and_hash_lines(self) -> None:
        self.write_raw("docs/ocr-eval/report.md", "# Report\n")
        self.write_exclusions("# evaluation output", "", "docs/ocr-eval/")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 0, payload)

    def test_documents_outside_excluded_directory_are_still_validated(self) -> None:
        self.write_raw("docs/ocr-eval/report.md", "# Report\n")
        self.write_raw("docs/ocr-evaluation.md", "# Similar name, not excluded\n")
        self.write_raw("docs/appstore/metadata.md", "# Store copy\n")
        self.write_exclusions("docs/ocr-eval")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        rendered = "\n".join(payload["errors"])
        self.assertIn("docs/ocr-evaluation.md: missing frontmatter", rendered)
        self.assertIn("docs/appstore/metadata.md: missing frontmatter", rendered)
        self.assertNotIn("docs/ocr-eval/report.md", rendered)

    def test_governed_locations_cannot_be_excluded(self) -> None:
        for excluded in (
            "docs",
            "docs/adr",
            "docs/execution",
            "docs/execution/specs",
            "docs/runbooks",
            "docs/ideas",
            "docs/backlog",
            "docs/archive",
            "docs/archive/specs",
            "docs/lessons.md",
            "docs/prd-v1.0.md",
            "docs/architecture-v1.0.md",
        ):
            with self.subTest(excluded=excluded):
                self.write_exclusions(excluded)

                result, payload = self.run_validator(strict=False)

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    f"{EXCLUSION_FILE}: cannot exclude governed location '{excluded}'",
                    "\n".join(payload["errors"]),
                )

    def test_exclusion_must_stay_inside_docs(self) -> None:
        for excluded in ("README.md", "/tmp/elsewhere", "docs/../src", "docs/a/../../src"):
            with self.subTest(excluded=excluded):
                self.write_exclusions(excluded)

                result, payload = self.run_validator(strict=False)

                self.assertEqual(result.returncode, 1)
                self.assertIn(
                    f"{EXCLUSION_FILE}: excluded path must be a relative path under docs/: '{excluded}'",
                    "\n".join(payload["errors"]),
                )

    def test_missing_excluded_path_is_reported(self) -> None:
        self.write_exclusions("docs/gone")

        result, payload = self.run_validator(strict=True)

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            f"{EXCLUSION_FILE}: excluded path does not exist: 'docs/gone'",
            "\n".join(payload["errors"]),
        )

    def test_missing_excluded_path_is_a_warning_in_migration_mode(self) -> None:
        self.write_exclusions("docs/gone")

        result, payload = self.run_validator(strict=False)

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            f"{EXCLUSION_FILE}: excluded path does not exist: 'docs/gone'",
            "\n".join(payload["warnings"]),
        )

if __name__ == "__main__":
    unittest.main()
