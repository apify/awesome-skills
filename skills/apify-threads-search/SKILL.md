---
name: apify-threads-search
description: >-
  Search and verify newly collected public Meta Threads data with Apify. Use when a user asks to search Threads posts by keyword or hashtag, compare top and recent public results, collect public posts from known Threads accounts, or discover public Threads profiles by niche or local phrase. Do not use for reply trees, private or login-only content, publishing or account actions, non-Threads platforms, generic programming threads, hidden contact discovery, exhaustive coverage claims, or analysis that must use only an existing local file. Sentiment and themes are downstream analysis, not scraped fields.
metadata:
  author: FuturizeRush
  author_url: https://github.com/FuturizeRush
---

# Apify Threads Search

Use `futurizerush/meta-threads-scraper` to collect public Threads data, then verify the run, dataset, and `OUTPUT` summary before reporting findings. Treat the results as public data available at collection time, not complete Threads coverage.

## Prerequisites

- An Agent Skills-compatible client that can run shell commands
- An authenticated Apify CLI session
- `jq`
- Node.js

Never put an API token in a URL, command argument, log, or report.

## Choose the workflow

| User goal | Mode | Required input | Notes |
|---|---|---|---|
| Search public posts | `search` | `keywords` | Supports `top` or `recent` |
| Collect posts from known accounts | `user` | `usernames` | Accepts a bare name, `@name`, or a Threads profile URL |
| Discover public accounts | `profiles` | `keywords` | Returns profile rows, with up to 10 matches per keyword |

Current supported inputs:

- `mode`: `user`, `search`, or `profiles`
- `usernames`: 1–20 values in `user` mode
- `keywords`: 1–20 values in `search` and `profiles`; optional in `user` to set `keyword_match`; each query is limited to 100 characters after input cleanup
- `max_posts`: 10–10000 per username or search keyword; profile discovery remains capped at 10 per keyword
- `search_filter`: `top` or `recent`, for `search` only

Use only the inputs listed above. Treat location words as query text, not proof of an author's location. A post's `reply_count` is not the reply text.

## Confirm the scope

Tell the user the exact mode, inputs, sort order, and per-input result limit. Set `max_posts` explicitly and, in `search` mode, set `search_filter` explicitly so the run scope is unambiguous. Explain that public availability and Threads ranking can return fewer rows than requested.

A direct request to collect current Threads data authorizes the run it specifies. An explicit request to compare `top` and `recent` authorizes those two runs with otherwise identical inputs. Ask before running only when a required input or the intended scope is unclear. Any additional run, changed scope, or retry requires separate approval. A request to explain or inspect this skill does not authorize a run.

When comparing `top` and `recent`, keep the keywords and `max_posts` unchanged; change only `search_filter` between the two approved runs.

## Choose search terms

Logged-out public search is ranked, not exhaustive. A niche compound query can return `no_results` even when matching public posts exist, while common phrases of three or more terms can return rows. Do not treat word count as a fixed rule; results can differ across exact phrases, languages, and collection times.

Use the exact approved query for the first run. Do not add quotation marks or reorder its terms. After a verified `no_results`:

1. Confirm the spelling and intended specificity.
2. Propose a shorter common query, such as `Claude Code` after `Claude Code Harness`.
3. For CJK or mixed-language input, offer one distinctive term or a natural compact phrase as the next query.
4. Ask for approval before running the changed query.

For post search, use `keyword_match` and `text_content` to filter broader results. For profile discovery, filter `username`, `display_name`, and `bio`; `search_keyword` records the originating query. Do not impose a fixed word limit or promise that a shorter query will return results.

Example inputs:

```json
{"mode":"user","usernames":["@zuck","https://www.threads.com/@instagram"],"max_posts":20}
```

```json
{"mode":"profiles","keywords":["Taipei coffee roaster"],"max_posts":10}
```

## Prepare the approved input

Create a private working directory and write the exact approved JSON through a quoted heredoc. Run later blocks in the same shell session. If the client opens a new shell, first run `export WORKDIR='<exact printed path>'`; reuse that directory instead of creating a replacement. Do not interpolate user text into shell code.

