# Issue taxonomy

Classification rules for the quality-audit module ([quality-audit.md](quality-audit.md)). Apply against **title + body text, lowercased**.

## Labels

| Label | Meaning | Report use |
|---|---|---|
| `bug` | User reports broken, incorrect, or unexpected behaviour in current Actor functionality | Market pain points |
| `feature-request` | User asks for new capability, option, field, output format, or integration that doesn't exist | Potential powerups |
| `support` | User asks how to use an existing capability, or how to configure something documented | Noise — excluded from powerup/pain analysis |
| `other` | Meta, spam, duplicate, unclear, out-of-scope, or truly ambiguous after LLM review | Noise |

## Stage 1 — Keyword heuristics (fast pass)

Apply in **this priority order**. First rule to match wins — do not re-check later rules for the same issue unless the "ambiguous" branch below is hit.

### Feature-request patterns

Match any of:

- `/feature request/i`
- `/would be nice/i` / `/nice to have/i`
- `/can you add/i` / `/please add/i` / `/can we have/i`
- `/support for [a-z]/i` (e.g., "support for TikTok")
- `/option to [a-z]/i` (e.g., "option to exclude usernames")
- `/ability to [a-z]/i`
- `/add support/i` / `/add an option/i` / `/add a field/i`
- `/suggestion:/i` / `/\bsuggestion\b/i`
- `/^request:/i`
- `/allow [a-z]+ (ing|to)/i` (e.g., "allow filtering by…")
- `/\bimplement (a|the|an)\b/i`
- `/missing (field|option|param|parameter)/i`

### Bug patterns

Match any of:

- `/\berror\b/i` / `/\bexception\b/i`
- `/\bcrash(es|ed|ing)?\b/i`
- `/\bbroken\b/i` / `/not working/i` / `/doesn'?t work/i` / `/does not work/i`
- `/fail(ed|ing|s)\b/i` / `/\bfailure\b/i`
- `/returns? (empty|null|nothing|undefined|zero)/i`
- `/HTTP \d{3}/` (any explicit HTTP status in title/body)
- `/\btimeout\b/i` / `/times out/i` / `/\bhang(s|ing)?\b/i`
- `/unexpected (behavior|behaviour|result|response|output)/i`
- `/stuck (at|on|in)/i`
- `/stopped working/i` / `/suddenly/i` + (fail|error|break)
- `/(missing|wrong|incorrect) (data|output|result|response)/i`
- `/cannot (login|authenticate|connect|access)/i`
- `/scrap(e|ing) (fails|failed|returns empty|not working)/i`

### Support/question patterns

Match any of, **only if no bug or feature-request pattern matched**:

- `/how (do|can|should) I/i`
- `/how to [a-z]/i`
- `/\?$/` at end of title (bare question)
- `/\bquestion:/i` / `/^question\b/i`
- `/\bhelp\b/i` + no bug match
- `/is it possible to [a-z]/i`
- `/can I [a-z]/i` + no bug or feature match (careful — many of these are feature requests in disguise; let LLM handle)

### Routing from Stage 1

- Matches feature-request only → label `feature-request` (done, skip LLM)
- Matches bug only → label `bug` (done, skip LLM)
- Matches support only → label `support` (done, skip LLM)
- Matches BOTH feature-request AND bug → **ambiguous**, send to LLM
- Matches nothing → label `other`, send to LLM

### Fast path shortcut

An issue where `source == "MANUAL"` AND `title` starts (case-insensitive) with one of:

- `Feature request:`
- `[Feature]`
- `[FR]`

is a certain `feature-request`. Skip the LLM stage.

Similarly, a title starting with `[Bug]`, `Bug:`, or `BUG -` is a certain `bug`.

## Stage 2 — LLM fallback

Only for `ambiguous` or `other` from Stage 1.

**Batch size:** 10 issues per call.

**Prompt skeleton:**

```
You are classifying user-submitted issues on an Apify Actor's public issues page.
Labels:
  - bug: user reports broken, incorrect, or unexpected behaviour in current functionality
  - feature-request: user asks for a new capability, option, output field, or integration
  - support: user asks how to use something that already exists
  - other: meta, spam, duplicate, unclear, out-of-scope

For each of the N issues below, return a JSON array with one object per issue:
  { "id": <issue._id>, "label": "<one of the four>", "rationale": "<≤ 15 words>" }

No prose outside the JSON array.

Issues:
1. [id=<_id>]
   Title: <title>
   Body: <first 800 chars of body>
...
```

Merge the LLM labels back onto the issue records. Keep Stage-1 confident labels untouched.

## Worked examples

| Title | Body (truncated) | Stage-1 hits | Final label | Notes |
|---|---|---|---|---|
| "Feature request: option to exclude specific usernames" | "I want to pass a list of usernames to skip…" | feature-request (both "feature request" and "option to") | feature-request | Fast path (MANUAL + "Feature request:") |
| "Accidental Run" | "I started a run by mistake, how do I cancel billing?" | support ("how do I") | support | Noise — excluded from analysis |
| "Scraping fails on private profiles" | "Error: 401 Unauthorized when hitting private accounts…" | bug ("fails", "error", "HTTP 401") | bug | Clear bug, Stage 1 only |
| "Could you add TikTok support and fix the timeout bug while you're at it" | — | ambiguous (feature + bug) | LLM decides — likely splits into two themes in clustering | Edge case |
| "Returns empty on hashtags with special chars" | "If the hashtag has an emoji it returns []" | bug ("returns empty") | bug | Reliability pattern |
| "How to configure the proxy for my enterprise account?" | — | support ("how to") | support | Noise |
| "Rate limited after 3 requests — is this expected?" | "Getting 429 every third call" | bug ("HTTP 429") | bug | Even phrased as a question, the behaviour is the bug |

## Clustering guidance (step A6 of [quality-audit.md](quality-audit.md))

When grouping feature requests into "potential powerup" themes, prefer **capability-level** names, not literal title words:

- Three issues saying "Add TikTok", "Scrape TikTok videos", "TikTok support please" → cluster theme: **"TikTok source"**.
- Four issues about excluding/including specific items → cluster theme: **"Include/exclude filters"**.
- Issues asking for JSON output, CSV export, XLSX → cluster theme: **"Alternate output formats"**.

When grouping bugs into "market pain points", prefer **symptom-level** names:

- Any variant of "empty result", "returns []", "no data back" → cluster theme: **"Empty results on valid input"**.
- 429s, rate limit, blocked → cluster theme: **"Rate limiting / anti-bot blocks"**.
- "stale data", "shows old", "cached" → cluster theme: **"Staleness"**.

Minimum cluster size is **2** — singletons stay in the per-Actor appendix only.
