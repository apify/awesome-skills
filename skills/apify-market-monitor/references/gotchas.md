# Gotchas — cost and reliability

## Cost

- These Actors render real pages and default to Apify **residential** proxies. Residential transfer is the dominant cost; a large market or high `maxResults`/`maxProducts`/`maxVideos*` run costs materially more than a small one. Confirm scope with the user before raising limits.
- Several Actors are pay-per-event (PPE) on top of compute. Read the per-event price on the Store listing before a bulk run.
- Start small: run one entity (one hashtag, one ASIN, one market) to confirm the output shape and cost, then scale.

## The memory clock

- Monitoring value comes from a named `watchlistName` (or `mode: "monitor"`). State is keyed on that name.
- Renaming the watchlist starts a fresh memory clock — prior history is not carried over.
- The clock cannot be backfilled. Run 1 is a baseline with no deltas; trajectory and anomaly reads unlock only after several scheduled runs.

## Coverage honesty

- Platforms cap results per query (for example Amazon search ~7 pages, Airbnb a market ~240 listings). These Actors report requested vs returned coverage rather than silently truncating — surface that number to the user instead of implying a full census.

## Recovery

- A failed run carries a `.consoleUrl` in its run metadata; open it for logs.
- On no results, broaden the query or check that the target (ASIN, market, handle, URL) is valid and public.
