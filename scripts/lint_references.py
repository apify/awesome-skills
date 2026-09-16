#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Lint typed references in skill docs.

Scans skills/*/SKILL.md plus skills/*/references/**/*.md (and the legacy
singular reference/ layout) and extracts typed references:

  - repo-path   ${CLAUDE_PLUGIN_ROOT}/<path> occurrences, and
                `node|python|python3|bash|sh <relative-path>` run commands
                inside fenced code blocks (path relative to the skill dir)
  - actor-id    arguments of `apify actors call|info|start`, `--actor` flag
                values, owner/name from Apify Store URLs, and backticked
                owner/name ids in markdown table cells (actor routing tables)
  - store-url   URLs of the form apify.com/<owner>/<name>
  - apify-url   any URL on apify.com or *.apify.com
  - token       apify_api_[A-Za-z0-9]{20,} anywhere in the skill's files

Offline rules (always):
  - repo-path must exist in the repo
  - apify-url/store-url must not carry fpr=/fp_sid= tracking parameters
  - no hardcoded Apify tokens
  - no leftover REPLACE placeholders from skills/_template
  - warn (stderr, non-fatal) on singular reference/ directories

Online rules (only with --check-actors):
  - actor-id must exist on the Apify Store, be public, and not deprecated
    (unauthenticated GET https://api.apify.com/v2/acts/{owner}~{name});
    API unavailability is reported as a warning, never as a failure.
  - (warning only) a documented `--input '{...}'` / `-i '{...}'` JSON value
    next to an actor invocation is compared against that actor's default
    build input schema (GET .../builds/default); fields not in the schema
    are reported as warnings, never errors. Unparseable or absent examples,
    and API unavailability, are skipped silently.

Usage:
  uv run scripts/lint_references.py                      # offline, all skills
  uv run scripts/lint_references.py skills/apify-foo     # offline, one skill
  uv run scripts/lint_references.py --check-actors       # + online, all skills
  uv run scripts/lint_references.py skills/apify-foo --check-actors skills/apify-foo
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

# Skill directories that exist for tooling/templates, not for discovery.
EXCLUDED_DIRS = {"_template"}

APIFY_API_BASE = "https://api.apify.com/v2/acts"
API_TIMEOUT = 10  # seconds per request
API_RETRIES = 2  # extra attempts on network errors / 5xx
API_USER_AGENT = "apify-awesome-skills/lint_references"

TOKEN_RE = re.compile(r"apify_api_[A-Za-z0-9]{20,}")
PLUGIN_ROOT_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_.\-/]+)")
# Run commands: skip flag tokens (--env-file=.env, -m, ...) and require a
# relative script path with a known extension so prose never matches.
RUN_CMD_RE = re.compile(
    r"\b(?:node|python3|python|bash|sh)\s+"
    r"(?:--?[A-Za-z0-9_.=\-/]+\s+)*"
    r"([A-Za-z0-9_][A-Za-z0-9_.\-/]*\.(?:js|mjs|cjs|py|sh))\b"
)
CLI_ACTOR_RE = re.compile(
    r"apify\s+actors?\s+(?:call|info|start)\s+\"?([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)\"?"
)
ACTOR_FLAG_RE = re.compile(r"--actor[=\s]+\"?([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)\"?")
ACTOR_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*$")
URL_RE = re.compile(r"https?://[^\s<>\"'`\\)\]]+")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
REPLACE_RE = re.compile(r"\bREPLACE\b")
# Table cells that are exactly a backticked id (or a comma-separated list of
# them) — the actor routing-table shape used across skills.
TABLE_CELL_IDS_RE = re.compile(r"^`[^`]+`(?:\s*,\s*`[^`]+`)*$")
BACKTICKED_RE = re.compile(r"`([^`]+)`")

# apify.com first path segments that are site sections, not actor owners.
RESERVED_STORE_SEGMENTS = {
    "about", "account", "actors", "affiliate", "alternatives", "api", "blog",
    "change-log", "community", "console", "contact", "contact-sales",
    "dashboard", "docs", "ideas", "industries", "integrations", "jobs",
    "legal", "library", "login", "marketplace", "partners", "platform",
    "pricing", "privacy", "professional-services", "protocols", "proxy",
    "resources", "settings", "sign-in", "sign-up", "storage", "store",
    "success-stories", "templates", "terms", "use-cases", "v2", "web-scraping",
}

