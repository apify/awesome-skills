#!/usr/bin/env bash
# lint_telemetry.sh — verify every apify CLI invocation in SKILL.md files
# follows the three telemetry rules from CONTRIBUTING.md:
#   Rule 1 — --user-agent apify-awesome-skills/<skill-name>
#   Rule 2 — --json (or --format json for `datasets get-items`)
#   Rule 3 — 2>/dev/null stderr redirect
# Exception: commands fetching an Actor README (--readme) return markdown,
# not JSON — Rules 2 and 3 do not apply to them (Rule 1 still does).
#
# Checked surfaces (measured 2026-08-12: 27 command lines in the upstream
# catalog lived OUTSIDE fenced blocks — fences alone are not enough):
#   - fenced code blocks (``` ... ```)
#   - indented code blocks (4 spaces / tab — the template itself uses these)
#   - inline code spans in prose, but only when the span carries flags
#     (`apify actors call X --json ...`) — that is a command an agent will
#     copy verbatim. A bare mention like `apify actors call` is documentation
#     and is ignored.
#
# Usage:
#   bash scripts/lint_telemetry.sh                       # all skills
#   bash scripts/lint_telemetry.sh skills/apify-foo ...  # only these dirs/files
#
# Exit 0 if all checks pass, exit 1 if any violation is found.
# Requires bash 4+ (available on all GitHub Actions runners).

set -euo pipefail

FAIL=0
WARN=0
MAX_SPAN=40  # safety cap for a single command extent scan

# Patterns that signal an apify CLI invocation
CLI_PATTERNS=(
  "apify actors call"
  "apify actors run"
  "apify actors info"
  "apify datasets get-items"
  "apify call"
)
# NOTE: `apify run` is deliberately NOT a pattern — it runs an actor locally
# during development and the real CLI has no --json/--user-agent flags there
# (verified against apify-cli 1.7/1.8); demanding them forces broken commands.

# Check one inline code span from prose. Only spans that carry flags are
# commands (an agent copies them verbatim); bare mentions are documentation.
check_inline_span() {
  local file="$1" lineno="$2" span="$3"
  if [[ "$span" != *"--"* && "$span" != *"2>"* ]]; then
    return 0
  fi
  local matched=0 pat rest first
  for pat in "${CLI_PATTERNS[@]}"; do
    if [[ "$span" == *"$pat"* ]]; then
      rest="${span#*"$pat"}"
      first="${rest:0:1}"
      if [[ -z "$first" ]] || [[ ! "$first" =~ [a-zA-Z0-9-] ]]; then
        matched=1
        break
      fi
    fi
  done
  [ "$matched" -eq 0 ] && return 0

  local ua=0 json=0 stderr=0 readme=0 info_input=0 csv=0
  [[ "$span" == *"--user-agent apify-awesome-skills/"* ]] && ua=1
  if [[ "$span" == *"--json"* ]] || [[ "$span" == *"--format json"* ]]; then
    json=1
  fi
  [[ "$span" == *"2>/dev/null"* ]] && stderr=1
  [[ "$span" == *"--readme"* ]] && readme=1
  [[ "$span" == *"--format csv"* ]] && csv=1
  if [[ "$span" == *"apify actors info"* ]] && [[ "$span" == *"--input"* ]]; then
    info_input=1
  fi

  if [ "$ua" -eq 0 ]; then
    echo "lint: $file:$lineno: inline code command missing --user-agent apify-awesome-skills/ flag"
    echo "      offending span: $span"
    FAIL=$(( FAIL + 1 ))
  fi
  if [ "$readme" -eq 0 ] && [ "$info_input" -eq 0 ] && [ "$json" -eq 0 ]; then
    if [ "$csv" -eq 1 ]; then
      echo "lint warning: $file:$lineno: --format csv output — allowed, but make sure the skill handles non-JSON output deliberately (default contract is --json)"
      WARN=$(( WARN + 1 ))
    else
      echo "lint: $file:$lineno: inline code command missing --json flag (or --format json for datasets get-items)"
      echo "      offending span: $span"
      FAIL=$(( FAIL + 1 ))
    fi
  fi
  if [ "$readme" -eq 0 ] && [ "$stderr" -eq 0 ]; then
    echo "lint: $file:$lineno: inline code command missing 2>/dev/null stderr redirect"
    echo "      offending span: $span"
    FAIL=$(( FAIL + 1 ))
  fi
}

