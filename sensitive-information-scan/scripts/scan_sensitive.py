from __future__ import annotations

import argparse
import io
import ipaddress
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

RULES = {
    "private-key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "api-key": r"\bsk-(?:proj-|ant-api\d{2}-|ant-)?[A-Za-z0-9_-]{20,}",
    "github-token": r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{22,})\b",
    "gitlab-token": r"\bglpat-[A-Za-z0-9_-]{20,}",
    "npm-token": r"\bnpm_[A-Za-z0-9]{30,}",
    "pypi-token": r"\bpypi-[A-Za-z0-9_-]{40,}",
    "aws-access-key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "google-api-key": r"\bAIza[A-Za-z0-9_-]{35}\b",
    "slack-token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}",
    "telegram-token": r"\b\d{8,12}:[A-Za-z0-9_-]{35}\b",
    "stripe-token": r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}",
    "sendgrid-token": r"\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{30,}",
    "resend-token": r"\bre_[A-Za-z0-9]{24,}\b",
    "bearer-token": r"(?i)\b(?:Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{16,}",
    "jwt": r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}",
    "session-cookie": r"(?i)\b(?:Cookie|Set-Cookie)\s*:\s*[^\r\n]{8,}",
    "signed-url": r"(?i)\b(?:X-Amz-Signature|sig|cf_access_token|access_token)=[A-Za-z0-9%_.~+/-]{16,}",
    "credential-url": r"\b(?:https?|postgres(?:ql)?|mysql|redis|mongodb(?:\+srv)?|amqps?)://[^\s/:]+:[^\s/@]+@[^\s\"'<>`]+",
    "secret-assignment": r'''(?i)\b(?:[A-Za-z0-9_]*(?:password|passwd|api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|secret[_-]?key|private[_-]?key)[A-Za-z0-9_]*|(?:[A-Za-z0-9_]+_)?(?:pwd|pass|passphrase|secret|token))["']?\s*[:=]\s*(?:["'](?P<quoted>[^"'\r\n]{5,})["']|(?P<bare>[A-Za-z0-9+/_.=-]{8,}))''',
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "home-path": r"(?:/Users|/home)/[A-Za-z0-9._-]+(?:/[^\s\"'<>`]*)?",
    "windows-home-path": r"(?i)\b[A-Z]:\\Users\\[A-Za-z0-9._-]+(?:\\[^\s\"'<>`]*)?",
    "account-id": r'''(?im)\b(?:username|user_name|login|ssh_user|account_id|user_id|account_name|github_user|gitlab_user|telegram_user|discord_user)["']?\s*[:=]\s*(?:["'](?P<value>[^"'\r\n]{3,})["']|(?P<bare>[A-Za-z0-9_.@-]{3,})(?=\s*(?:$|[,;#\r\n])))''',
    "personal-name": r'''(?i)\b(?:full_name|fullname|real_name|legal_name|personal_name|contact_name)["']?\s*[:=]\s*["'](?P<value>[^"'\r\n]{3,})["']''',
    "account-url": r"(?i)\bhttps?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org|t\.me|instagram\.com|linkedin\.com/in|x\.com|twitter\.com)/[A-Za-z0-9][A-Za-z0-9._/-]*",
    "cloud-connection": r'''(?i)\b(?:AccountKey|SharedAccessKey|aws_secret_access_key|azure_client_secret|AccessKeySecret)\s*[:=]\s*["']?(?P<value>[A-Za-z0-9+/=_-]{16,})''',
    "project-context": r'''(?im)\b(?:sourceProject|sourceSessionId|project_root|project_path|workspace_root|customer_name|client_name)["']?\s*[:=]\s*(?:["'](?P<value>[^"'\r\n]{3,})["']|(?P<bare>[A-Za-z0-9_./@-]{3,})(?=\s*(?:$|[,;#\r\n])))''',
    "phone": r"(?<![\w])(?:\+\d{1,3}[ -]?)?1[3-9]\d{9}(?!\w)|(?<!\w)\+[1-9]\d{0,2}[ -](?:\d[ -]?){7,13}\d(?!\w)",
    "identity-number": r"(?<!\w)[1-9]\d{5}(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx](?!\w)",
    "ip-address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "ipv6-address": r"(?<![\w:])(?:[A-Fa-f0-9]{0,4}:){2,7}[A-Fa-f0-9]{0,4}(?![\w:])",
    "internal-host": r"(?i)\b[A-Za-z0-9][A-Za-z0-9.-]*\.(?:internal|lan|local|ts\.net|cfargotunnel\.com|trycloudflare\.com)\b",
    "personal-project-default": r'''(?i)\bDEFAULT_[A-Z_]*(?:ROOT|PROJECT|WORKSPACE)\s*=\s*["'](?P<value>~/[^"'\r\n]+)["']''',
}
COMPILED = {kind: re.compile(pattern) for kind, pattern in RULES.items()}
NOREPLY = re.compile(r"(?:\d+\+)?[A-Za-z0-9_.+-]+@users\.noreply\.github\.com|noreply@github\.com")
PUBLIC_NAMES = {"Contributor", "GitHub", "github-actions[bot]", "dependabot[bot]"}
PLACEHOLDER = re.compile(r"(?:<[^>]+>|\$\{?[^\s}]+\}?|\{[^}]+\}|(?:YOUR|EXAMPLE|PLACEHOLDER)[_-].*)", re.IGNORECASE)
SECRET_KINDS = set(RULES) - {
    "email", "home-path", "windows-home-path", "account-id", "personal-name", "account-url", "project-context", "phone",
    "identity-number", "ip-address", "ipv6-address", "internal-host", "personal-project-default",
}


