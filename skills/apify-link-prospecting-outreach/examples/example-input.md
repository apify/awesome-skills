# Example: full input walkthrough + sample output

A worked example of one full run through the skill. The data below is illustrative, not from a real Actor run — domain names, contacts, Ahrefs metrics, and article titles are placeholders.

## Step 1: Required anchor inputs

| Field | Value |
|---|---|
| Concrete goal | `Topical authority links to specific URL` |
| Target keyword(s) | `headless cms for ecommerce`, `best headless cms 2026` |
| Brand name | `AcmeCMS` |
| Product/category description | `AcmeCMS — headless CMS purpose-built for D2C ecommerce. We sell to merchants and storefront developers who need Stripe-readiness scoring and Shopify-equivalent ergonomics from their CMS.` |
| Content URL to link to | `https://acmecms.example/headless-cms-comparison-2026` |
| Competitors | `contentful.com`, `sanity.io`, `strapi.io`, `prismic.io`, `crystallize.com`, `storyblok.com`, `hygraph.com`, `dato.cms`, `kontent.ai`, `directus.io` (user-supplied — the prompt explicitly asks for "anyone who'd write a vs-AcmeCMS comparison page on their site, even small competitors"; agent offered Ahrefs auto-pull but user declined for this run) |
| Already-pitched domains (optional) | `crystallize.com`, `prismic.io` |
| Organic results per keyword | `10` |
| LLM sources to track | All 6 enabled: ChatGPT Search, Gemini, Copilot, Perplexity, Google AI Mode, Google AI Overviews |
| Run email verification? | `yes` (`enableEmailVerification: true`) |

The product/category description is used in Step 6 (topical-fit gate) to extract specific topical keywords (`headless cms`, `ecommerce`, `d2c`, `stripe`, `merchant`, `comparison`) that prospect articles must contain. It's also used in Step 6 (adversarial-mention detection) to recognise when a "Mentions AcmeCMS" page is actually a competitor's comparison footer.

The LLM-source multi-select maps directly to the Actor's `enableChatGpt` / `enableGemini` / `enableCopilot` / `enablePerplexity` / `enableAiMode` / `enableAiOverviews` flags. Email verification maps to `enableEmailVerification` — every email returned in the leads dataset gets an `email_verification` status (`verified`, `catch-all`, `risky`, `invalid`, or `unknown`) which feeds the `Email Verification` output column and the Step 6 invalid-email skip rule.

## Step 2: Secondary inputs

**Brand voice**:

> We're a small, founder-led team. Casual but precise — we use contractions, em-dashes, and we don't pretend we're a Fortune 500. Bias for honesty over hype: if a competitor does something well we'd say so. Open emails with "Hey {first_name}," and close with "— Nadia".

**Partnership type**: ABC link exchange (with partner site `decoupled.example`)

**Output format**: Markdown

## Step 3: Actor call

```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/scripts/run_actor.js \
  --actor "apify/link-prospecting-tool" \
  --input '{
    "queries": "headless cms for ecommerce\nbest headless cms 2026",
    "brand": "AcmeCMS",
    "ownDomains": ["acmecms.example", "docs.acmecms.example"],
    "competitorDomains": ["contentful.com", "sanity.io", "strapi.io"],
    "ignoreDomains": [
      "wikipedia.org","github.com","stackoverflow.com","stackexchange.com",
      "reddit.com","quora.com","youtube.com","twitter.com","x.com",
      "linkedin.com","facebook.com","medium.com","archive.org"
    ],
    "organicResult": 10,
    "maxContactsPerDomain": 3,
    "department": ["marketing"],
    "searchAuthorName": true,
    "includeMention": true,
    "enableChatGpt": true,
    "enableAiMode": true,
    "enableAiOverviews": true,
    "enablePerplexity": true
  }' \
  --timeout 1200 \
  --fetch-sub-datasets \
  --output 2026-05-13_acmecms_outreach.json \
  --format json
```

Note that `department` is `["marketing"]` only — `c_suite` is dropped because CEOs don't edit articles. The competitor list passed to the Actor is also reused in Step 7 to detect the `Links to competitor` tag.

## Step 5: Ahrefs enrichment (per surviving domain)

For each unique domain in the Actor output, fetch:

- `mcp__claude_ai_Ahrefs__site-explorer-domain-rating` → `Domain DR`
- `mcp__claude_ai_Ahrefs__site-explorer-metrics` (target=article URL, `mode: "exact"`) → `Page Traffic` (last 30 days, organic)
- `mcp__claude_ai_Ahrefs__site-explorer-backlinks-stats` → `Referring Domains`

