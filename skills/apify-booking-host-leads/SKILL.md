---
name: apify-booking-host-leads
description: Find and enrich B2B leads from Booking.com - hotels, apartments, and vacation rentals - and pull each host's or property manager's real contact details (email, phone, company name, registration number). Use when the user says things like "get emails from Booking.com", "Booking.com lead generation", "find tour operator / property manager / host contacts", "scrape accommodation owner emails", or "build a list of Booking hosts". The host's email is usually already inside the Booking scraper's traderInfo field (EU/AU trader-transparency disclosure) - this skill leads with that and uses a Google Maps email scraper only as a fallback, instead of relying on Google Maps first (which mostly returns the wrong business).
author: Daniela Ryplová
author_url: https://github.com/danielarypl
---

# Booking.com host & operator lead finder

Turn a Booking.com destination search into a clean table of accommodation hosts / property managers with their real contact details.

## The key insight

When you scrape Booking.com, the host's contact email is **sometimes already in the data** under `traderInfo` (a trader-transparency disclosure). But this is **region-dependent**: strong in the EU (Zurich apartments: 80%) and Australia (Melbourne apartments: 82% in a 50-property test), and increasingly present in Asia (Beijing apartments: 65% as of June 2026, typically a QQ, 163, or Gmail address plus a Chinese company name). It is historically sparser in the US and UK. A naive chained Google Maps email scraper found emails for only ~10% and often matched the wrong business.

**So use a waterfall**: try the cheapest source first, fall through to more expensive ones only for leads still missing a contact. Never start with a Google Maps email extractor.

| Tier | Source | Gets | Fires when |
|------|--------|------|-----------|
| 1 | Booking `traderInfo` | email, phone, company | always (free, already scraped) |
| 2 | Google Maps Email Extractor (by name) | email, phone, socials, **website** | lead still has no email |
| 3 | Google Search (by name) | a candidate **website** | lead still has no website |
| 4 | Website contact scraper (on the website) | email / phone / socials | lead has a website but still no email |

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. **Collect inputs.** Ask the user for: destination (city/area), property type (Apartments / Guest houses / Holiday homes / Villas surface the most independent operators; `none` = all), max properties, and output format (CSV / JSON / Google Sheet).
2. **Tier 1 - Scrape Booking.com.** Run `voyager/booking-scraper`. Build a lead row per property from `traderInfo` and `hostInfo` (see Mapping below). Mark rows where `traderInfo.email` is present as `contactSource: booking-trader`.
3. **Tier 2 - Google Maps (only rows still missing an email).** Run `lukaskrivka/google-maps-with-contact-details` with `searchStringsArray = ["<name>, <destination>", ...]`. Fill email/phone/socials and capture any **website** it returns. Mark filled rows `google-maps`.
4. **Tier 3 - Google Search (only rows still missing a website).** Run `apify/google-search-scraper` with one query per lead (`"<name> <city> official website"`). Take the first non-OTA/non-social `organicResults[].url` as the candidate website.
5. **Tier 4 - scrape the website (only rows with a website but no email).** Default: `vdrmota/contact-info-scraper` (deterministic, ~14s/site). Optional: `apify/ai-web-scraper` with a prompt for email/phone/contact-form URL - but in live testing it was slow and failed on multiple sites, so prefer the contact scraper. Mark filled rows `website-contact` (or `website-ai`). Cap the count to control cost.
6. **Deliver.** Output one row per property. Report total rows, % with an email, and the `contactSource` breakdown. Rows still empty keep `BookingURL` (contact via Booking messaging).

### Mapping (Booking item → lead row)

| Output column | Source field |
|---------------|--------------|
| `name`, `type`, `address`, `city`, `country`, `rating`, `ratingLabel`, `stars`, `reviews`, `BookingURL` | top-level Booking fields (`address.full`, `address.city`, `address.country`, `rating`, `ratingLabel`, `reviews`, `url`) |
| `email`, `phone` | `traderInfo.email` / `traderInfo.phone` → fallback Google Maps `emails[0]` / `phones[0]` |
| `companyName`, `registrationNumber`, `traderAddress` | `traderInfo.companyName` / `.registrationNumber` / `.address` |
| `hostName`, `managedProperties` | `hostInfo.name` / `hostInfo.managedProperties` (operator-size signal) |
| `website`, `socials` | Google Maps fallback only; drop OTA domains (booking.com, agoda, expedia, etc.) |
| `contactSource` | `booking-trader` \| `google-maps` \| `none` |