```bash
set -euo pipefail
umask 077
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/apify-threads-search.XXXXXX")"
export WORKDIR
printf 'Working directory: %s\n' "$WORKDIR"
cat >"$WORKDIR/input.json" <<'JSON'
{"mode":"search","keywords":["AI policy"],"search_filter":"recent","max_posts":10}
JSON

if ! jq -e '
  type == "object"
  and (.mode == "user" or .mode == "search" or .mode == "profiles")
  and (.max_posts | type == "number" and . == floor and . >= 10 and . <= 10000)
  and (if .mode == "user" then
    (.usernames | type == "array" and length >= 1 and length <= 20 and all(.[]; type == "string" and test("\\S")))
    and (if has("keywords") then
      (.keywords | type == "array" and length <= 20 and all(.[]; type == "string" and test("\\S")))
    else true end)
  else
    (.keywords | type == "array" and length >= 1 and length <= 20 and all(.[]; type == "string" and test("\\S")))
  end)
  and (if .mode == "user" then
    ((keys - ["mode", "usernames", "keywords", "max_posts"]) | length == 0)
  elif .mode == "search" then
    ((keys - ["mode", "keywords", "max_posts", "search_filter"]) | length == 0)
  else
    ((keys - ["mode", "keywords", "max_posts"]) | length == 0)
  end)
  and (if .mode == "search" then
    (.search_filter == "top" or .search_filter == "recent")
  else
    (has("search_filter") | not)
  end)
' "$WORKDIR/input.json" >/dev/null; then
  printf 'Input validation failed. Check the mode-specific usernames or keywords, max_posts (10-10000), and search_filter before starting a run.\n' >&2
  exit 1
fi

if ! node 2>/dev/null <<'NODE'
const fs = require('node:fs');

const input = JSON.parse(fs.readFileSync(`${process.env.WORKDIR}/input.json`, 'utf8'));
const dedupe = (values) => [...new Set(values)];
const trimPythonWhitespace = (value) => value.replace(
    /^[\p{White_Space}\u001C-\u001F]+|[\p{White_Space}\u001C-\u001F]+$/gu,
    '',
);
const normalizeKeyword = (value) => {
    const normalized = trimPythonWhitespace(
        value.normalize('NFKC').replace(/[\p{White_Space}\u001C-\u001F]+/gu, ' '),
    );
    return trimPythonWhitespace(normalized.replace(/^#+/u, ''));
};
const normalizeUsername = (raw) => {
    const value = trimPythonWhitespace(raw);
    if (/^(https?:\/\/)?(www\.)?threads\.(com|net)\//iu.test(value)) {
        const url = new URL(value.includes('://') ? value : `https://${value}`);
        if (!['threads.com', 'www.threads.com', 'threads.net', 'www.threads.net'].includes(url.hostname)) return '';
        return url.pathname.match(/\/@([A-Za-z0-9._]+)/u)?.[1] ?? '';
    }
    return trimPythonWhitespace(value.replace(/^@/u, '').split(/[/?]/u, 1)[0]);
};
const keywords = dedupe((input.keywords ?? []).map(normalizeKeyword));
const usernames = dedupe((input.usernames ?? []).map(normalizeUsername));
const invalidKeyword = (value) => !value
    || [...value].length > 100
    || [...value].some((character) => character.codePointAt(0) < 32);
if (keywords.some(invalidKeyword) || usernames.some((value) => !value)) process.exit(1);
const effectiveLimit = input.mode === 'profiles' ? Math.min(input.max_posts, 10) : input.max_posts;
const expectedItems = input.mode === 'user' ? usernames.length : keywords.length;
fs.writeFileSync(`${process.env.WORKDIR}/scope.json`, JSON.stringify({
    mode: input.mode,
    keywords,
    usernames: dedupe(usernames.map((value) => value.toLowerCase())),
    effectiveLimit,
    expectedItems,
    maxRows: effectiveLimit * expectedItems,
    searchFilter: input.search_filter ?? null,
}));
NODE
then
  printf 'Input normalization failed. Check the approved usernames and keywords before starting a run.\n' >&2
  exit 1
