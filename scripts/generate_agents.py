#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate .claude-plugin/marketplace.json, agents/AGENTS.md and the README
skills table from SKILL.md frontmatter.

SKILL.md frontmatter is the single source of truth; the marketplace catalog and
docs are derived artifacts. Fails (exit 1) on hard errors; prints nothing for
healthy skills.

Frontmatter fields:
  - name              (required) — must match folder name, kebab-case, apify- prefix
  - description       (required) — max 1024 chars per agentskills.io spec
  - author            (optional) — free string
  - author_url        (optional) — must be a valid http(s) URL if present
  - metadata          (required) — nested map:
      - keywords      (required) — comma-separated string, e.g. "seo, pricing"
      - category      (optional) — defaults to DEFAULT_CATEGORY

Usage:
  uv run scripts/generate_agents.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "scripts" / "AGENTS_TEMPLATE.md"
OUTPUT_PATH = ROOT / "agents" / "AGENTS.md"
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
README_PATH = ROOT / "README.md"
SKILLS_DIR = ROOT / "skills"

README_TABLE_START = "<!-- BEGIN_SKILLS_TABLE -->"
README_TABLE_END = "<!-- END_SKILLS_TABLE -->"

DESCRIPTION_MAX_CHARS = 1024
NAME_PATTERN = re.compile(r"^apify-[a-z0-9]+(-[a-z0-9]+)*$")
URL_PATTERN = re.compile(r"^https?://[^\s]+$")

# Skill directories that exist for tooling/templates, not for discovery.
EXCLUDED_DIRS = {"_template"}

MARKETPLACE_NAME = "awesome-skills"
MARKETPLACE_OWNER = {
    "name": "Apify Community",
    "email": "support@apify.com",
}
MARKETPLACE_METADATA = {
    "description": "Community collection of Apify agent skills for web scraping, data extraction, and automation",
    "version": "1.0.0",
}
DEFAULT_CATEGORY = "data-extraction"

def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> dict:
    """Parse a minimal YAML-ish frontmatter block without external deps.

    Supports:
      - Single-line scalars:        key: value
      - Folded scalars over lines:  key: >- ... (joined with single spaces)
      - One level of nested maps:   key: followed by indented `sub: value` pairs
    """
    match = re.search(r"^---\s*\n(.*?)\n---\s*", text, re.DOTALL)
    if not match:
        return {}

    data: dict = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line or line.startswith((" ", "\t")):
            i += 1
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()

        if value in {">-", ">", "|", "|-"}:
            # Folded/block scalar — collect indented continuation lines
            parts: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or lines[i] == ""):
                stripped = lines[i].strip()
                if stripped:
                    parts.append(stripped)
                i += 1
            data[key] = " ".join(parts)
            continue

        if value == "":
            # Nested map — collect indented `sub: value` pairs
            nested: dict[str, str] = {}
            i += 1
            while i < len(lines) and lines[i].startswith((" ", "\t")) and ":" in lines[i]:
                sub_key, sub_value = lines[i].split(":", 1)
                nested[sub_key.strip()] = _strip_quotes(sub_value.strip())
                i += 1
            data[key] = nested
            continue

        data[key] = value
        i += 1
    return data


def collect_skills() -> list[dict]:
    """Discover all SKILL.md files under skills/ (excluding _template, etc.).

    Directories without a top-level SKILL.md are not silently skipped — they
    fail layout_errors(). There are no special cases: a directory that does
    not fit the model is resolved by a maintainer in the PR that carries it.
    """
    skills: list[dict] = []
    for skill_md in SKILLS_DIR.glob("*/SKILL.md"):
        folder = skill_md.parent.name
        if folder in EXCLUDED_DIRS:
            continue
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        metadata = meta.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        skills.append(
            {
                "folder": folder,
                "name": meta.get("name", ""),
                "description": meta.get("description", ""),
                "author": meta.get("author", ""),
                "author_url": meta.get("author_url", ""),
                "metadata": metadata,
                "path": str(skill_md.parent.relative_to(ROOT)),
            }
        )
    return sorted(skills, key=lambda s: s["name"].lower())