# Owner-like prefixes that produce false-positive actor ids in table cells
# (MIME types, LLM model ids, subreddit shorthand). Calibrated against the
# repo: `application/json`, `openai/gpt-4o-mini`, `r/productivity` must never
# be reported as actors.
NON_ACTOR_OWNERS = {
    "anthropic", "application", "audio", "deepseek", "font", "google", "image",
    "message", "meta-llama", "mistralai", "model", "multipart", "openai",
    "r", "text", "u", "video",
}

# Backticked relative file paths in table cells look like actor ids
# (`reference/multi-module-playbook.md`) — reject by extension and by
# doc-directory owner segments.
NON_ACTOR_EXTENSIONS = (
    ".md", ".js", ".mjs", ".cjs", ".py", ".sh", ".json", ".txt", ".yml",
    ".yaml", ".csv", ".html", ".ts",
)
NON_ACTOR_PATH_OWNERS = {"reference", "references", "scripts", "examples", "docs", "skills"}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def resolve_skill_dir(arg: str) -> Path:
    """Normalize a CLI skill-dir argument to an existing skills/<name> path."""
    p = Path(arg)
    candidates = [p if p.is_absolute() else ROOT / p, SKILLS_DIR / p.name]
    for candidate in candidates:
        if candidate.is_dir() and candidate.parent == SKILLS_DIR:
            return candidate
    raise SystemExit(f"error: '{arg}' is not a skill directory under skills/")


def iter_skill_dirs(selected: list[str]) -> list[Path]:
    if selected:
        return [resolve_skill_dir(arg) for arg in selected]
    return sorted(
        d for d in SKILLS_DIR.iterdir()
        if d.is_dir() and d.name not in EXCLUDED_DIRS
    )


def collect_md_files(skill_dir: Path) -> list[Path]:
    files: list[Path] = []
    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        files.append(skill_md)
    for ref_dir_name in ("references", "reference"):
        ref_dir = skill_dir / ref_dir_name
        if ref_dir.is_dir():
            files.extend(sorted(ref_dir.rglob("*.md")))
    return files


def is_placeholder_actor_id(actor_id: str) -> bool:
    """Filter out placeholder ids like nexgendata/SLUG or apify/REPLACE-actor."""
    if "REPLACE" in actor_id:
        return True
    owner, name = actor_id.split("/", 1)
    return bool(
        re.fullmatch(r"[A-Z0-9_]+", owner) or re.fullmatch(r"[A-Z0-9_]+", name)
    )


def valid_actor_id(actor_id: str) -> bool:
    if actor_id.count("/") != 1 or not ACTOR_ID_RE.fullmatch(actor_id):
        return False
    if is_placeholder_actor_id(actor_id):
        return False
    owner, name = actor_id.split("/", 1)
    if name.lower().endswith(NON_ACTOR_EXTENSIONS):
        return False
    if owner.lower() in NON_ACTOR_PATH_OWNERS:
        return False
    return owner.lower() not in NON_ACTOR_OWNERS


def clean_url(url: str) -> str:
    return url.rstrip(".,;:!?")


def store_url_actor_id(url: str) -> str | None:
    """Return owner/name for apify.com/<owner>/<name> store URLs, else None."""
    parts = urllib.parse.urlsplit(url)
    if parts.hostname not in {"apify.com", "www.apify.com"}:
        return None
    segments = [s for s in parts.path.split("/") if s]
    if len(segments) < 2 or segments[0].lower() in RESERVED_STORE_SEGMENTS:
        return None
    actor_id = f"{segments[0]}/{segments[1]}"
    return actor_id if valid_actor_id(actor_id) else None


def is_apify_url(url: str) -> bool:
    hostname = urllib.parse.urlsplit(url).hostname or ""
    return hostname == "apify.com" or hostname.endswith(".apify.com")


