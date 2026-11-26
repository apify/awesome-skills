# Fields — what each row means, and the traps

Measured on 2026-09-21 runs of every mode. Types were checked with `jq type`.

## Row kinds

`record_type` is `"post"` or `"profile"`. Profile rows have no `created_at`, so date checks apply
to posts only. `source_tab` is `"posts"`, `"reposts"` or `"replies"` in the account modes and `""`
in search.

## Matching a keyword

- **`keyword_match`** (boolean in search). `true` means every word of the keyword appears in the
  post, not always side by side: 3 of 63 `true` rows in one "Claude Code" run had the words apart
  ("source code … Ask Claude"), so read a row before you quote it. `false` means only part of a
  multi-word keyword appears, or none of it. Those rows are delivered and billed: 37 of 100 in
  that run. In the account modes it is `null` unless you sent `keywords`, which only tag rows
  there, never filter them.
- **`search_keywords`** lists every keyword that selected a post (a post found by two keywords is
  stored once). `search_keyword` holds only the first, so never count per-keyword hits from it.
- Profiles: `search_keyword` is the first keyword that matched. An account matched by a second
  keyword is not stored again; `OUTPUT.keyword_membership_updates` lists the extra keyword.

## Replies and reposts

- **`is_reply`** marks replies. In `user` mode it is also `true` on the later parts of an
  account's own thread (`reply_to_username` = the account itself): 6 of 20 rows in a measured
  @zuck + @instagram run. They count toward `max_posts`.
- `user_replies` rows carry `reply_to_username` and, when Threads shows the answered post,
  `replied_to_text`. On some accounts most replies arrive without it; `replied_to_available`
  says so row by row.
- `user_reposts` rows: `username` is the **original author** (a @zuck repost row had
  `username: "meta"`); the account you asked about is in `requested_username` and
  `reposted_by_username`, with `reposted_at` and `repost_url`. `is_repost` was `false` on those
  rows — identify reposts by `source_tab: "reposts"`.
- Every account-mode post row carries all of these keys, empty or `null` where they do not apply.

## Numbers

- `like_count`, `reply_count`, `repost_count` and `quote_count` are numbers; `view_count` is a
  number only when `view_count_status` is `available`, and `null` otherwise. `reply_count` is a
  count; the reply text is not in the row.
- **`share_count`** is often `null`: 54 of 100 search rows, 3 of 20 account rows. Threads does not
  always publish it. Treat it as a bonus, not a metric.
- **`view_count_status`**: `available` (a number was read, 0 included), `not_public_yet` (the post
  is too recent for a count; 4 of 100 search rows) or `not_checked` (not read on this run; a
  later run picks it up). Never read a missing `view_count` as 0.

## Other traps

- **`language`** is often empty whatever the post's language — 70 of 100 search rows, including
  German, Russian and Chinese posts. Do not filter on it.
- **Renamed accounts**: if Threads redirects an old handle, rows still arrive;
  `requested_username` keeps what you sent.
- **`post_code`** identifies a post — use it to deduplicate across runs and to compare two runs.
  In `user_reposts` with several accounts, a post two of them boosted arrives once per account,
  so key those rows on `post_code` plus `reposted_by_username`.
- Profile rows also carry `is_verified`, `external_links` and the contact details the account
  published in its bio (`emails`, `phones`); empty means the account did not publish them.