fi
```

The Actor performs the final input validation. If startup fails or no run ID is returned, report that no run was confirmed and do not retry automatically. Correct the input only after the user approves a changed run.

## Start exactly one run

Run this block once. Save the returned run ID immediately. If the result is ambiguous, inspect that attempt in Apify Console; do not start another run automatically.

```bash
set -euo pipefail
: "${WORKDIR:?Reuse the directory from the preparation step}"
if ! apify actors start "futurizerush/meta-threads-scraper" \
  --input-file "$WORKDIR/input.json" \
  --json \
  --user-agent apify-awesome-skills/apify-threads-search \
  2>/dev/null >"$WORKDIR/run-start.json"; then
  printf 'The run could not be started; no run ID was confirmed.\n' >&2
  exit 1
fi
if ! RUN_ID="$(jq -er '.run.id | select(type == "string" and length > 0)' "$WORKDIR/run-start.json")"; then
  printf 'The start response did not contain a run ID; no run was confirmed.\n' >&2
  exit 1
fi
printf 'Started run: %s\n' "$RUN_ID"
```

Wait for that run, then fetch its current metadata. Waiting again is safe because it does not create another run.

```bash
set -euo pipefail
: "${WORKDIR:?Reuse the directory from the preparation step}"
RUN_ID="$(jq -er '.run.id | select(type == "string" and length > 0)' "$WORKDIR/run-start.json")"
if ! apify runs wait "$RUN_ID" --timeout 600 --json \
  --user-agent apify-awesome-skills/apify-threads-search \
  2>/dev/null >"$WORKDIR/run-wait.json"; then
  printf 'The run did not reach a successful terminal state during this wait; inspecting the same run ID.\n' >&2
fi
if ! apify runs info "$RUN_ID" --json \
  --user-agent apify-awesome-skills/apify-threads-search \
  2>/dev/null >"$WORKDIR/run.json"; then
  printf 'Could not read run %s. Check the same run ID later; do not start a replacement automatically.\n' "$RUN_ID" >&2
  exit 1
fi
if ! jq -e --arg run_id "$RUN_ID" '
  type == "object"
  and .id == $run_id
  and (.status | type == "string" and length > 0)
' "$WORKDIR/run.json" >/dev/null; then
  printf 'Could not verify metadata for run %s. Check the same run ID later; do not start a replacement automatically.\n' "$RUN_ID" >&2
  exit 1
fi
RUN_STATUS="$(jq -er '.status' "$WORKDIR/run.json")"
if [[ "$RUN_STATUS" == "READY" || "$RUN_STATUS" == "RUNNING" || "$RUN_STATUS" == "TIMING-OUT" || "$RUN_STATUS" == "ABORTING" ]]; then
  printf 'Run %s is still in status %s. Check this same run ID later; do not start a replacement.\n' "$RUN_ID" "$RUN_STATUS" >&2
  exit 1
fi
KVS_ID="$(jq -r '.defaultKeyValueStoreId // empty' "$WORKDIR/run.json")"
OUTPUT_AVAILABLE=false
if [[ -n "$KVS_ID" ]] \
  && apify api GET "/v2/key-value-stores/$KVS_ID/records/OUTPUT" \
  --user-agent apify-awesome-skills/apify-threads-search \
  2>/dev/null >"$WORKDIR/output.json" \
  && jq -e 'type == "object" and (.status | type == "string")' "$WORKDIR/output.json" >/dev/null; then
  OUTPUT_AVAILABLE=true