def layout_errors() -> list[str]:
    """Every directory under skills/ must carry a top-level SKILL.md.

    The catalog is generated from that frontmatter; a directory without it
    (e.g. a nested plugin bundle) cannot be derived and fails the build
    loudly instead of being special-cased in code.
    """
    errors: list[str] = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.name in EXCLUDED_DIRS:
            continue
        if not (entry / "SKILL.md").is_file():
            errors.append(
                f"skills/{entry.name}/: no top-level SKILL.md — every skill "
                "directory must carry one (the catalog is generated from its "
                "frontmatter). Nested plugin bundles are not supported: add a "
                "SKILL.md, restructure into flat skills, or remove the directory."
            )
    return errors


def build_marketplace(skills: list[dict]) -> dict:
    """Build the marketplace.json document from SKILL.md frontmatter."""
    plugins: list[dict] = []
    for skill in skills:
        metadata = skill["metadata"]
        keywords = [
            keyword.strip()
            for keyword in metadata.get("keywords", "").split(", ")
            if keyword.strip()
        ]
        plugins.append(
            {
                "name": skill["name"],
                "source": f"./{skill['path']}",
                "skills": "./",
                "description": skill["description"],
                "keywords": keywords,
                "category": metadata.get("category") or DEFAULT_CATEGORY,
            }
        )
    plugins.sort(key=lambda p: p["name"].lower())
    return {
        "name": MARKETPLACE_NAME,
        "owner": dict(MARKETPLACE_OWNER),
        "metadata": dict(MARKETPLACE_METADATA),
        "plugins": plugins,
    }


def _read_frontmatter_file(path: Path) -> dict:
    """Read frontmatter from a SKILL.md (returns empty dict if missing)."""
    if not path.is_file():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def plugins_to_rows(plugins: list[dict]) -> list[dict[str, str]]:
    """Convert marketplace plugin entries to renderable row dicts.

    One row per plugin entry. This is the
    single source of truth for both agents/AGENTS.md and the README skills
    table. Description and author info come from the SKILL.md frontmatter
    (layout_errors() guarantees every entry has one).
    """
    rows: list[dict[str, str]] = []
    for plugin in plugins:
        name = plugin.get("name", "")
        source = plugin.get("source", "")
        source_rel = source.lstrip("./")
        source_dir = ROOT / source_rel

        # Read the SKILL.md frontmatter for the richer description + author
        # attribution (layout_errors() guarantees the file exists).
        meta = _read_frontmatter_file(source_dir / "SKILL.md")
        description = meta.get("description") or plugin.get("description", "")
        author = meta.get("author", "")
        author_url = meta.get("author_url", "")
        path_link = f"{source_rel}/SKILL.md"

        rows.append(
            {
                "name": name,
                "description": description,
                "author": author,
                "author_url": author_url,
                "path_link": path_link,
            }
        )

    return sorted(rows, key=lambda r: r["name"].lower())


def render_template(template: str, rows: list[dict[str, str]]) -> str:
    """Tiny Mustache-like renderer for the {{#skills}}...{{/skills}} loop.

    `rows` come from plugins_to_rows() — one row per marketplace plugin.
    """

    def repl(match: re.Match[str]) -> str:
        block = match.group(1).strip("\n")
        rendered_blocks: list[str] = []
        for row in rows:
            attribution = ""
            if row["author"] and row["author_url"]:
                attribution = f" by [{row['author']}]({row['author_url']})"
            elif row["author"]:
                attribution = f" by {row['author']}"
            rendered = (
                block.replace("{{name}}", row["name"])
                .replace("{{description}}", row["description"])
                .replace("{{path}}", row["path_link"])
                .replace("{{attribution}}", attribution)
            )
            rendered_blocks.append(rendered)
        return "\n".join(rendered_blocks)

    return re.sub(r"{{#skills}}(.*?){{/skills}}", repl, template, flags=re.DOTALL)


def generate_readme_table(rows: list[dict[str, str]]) -> str:
    """Render the README skills table with an Author column.

    `rows` come from plugins_to_rows() — one row per marketplace plugin.
    """
    lines = [
        "| Name | Description | Author |",
        "|------|-------------|--------|",
    ]
    for row in rows:
        name = row["name"]
        description = row["description"]
        doc_link = f"[`{name}`]({row['path_link']})"
        if row["author"] and row["author_url"]:
            author_cell = f"[{row['author']}]({row['author_url']})"
        elif row["author"]:
            author_cell = row["author"]
        else:
            author_cell = "—"
        lines.append(f"| {doc_link} | {description} | {author_cell} |")
    return "\n".join(lines)