# Find SKILL.md files: all under skills/ by default, or only under the
# dirs/files passed as arguments (used by CI to lint just the skills a PR
# changes — pre-existing findings on main are kept as exhibits, decision D2).
SKILL_FILES=()
if [ "$#" -gt 0 ]; then
  for arg in "$@"; do
    if [ -f "$arg" ]; then
      SKILL_FILES+=("$arg")
    elif [ -d "$arg" ]; then
      while IFS= read -r f; do
        SKILL_FILES+=("$f")
      done < <(find "$arg" -name "SKILL.md" | sort)
    else
      echo "lint: $arg: not a file or directory" >&2
      exit 2
    fi
  done
else
  while IFS= read -r f; do
    SKILL_FILES+=("$f")
  done < <(find skills -name "SKILL.md" | sort)
fi

if [ ${#SKILL_FILES[@]} -eq 0 ]; then
  echo "lint: no SKILL.md files found under skills/"
  exit 0
fi

for file in "${SKILL_FILES[@]}"; do
  # Read file lines into indexed array
  idx=0
  unset LINES
  declare -a LINES
  while IFS= read -r raw_line; do
    LINES[$idx]="$raw_line"
    (( idx++ )) || true
  done < "$file"
  total=${#LINES[@]}

  in_code_block=0

  for (( i=0; i<total; i++ )); do
    line="${LINES[$i]}"

    # Track fenced code block boundaries (``` or ~~~)
    if [[ "$line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
      if [ "$in_code_block" -eq 0 ]; then
        in_code_block=1
      else
        in_code_block=0
      fi
      continue
    fi

    # Classify the line: fenced code, indented code (4 spaces / tab outside a
    # fence — the template and several skills write commands this way), or
    # prose. An indented line starting with a list marker is a nested prose
    # list, not code.
    is_code=$in_code_block
    cmd_fenced=$in_code_block
    if [ "$is_code" -eq 0 ] && { [[ "$line" == "    "* ]] || [[ "$line" == $'\t'* ]]; }; then
      stripped="${line#"${line%%[![:space:]]*}"}"
      if [[ ! "$stripped" =~ ^([-*+]|[0-9]+\.)([[:space:]]|$) ]]; then
        is_code=1
      fi
    fi

    if [ "$is_code" -eq 0 ]; then
      # Prose: check inline code spans that carry a full command.
      if [[ "$line" == *'`'* ]]; then
        while IFS= read -r span; do
          span="${span#\`}"
          span="${span%\`}"
          check_inline_span "$file" "$(( i + 1 ))" "$span"
        done < <(grep -oE '`[^`]+`' <<<"$line" || true)
      fi
      continue
    fi

    # Skip shell comment lines
    if [[ "$line" =~ ^[[:space:]]*# ]]; then
      continue
    fi

    # Check if this line contains any CLI trigger pattern. The character after
    # the pattern must not be alphanumeric, so "apify run" does not match
    # "apify runs ls".
    matched=0
    for pat in "${CLI_PATTERNS[@]}"; do
      if [[ "$line" == *"$pat"* ]]; then
        rest="${line#*"$pat"}"
        first="${rest:0:1}"
        if [[ -z "$first" ]] || [[ ! "$first" =~ [a-zA-Z0-9-] ]]; then
          matched=1
          break
        fi
      fi
    done
    [ "$matched" -eq 0 ] && continue

    # Scan the command's own extent: from the command line until the closing
    # fence, a blank line (unless continued with \), or the NEXT CLI command.
    # No fixed cap — multi-line JSON inputs put the flags well past 5 lines,
    # and a fixed window bled flags from adjacent commands into this one.
    found_ua=0
    found_json=0
    found_stderr=0
    has_readme=0
    has_info_input=0
    has_csv=0

    for (( j=i; j<total && j<i+MAX_SPAN; j++ )); do
      window_line="${LINES[$j]}"
      # Stop at the closing fence of the code block
      if [ "$j" -gt "$i" ] && [[ "$window_line" =~ ^[[:space:]]*(\`\`\`|~~~) ]]; then
        break
      fi
      # Indented block context: a non-blank line without the indent means the
      # block ended and prose resumed — its text must not satisfy the flags.
      if [ "$cmd_fenced" -eq 0 ] && [ "$j" -gt "$i" ]; then
        if [[ -n "${window_line// /}" ]] && [[ "$window_line" != "    "* ]] && [[ "$window_line" != $'\t'* ]]; then
          break
        fi
      fi
      # Stop at the next CLI command — its flags must not satisfy this one
      if [ "$j" -gt "$i" ]; then
        next_cmd=0
        for pat in "${CLI_PATTERNS[@]}"; do
          if [[ "$window_line" == *"$pat"* ]]; then
            next_cmd=1
            break
          fi
        done
        [ "$next_cmd" -eq 1 ] && break
      fi
      # Stop at blank lines unless the previous line is a continuation (\)
      if [ "$j" -gt "$i" ]; then
        prev="${LINES[$((j-1))]}"
        if [[ "$prev" != *\\ ]] && [[ -z "${window_line// /}" ]]; then
          break
        fi
      fi
      [[ "$window_line" == *"--user-agent apify-awesome-skills/"* ]] && found_ua=1
      if [[ "$window_line" == *"--json"* ]] || [[ "$window_line" == *"--format json"* ]]; then
        found_json=1
      fi
      [[ "$window_line" == *"2>/dev/null"* ]] && found_stderr=1
      [[ "$window_line" == *"--readme"* ]] && has_readme=1
      [[ "$window_line" == *"--format csv"* ]] && has_csv=1
      if [[ "$line" == *"apify actors info"* ]] && [[ "$window_line" == *"--input"* ]]; then
        has_info_input=1
      fi
    done

    lineno=$(( i + 1 ))
    clean_line="$(printf '%s' "$line" | sed 's/^[[:space:]]*//')"

    if [ "$found_ua" -eq 0 ]; then
      echo "lint: $file:$lineno: missing --user-agent apify-awesome-skills/ flag"
      echo "      offending line: $clean_line"
      FAIL=$(( FAIL + 1 ))
    fi

    # Rule 2 exemptions: --readme returns markdown; `actors info --input`
    # returns the bare input schema (adding --json buries it in the full
    # actor object). CSV export is allowed but downgraded to a warning —
    # the skill must handle non-JSON output deliberately.
    if [ "$has_readme" -eq 0 ] && [ "$has_info_input" -eq 0 ]; then
      if [ "$found_json" -eq 0 ]; then
        if [ "$has_csv" -eq 1 ]; then
          echo "lint warning: $file:$lineno: --format csv output — allowed, but make sure the skill handles non-JSON output deliberately (default contract is --json)"
          WARN=$(( WARN + 1 ))
        else
          echo "lint: $file:$lineno: missing --json flag (or --format json for datasets get-items)"
          echo "      offending line: $clean_line"
          FAIL=$(( FAIL + 1 ))
        fi
      fi
    fi
    if [ "$has_readme" -eq 0 ] && [ "$found_stderr" -eq 0 ]; then
      echo "lint: $file:$lineno: missing 2>/dev/null stderr redirect"
      echo "      offending line: $clean_line"
      FAIL=$(( FAIL + 1 ))
    fi
  done
done

# Full URL when running in CI; plain filename locally (the file is present there).
if [ -n "${GITHUB_SERVER_URL:-}" ] && [ -n "${GITHUB_REPOSITORY:-}" ]; then
  CONTRIB_REF="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY/blob/main/CONTRIBUTING.md"
else
  CONTRIB_REF="CONTRIBUTING.md"
fi

if [ "$FAIL" -gt 0 ]; then
  echo ""
  echo "lint: $FAIL violation(s) found."
  echo "      Every apify CLI call in SKILL.md — fenced or indented code"
  echo "      blocks, and inline code spans that carry flags — must include:"
  echo "        --user-agent apify-awesome-skills/<skill-dir-name>"
  echo "        --json (or --format json for datasets get-items)"
  echo "        2>/dev/null"
  echo "      Place each flag on the apify command line itself or on its"
  echo "      continuation lines (before the next command or blank line)."
  echo "      Exceptions: --readme commands are exempt from --json and 2>/dev/null;"
  echo "      'actors info --input' (schema fetch) is exempt from --json;"
  echo "      --format csv is a warning, not an error."
  echo "      See $CONTRIB_REF § 'Telemetry on CLI commands' for details."
  exit 1
fi

[ "$WARN" -gt 0 ] && echo "lint: $WARN warning(s) — see above."
echo "lint: all SKILL.md telemetry checks passed."
exit 0
