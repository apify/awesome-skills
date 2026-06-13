# Gotchas — cost guardrails & error recovery

## Route = cost

- `google-maps-businesses` is the cheap path: Maps data only, no website visits. Use it when the user wants reach (map a whole niche) or only needs phone + signals.
- `google-maps-leads-with-emails` is richer and costlier: it visits each business website to extract and verify emails. Cost scales with `maxResults` × sites crawled. For a first pass, run 25–50 and inspect before scaling.
- `website-contact-finder` cost scales with domains × `maxPagesPerDomain` (default 4). Lower pages for a quick email-only sweep.

A cheap calibration run: one query, depth 25, on `google-maps-businesses` first to gauge niche density and signal quality, then switch to the email path for the shortlist.

## Google Maps fragility

Google Maps occasionally throttles or times out (the Actor uses a real browser). A run that fails with a `page.goto` timeout is usually transient — retry once, or retry with a slightly different phrasing of the query. This is upstream behavior, not a bad input.

## Opportunity-signal caveats

- A missing `website` field can mean "no site" **or** "Google didn't surface one." For the `web-design` angle, spot-check a few before pitching "you have no website."
- `rating` / `reviewCount` are point-in-time. A 3.9 with 200 reviews is a different story than a 3.9 with 4 reviews — weight both together, don't rank on rating alone.

## Email deliverability

When the email path runs, every address is tagged `valid` / `risky` / `invalid` (syntax + disposable + role + live MX). Don't mass-send to `risky`/`invalid` — filter to `validEmails` for cold outreach and keep `risky` (often role addresses like `info@`) for a separate, lower-volume touch.

## Empty results

Zero businesses usually means the niche+city phrasing was too narrow or misspelled. Broaden ("dentists in Miami" vs "pediatric dentists in Miami Beach FL 33139") and retry.
