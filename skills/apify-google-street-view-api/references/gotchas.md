# Gotchas: Google Maps Photos API (`johnvc/google-maps-photos-api`)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, plus a platform fee of about $0.00001 per dataset row. Charge events:

- `photo_returned`: about $0.0015 per image returned (BRONZE tier at the time of writing).
- `place_search`: about $0.012 per search term, and not charged at all when you pass `placeUrls` or `dataIds`.
- `actor_start`: about $0.001 per run.

Confirm the live price before a large batch:

```bash
apify actors info "johnvc/google-maps-photos-api" --json \
  --user-agent apify-awesome-skills/apify-google-street-view-api \
  2>/dev/null
```

Worked estimates for this skill:

- One site checked by URL, a few panoramas, is a few tenths of a cent.
- Fifty sites passed as URLs is well under $1.
- Fifty sites found by name instead adds about $0.60 in search charges, so hold identifiers where you can.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Actor-specific notes

- Set `photoCategory` to `street_view` for panoramas or `videos` for clips. Both are universal categories that work on any place.
- Keep `maxPlacesPerSearch` at 1 for a single site; the default of 3 will sweep neighbouring businesses on a loose name.
- Coverage is genuinely uneven. Rural addresses, interior units, and new construction often have no panoramas, and an empty result is a real answer.
- You cannot request a heading, pitch, or field of view. This lists what is attached to the place rather than rendering a tile.
- No capture dates are returned, so panorama age is unknowable from the data.
- Read `place_categories` on the `place_summary` row to confirm which sections a place actually offers before concluding coverage is missing.

## Error recovery

- An empty `street_view` result means no panoramas are attached, not that the run failed. Check `photos_returned` on the summary row.
- Wrong building: the name matched a neighbour. Pass the Google Maps URL instead of a search term.
- Transient upstream failures: retry once before changing inputs.
- Input rejections happen before any charge; fix the named field and re-run.
- Image URLs are Google-hosted and can rotate. Re-host anything you intend to archive.