def extract_refs(skill_dir: Path, path: Path) -> dict[str, list[tuple[str, Path, int]]]:
    """Extract typed references from one markdown file.

    Returns {"repo-path": [...], "actor-id": [...], "apify-url": [...]} where
    each entry is (value, file, line). Tracking-parameter values keep the full
    URL; actor ids are owner/name; repo paths are relative to the skill dir.
    """
    refs: dict[str, list[tuple[str, Path, int]]] = {
        "repo-path": [],
        "actor-id": [],
        "apify-url": [],
    }
    in_fence = False
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue

        for match in PLUGIN_ROOT_RE.finditer(line):
            refs["repo-path"].append((match.group(1), path, lineno))

        if in_fence:
            for match in RUN_CMD_RE.finditer(line):
                refs["repo-path"].append((match.group(1), path, lineno))
            for match in ACTOR_FLAG_RE.finditer(line):
                if valid_actor_id(match.group(1)):
                    refs["actor-id"].append((match.group(1), path, lineno))

        for match in CLI_ACTOR_RE.finditer(line):
            if valid_actor_id(match.group(1)):
                refs["actor-id"].append((match.group(1), path, lineno))

        for match in URL_RE.finditer(line):
            url = clean_url(match.group(0))
            if not is_apify_url(url):
                continue
            refs["apify-url"].append((url, path, lineno))
            actor_id = store_url_actor_id(url)
            if actor_id:
                refs["actor-id"].append((actor_id, path, lineno))

        if not in_fence and line.lstrip().startswith("|") and line.count("|") >= 2:
            for cell in line.strip().strip("|").split("|"):
                cell = cell.strip()
                if not TABLE_CELL_IDS_RE.fullmatch(cell):
                    continue
                for token in BACKTICKED_RE.findall(cell):
                    if valid_actor_id(token):
                        refs["actor-id"].append((token, path, lineno))

    return refs