Put `email` and `phone` immediately after `address` in the output.

Always return `BookingURL` (link to the property), `rating`, `ratingLabel` (e.g. "Superb", "Exceptional"), and `reviews` (review count) for every lead. These give each row its own quality signal, so leads can be ranked and prioritized without re-opening Booking.

## Actor routing

| Waterfall tier | Actor ID | Maintainer | Best for |
|----------------|----------|------------|----------|
| 1 - Booking + trader contacts | `voyager/booking-scraper` | community | **Primary.** `traderInfo` holds host email/phone/company |
| 2 - email/social/website by name | `lukaskrivka/google-maps-with-contact-details` | community | Emails Booking doesn't disclose; also returns a website |
| 3 - discover a website | `apify/google-search-scraper` | apify | Finding the host's official site when Maps has none |
| 4 - extract from the website (default) | `vdrmota/contact-info-scraper` | community | Deterministic email/phone/social extraction; fast and reliable |
| 4 - extract from the website (alt) | `apify/ai-web-scraper` | apify | LLM extraction via prompt; flexible but slow/unreliable in testing |

Prefer `apify`-maintained Actors where available.

## Calling Actors — Apify CLI

Three flags on every call (`--json`, `--user-agent`, `2>/dev/null`):

    # 1. Scrape Booking.com
    apify actors call "voyager/booking-scraper" \
      -i '{"search":"Melbourne","maxItems":50,"propertyType":"Apartments","currency":"USD","language":"en-us","sortBy":"distance_from_search","rooms":1,"adults":2}' \
      --json \
      --user-agent apify-awesome-skills/apify-booking-host-leads \
      2>/dev/null

    # Tier 2 - enrich names that have no traderInfo email
    apify actors call "lukaskrivka/google-maps-with-contact-details" \
      -i '{"searchStringsArray":["<name>, Melbourne"],"locationQuery":"Melbourne","maxCrawledPlacesPerSearch":1,"language":"en"}' \
      --json \
      --user-agent apify-awesome-skills/apify-booking-host-leads \
      2>/dev/null

    # Tier 3 - discover a website for leads that still have none
    apify actors call "apify/google-search-scraper" \
      -i '{"queries":"<name> Melbourne official website","maxPagesPerQuery":1,"resultsPerPage":5,"countryCode":"us","languageCode":"en"}' \
      --json \
      --user-agent apify-awesome-skills/apify-booking-host-leads \
      2>/dev/null

    # Tier 4 - AI-extract a contact email / form URL from the website
    # (confirm the prompt/instructions field name against the Actor's input schema)
    apify actors call "apify/ai-web-scraper" \
      -i '{"startUrls":[{"url":"<website>"}],"prompt":"Extract the contact email, phone, and contact-form URL. Return JSON keys: email, phone, contactFormUrl."}' \
      --json \
      --user-agent apify-awesome-skills/apify-booking-host-leads \
      2>/dev/null

    # Inspect input schema / fetch results
    apify actors info "voyager/booking-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-booking-host-leads 2>/dev/null
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-booking-host-leads 2>/dev/null

The Apify MCP server (<https://mcp.apify.com>) and any MCP client (e.g. `mcpc`) are equivalent alternatives.

## Troubleshooting

- **No emails returned** → you are probably reading Google Maps output instead of `traderInfo`. Re-check the Booking item's `traderInfo` field first.
- **Emails for the wrong business** → that is the Google Maps fallback matching a generic place. Trust `contactSource: booking-trader` rows; treat `google-maps` rows as lower confidence.
- **Many `contactSource: none` rows** → those hosts disclosed no trader info and have no Google Business match. Use the `BookingURL` to contact via Booking, or accept the blank.
- **Run cost climbs** → skip the Google Maps fallback entirely; `traderInfo` alone covers ~80%.
- See [references/gotchas.md](references/gotchas.md) for cost notes.
