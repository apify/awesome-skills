---
name: apify-google-street-view-api
description: Pull Street View and 360 panoramas for a place by name with a google maps street view api built on the Apify Google Maps Photos API Actor (johnvc/google-maps-photos-api). The official Street View Static endpoint wants a latitude, longitude and heading and returns one rendered tile; this returns a listing of the panoramas actually attached to a business, addressed by its name or its Google Maps URL, as rows with the full-size image url, a thumbnail, gallery position and a stable photo id. Set the category to street_view for panoramas or videos for clips. Use when the user wants a street view api, google street view images for a business, 360 photos of a location, exterior or frontage imagery for site surveys, real estate, insurance or field-service work, without geocoding first. Pay per image returned, MCP-ready for Claude and other AI agents.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
---

# Street View and 360 Panoramas, Addressed by Place Name

A Street View API you can call with a business name instead of coordinates, returning the panoramas attached to that place as rows.

## When to use this skill

- The user wants a "street view api" or "google street view images" for a specific business.
- They need 360 panoramas or exterior frontage shots for site surveys, real estate, insurance, or field-service prep.
- They have a place name or a Google Maps URL and do not want to geocode and pick a heading first.
- They want the video clips attached to a place rather than still photos.

Not for: bulk gallery download across a whole category (use the companion apify-google-maps-photo-download skill) or routing and drive times (`johnvc/google-maps-directions-api`). See `references/actor-index.md`.

## Why this is not the official Street View endpoint

Street View Static renders one tile from a latitude, longitude, heading, pitch, and field of view you supply. Getting from "this restaurant" to "the right panorama facing the right way" is a geocoding and aiming problem you own. This skill instead lists the panoramas Google already associates with the place, so the aiming is already done and the input is a name.

## What you get

One dataset row per image. `result_type` separates the row kinds:

- `image` (full-size URL) and `thumbnail`
- `position` in the gallery section
- `photo_id`, stable across runs
- `data_id` and `place_title`
- `category_id`, echoing the filter that was applied
- one `place_summary` row per place with `photos_returned` and `place_categories`

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authentication via `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## The Actor

- Store page: https://apify.com/johnvc/google-maps-photos-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/google-maps-photos-api`
- Pricing: pay per event; see the cost section below and `references/gotchas.md` for live-price commands.

## Run it with the Apify CLI

Street View and 360 panoramas for one place:

```bash
apify actors call "johnvc/google-maps-photos-api" -i '{"searchTerm":"Mozart Coffee Roasters, Austin TX","maxPlacesPerSearch":1,"photoCategory":"street_view","maxPhotosPerPlace":20}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-street-view-api \
  2>/dev/null
```

Panoramas for a list of sites you already hold URLs for:

```bash
apify actors call "johnvc/google-maps-photos-api" -i '{"placeUrls":["https://www.google.com/maps/place/..."],"photoCategory":"street_view"}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-street-view-api \
  2>/dev/null
```

Video clips instead of stills:

```bash
apify actors call "johnvc/google-maps-photos-api" -i '{"searchTerm":"Mozart Coffee Roasters, Austin TX","maxPlacesPerSearch":1,"photoCategory":"videos"}' \
  --json \
  --user-agent apify-awesome-skills/apify-google-street-view-api \
  2>/dev/null
```

Confirm live pricing and the input schema before a large batch:

```bash
apify actors info "johnvc/google-maps-photos-api" --json \
  --user-agent apify-awesome-skills/apify-google-street-view-api \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-google-street-view-api`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-photos-api`

Then ask, for example: "Get the Street View panoramas for this address and tell me whether the entrance looks step-free." MCP setup docs: https://docs.apify.com/platform/integrations/mcp

## Workflow

1. Identify the place by name plus city, or by its Google Maps URL. A URL costs nothing to resolve; a search adds one charge.
2. Set `photoCategory` to `street_view` for panoramas, or `videos` for clips.
3. Keep `maxPlacesPerSearch` at 1 when you mean one specific site, so a loose name does not sweep neighbours.
4. Read the rows; check `photos_returned` on the summary row before concluding a place has no coverage.
5. Re-host anything you plan to display or archive.

## Inputs

- `searchTerm` (string): a place name, ideally with city and state
- `placeUrls` (array): Google Maps URLs, parsed locally at no API cost
- `dataId` / `dataIds` (string, array): place identifiers you already hold
- `photoCategory` (enum, use `street_view` here, or `videos` for clips)
- `maxPlacesPerSearch` (integer, default 3, max 20): keep at 1 for a single site
- `maxPhotosPerPlace` (integer, default 20, max 1000)
- `hl` (string, default `en`): interface language

## Cost

Billing is pay per event, plus a negligible platform fee per dataset row. Prices below are the BRONZE tier at the time of writing; confirm live prices with the info command above.

- About $0.0015 per image returned.
- About $0.012 per search term, and nothing when you pass URLs or identifiers instead.
- About $0.001 to start a run.
- Checking 50 sites by URL, a few panoramas each, is well under $1.

Suggested confirmation thresholds: warn the user over about $5; get explicit confirmation over about $20. Present cost as "around $X", never a guarantee.

## Honest limits

- Street View coverage is uneven. Rural addresses, interior units, and new construction often have none, and an empty result is a real answer rather than a failure.
- The panoramas are whatever Google associates with the place. You cannot request a specific heading, pitch, or field of view the way the Static endpoint lets you.
- No capture dates, so there is no way to tell how old a panorama is or to request an older one.
- Image URLs are Google-hosted and can rotate, so hotlinking them long term is unreliable.

## Troubleshooting

- Empty result for `street_view`: that place has no panoramas attached. Read `place_categories` on the summary row to see which sections do exist.
- Wrong building: the name matched a neighbour. Pass the Google Maps URL instead of a search term.
- Several places came back when you wanted one: set `maxPlacesPerSearch` to 1.
- An `error` row: clean failure, stated plainly; retry once before investigating.

See `references/gotchas.md` for cost guardrails and error recovery, and `references/actor-index.md` for the Actor routing table.

## Related Actors

- Google Maps Places API: https://apify.com/johnvc/google-maps-places-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Directions API: https://apify.com/johnvc/google-maps-directions-api?fpr=9n7kx3&fp_sid=awesomeskills
- Google Maps Contributor Reviews API: https://apify.com/johnvc/google-maps-contributor-reviews-api?fpr=9n7kx3&fp_sid=awesomeskills
- Apple Maps API: https://apify.com/johnvc/apple-maps-api?fpr=9n7kx3&fp_sid=awesomeskills
