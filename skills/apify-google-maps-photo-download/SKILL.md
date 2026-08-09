---
name: apify-google-maps-photo-download
description: Bulk google maps photo download with the Apify Google Maps Photos API Actor (johnvc/google-maps-photos-api). Name a place, paste a Google Maps URL, or search a category and city, and get one row per photo with the full-size image url, a thumbnail, its gallery position, and a stable photo id you can de-duplicate on across runs. One run sweeps up to 20 places, so a whole neighbourhood of businesses comes back in a single pass instead of one right-click at a time. Filter to a gallery section when you only want menus, interiors, or owner uploads. Use when the user wants to download google maps photos, bulk place images, a google maps images api, place photos api access, or imagery for a directory, listings site, or dataset. Pay per photo returned, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Bulk Google Maps Photo Download, One Row Per Photo

Every photo a place has on Google Maps, as structured rows: full-size URL, thumbnail, gallery position, and a stable ID you can dedupe on.

## When to use this skill

- The user wants to "download google maps photos" for a business, or for many businesses at once.
- They need imagery for a directory, listings site, travel app, or training dataset.
- They want a "google maps images api" or "place photos api" they can call from code.
- They already have Google Maps URLs or place identifiers and want the galleries behind them.

Not for: Street View and 360 panoramas (use the companion apify-google-street-view-api skill), place details like ratings and hours (`johnvc/google-maps-places-api`), or review text (`johnvc/google-maps-contributor-reviews-api`). See `references/actor-index.md`.

## What you get

One dataset row per photo. `result_type` separates the row kinds:

- `image` (full-size URL) and `thumbnail` (smaller preview of the same shot)
- `position`, where it sits in the place's gallery
- `photo_id`, stable across runs, which is what makes scheduled refreshes cheap
- `data_id` and `place_title`, the place the photo belongs to
- `category_id` when a gallery filter was applied
- one `place_summary` row per place with `photos_returned`, `pages_fetched`, and `place_categories`

It does not return captions, EXIF, contributor names, or upload dates.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/google-maps-photos-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/google-maps-photos-api`
- Pricing: pay per event; see the cost section below and `references/gotchas.md` for live-price commands.

## Run it with the Apify CLI

One place by name:

```bash
apify actors call "johnvc/google-maps-photos-api" -i '{"searchTerm":"Mozart Coffee Roasters, Austin TX","maxPlacesPerSearch":1,"maxPhotosPerPlace":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-maps-photo-download \
  2>/dev/null
```

Sweep a category across a city:

```bash
apify actors call "johnvc/google-maps-photos-api" -i '{"searchTerm":"coffee shops in Austin, TX","maxPlacesPerSearch":10,"maxPhotosPerPlace":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-maps-photo-download \
  2>/dev/null
```

Skip the search charge with URLs you already hold:

```bash
apify actors call "johnvc/google-maps-photos-api" -i '{"placeUrls":["https://www.google.com/maps/place/..."],"maxPhotosPerPlace":40}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-maps-photo-download \
  2>/dev/null
```

Confirm live pricing and the input schema before a large batch:

```bash
apify actors info "johnvc/google-maps-photos-api" --json \
  --user-agent apify-awesome-skills/apify-google-maps-photo-download \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-google-maps-photo-download`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-photos-api`

Then ask, for example: "Download every photo for the three highest-rated ramen places in Austin and list the full-size URLs." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Pick the cheapest way in. A Google Maps URL or a place identifier costs nothing to resolve; a `searchTerm` adds one search charge.
2. Bound the sweep with `maxPlacesPerSearch` (default 3, max 20) and the depth with `maxPhotosPerPlace` (default 20).
3. Run, then split rows on `result_type`: `photo`, `place_summary`, `error`.
4. Store `photo_id` alongside each image. On the next run, skip IDs you already hold.
5. Re-host anything you plan to display; the Google-hosted URLs can rotate.

## Inputs

- `searchTerm` (string): a place name, or a category plus a city
- `searchTerms` (array): several searches in one run
- `placeUrls` (array): Google Maps URLs, parsed locally at no API cost
- `dataId` / `dataIds` (string, array): place identifiers you already hold
- `maxPlacesPerSearch` (integer, default 3, max 20): how wide a search sweeps
- `maxPhotosPerPlace` (integer, default 20, max 1000): how deep per place
- `photoCategory` (enum `all`, `latest`, `videos`, `by_owner`, `street_view`, `menu`, `food_and_drink`, `vibe`, default `all`)
- `categoryId` (string): a venue-specific section ID taken from a `place_summary` row
- `hl` (string, default `en`): interface language

## Cost

Billing is pay per event, plus a negligible platform fee per dataset row. Prices below are the BRONZE tier at the time of writing; confirm live prices with the info command above.

- About $0.0015 per photo returned.
- About $0.012 per search term, and nothing when you pass URLs or identifiers instead.
- About $0.001 to start a run.
- A 10-place sweep at 20 photos each is about $0.32.

Suggested confirmation thresholds: warn the user over about $5; get explicit confirmation over about $20. Present cost as "around $X", never a guarantee.

## Honest limits

- Gallery size varies enormously, from a handful at a small office to several hundred at a busy restaurant. Photos arrive in blocks of twenty.
- `menu`, `food_and_drink`, and `vibe` exist only on food and drink venues; the other five categories work anywhere.
- No captions, EXIF, contributor names, or upload dates, so there is no way to filter by when a photo was taken.
- No historical imagery. This returns the current gallery, not what the place looked like years ago.
- Image URLs are Google-hosted and can rotate, so hotlinking them long term is unreliable.

## Troubleshooting

- Fewer photos than `maxPhotosPerPlace`: the place has that many, and `photos_returned` on the summary row confirms it.
- A category returns nothing: it is probably food-venue only. Read `place_categories` on the summary row to see what that place actually offers.
- Search matched the wrong place: add the city and state to `searchTerm`, or pass the Google Maps URL directly.
- An `error` row: clean failure, stated plainly; retry once before investigating.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Google Maps Places API: https://apify.com/johnvc/google-maps-places-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Contributor Reviews API: https://apify.com/johnvc/google-maps-contributor-reviews-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Directions API: https://apify.com/johnvc/google-maps-directions-api?fpr=9n7kx3&fp_sid=awesomeskills
- Apple Maps API: https://apify.com/johnvc/apple-maps-api?fpr=9n7kx3&fp_sid=awesomeskills
