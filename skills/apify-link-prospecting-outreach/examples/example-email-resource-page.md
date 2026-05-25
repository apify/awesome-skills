# Example: resource-page-inclusion outreach with the Resource page partnership type

Resource-page outreach is a different beast from the other outreach types. The prospect page is a curated list (roundup, "best of", "top 10"). The pitch is to be added as a new entry on the list, not to splice a link into prose.
In the new skill model:

- **Outreach Type** = `resource-page-inclusion` (auto-detected from the `Why This Prospect` tag `Resource / roundup page`, which is set in Step 7 when the WCC body has 10+ outbound links and a list-flavored title).
- **Partnership Type** = `Resource page / list inclusion` (selected by the user at Step 2). 
- **Placement** is always a **new insertion** (column `Placement New Insertion`), never a splice into an existing sentence. Resource pages are list-structured; you're adding a new list item.

## Context

- Prospect article: `"50 best open-source developer tools we use in 2026"` at `devstackpicks.example`.
- Article author (from `searchAuthorName`): `Linus Mehta`.
- Outreach contact (from All leads): `Aria Chen, Editor-in-Chief, aria@devstackpicks.example` — picked over the listed Head of Marketing because `Editor-in-Chief` matches the editorial-leaning regex in Step 8 rule 2.
- User's brand: `AcmeMonitor` — an open-source uptime monitor.
- User's content URL: `acmemonitor.example`.
- Goal: `Topical authority links to specific URL`.
- Partnership type: `Resource page / list inclusion`.
- Ahrefs metrics: `Domain DR = 71`, `Page Traffic = 2,400/mo`, `Referring Domains = 89`.
- Prospect Tier: `A`.
- Why This Prospect: `Resource / roundup page`.
- Outreach Type: `resource-page-inclusion`.

### Placement artifacts

The article is a numbered list of 50 tools grouped by subsection. There's no existing sentence to splice into — the natural placement is a brand-new entry alongside `Uptime Kuma` in the "Monitoring and observability" subsection. So `Placement New Insertion` is filled and the other two are `"-"`.

- **Placement Source Sentence**: `"-"`
- **Placement With Link**: `"-"`
- **Placement New Insertion**:

  > Insert as a new list item in the "Monitoring and observability" subsection, immediately after the `Uptime Kuma` entry. Format to match the existing list entries (bold tool name, one-paragraph description, link in parentheses):
  >
  > **AcmeMonitor** — Lightweight self-hosted uptime monitor. Single Go binary, MIT-licensed, no database required, runs on a $4/mo VPS. Trade-off vs. Uptime Kuma: smaller surface area, no built-in JS notifications dashboard. ([acmemonitor.example](https://acmemonitor.example))

The inserted draft matches the article's list format (bold name → one-paragraph description → link in parentheses) so the editor can drop it in without rewriting.

## Voice and email

User's voice paragraph:

> Direct, technical, no fluff. We're a small open-source project run by two engineers. We don't oversell. Open "Hi {first_name}," and close with "— the AcmeMonitor maintainers".

Email:

```
Subject: Suggestion for your 2026 open-source dev tools list

Hi Aria,

Just went through "50 best open-source developer tools we use in 2026" — really tight selection. The Plausible Analytics entry is the first place I've seen anyone explain the GoatCounter trade-off honestly instead of just saying "it's lighter".

I'm one of the maintainers of AcmeMonitor (acmemonitor.example) — an open-source uptime monitor, MIT-licensed, single Go binary. It sits naturally in your "Monitoring and observability" subsection, right next to Uptime Kuma. Would you consider adding it in your list? Happy to discuss potential ways of collaboration.

Best,

— the AcmeMonitor maintainers
```

Word count: 144. Voice traits hit:
- "Hi Aria," opener.
- "— the AcmeMonitor maintainers" close (plural, since the voice paragraph said "two engineers").
- The `{{offer_paragraph}}` substitution from `Resource page / list inclusion` partnership type is the line `"I'm not asking for a reciprocal link — happy to send this in as a straight suggestion for your list."`

## What's different from other outreach-type templates

| Element | `topical-niche-edit` / `competitor-link-replacement` / `outdated-content-replacement` | `resource-page-inclusion` |
|---|---|---|
| Placement mode | Either splice into existing sentence (`Placement With Link`) or new insertion (`Placement New Insertion`) | **Always new insertion** — you're adding a list item, not editing prose |
| Reference | A section heading, claim, or competitor link | A specific listed item (the entry adjacent to where yours would go) |
| Tone | Transactional — focus on what the addition gains the reader | Editorial — "would you consider adding it?" |
| Risk if you skip the merit | Acceptable for ABC/AB — the exchange motivates them anyway | Fatal — there's nothing in it for them otherwise |
| Format match | Doesn't matter | The new insertion **must** match the article's existing list entry format (bold name + paragraph + link, or whatever the page uses) |

## What's still constant across all outreach types

- Opens with a concrete reference to something in the article (here: the Plausible / GoatCounter call).
- Cites a real adjacent item / claim (here: Uptime Kuma) so the recipient can see the context.
- Names the placement spot precisely ("Monitoring and observability" subsection, immediately after Uptime Kuma).
- No fabricated stats, no fabricated user counts, no fabricated "as featured in TechCrunch".
- Under 150 words.
- The drafted new insertion is the same text used in the `Placement New Insertion` column and in the email body — agent must keep them in sync.

## Outreach-type override on the fly

The user's Step 2 partnership type and the per-row outreach type are normally chosen independently. But the `Why This Prospect` tag `Resource / roundup page` should auto-set `Outreach Type = resource-page-inclusion` regardless of partnership type — splicing a link into a list page reads as spam.

If the user's partnership type is `ABC link exchange` or `Direct A B link exchange` but the row is a resource page, the agent should:

1. Still use the `resource-page-inclusion` template structure.
2. Substitute the `{{offer_paragraph}}` for whatever partnership type the user picked — but flag in `Notes`: `"Resource page detected — partnership type ABC may weaken the pitch on a list page. Consider switching this row to Unilateral ask before sending."`

The user can revert if they disagree; the override is a default, not a lock.
