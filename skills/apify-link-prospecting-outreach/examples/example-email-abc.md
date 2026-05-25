# Example: two brand voices for a topical-niche-edit row with ABC partnership offer

The same prospect (an editor at a SaaS comparison blog) approached twice — once in a casual founder-led voice, once in a formal B2B voice. Note what changes (voice surface) and what stays constant (outreach type structure, placement artifacts, ABC offer).

The row in question is a typical `topical-niche-edit`: the article is topically relevant, ranks top-3 for the user's keyword, and has a clean existing sentence the link can be spliced into. No special angle like an unlinked mention or competitor link — just a strong topical fit.

## Shared context across both examples

- Prospect article: `"The 6 best customer feedback tools for product teams"` at `feedbackdaily.example`.
- Article author (from `searchAuthorName`): `Sara Bittencourt`.
- Outreach contact (from All leads, picked over a higher-ranking VP Marketing because of editorial-leaning job title): `Daniel Reyes, Head of Content, daniel@feedbackdaily.example`.
- User's brand: `AcmeFeedback`.
- User's content URL: `acmefeedback.example/in-app-vs-email-feedback-2026`.
- Goal: `Topical authority links to specific URL`.
- Partnership type: `ABC link exchange` with a partner site `productloop.example`.
- Ahrefs metrics: `Domain DR = 64`, `Page Traffic = 1,800/mo`, `Referring Domains = 47`.
- Prospect Tier: `A`.
- Why This Prospect: `Top-3 SERP for customer feedback tools`.
- Outreach Type: `topical-niche-edit`.

### Placement artifacts (same for both versions)

The article contains a clean existing sentence where the link fits naturally, so the **`Placement With Link`** column is filled and `Placement New Insertion` is `"-"`:

- **Placement Source Sentence**: `"In-app prompts beat email surveys for activated users; the inverse holds for churned ones."`
- **Placement With Link**: `"~~In-app prompts beat email surveys for activated users;~~ → "In-app prompts beat email surveys for activated users — see **[AcmeFeedback's breakdown](https://acmefeedback.example/in-app-vs-email-feedback-2026)** for the activation-stage cutoff — the inverse holds for churned ones."`
- **Placement New Insertion**: `"-"`

The diff shows the splice: the existing sentence is kept; an em-dash clause carrying the link is inserted mid-sentence.

## Version 1: casual, founder-led voice

User's voice paragraph:

> Casual but precise. Contractions are fine. We sound like one person, not a marketing team. Lead with what we noticed, not what we want. Open "Hey {first_name}," and sign off "— Maya, AcmeFeedback".

Email:

```
Subject: Addition to your "6 best customer feedback tools" piece?

Hey Daniel,

Just read Sara's "The 6 best customer feedback tools for product teams" — the call that in-app prompts beat email for activated users but lose for churned ones is the cleanest framing on this I've seen.

I'm Maya from AcmeFeedback. We published acmefeedback.example/in-app-vs-email-feedback-2026 which goes deep on the activation-stage cutoff (the "when does in-app beat email?" cutoff specifically). Natural place for it: a quick em-dash clause inside Sara's "In-app prompts beat email surveys for activated users" sentence — happy to suggest exact wording.

In exchange, I'd link to your piece from ours, and a partner site (productloop.example) would add a link to yours too.

Worth a look?

— Maya, AcmeFeedback
```

Word count: 138. Voice traits hit:
- "Hey Daniel," opener (per voice paragraph).
- Contractions ("I'm", "I'd", "it's").
- One-person tone — no "we at AcmeFeedback" corporate plural.
- Leads with what was noticed about Sara's piece, not what Maya wants.
- "— Maya, AcmeFeedback" close.

## Version 2: formal B2B voice

User's voice paragraph:

> Formal, polished, no contractions. We represent a company, not an individual. Use full sentences. Open with "Dear {first_name}," and close with "Regards, the AcmeFeedback team".

Email:

```
Subject: Addition to "The 6 best customer feedback tools for product teams"

Dear Daniel,

We read with interest the recent article by Sara Bittencourt, "The 6 best customer feedback tools for product teams," and noted the distinction drawn between in-app prompts and email surveys, particularly regarding their differential effectiveness for activated versus churned users.

The AcmeFeedback team has published a complementary analysis at acmefeedback.example/in-app-vs-email-feedback-2026, which examines the activation-stage cutoff in detail. A natural placement would be as a parenthetical reference within the existing sentence about in-app prompts beating email for activated users.

In exchange, we would link to your article from our publication, and a partner publication, productloop.example, would extend an inbound link to your piece as well.

We welcome the opportunity to discuss.

Regards,
the AcmeFeedback team
```

Word count: 140. Voice traits hit:
- "Dear Daniel," opener.
- No contractions anywhere.
- Plural corporate voice ("we", "the AcmeFeedback team").
- Full sentences, no em-dashes, no fragments.
- "Regards, the AcmeFeedback team" close.

## What stayed constant across both versions

- The opening reference to a specific subsection (the in-app vs email distinction) — both emails earn the recipient's attention by demonstrating they read the piece.
- The article author (Sara) is named in v2 because `searchAuthorName` returned her, but the outreach is addressed to Daniel (the actual contact). Author mention is optional in v1 because the casual tone doesn't require attribution.
- The ABC `{{offer_paragraph}}` substitution: I link to you, partner links to you, you link to me. Both versions describe the trade clearly.
- The placement summary maps directly to the row's `Placement With Link` cell — no "somewhere in the piece" hand-waving.
- Both are under 150 words.
- Both use the **same outreach-type template** (`topical-niche-edit`) and the **same offer paragraph** (ABC). Only the voice surface differs.

## What changed

| Element | Casual | Formal |
|---|---|---|
| Opener | "Hey Daniel," | "Dear Daniel," |
| Pronoun | "I" | "We" / "the AcmeFeedback team" |
| Contractions | yes | no |
| Sentence length | mixed, with em-dashes | longer, formal |
| Author mention | implicit (just the article title) | explicit ("by Sara Bittencourt") |
| Closing CTA | "Worth a look?" | "We welcome the opportunity to discuss." |
| Sign-off | "— Maya, AcmeFeedback" | "Regards, the AcmeFeedback team" |

The skill must produce both correctly. If the user's voice paragraph is closer to v1, the agent must not regress to v2 — even though v2 is the "safer" generic default for outreach.

## What would change if the row's outreach type were different

This row uses `topical-niche-edit` because no stronger angle was detected. If the same article had instead:

- **Mentioned AcmeFeedback without linking** → `unlinked-mention-claim` template, subject would be `"Quick fix on your '6 best customer feedback tools' piece — missed link?"`, opener would lead with the unlinked mention itself, not with the in-app/email distinction. The ABC offer paragraph would still substitute in.
- **Linked to a competitor** (e.g., Hotjar) → `competitor-link-replacement` template, subject would be `"Updated alternative to hotjar.com in your '6 best customer feedback tools' piece"`, opener would acknowledge the Hotjar link and offer AcmeFeedback as an addition (not a replacement). ABC offer paragraph still substitutes in.

The partnership type (ABC) stays constant across the user's whole campaign; the outreach type varies per-row based on `Why This Prospect`.
