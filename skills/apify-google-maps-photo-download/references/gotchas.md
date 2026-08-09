# Gotchas: Google Maps Photos API (`johnvc/google-maps-photos-api`)

Cost guardrails, error recovery, and input quirks. The agent reads this on demand when building inputs or when a run fails.

## Cost guardrails

Pricing model: pay per event, plus a platform fee of about $0.00001 per dataset row. Charge events:

- `photo_returned`: about $0.0015 per photo returned (BRONZE tier at the time of writing).
- `place_search`: about $0.012 per search term, and not charged at all when you pass `placeUrls` or `dataIds`.
- `actor_start`: about $0.001 per run.

Confirm the live price before a large batch:

```bash
apify actors info "johnvc/google-maps-photos-api" --json \
  --user-agent apify-awesome-skills/apify-google-maps-photo-download \
  2>/dev/null
```

Worked estimates for this skill:

- One place at 20 photos, found by search, is about $0.043.
- A 10-place sweep at 20 photos each is about $0.32.
- The same 10 places passed as URLs instead of a search is about $0.30, and scales better the more you run it.

Suggested confirmation thresholds:

- Rough estimate over $5: warn the user.
- Rough estimate over $20: get explicit confirmation before running.
- Always present cost as "around $X", not a guarantee.

## Actor-specific notes

- Billing is per photo delivered, so a place with a small gallery costs less; there is no per-page charge.
- `placeUrls` and `dataIds` are parsed locally and skip the search charge entirely. This is the single biggest cost lever.
- `maxPlacesPerSearch` defaults to 3 and caps at 20, so a bare category search sweeps more than one place unless you set it.
- Photos arrive from the source in blocks of twenty; `maxPhotosPerPlace` is the cap, not a guarantee.
- `menu`, `food_and_drink`, and `vibe` categories exist only on food and drink venues. `all`, `latest`, `videos`, `by_owner`, and `street_view` work anywhere.
- The `place_summary` row is not billed as a photo and carries `place_categories`, the venue's own gallery sections with their filter IDs.
- `photo_id` is stable across runs, which is what makes a scheduled refresh cheap: dedupe on it and only pay for new images.

## Error recovery

- A failed place emits an `error` row explaining the failure in plain terms; photos that never arrived are not charged.
- Transient upstream failures: retry once before changing inputs.
- Input rejections happen before any charge; fix the named field and re-run.
- If a run stops early at your budget limit, rows already delivered are kept and billed; raise the limit or narrow the input.
- Image URLs are Google-hosted and can rotate. Re-host anything you intend to display long term.
