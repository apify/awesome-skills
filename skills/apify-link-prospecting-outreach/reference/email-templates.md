# Email Templates

Templates are keyed by **outreach type** (determined per-row from `Why This Prospect` tags + the user's goal — see SKILL.md Step 8 rule 4). The user's **partnership type** answer at Step 2 substitutes into the `{{offer_paragraph}}` placeholder inside each template.

Outreach type controls the opening hook and pitch structure. Partnership type controls what the user is offering in return.

## Hard rules (apply to every template)

- Word cap: 150 words total, including subject line.
- Open with a concrete reference to the article — title plus one specific takeaway from its content. No generic "I loved your article" openers.
- **Include the verbatim placement wording in the body.** This is non-negotiable. Pull the source sentence (quoted, verbatim from the article) and the proposed change (linked version for drop-in, full follow-on sentence for additive, full drafted paragraph for new insertion) directly into the email. The recipient must see the exact text on first read, not be asked to click through to a separate document or reply for "details". Vague phrasing like *"happy to send exact wording"* / *"happy to draft for you"* / *"a follow-on linking to..."* is a content-skill bug. Always rewrite to embed the proposal.
- Never fabricate the author's name. If `Article Author = "Not found"`, address the contact by their first name from the All leads dataset.
- Never fabricate stats or quotes about the user's product. If the user didn't give you a number, don't invent one.
- **Never suggest external lookup tools or workarounds** (hunter.io, LinkedIn search, third-party verifiers, etc.) — in the email body or in Notes. State facts; don't coach the user on tools they already know about.

## Placement priority (try in order)

Every per-row email body references one of three placement strategies, tried in this order. The placement is drafted in Step 8 and surfaced in the output's three placement columns; the email body should match the strategy that was used.

1. **Drop-in (preferred)** — The user's URL is added to a word/phrase the author already wrote. No prose changes, no new sentences. The email's "natural place for it" line is something like *"as a hyperlink on the word 'BeautifulSoup' in your tools-comparison paragraph"*. This is the *lowest-friction* ask: "could you turn one of your existing words into a hyperlink?"

2. **Additive (second choice)** — Keep an existing sentence verbatim; add one new sentence after it that introduces an adjacent reader-need the article doesn't already address. The email's placement line is something like *"as a follow-on after your sentence about API integration — 'In need of competitor data the API doesn't expose? Then you need [Brand]'"*. The new sentence must raise a need the existing prose doesn't, in the article's voice, ≤25 words.

3. **New insertion (last resort)** — A fully drafted 1–2 sentence paragraph at a precise anchor. Use only when no relevant sentence exists in the article body. The email's placement line names the H2/section and the anchor sentence: *"as a new paragraph after the sentence ending in '…each platform has its own trade-offs.' in the Honorable Mentions section"*.

Match the email's placement language to the strategy. A drop-in pitch ("could you hyperlink one existing word") reads very differently from a new-insertion pitch ("here's a paragraph I drafted in your voice"). Editors notice when the ask matches the effort.

## Outreach-type templates

### `unlinked-mention-claim`

Used when `Why This Prospect` includes `Mentions brand, no backlink`. The page already references the user's brand — they just forgot the link. Easiest ask of the five types; reply rates are highest. Keep it short.

Subject: `Quick fix on your "{{article_title}}" — missed link?`

Body skeleton:

```
Hi {{first_name}},

I noticed your "{{article_title}}" mentions {{user_brand}} in {{specific_mention_location}} — thanks for the shout-out.

Looks like the mention isn't linked. Would you be open to adding a link to {{user_content_url}}? It would help readers who want more on {{specific_topic}}.

{{offer_paragraph}}

Either way, appreciated the mention.

{{user_first_name}}
```

Substitution rules:
- `{{specific_mention_location}}` must quote or paraphrase the actual sentence where the brand is mentioned — pull from the WCC page body. If you can't find the mention text in the WCC body, flag the row with `Notes: "Mentions dataset says brand was mentioned but WCC body doesn't contain it — verify manually"`.
- This is the one outreach type where a unilateral ask (no reciprocal link) is perfectly normal — many publishers fix unlinked mentions without expecting anything. If the partnership type is `Unilateral ask`, leave `{{offer_paragraph}}` as a single line: `It's a small change and I'm not asking for anything in return.`

### `competitor-link-replacement`

Used when `Why This Prospect` includes `Links to competitor`. The page already links to a similar resource — the pitch is to add (or swap to) the user's URL.

Subject: `Updated alternative to {{competitor_domain}} in your "{{article_title}}"`

Body skeleton:

```
Hi {{first_name}},

In your "{{article_title}}" you link to {{competitor_domain}} in the {{specific_subsection_or_claim}} section — solid pick, though I noticed it's missing {{specific_gap_or_angle}}.

I'm {{user_first_name}} from {{user_brand}}. We published {{user_content_title}} at {{user_content_url}} which covers {{specific_gap_or_angle}} directly.

{{offer_paragraph}}

The natural place for it: {{placement_summary}}.

Worth a look?

{{user_first_name}}
```

Substitution rules:
- `{{competitor_domain}}` is the specific competitor URL the page links to — pull from the WCC body's outbound link list.
- `{{specific_gap_or_angle}}` should be one concrete way the user's content differs from the competitor's. Ask the user for this during Step 2 (brand voice) if not already supplied. Never invent a "gap" — leave the placeholder and flag in `Notes` if the user didn't give you anything.
- `{{placement_summary}}` is a one-line description of the placement (e.g., `"alongside your existing X mention in the comparison list"`). Pull from the `Placement With Link` or `Placement New Insertion` cell.
- Do NOT say "remove the link to {{competitor_domain}}" — asking the publisher to delete an existing link is a much harder ask and usually kills the reply. Frame as addition, not replacement.

### `resource-page-inclusion`

Used when `Why This Prospect` includes `Resource / roundup page`. The page is a curated list (best-of, top-10, tool roundup). The ask is inclusion on the list.

Subject: `Suggestion for your "{{article_title}}" roundup`

Body skeleton:

```
Hi {{first_name}},

I just went through your list "{{article_title}}" — tight selection, especially {{specific_listed_item_or_section}}.

I'm {{user_first_name}} from {{user_brand}}. We built {{user_content_title}} ({{user_content_url}}) which covers {{specific_gap_or_angle}} — I think it'd sit naturally alongside {{adjacent_listed_item}}.

{{offer_paragraph}}

Happy to send a one-line description if it'd save you time.

Thanks for keeping the list updated,
{{user_first_name}}
```

Substitution rules:
- `{{specific_listed_item_or_section}}` and `{{adjacent_listed_item}}` must come from the actual page body. If the WCC dataset doesn't have enough body text to identify list items, set `Outreach Status = "Skip"` with `Notes: "Resource page detected but list structure unreadable — manual review needed"`.
- Roundup pages typically get unilateral asks. If the partnership type is `ABC link exchange` or `Direct A B link exchange`, the offer often weakens the pitch — note this in `Notes` and consider downgrading to `Unilateral ask` for the row.

### `outdated-content-replacement`

Used when `Why This Prospect` includes `Outdated content`. Article was published 2+ years ago and could use a refresh. The pitch is an updated resource the editor can plug into the post.

Subject: `Refresh idea for "{{article_title}}" (published {{publish_year}})`

Body skeleton:

```
Hi {{first_name}},

Re-read your "{{article_title}}" — the {{specific_subsection_or_claim}} section still holds up, but a few of the data points are from {{publish_year}} and {{specific_outdated_claim}}.

I'm {{user_first_name}} from {{user_brand}}. We just published {{user_content_title}} ({{user_content_url}}) with current numbers on {{specific_topic}}.

{{offer_paragraph}}

Suggested swap: {{placement_summary}}.

Would a refresh be useful?

{{user_first_name}}
```

Substitution rules:
- `{{publish_year}}` is the four-digit year from `Publish Date`.
- `{{specific_outdated_claim}}` should reference something concrete in the article that has plausibly changed — pricing, a tool name, a stat. If the WCC body doesn't give you a clear outdated claim, drop the second sentence and pivot to a softer "could use a refresh" framing. Do NOT invent specific outdated claims.

### `topical-niche-edit`

Default fallback when `Why This Prospect` has no specific tag (or only `Top-3 SERP`). The article is topically relevant — the pitch is a clean addition of the user's URL in an existing section.

Subject: `Addition to "{{article_title}}"?`

Body skeleton:

```
Hi {{first_name}},

Your "{{article_title}}" is one of the clearer pieces on {{topic}} I've found — particularly {{specific_subsection_or_claim}}.

I'm {{user_first_name}} from {{user_brand}}. We recently published {{user_content_title}} at {{user_content_url}} — same topic, {{angle_one_liner}}.

If it fits, the natural place for it is {{placement_summary}}.

{{offer_paragraph}}

Open to it?

{{user_first_name}}
```

Substitution rules:
- `{{angle_one_liner}}` should be one sentence the user supplied at Step 2 describing how their content differs from the prospect's. Ask if not supplied. Do not invent.
- `{{placement_summary}}` is one line drawn from the `Placement With Link` or `Placement New Insertion` cell.

## Partnership-type offer paragraphs

The user's Step 2 partnership type answer substitutes into `{{offer_paragraph}}`. Use the matching block verbatim, with the listed substitutions:

### `ABC link exchange`

```
In exchange, I'd link to your article from {{user_content_url}}, and a partner site I work with ({{partner_domain}}) would add a link to {{user_article_url}}.
```

Substitution rules:
- `{{partner_domain}}` is filled out-of-band by the user. The skill leaves the placeholder and adds to `Notes`: `"Replace {{partner_domain}} before sending — three-way deal needs a confirmed partner."`

### `Direct A B link exchange`

```
In exchange, I'd link to your article from {{user_content_url}} where it fits. Straight two-way swap, no third party.
```

If the prospect domain has `Domain DR ≥ 70`, flag in `Notes`: `"High-DR prospect — direct exchange may be seen as old-school SEO. Consider switching this row's partnership type to Unilateral ask."`

### `Resource page / list inclusion`

```
I'm not asking for a reciprocal link — happy to send this in as a straight suggestion for your list.
```

(This offer paragraph essentially becomes unilateral. Used only when the user explicitly picks `Resource page / list inclusion` at Step 2 across all rows. Per-row overrides happen in the outreach-type templates themselves.)

### `Unilateral ask (no reciprocal)`

```
I'm not asking for anything in return — just thought it'd be useful for your readers.
```

### `Other`

The user typed their own offer at Step 2. Use the literal language verbatim. Do not soften, summarise, or substitute synonyms. If they wrote `"we pay $300 per placement"`, the email must say `"we pay $300 per placement"` — not `"we offer competitive compensation"`.

If the user gave no custom offer text, fall back to the `Unilateral ask` paragraph and flag in `Notes`: `"No custom offer supplied — defaulted to unilateral ask."`

## Brand voice substitution

The user's brand voice paragraph (from Step 2 input #1) governs every word that isn't a template placeholder. Apply these rules:

1. **Keep their adjectives.** If they wrote "casual, helpful, slightly nerdy", use "casual" not "informal", "helpful" not "useful", "nerdy" not "technical".
2. **Mirror sentence length.** If their voice paragraph uses short sentences, generate short sentences. If they write in long flowing sentences, do the same.
3. **Mirror formality register.** "Founder-led casual" allows "Hey" openings, contractions, em-dashes. "Formal B2B" rules out contractions and "Hey". Match what they used in their own paragraph.
4. **Mirror idiom and slang.** Don't substitute their phrases with generic synonyms. If they say "we're not in the AI hype train business", that phrasing must appear in the email — verbatim or with minimal adjustment to fit grammar.
5. **Match opener style.** If their voice paragraph implies they'd open with "Hey there," use that. If it implies "Hi {{first_name}},", use that.
6. **Match close style.** Same — pull the close phrasing from the voice paragraph. If absent, use a neutral close (`Best,` or just the first name) and surface a `Notes` flag so the user can replace it.

When the user skipped voice input entirely, use generic-professional defaults (`Hi {{first_name}},`, no contractions, neutral adjectives, `Best,` close) and add a `Notes` row flag: `"Voice not specified — generic-professional default used"`.