fi
if [[ "$RUN_STATUS" != "SUCCEEDED" ]]; then
  RUN_MESSAGE="$(jq -r '.statusMessage // ""' "$WORKDIR/run.json")"
  printf 'Run %s ended with status %s. %s\n' "$RUN_ID" "$RUN_STATUS" "$RUN_MESSAGE" >&2
  if [[ "$OUTPUT_AVAILABLE" == true && "$(jq -r '.status' "$WORKDIR/output.json")" == "FAILED" ]]; then
    FAILURE_REASON="$(jq -r '.reason // "unspecified"' "$WORKDIR/output.json")"
    FAILED_ITEMS="$(jq -c '.failed_items // []' "$WORKDIR/output.json")"
    printf 'Run summary reason: %s; failed items: %s\n' "$FAILURE_REASON" "$FAILED_ITEMS" >&2
    if [[ "$FAILURE_REASON" == "invalid_input" ]]; then
      INPUT_ERROR="$(jq -r '.error // "The input was rejected."' "$WORKDIR/output.json")"
      printf 'Input guidance: %s Check the approved JSON and ask before running corrected input. Do not retry it unchanged.\n' "$INPUT_ERROR" >&2
    elif jq -e '
      (.collection_stop_reason? == "temporarily_unavailable")
      or ([((.failed_reasons? // {}) | to_entries[]? | .value)]
        | any(. == "setup_unavailable"
          or . == "request_timeout"
          or . == "request_unavailable"
          or . == "temporarily_unavailable"))
    ' "$WORKDIR/output.json" >/dev/null; then
      printf 'The summary reports temporary unavailability. Suggest trying the same approved input again later; do not retry automatically.\n' >&2
    else
      printf 'Report the available run summary without guessing the cause; do not retry automatically.\n' >&2
    fi
  else
    printf 'The run summary did not verify the failure cause. Report only the run status and message without guessing; do not retry automatically.\n' >&2
  fi
  exit 1
fi
if [[ "$OUTPUT_AVAILABLE" != true ]]; then
  printf 'The Actor OUTPUT summary is missing or unreadable; the result is not verified.\n' >&2
  exit 1
fi
```

The 600-second timeout limits only the local wait. If it expires, continue checking the same run ID. Never start a replacement run silently.

Handle a failed run from its `OUTPUT` summary when available:

- When `reason` is `invalid_input`, show `error`, compare the approved JSON with the supported inputs above, and propose corrected JSON. Do not retry the unchanged input.
- When `collection_stop_reason` is `temporarily_unavailable`, or `failed_reasons` reports `setup_unavailable`, `request_timeout`, `request_unavailable`, or `temporarily_unavailable`, suggest trying the same approved input again later.
- Otherwise, report the run ID, status, available reason, failed items, and message without guessing the cause.

If `OUTPUT` cannot be read, use only the run status and message and say that the cause was not verified. Do not start any retry or corrected run without approval. A failed run is never `no_results`.

## Verify the result

Fetch the dataset through the authenticated CLI session after the Actor's `OUTPUT` summary has been read:

```bash
set -euo pipefail
: "${WORKDIR:?Reuse the directory from the preparation step}"
RUN_ID="$(jq -er '.run.id | select(type == "string" and length > 0)' "$WORKDIR/run-start.json")"
DATASET_ID="$(jq -r '.defaultDatasetId // empty' "$WORKDIR/run.json")"
if [[ -z "$DATASET_ID" ]]; then
  printf 'Run %s does not provide a readable dataset ID; the result is not verified.\n' "$RUN_ID" >&2
  exit 1
fi
if ! apify datasets get-items "$DATASET_ID" --format json \
  --user-agent apify-awesome-skills/apify-threads-search \
  2>/dev/null >"$WORKDIR/dataset.json"; then
  printf 'Could not read the run dataset; the result is not verified.\n' >&2
  exit 1
fi
if ! jq -e 'type == "array"' "$WORKDIR/dataset.json" >/dev/null; then
  printf 'The run dataset is missing or unreadable; the result is not verified.\n' >&2
  exit 1
fi
```

Check that every row belongs to the approved input, has the expected type and public source URL, stays within the requested limit, and agrees with the Actor summary:

```bash
set -euo pipefail
: "${WORKDIR:?Reuse the directory from the preparation step}"
MODE="$(jq -er '.mode' "$WORKDIR/input.json")"
ROWS="$(jq -er 'length' "$WORKDIR/dataset.json")"
if ! node 2>/dev/null <<'NODE'
const fs = require('node:fs');

const run = JSON.parse(fs.readFileSync(`${process.env.WORKDIR}/run.json`, 'utf8'));
const output = JSON.parse(fs.readFileSync(`${process.env.WORKDIR}/output.json`, 'utf8'));
const dataset = JSON.parse(fs.readFileSync(`${process.env.WORKDIR}/dataset.json`, 'utf8'));
const parseActorIso = (value) => {
    if (typeof value !== 'string') return null;
    const match = value.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d+)?(?:Z|\+00:00)$/u);
    if (!match) return null;
    const epoch = Date.parse(value);
    if (!Number.isFinite(epoch)) return null;
    const date = new Date(epoch);
    const expected = match.slice(1, 7).map(Number);
    const actual = [
        date.getUTCFullYear(), date.getUTCMonth() + 1, date.getUTCDate(),
        date.getUTCHours(), date.getUTCMinutes(), date.getUTCSeconds(),
    ];
    return expected.every((part, index) => part === actual[index]) ? Math.floor(epoch / 1000) : null;
};
const startedAt = new Date(run.startedAt);
const finishedAt = new Date(run.finishedAt);
if (!Number.isFinite(startedAt.getTime()) || !Number.isFinite(finishedAt.getTime())) process.exit(1);
const runWindowStart = Math.floor(startedAt.getTime() / 1000) - 300;
const runWindowEnd = Math.floor(finishedAt.getTime() / 1000) + 300;
const inRunWindow = (value) => value !== null && value >= runWindowStart && value <= runWindowEnd;
if (!inRunWindow(parseActorIso(output.updated_at))) process.exit(1);
if (!Array.isArray(dataset) || dataset.some((row) => !inRunWindow(parseActorIso(row?.scraped_at)))) process.exit(1);
NODE
then
  printf 'The collection timestamps do not match the run time; the result is not verified.\n' >&2
  exit 1
fi
if ! jq -e --arg mode "$MODE" --slurpfile scope "$WORKDIR/scope.json" '
  ($scope[0]) as $approved
  | type == "array"
  and length <= $approved.maxRows
  and all(.[];
    type == "object"
    and (.scraped_at | type == "string")
    and (if $mode == "profiles" then
      .record_type == "profile"
      and (.profile_url | type == "string" and test("^https://(www\\.)?threads\\.(com|net)/@[A-Za-z0-9._]+/?([?#].*)?$"; "i"))
      and (.search_keyword | type == "string" and . as $keyword | $approved.keywords | index($keyword) != null)
    elif $mode == "search" then
      .record_type == "post"
      and (.post_url | type == "string" and test("^https://(www\\.)?threads\\.(com|net)/@[A-Za-z0-9._]+/post/[A-Za-z0-9_-]+/?([?#].*)?$"; "i"))
      and (.search_keyword | type == "string" and . as $keyword | $approved.keywords | index($keyword) != null)
      and .search_filter == $approved.searchFilter
    else
      .record_type == "post"
      and (.post_url | type == "string" and test("^https://(www\\.)?threads\\.(com|net)/@[A-Za-z0-9._]+/post/[A-Za-z0-9_-]+/?([?#].*)?$"; "i"))
      and (.username | type == "string" and ascii_downcase as $username | $approved.usernames | index($username) != null)
    end)
  )
  and (if $mode == "search" or $mode == "profiles" then
    (group_by(.search_keyword) | all(.[]; length <= $approved.effectiveLimit))
  else
    (group_by(.username | ascii_downcase) | all(.[]; length <= $approved.effectiveLimit))
  end)
' "$WORKDIR/dataset.json" >/dev/null; then
  printf 'The dataset rows do not match the approved input scope or expected public Threads result shape; the result is not verified.\n' >&2
  exit 1
fi
if ! jq -e --arg mode "$MODE" --argjson rows "$ROWS" --slurpfile scope "$WORKDIR/scope.json" '
  ($scope[0]) as $approved
  | type == "object"
  and .status == "SUCCEEDED"
  and .mode == $mode
  and .max_posts == $approved.effectiveLimit
  and (.updated_at | type == "string")
  and ((.start_date? // null) == null)
  and ((.end_date? // null) == null)
  and (if $mode == "search" then
    .search_filter == $approved.searchFilter
  else
    ((.search_filter? // null) == null)
  end)
  and (.items_total | type == "number" and . == floor and . == $approved.expectedItems)
  and (.items_succeeded | type == "number" and . == floor and . >= 0)
  and (.items_errored | type == "number" and . == floor and . >= 0)
  and .items_succeeded + .items_errored == .items_total
  and (if has("failed_items") then
    (.failed_items | type == "array" and all(.[]; type == "string"))
  else true end)
  and (if has("failed_reasons") then
    (.failed_reasons | type == "object" and all(.[]; type == "string"))
  else true end)
  and (if $rows == 0 then
    ((.results_save_attempted? // 0) == 0)
    and ((.results_save_failed? // 0) == 0)
    and (if $mode == "profiles" then .accounts_saved == 0 else .posts_saved == 0 end)
    and (if .reason == "no_results" then
      .items_succeeded == .items_total
      and .items_errored == 0
      and (((.failed_items? // []) | length) == 0)
      and (((.failed_reasons? // {}) | length) == 0)
      and ((.collection_status? // "complete") == "complete")
    else
      .collection_status == "partial"
      and .collection_stop_reason == "budget_reached"
    end)
  else
    (.collection_status == "complete" or .collection_status == "partial")
    and ((.reason? // "") != "no_results")
    and ((.collection_stop_reason? // "") != "no_results")
    and .results_save_attempted == $rows
    and .results_save_failed == 0
    and (if $mode == "profiles" then .accounts_saved == $rows else .posts_saved == $rows end)
    and (if .collection_status == "complete" then
      .items_succeeded == .items_total
      and .items_errored == 0
      and (((.failed_items? // []) | length) == 0)
      and (((.failed_reasons? // {}) | length) == 0)
      and ((.collection_stop_reason? // "") != "temporarily_unavailable")
      and ((.collection_stop_reason? // "") != "time_limit_reached")
      and ((.collection_stop_reason? // "") != "budget_reached")
    else true end)
  end)
' "$WORKDIR/output.json" >/dev/null; then
  printf 'The dataset and Actor OUTPUT summary disagree; the result is not verified.\n' >&2
  exit 1
fi

RESULT_STATE="$(jq -er --arg mode "$MODE" --argjson rows "$ROWS" '
  if $rows == 0 and .reason == "no_results" then "no_results"
  elif $rows == 0 then "partial"
  elif .collection_status == "complete"
    and ((.reason? // "") != "no_results")
    and ((.collection_stop_reason? // "") != "no_results")
    and ((.collection_stop_reason? // "") != "temporarily_unavailable")
    and ((.collection_stop_reason? // "") != "time_limit_reached")
    and ((.collection_stop_reason? // "") != "budget_reached")
    and (.items_succeeded == .items_total)
    and (.items_errored == 0)
    and ((.failed_items // []) | type == "array" and length == 0)
    and ((.failed_reasons // {}) | type == "object" and length == 0)
    and (if $mode == "profiles" then true else .result_quality == "complete" end)
  then "complete"
  else "partial"
  end
' "$WORKDIR/output.json")"
printf 'Verified result state: %s\n' "$RESULT_STATE"
```

Report only a state that passes these checks:

- `complete`: The run and saved rows passed every check above.
- `partial`: Usable rows may exist, but do not describe the result as complete.
- `no_results`: The exact input returned no public rows at collection time; it does not prove that no matching Threads content exists.

A failed run has none of these states. If `OUTPUT` is missing or a check fails, say that the result is not verified. For `user` mode with `no_results`, ask the user to confirm the username or profile URL. For `search` or `profiles`, follow **Choose search terms**. Never change the query or filters silently.

## Report verified evidence

Include the Actor, collection time, approved input, run ID and status, requested limit, returned-row count, verified result state, `collection_status`, `result_quality` when present, failed items or reasons, and Threads source URLs used as evidence.

Missing metrics remain missing; never replace them with zero. Label themes, relevance judgments, or sentiment as downstream analysis rather than scraped fields. Treat `top` as results Threads surfaced for that query, and note that `recent` may still contain older related posts.

Keep the private working directory only until the report is delivered. Then remove its files and directory through the client's normal temporary-file cleanup unless the user asks to retain the evidence.