class ScanError(Exception):
    pass


class Scanner:
    def __init__(self, max_bytes=10 * 1024 * 1024, policy=None, private_patterns=None):
        self.max_bytes = max_bytes
        self.findings = []
        self.errors = []
        self.coverage = {"files": 0, "blobs": 0, "commits": 0, "archives": 0, "bytes": 0}
        self.allow = []
        self.private = []
        self.seen = set()
        if policy:
            data = json.loads(Path(policy).read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("allow", []), list):
                raise ScanError("policy must use version 1 and an allow list")
            for entry in data.get("allow", []):
                if not isinstance(entry, dict) or not isinstance(entry.get("pattern"), str):
                    raise ScanError("policy entries must be objects with a string pattern")
                if entry.get("rule") not in set(RULES) | {"commit-email", "current-author-email", "commit-name", "current-author-name"}:
                    raise ScanError("unknown policy rule")
                if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
                    raise ScanError("every policy allowance must have a reason")
                pattern = re.compile(entry["pattern"])
                if pattern.fullmatch(""):
                    raise ScanError("policy cannot allow an empty match")
                self.allow.append((entry["rule"], pattern))
        if private_patterns:
            for line in Path(private_patterns).read_text(encoding="utf-8").splitlines():
                if line.strip():
                    pattern = re.compile(line)
                    if pattern.search(""):
                        raise ScanError("private patterns cannot match empty text")
                    self.private.append(pattern)

    def safe_path(self, path):
        label = str(path)
        for pattern in [*COMPILED.values(), *self.private]:
            label = pattern.sub("<private>", label)
        return label

    def error(self, scope, path, message):
        self.errors.append({"scope": scope, "path": self.safe_path(path), "message": message})

    def add(self, kind, value, scope, path, line, commit=None):
        if PLACEHOLDER.fullmatch(value):
            return
        if kind in {"email", "commit-email", "current-author-email"} and NOREPLY.fullmatch(value):
            return
        if kind in {"commit-name", "current-author-name"} and value in PUBLIC_NAMES:
            return
        if kind in {"ip-address", "ipv6-address"}:
            try:
                address = ipaddress.ip_address(value)
            except ValueError:
                return
            if address.is_loopback or address.is_unspecified:
                return
        if any(rule == kind and pattern.fullmatch(value) for rule, pattern in self.allow):
            return
        key = (scope, str(path), line, kind, value, commit)
        if key in self.seen:
            return
        self.seen.add(key)
        finding = {
            "scope": scope, "path": self.safe_path(path), "line": line, "kind": kind,
            "severity": "high" if kind in SECRET_KINDS or kind == "credential-file" else "review",
            "redacted": True,
        }
        if commit:
            finding["commit"] = commit
        self.findings.append(finding)

    def text(self, text, scope, path, origin_line=1, commit=None, decode_json=True):
        for kind, pattern in COMPILED.items():
            for match in pattern.finditer(text):
                groups = match.groupdict()
                value = groups.get("value") or groups.get("quoted") or groups.get("bare") or match.group()
                if kind == "secret-assignment" and groups.get("bare"):
                    if value in {"example", "marker", "getenv", "os.environ", "None", "null", "undefined"}:
                        continue
                    if value.startswith(("re.compile", "args.", "self.", "os.", "process.", "config.")):
                        continue
                line = origin_line + text.count("\n", 0, match.start())
                self.add(kind, value, scope, path, line, commit)
        for pattern in self.private:
            for match in pattern.finditer(text):
                self.add("private-context", match.group(), scope, path, origin_line + text.count("\n", 0, match.start()), commit)
        if decode_json:
            for match in re.finditer(r'"(?:\\.|[^"\\])*"', text):
                if "\\" not in match.group():
                    continue
                try:
                    decoded = json.loads(match.group())
                except json.JSONDecodeError:
                    continue
                self.text(decoded, scope, path, origin_line + text.count("\n", 0, match.start()), commit, False)

    def content(self, data, scope, path, commit=None, depth=0):
        self.coverage["bytes"] += len(data)
        if len(data) > self.max_bytes:
            self.error(scope, path, "content exceeds the configured byte limit")
            return
        name = Path(str(path)).name.lower()
        self.text(str(path), scope + "-path", path, commit=commit, decode_json=False)
        if name in {"id_rsa", "id_ed25519", "credentials", "credentials.json", ".env", "auth.json"} or name.endswith((".pem", ".key", ".p12", ".pfx", ".kdbx")):
            self.add("credential-file", name, scope, path, 1, commit)
        if zipfile.is_zipfile(io.BytesIO(data)):
            if depth >= 3:
                self.error(scope, path, "archive nesting exceeds the scan limit")
                return
            self.coverage["archives"] += 1
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    members = archive.infolist()
                    if len(members) > 1000 or sum(m.file_size for m in members) > self.max_bytes:
                        self.error(scope, path, "archive expansion exceeds the scan limit")
                        return
                    for member in members:
                        if not member.is_dir():
                            self.content(archive.read(member), scope, str(path) + "!" + member.filename, commit, depth + 1)
            except (OSError, RuntimeError, NotImplementedError, zipfile.BadZipFile):
                self.error(scope, path, "archive could not be completely read")
            return
        if name.endswith((".zip", ".docx", ".xlsx", ".pptx", ".odt", ".ods", ".epub")):
            self.error(scope, path, "expected archive format could not be read")
        try:
            text = data.decode("utf-8")
            undecodable = False
        except UnicodeDecodeError:
            text = data.decode("utf-8", errors="replace")
            undecodable = True
        self.text(text, scope, path, commit=commit)
        if undecodable or b"\x00" in data or data.startswith(b"%PDF-"):
            self.error(scope, path, "binary strings were scanned; structured binary content needs a format-specific review")

    def file(self, path):
        label = Path(path).name
        try:
            if Path(path).is_symlink():
                self.error("file", label, "symbolic link was not followed")
                return
            if Path(path).stat().st_size > self.max_bytes:
                self.error("file", label, "file exceeds the configured byte limit")
                return
            data = Path(path).read_bytes()
        except OSError:
            self.error("file", label, "file could not be read")
            return
        self.coverage["files"] += 1
        self.content(data, "file", label)

    def git(self, repo, *arguments, data=None):
        result = subprocess.run(
            ["git", "--literal-pathspecs", "-C", str(repo), *arguments],
            input=data, capture_output=True, check=False,
        )
        if result.returncode:
            raise ScanError("Git could not read the requested repository or revision")
        return result.stdout

    def identities(self, repo, commits):
        for commit in commits:
            record = self.git(repo, "show", "-s", "--format=%an%x00%ae%x00%cn%x00%ce%x00%B", commit).decode("utf-8", errors="replace")
            author_name, author_email, committer_name, committer_email, message = record.split("\0", 4)
            for role, name, email in [("author", author_name, author_email), ("committer", committer_name, committer_email)]:
                self.add("commit-email", email.strip(), "commit", role, 1, commit)
                self.add("commit-name", name.strip(), "commit", role, 1, commit)
            self.text(message, "commit", "message", commit=commit)
            self.coverage["commits"] += 1

    def repository(self, repo, staged=False, history=False, include_ignored=False, current_author=False, commit_range=None):
        root = Path(self.git(repo, "rev-parse", "--show-toplevel").decode().strip())
        if history:
            rows = self.git(root, "rev-list", "--objects", "--all").decode("utf-8", errors="replace").splitlines()
            objects = {row.partition(" ")[0]: row.partition(" ")[2] for row in rows}
            infos = self.git(root, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)", data=("\n".join(objects) + "\n").encode()).decode().splitlines()
            for info in infos:
                oid, kind, size = info.split()
                if kind == "blob":
                    if int(size) > self.max_bytes:
                        self.error("history", objects[oid], "historical blob exceeds the configured byte limit")
                        continue
                    self.coverage["blobs"] += 1
                    self.content(self.git(root, "cat-file", "blob", oid), "history", objects[oid], oid)
            self.identities(root, self.git(root, "rev-list", "--all").decode().splitlines())
        elif staged:
            for row in self.git(root, "ls-files", "--stage", "-z").split(b"\0"):
                if not row:
                    continue
                meta, filename = row.split(b"\t", 1)
                mode, oid, stage = meta.decode().split()
                name = filename.decode("utf-8", errors="surrogateescape")
                if stage != "0" or mode in {"120000", "160000"}:
                    self.error("index", name, "unmerged entry, symbolic link or submodule needs separate review")
                    continue
                self.coverage["files"] += 1
                self.content(self.git(root, "cat-file", "blob", oid), "index", name)
        elif not commit_range:
            paths = set(self.git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0"))
            if include_ignored:
                paths.update(self.git(root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z").split(b"\0"))
            for filename in sorted(paths - {b""}):
                name = filename.decode("utf-8", errors="surrogateescape")
                path = root / name
                if not path.exists() and not path.is_symlink():
                    continue
                if path.is_symlink():
                    self.error("working-tree", name, "symbolic link was not followed")
                    continue
                try:
                    if path.stat().st_size > self.max_bytes:
                        self.error("working-tree", name, "file exceeds the configured byte limit")
                        continue
                    self.coverage["files"] += 1
                    self.content(path.read_bytes(), "working-tree", name)
                except OSError:
                    self.error("working-tree", name, "file could not be read")
        if commit_range:
            if not re.fullmatch(r"[0-9a-fA-F]{40}\.\.(?:[0-9a-fA-F]{40}|HEAD)", commit_range):
                raise ScanError("commit range must use a full base hash and a full head hash or HEAD")
            self.identities(root, self.git(root, "rev-list", commit_range).decode().splitlines())
        if current_author:
            for role in ["GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT"]:
                identity = self.git(root, "var", role).decode()
                match = re.fullmatch(r"(.+) <([^<>]+)> \d+ [+-]\d{4}\s*", identity)
                if not match:
                    raise ScanError("current Git identity could not be read")
                self.add("current-author-name", match[1], "identity", role, 1)
                self.add("current-author-email", match[2], "identity", role, 1)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Scan publishable content and Git identities without printing sensitive values")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--repo", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true")
    mode.add_argument("--history", action="store_true")
    parser.add_argument("--include-ignored", action="store_true")
    parser.add_argument("--current-author", action="store_true")
    parser.add_argument("--commit-range")
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--private-patterns", type=Path)
    parser.add_argument("--max-bytes", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args(argv)
    scanner = Scanner()
    try:
        if args.max_bytes < 1 or not (args.paths or args.repo):
            raise ScanError("provide files or --repo, with a positive byte limit")
        if (args.staged or args.history or args.include_ignored or args.current_author or args.commit_range) and not args.repo:
            raise ScanError("Git scan options require --repo")
        scanner = Scanner(args.max_bytes, args.policy, args.private_patterns)
        for path in args.paths:
            scanner.file(path)
        if args.repo:
            scanner.repository(args.repo, args.staged, args.history, args.include_ignored, args.current_author, args.commit_range)
    except (ScanError, OSError, ValueError, re.error, KeyError, TypeError):
        scanner.error("configuration", "scanner", "scan could not complete; check policy, patterns, Git target and input permissions")
    print(json.dumps({"findings": scanner.findings, "errors": scanner.errors, "coverage": scanner.coverage}, ensure_ascii=True, indent=2))
    if scanner.errors:
        return 2
    return 1 if args.fail_on_findings and scanner.findings else 0


if __name__ == "__main__":
    sys.exit(main())
