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
    """Discover all SKILL.md files under skills/ (excluding _template, etc.)."""
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


def render_template(template: str, skills: list[dict[str, str]]) -> str:
    """Tiny Mustache-like renderer for the {{#skills}}...{{/skills}} loop."""

    def repl(match: re.Match[str]) -> str:
        block = match.group(1).strip("\n")
        rendered_blocks: list[str] = []
        for skill in skills:
            attribution = ""
            if skill["author"] and skill["author_url"]:
                attribution = f" by [{skill['author']}]({skill['author_url']})"
            elif skill["author"]:
                attribution = f" by {skill['author']}"
            rendered = (
                block.replace("{{name}}", skill["name"])
                .replace("{{description}}", skill["description"])
                .replace("{{path}}", skill["path"])
                .replace("{{attribution}}", attribution)
            )
            rendered_blocks.append(rendered)
        return "\n".join(rendered_blocks)

    return re.sub(r"{{#skills}}(.*?){{/skills}}", repl, template, flags=re.DOTALL)


def load_marketplace() -> dict:
    if not MARKETPLACE_PATH.exists():
        raise FileNotFoundError(f"marketplace.json not found at {MARKETPLACE_PATH}")
    return json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))


def generate_readme_table(skills: list[dict[str, str]]) -> str:
    """Render the README skills table with an Author column."""
    lines = [
        "| Name | Description | Author |",
        "|------|-------------|--------|",
    ]
    for skill in skills:
        name = skill["name"]
        description = skill["description"]
        doc_link = f"[`{name}`]({skill['path']}/SKILL.md)"
        if skill["author"] and skill["author_url"]:
            author_cell = f"[{skill['author']}]({skill['author_url']})"
        elif skill["author"]:
            author_cell = skill["author"]
        else:
            author_cell = "—"
        lines.append(f"| {doc_link} | {description} | {author_cell} |")
    return "\n".join(lines)


def update_readme(skills: list[dict[str, str]]) -> bool:
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

    table = generate_readme_table(skills)
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
        if "skills" not in plugin:
            continue
        if plugin["source"] not in skill_by_source:
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

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(render_template(template, skills), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)} ({len(skills)} skills).")

    if update_readme(skills):
        print(f"Updated {README_PATH.relative_to(ROOT)} skills table.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