Compute `Prospect Tier` using the `Topical authority` thresholds (since that's the goal):
- A: DR ≥ 50 AND Page Traffic ≥ 300/mo
- B: DR 30–49 OR Page Traffic 50–299
- C: everything below

## Step 6: Skip pass results

Of the 14 leads the Actor returned, 3 were skipped:

| Domain | Skip reason |
|---|---|
| `crystallize.com` | Already pitched (Step 1 input #6) |
| `oldcms-blog.example` | Stale content (published 2019-03-22, > 5 years old) |
| `pricing-page.example` | Non-editorial page type (vendor pricing page) |

Surviving rows: 11. We'll show 4 of them below.

## Step 7-8: Sample 4-row Markdown output

```
# Link prospecting results — 2026-05-13

Run ID: aB12cDeFgHiJk
Goal: Topical authority links to specific URL
Keywords: headless cms for ecommerce, best headless cms 2026
Brand: AcmeCMS
Content URL: https://acmecms.example/headless-cms-comparison-2026
Partnership: ABC link exchange
Tier breakdown: A: 4, B: 5, C: 2, Skipped: 3

| # | Tier | Why | SERP | Engines | Domain | DR | Traffic | Article | Contact | Email Verif | Outreach Type | Placement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A | Top-3 SERP for headless cms for ecommerce | 2 | Google Organic, ChatGPT, Gemini | saasdigest.example | 78 | 4,200 | [Headless CMS in 2026: a buyer's guide](https://saasdigest.example/headless-cms-2026-guide) | Elena Vargas, Content Editor — elena@saasdigest.example | verified | topical-niche-edit | Strategy: additive — original sentence kept verbatim + follow-on naming AcmeCMS |
| 2 | B | Links to competitor (sanity.io) | 5 | Google Organic, Perplexity, Copilot | merchantsblog.example | 41 | 180 | [Why we moved off Shopify to a headless setup](https://merchantsblog.example/moved-off-shopify) | Tom Park, Founder — tom@merchantsblog.example | catch-all | competitor-link-replacement | Strategy: new insertion — after the "Picking the CMS" subsection |
| 3 | A | Mentions brand, no backlink | 4 | Google Organic, ChatGPT, Gemini, Copilot | dtcweekly.example | 62 | 1,100 | [The 8 best headless CMSes for D2C in 2026](https://dtcweekly.example/headless-cms-d2c-2026) | Mark Lee, Head of Content — mark.lee@dtcweekly.example | verified | unlinked-mention-claim | Strategy: drop-in — link added onto the existing word "AcmeCMS" |
| 4 | B | Top-3 SERP for best headless cms 2026 | 3 | Google Organic, Gemini | ecombytes.example | 35 | 240 | [Ranking the best headless CMS platforms for 2026](https://ecombytes.example/best-headless-cms-2026) | Priya Raman, Marketing Director — priya@ecombytes.example | risky | topical-niche-edit | Strategy: new insertion — Honorable Mentions section |

## Skipped (3)

| Domain | Reason |
|---|---|
| crystallize.com | Already pitched (Step 1 input #6) |
| oldcms-blog.example | Stale content (published 2019-03-22) |
| pricing-page.example | Non-editorial page type (vendor pricing page) |
```

## Per-row placement detail

### Row 1 — saasdigest.example — Tier A — topical-niche-edit (Strategy: additive)

- **Placement Source Sentence**: `"For teams scaling across many storefronts, some teams need a more API-first approach."`
- **Placement With Link**: `"For teams scaling across many storefronts, some teams need a more API-first approach. → For teams scaling across many storefronts, some teams need a more API-first approach. If your storefront also needs Stripe-readiness scoring, [AcmeCMS](https://acmecms.example/headless-cms-comparison-2026) is purpose-built for that."` (original sentence kept verbatim; one follow-on sentence added raising a need the original doesn't address)
- **Placement New Insertion**: `"-"`
- `Notes` prepended with `Placement: additive`.

### Row 2 — merchantsblog.example — Tier B — competitor-link-replacement (Strategy: new insertion)

- **Placement Source Sentence**: `"-"` (no existing sentence fits naturally)
- **Placement With Link**: `"-"`
- **Placement New Insertion**: `"Insert as a new paragraph immediately after the sentence ending in '…we shortlisted Sanity.' in the 'Picking the CMS' subsection: 'If you're specifically optimizing for D2C ecommerce, it's worth comparing against [AcmeCMS](https://acmecms.example/headless-cms-comparison-2026), which scores merchants on Stripe-readiness — something Sanity doesn't surface directly.'"`
- `Notes` prepended with `Placement: new insertion`.

### Row 3 — dtcweekly.example — Tier A — unlinked-mention-claim (Strategy: drop-in)

- **Placement Source Sentence**: `"For D2C brands going headless this year, tools like AcmeCMS and Contentful are taking this approach."`
- **Placement With Link**: `"For D2C brands going headless this year, tools like **[AcmeCMS](https://acmecms.example/headless-cms-comparison-2026)** and Contentful are taking this approach."` (the link is added onto the existing word "AcmeCMS" — no other text changes, no new prose)
- **Placement New Insertion**: `"-"`
- `Notes` prepended with `Placement: drop-in`. This is the lowest-friction ask of all three strategies — the editor just turns one of their own words into a hyperlink.

### Row 4 — ecombytes.example — Tier B — topical-niche-edit (Strategy: new insertion)

- **Placement Source Sentence**: `"-"`
- **Placement With Link**: `"-"`
- **Placement New Insertion**: `"Insert as a new paragraph at the end of the 'Honorable mentions' section, after the sentence ending in '…each platform has its own trade-offs.': 'AcmeCMS is worth a look if you're specifically headless-for-D2C — they score CMSes by Stripe-readiness rather than treating ecommerce as a generic content domain. See their 2026 comparison: [acmecms.example/headless-cms-comparison-2026](https://acmecms.example/headless-cms-comparison-2026).'"`
- `Notes` prepended with `Placement: new insertion`.

## Email drafts

### Row 1 — Tier A — saasdigest.example — topical-niche-edit — Elena Vargas

**Subject:** Addition to "Headless CMS in 2026: a buyer's guide"?

> Hey Elena,
>
> Your "Headless CMS in 2026: a buyer's guide" is one of the clearer pieces on this I've found — particularly the scoring on Stripe-readiness instead of just "good for ecommerce".
>
> I'm Nadia from AcmeCMS. We recently published acmecms.example/headless-cms-comparison-2026 — same topic, with a D2C-merchant-fit angle. If it fits, the natural place is alongside your existing "some teams need a more API-first approach" line in the comparison.
>
> In exchange, I'd link to your guide from our piece, and a partner site (decoupled.example) would add a link to yours too.
>
> Open to it?
>
> — Nadia

### Row 2 — Tier B — merchantsblog.example — competitor-link-replacement — Tom Park

**Subject:** Updated alternative to sanity.io in your "Why we moved off Shopify to a headless setup"

> Hey Tom,
>
> Read your write-up — the part on ditching the storefront API in favor of a CMS-first pipeline is exactly the trap most teams fall into. You shortlisted Sanity, which is a solid pick, though it doesn't surface Stripe-readiness directly.
>
> I'm Nadia from AcmeCMS. We just published acmecms.example/headless-cms-comparison-2026 which scores CMSes by D2C-merchant fit, including the Stripe-readiness gap.
>
> The natural place: a new paragraph after your "we shortlisted Sanity" line.
>
> In exchange, I'd link to your piece from ours and a partner site (decoupled.example) would too.
>
> Worth a look?
>
> — Nadia

### Row 3 — Tier A — dtcweekly.example — unlinked-mention-claim — Mark Lee

**Subject:** Quick fix on your "The 8 best headless CMSes for D2C in 2026" — missed link?

> Hey Mark,
>
> Noticed your piece "The 8 best headless CMSes for D2C in 2026" mentions AcmeCMS in the line "tools like AcmeCMS and Contentful are taking this approach" — thanks for the shout-out.
>
> Looks like the mention isn't linked. Would you be open to adding a link to acmecms.example/headless-cms-comparison-2026? Helps readers who want the full D2C-merchant scoring methodology.
>
> Happy to do an ABC swap in return if useful — I'd link your piece from ours and a partner site (decoupled.example) would too.
>
> Either way, appreciate the mention.
>
> — Nadia

### Row 4 — Tier B — ecombytes.example — topical-niche-edit — Priya Raman

**Subject:** Addition to "Ranking the best headless CMS platforms for 2026"?

> Hey Priya,
>
> Just went through your ranking — the "honorable mentions" section is the most useful part because it's where the niche-fit picks actually surface.
>
> I'm Nadia from AcmeCMS. We score CMSes by Stripe-readiness for D2C merchants specifically — acmecms.example/headless-cms-comparison-2026. Could fit naturally as a new entry at the end of your honorable mentions, after the "each platform has its own trade-offs" line.
>
> In exchange, I'd link to your ranking from our piece, and a partner site (decoupled.example) would link to yours too.
>
> Open to it?
>
> — Nadia

## Notes on this example

- All names, domains, articles, contacts, and Ahrefs metrics are placeholders. Do not use them as templates for real outreach.
- Each row uses a different outreach-type template even though every row uses the same partnership type (ABC). The outreach type is determined per-row from `Why This Prospect`; the partnership type substitutes into `{{offer_paragraph}}` in whichever template was chosen.
- Row 1 illustrates the **with-link diff** placement: an existing sentence is a clean fit, the diff column shows the splice.
- Rows 2 and 4 illustrate the **new insertion** placement: no existing sentence fits, so a drafted 1–2 sentence paragraph is provided with a precise location.
- Row 3 illustrates the **simplest splice**: the brand is already named in a sentence, so the link goes on the existing word — no other text changes.
- The contact in Row 1 is "Content Editor" (not "Head of Marketing") because Step 8 rule 2 prioritises editorial-leaning job titles when the All leads dataset returns multiple contacts for one domain.
- Row 3's email uses `unlinked-mention-claim` even though the user picked ABC partnership at Step 2 — the offer paragraph still uses the ABC offer, but the template structure is the mention-claim opener and the ask is gentler.
- Tier counts in the header (`A: 4, B: 5, C: 2`) and skip counts (`3`) are surfaced in the `run_metadata.json` sidecar's `tierCounts` and `skipCounts` blocks.
