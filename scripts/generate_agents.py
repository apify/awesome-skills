#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generate agents/AGENTS.md and the README skills table from SKILL.md frontmatter.

Also validates that .claude-plugin/marketplace.json is in sync with discovered
skills. Fails (exit 1) on hard errors; prints nothing for healthy skills.

Frontmatter fields:
  - name         (required) — must match folder name, kebab-case, apify- prefix
  - description  (required) — max 1024 chars per agentskills.io spec
  - author       (optional) — free string
  - author_url   (optional) — must be a valid http(s) URL if present

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


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse a minimal YAML-ish frontmatter block without external deps.

    Supports:
      - Single-line scalars:        key: value
      - Folded scalars over lines:  key: >- ... (joined with single spaces)
    """
    match = re.search(r"^---\s*\n(.*?)\n---\s*", text, re.DOTALL)
    if not match:
        return {}

    data: dict[str, str] = {}
    lines = match.group(1).splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" not in line:
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

        data[key] = value
        i += 1
    return data


def collect_skills() -> list[dict[str, str]]:
    """Discover all SKILL.md files under skills/ (excluding _template, etc.).

    Used by the validator (validate_marketplace_sync) to cross-check filesystem
    against marketplace.json. NOT used by the doc generators — those iterate
    marketplace.json directly via plugins_to_rows() so nested-plugin entries
    (e.g. apify-financial-services with skills=["./skills"]) are surfaced as a
    single parent row rather than missed.
    """
    skills: list[dict[str, str]] = []
    for skill_md in SKILLS_DIR.glob("*/SKILL.md"):
        folder = skill_md.parent.name
        if folder in EXCLUDED_DIRS:
            continue
        meta = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        skills.append(
            {
                "folder": folder,
                "name": meta.get("name", ""),
                "description": meta.get("description", ""),
                "author": meta.get("author", ""),
                "author_url": meta.get("author_url", ""),
                "path": str(skill_md.parent.relative_to(ROOT)),
            }
        )
    return sorted(skills, key=lambda s: s["name"].lower())


def _read_frontmatter_file(path: Path) -> dict[str, str]:
    """Read frontmatter from a SKILL.md (returns empty dict if missing)."""
    if not path.is_file():
        return {}
    return parse_frontmatter(path.read_text(encoding="utf-8"))


def plugins_to_rows(plugins: list[dict]) -> list[dict[str, str]]:
    """Convert marketplace.json plugin entries to renderable row dicts.

    One row per plugin entry, regardless of flat vs nested layout. This is the
    single source of truth for both agents/AGENTS.md and the README skills
    table. Description and author info prefer the SKILL.md frontmatter when
    available (richer, includes trigger phrases), falling back to
    marketplace.json's `description` for nested plugins where there's no
    parent-level SKILL.md.
    """
    rows: list[dict[str, str]] = []
    for plugin in plugins:
        name = plugin.get("name", "")
        source = plugin.get("source", "")
        source_rel = source.lstrip("./")
        source_dir = ROOT / source_rel
        skills_field = plugin.get("skills", "./")

        is_nested = isinstance(skills_field, list)

        description = ""
        author = ""
        author_url = ""
        if is_nested:
            # Nested plugin: no parent SKILL.md. Use marketplace.json description.
            # Link to the source directory so users can browse the nested layout.
            description = plugin.get("description", "")
            path_link = f"{source_rel}/"
        else:
            # Flat plugin: read the SKILL.md frontmatter for the richer
            # description + author attribution.
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
                "nested": "1" if is_nested else "",
            }
        )

    return sorted(rows, key=lambda r: r["name"].lower())


def render_template(template: str, rows: list[dict[str, str]]) -> str:
    """Tiny Mustache-like renderer for the {{#skills}}...{{/skills}} loop.

    `rows` come from plugins_to_rows() — one row per marketplace.json plugin.
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


def load_marketplace() -> dict:
    if not MARKETPLACE_PATH.exists():
        raise FileNotFoundError(f"marketplace.json not found at {MARKETPLACE_PATH}")
    return json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))


def generate_readme_table(rows: list[dict[str, str]]) -> str:
    """Render the README skills table with an Author column.

    `rows` come from plugins_to_rows() — one row per marketplace.json plugin.
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


def validate_skills(skills: list[dict[str, str]]) -> list[str]:
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

    return errors


def validate_marketplace_sync(skills: list[dict[str, str]]) -> list[str]:
    errors: list[str] = []
    marketplace = load_marketplace()
    plugins = marketplace.get("plugins", [])

    skill_by_source = {f"./{s['path']}": s for s in skills}
    plugin_by_source = {p["source"]: p for p in plugins}

    for skill in skills:
        expected_source = f"./{skill['path']}"
        if expected_source not in plugin_by_source:
            errors.append(
                f"Skill '{skill['name']}' at '{skill['path']}' is missing "
                "from .claude-plugin/marketplace.json"
            )
        elif plugin_by_source[expected_source]["name"] != skill["name"]:
            errors.append(
                f"Name mismatch at '{expected_source}': "
                f"SKILL.md='{skill['name']}', "
                f"marketplace.json='{plugin_by_source[expected_source]['name']}'"
            )

    for plugin in plugins:
        skills_field = plugin.get("skills")
        source = plugin["source"]
        source_path = ROOT / source.lstrip("./")

        if isinstance(skills_field, list):
            # Nested-plugin layout. Validate each nested skills directory has
            # at least one sub-skill (i.e. <source>/<subdir>/*/SKILL.md).
            for subdir in skills_field:
                nested_root = source_path / subdir.lstrip("./")
                if not nested_root.is_dir():
                    errors.append(
                        f"Marketplace plugin '{plugin['name']}' references "
                        f"missing nested directory '{nested_root}'"
                    )
                    continue
                sub_skills = list(nested_root.glob("*/SKILL.md"))
                if not sub_skills:
                    errors.append(
                        f"Marketplace plugin '{plugin['name']}' has no sub-skills "
                        f"under '{nested_root}'"
                    )
            continue

        # Flat-skill layout (skills is "./" or absent).
        if source not in skill_by_source:
            errors.append(
                f"Marketplace plugin '{plugin['name']}' at '{plugin['source']}' "
                "has no SKILL.md"
            )

    return errors


def main() -> int:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    skills = collect_skills()

    errors = validate_skills(skills) + validate_marketplace_sync(skills)
    if errors:
        print("Validation failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    # Docs are driven by marketplace.json — one row per plugin entry, so
    # nested-plugin layouts (e.g. apify-financial-services) appear as a single
    # parent row rather than being skipped by the filesystem walk.
    marketplace = load_marketplace()
    rows = plugins_to_rows(marketplace.get("plugins", []))

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_template(template, rows), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} ({len(rows)} plugins).")

    if update_readme(rows):
        print(f"Updated {README_PATH.relative_to(ROOT)} skills table.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