def scan_tokens(skill_dir: Path) -> list[tuple[Path, int]]:
    """Find hardcoded Apify tokens anywhere in the skill's files."""
    hits: list[tuple[Path, int]] = []
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        text = path.read_bytes().decode("utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), 1):
            if TOKEN_RE.search(line):
                hits.append((path, lineno))
    return hits


def check_repo_paths(skill_dir: Path, repo_paths: list[tuple[str, Path, int]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for ref_path, path, lineno in repo_paths:
        if ref_path in seen:
            continue
        seen.add(ref_path)
        if not (skill_dir / ref_path).exists():
            errors.append(
                f"{rel(path)}:{lineno}: references '{ref_path}' which does not "
                "exist in the repo — ship the file in the same PR or remove the "
                "instruction (never point a token at undelivered code)"
            )
    return errors


def check_tracking_params(apify_urls: list[tuple[str, Path, int]]) -> list[str]:
    # Policy (2026-08-11): affiliate params are allowed with disclosure — this
    # is a warning, not an error. Final call rests with the Apify maintainers.
    warnings: list[str] = []
    for url, path, lineno in apify_urls:
        params = [p for p in ("fpr=", "fp_sid=") if p in url]
        if params:
            warnings.append(
                f"{rel(path)}:{lineno}: Apify URL carries affiliate/referral "
                f"parameter '{params[0].rstrip('=')}' — allowed, but the skill "
                "must disclose the author's financial interest (see CONTRIBUTING)"
            )
    return warnings


def check_replace_placeholders(md_files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in md_files:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if REPLACE_RE.search(line):
                errors.append(
                    f"{rel(path)}:{lineno}: leftover 'REPLACE' placeholder from "
                    "skills/_template — fill in the real value before submitting"
                )
    return errors


def fetch_actor_status(actor_id: str) -> tuple[str, dict | None, str]:
    """Return (status, data, detail); status: ok | missing | unavailable."""
    owner, name = actor_id.split("/", 1)
    url = f"{APIFY_API_BASE}/{urllib.parse.quote(owner)}~{urllib.parse.quote(name)}"
    detail = ""
    for attempt in range(1 + API_RETRIES):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": API_USER_AGENT})
            with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
                data = json.load(response).get("data") or {}
                return "ok", data, ""
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return "missing", None, ""
            detail = f"HTTP {exc.code}"  # 429/5xx — retry, then report unavailable
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            detail = str(getattr(exc, "reason", exc))
        if attempt < API_RETRIES:
            time.sleep(1)
    return "unavailable", None, detail


def check_actors_online(
    actor_refs: list[tuple[str, Path, int]],
) -> tuple[list[str], list[str]]:
    """Check each unique actor id against the Apify API."""
    errors: list[str] = []
    warnings: list[str] = []
    first_seen: dict[str, tuple[Path, int]] = {}
    for actor_id, path, lineno in actor_refs:
        first_seen.setdefault(actor_id, (path, lineno))

    for actor_id, (path, lineno) in sorted(first_seen.items()):
        status, data, detail = fetch_actor_status(actor_id)
        location = f"{rel(path)}:{lineno}"
        if status == "missing":
            errors.append(
                f"{location}: actor '{actor_id}' does not exist on Apify Store "
                "— replace it with a live actor or drop the reference"
            )
        elif status == "unavailable":
            warnings.append(
                f"warning: could not verify actor '{actor_id}' ({detail or 'network error'}) "
                "— Apify API unreachable, skipping this check"
            )
        elif data is not None:
            if data.get("isPublic") is False:
                errors.append(
                    f"{location}: actor '{actor_id}' is not public on Apify Store "
                    "— skills must only reference public Store actors"
                )
            if data.get("isDeprecated") is True:
                errors.append(
                    f"{location}: actor '{actor_id}' is deprecated on Apify Store "
                    "— replace it with a maintained alternative"
                )
    return errors, warnings


# --- Input-schema check (warning only, --check-actors mode) ---------------
#
# For each actor already being verified online, fetch its default build's
# input schema and compare it against any `--input '{...}'` / `-i '{...}'`
# JSON documented next to an invocation of that actor in fenced code. Fields
# the actor's current schema doesn't recognize are reported as warnings —
# never errors, since the schema can legitimately change independently of
# the skill doc, and this check's extraction is necessarily heuristic.

INPUT_FLAG_RE = re.compile(r"(?:--input|-i)\s+'")
INPUT_FILE_RE = re.compile(r"--input-file\b")
INPUT_SEARCH_SPAN = 3  # lines below the actor-id line to look for --input/-i
INPUT_JSON_MAX_LINES = 60  # safety cap collecting a multiline quoted JSON value


def fetch_input_schema_properties(actor_id: str) -> set[str] | None:
    """Return the default build's top-level input property names, or None to
    skip this actor (network error, missing build, or absent/malformed
    inputSchema — all treated as "can't verify, don't warn")."""
    owner, name = actor_id.split("/", 1)
    url = f"{APIFY_API_BASE}/{urllib.parse.quote(owner)}~{urllib.parse.quote(name)}/builds/default"
    for attempt in range(1 + API_RETRIES):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": API_USER_AGENT})
            with urllib.request.urlopen(request, timeout=API_TIMEOUT) as response:
                data = json.load(response).get("data") or {}
                raw_schema = data.get("inputSchema")
                if not raw_schema:
                    return None
                schema = json.loads(raw_schema)
                properties = schema.get("properties")
                return set(properties.keys()) if isinstance(properties, dict) else None
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            # 429/5xx — retry, then give up silently.
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError):
            pass
        if attempt < API_RETRIES:
            time.sleep(1)
    return None


def compute_fence_flags(lines: list[str]) -> list[bool]:
    """Per-line: True if the line sits inside a fenced code block (the fence
    marker lines themselves are False)."""
    flags: list[bool] = []
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            flags.append(False)
            continue
        flags.append(in_fence)
    return flags


def extract_quoted_value(lines: list[str], start_idx: int, start_col: int) -> str | None:
    """Collect text after an opening quote up to the matching closing quote,
    possibly spanning multiple lines. None if no closing quote is found
    within INPUT_JSON_MAX_LINES."""
    parts: list[str] = []
    for i in range(start_idx, min(start_idx + INPUT_JSON_MAX_LINES, len(lines))):
        segment = lines[i][start_col:] if i == start_idx else lines[i]
        q = segment.find("'")
        if q != -1:
            parts.append(segment[:q])
            return "\n".join(parts)
        parts.append(segment)
    return None


def find_input_json(
    lines: list[str], fence_flags: list[bool], anchor_idx: int
) -> tuple[dict, int] | None:
    """Look from the actor-id line (anchor_idx, 0-based) up to
    INPUT_SEARCH_SPAN lines below it, staying inside the fenced block, for a
    `--input '...'` / `-i '...'` value. Returns (parsed dict, 0-based line
    index of the flag), or None if none is found or it doesn't parse cleanly
    as JSON (placeholders, etc. — silently skipped, never reported)."""
    limit = min(anchor_idx + INPUT_SEARCH_SPAN, len(lines) - 1)
    for k in range(anchor_idx, limit + 1):
        if not fence_flags[k]:
            break
        line = lines[k]
        if INPUT_FILE_RE.search(line):
            continue
        match = INPUT_FLAG_RE.search(line)
        if not match:
            continue
        raw = extract_quoted_value(lines, k, match.end())
        if raw is None:
            return None
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return None
        return (parsed, k) if isinstance(parsed, dict) else None
    return None


def check_input_schema(actor_occurrences: list[tuple[str, Path, int]]) -> list[str]:
    """Warn (never error, never network-fatal) when a documented --input/-i
    JSON references a field absent from the actor's current input schema."""
    warnings: list[str] = []
    schema_cache: dict[str, set[str] | None] = {}
    file_cache: dict[Path, tuple[list[str], list[bool]]] = {}
    seen: set[tuple[str, Path, int]] = set()

    for actor_id, path, lineno in actor_occurrences:
        key = (actor_id, path, lineno)
        if key in seen:
            continue
        seen.add(key)

        if actor_id not in schema_cache:
            schema_cache[actor_id] = fetch_input_schema_properties(actor_id)
        properties = schema_cache[actor_id]
        if properties is None:
            continue

        if path not in file_cache:
            lines = path.read_text(encoding="utf-8").splitlines()
            file_cache[path] = (lines, compute_fence_flags(lines))
        lines, fence_flags = file_cache[path]

        anchor_idx = lineno - 1
        if anchor_idx >= len(lines) or not fence_flags[anchor_idx]:
            continue  # actor mention isn't inside a fenced code block

        found = find_input_json(lines, fence_flags, anchor_idx)
        if found is None:
            continue
        parsed, flag_idx = found

        for field in parsed:
            if field not in properties:
                warnings.append(
                    f"warning: {rel(path)}:{flag_idx + 1}: input field '{field}' "
                    f"is not in {actor_id}'s current input schema — the actor "
                    "will ignore or reject it; check `apify actors info "
                    f"{actor_id} --input`"
                )
    return warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "skills", nargs="*", metavar="SKILL_DIR",
        help="skill directories to lint (default: all under skills/)",
    )
    parser.add_argument(
        "--check-actors", nargs="*", metavar="SKILL_DIR", default=None,
        help="also verify actor references online for these skill dirs "
             "(no dirs = all linted skills)",
    )
    args = parser.parse_args()

    skill_dirs = iter_skill_dirs(args.skills)
    if args.check_actors is None:
        online_dirs: set[Path] = set()
    elif args.check_actors:
        online_dirs = set(resolve_skill_dir(arg) for arg in args.check_actors)
    else:
        online_dirs = set(skill_dirs)

    errors: list[str] = []
    warnings: list[str] = []
    online_actor_refs: list[tuple[str, Path, int]] = []
    files_scanned = 0

    for skill_dir in sorted(set(skill_dirs) | online_dirs):
        md_files = collect_md_files(skill_dir)
        files_scanned += len(md_files)

        repo_paths: list[tuple[str, Path, int]] = []
        actor_refs: list[tuple[str, Path, int]] = []
        apify_urls: list[tuple[str, Path, int]] = []
        for md_file in md_files:
            refs = extract_refs(skill_dir, md_file)
            repo_paths.extend(refs["repo-path"])
            actor_refs.extend(refs["actor-id"])
            apify_urls.extend(refs["apify-url"])

        if skill_dir in set(skill_dirs):
            errors.extend(check_repo_paths(skill_dir, repo_paths))
            warnings.extend(
                f"warning: {w}" for w in check_tracking_params(apify_urls)
            )
            if skill_dir.name not in EXCLUDED_DIRS:
                errors.extend(check_replace_placeholders(md_files))
            for path, lineno in scan_tokens(skill_dir):
                errors.append(
                    f"{rel(path)}:{lineno}: hardcoded Apify token — remove it; "
                    "skills must never contain credentials"
                )
            if (skill_dir / "reference").is_dir():
                warnings.append(
                    f"warning: {rel(skill_dir)}/reference: singular 'reference/' "
                    "directory — prefer 'references/' to match skills/_template"
                )

        if skill_dir in online_dirs:
            online_actor_refs.extend(actor_refs)

    if online_actor_refs:
        online_errors, online_warnings = check_actors_online(online_actor_refs)
        errors.extend(online_errors)
        warnings.extend(online_warnings)
        warnings.extend(check_input_schema(online_actor_refs))

    for warning in warnings:
        print(warning, file=sys.stderr)
    if errors:
        print("Reference lint failed:")
        for error in errors:
            print(f"  - {error}")
        print(f"\nlint: {len(errors)} violation(s) across {files_scanned} file(s).")
        return 1

    print(f"lint: all reference checks passed ({files_scanned} file(s) scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