def update_readme(rows: list[dict[str, str]]) -> bool:
    if not README_PATH.exists():
        print(f"Warning: README.md not found at {README_PATH}", file=sys.stderr)
        return False

    content = README_PATH.read_text(encoding="utf-8")
    start_idx = content.find(README_TABLE_START)
    end_idx = content.find(README_TABLE_END)

    if start_idx == -1 or end_idx == -1 or end_idx < start_idx:
        print(
            f"Warning: README.md markers {README_TABLE_START}/{README_TABLE_END} "
            "missing or out of order — skills table not regenerated.",
            file=sys.stderr,
        )
        return False

    table = generate_readme_table(rows)
    new_content = (
        content[: start_idx + len(README_TABLE_START)]
        + "\n"
        + table
        + "\n"
        + content[end_idx:]
    )
    if new_content == content:
        return False
    README_PATH.write_text(new_content, encoding="utf-8")
    return True


def validate_skills(skills: list[dict]) -> list[str]:
    """Hard validation. Returns list of error messages (empty = OK)."""
    errors: list[str] = []
    for skill in skills:
        folder = skill["folder"]
        name = skill["name"]
        description = skill["description"]

        if not name:
            errors.append(f"skills/{folder}/SKILL.md: missing 'name' in frontmatter")
            continue
        if not description:
            errors.append(f"skills/{folder}/SKILL.md: missing 'description' in frontmatter")

        if not NAME_PATTERN.match(name):
            errors.append(
                f"skills/{folder}/SKILL.md: name '{name}' must be kebab-case "
                "with 'apify-' prefix (lowercase letters, digits, hyphens)"
            )
        if name != f"apify-{folder.removeprefix('apify-')}":
            # Folder name and `name` must match exactly.
            if name != folder:
                errors.append(
                    f"skills/{folder}/SKILL.md: name '{name}' does not match "
                    f"folder name '{folder}' (they must be identical)"
                )

        if len(description) > DESCRIPTION_MAX_CHARS:
            errors.append(
                f"skills/{folder}/SKILL.md: description is {len(description)} chars "
                f"(max {DESCRIPTION_MAX_CHARS} per agentskills.io spec)"
            )

        author_url = skill["author_url"]
        if author_url and not URL_PATTERN.match(author_url):
            errors.append(
                f"skills/{folder}/SKILL.md: author_url '{author_url}' is not a valid http(s) URL"
            )

        if not skill["metadata"].get("keywords", "").strip():
            errors.append(
                f"skills/{folder}/SKILL.md: missing 'metadata.keywords' — "
                "add a 'metadata:' block to the frontmatter with keywords as "
                'a comma-separated string, e.g. keywords: "kw-one, kw-two"'
            )

    seen: dict[str, str] = {}
    for skill in skills:
        name = skill["name"]
        if not name:
            continue
        origin = f"skills/{skill['folder']}/SKILL.md"
        if name in seen:
            errors.append(
                f"{origin}: duplicate name '{name}' (already used by {seen[name]}) — "
                "skill names must be unique across the marketplace"
            )
        else:
            seen[name] = origin

    return errors


def main() -> int:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    skills = collect_skills()

    errors = layout_errors() + validate_skills(skills)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    marketplace = build_marketplace(skills)
    marketplace_json = json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n"
    if not MARKETPLACE_PATH.exists() or MARKETPLACE_PATH.read_text(encoding="utf-8") != marketplace_json:
        MARKETPLACE_PATH.parent.mkdir(parents=True, exist_ok=True)
        MARKETPLACE_PATH.write_text(marketplace_json, encoding="utf-8")
        print(f"Wrote {MARKETPLACE_PATH.relative_to(ROOT)} ({len(marketplace['plugins'])} plugins).")

    # Docs are driven by the generated plugins list — one row per plugin entry.
    rows = plugins_to_rows(marketplace["plugins"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_template(template, rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} ({len(rows)} plugins).")

    if update_readme(rows):
        print(f"Updated {README_PATH.relative_to(ROOT)} skills table.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
