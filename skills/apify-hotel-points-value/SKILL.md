---
name: apify-hotel-points-value
description: Work out what your hotel points are worth for a specific stay and whether to pay cash or redeem points. Given a destination, dates, party size, and a loyalty program (Marriott Bonvoy, Hilton Honors, World of Hyatt, IHG, Wyndham, and more), it pulls the live cash rate with the Apify Google Hotels Search Scraper (johnvc/google-hotels-search-scraper), divides by the award points cost to get cents per point, ranks where your points go furthest, and returns a cash-or-points verdict against each program's baseline value. Use when someone asks what are my Marriott points worth, what are Hilton points worth, should I pay cash or use points, best value points redemption, or how to get the most from hotel points. World of Hyatt uses its fixed award chart automatically; dynamic programs take the points from your app or an estimate.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
  keywords: "hotel points value, marriott points value, hilton points value, world of hyatt points value, cash or points, best value points redemption, how much are hotel points worth, points optimization, google hotels, apify"
---

# Hotel Points Value: what your points are worth, cash or points

Answer the question a points traveler asks on every booking: is this stay a good use of points, or should I pay cash? This skill pulls the live cash rate for a property and date, divides it by the award points cost to get cents per point, ranks the stays where your points go furthest, and gives a plain verdict against your program's baseline value.

## When to use this skill

- Someone asks "what are my Marriott points worth", "what are Hilton points worth", or "what is a World of Hyatt point worth" for a real stay.
- They are deciding "cash or points" for a hotel and want the math, not a hunch.
- They want the best value redemption across a city or a set of dates, ranked.
- They want to know if a specific award booking clears their program's baseline value before they burn the points.

Not for: booking the award (this reads cash prices and does the value math; you book in your program), flights or airline miles, or pulling your live points balance (it does not have your account).

## How the value math works (and its honest limit)

The Google Hotels Actor returns the live CASH rate. The AWARD cost in points is not in Google Hotels, so it comes from one of two places:

- **World of Hyatt:** a fixed published award chart, so the skill looks the points up itself from the property's category and season. No user input needed.
- **Dynamic programs (Marriott, Hilton, IHG, Wyndham):** points move with cash, so pass the number you see in the app, or let the skill estimate.

Then:

```
cents per point = nightly cash rate / points required * 100
```

The verdict compares that to a rough per-program baseline (Marriott about 0.7 cents, Hilton about 0.5, Hyatt about 1.7). Above baseline, use points; below, pay cash. Cents per point is the standard yardstick, not a guarantee: award stays can still carry resort fees, and a cash stay earns points and status the number does not capture. Say that in the output.

## What you get back (from the hotels Actor)

One dataset item per results page. Each property carries `name`, `rate_per_night` and `total_rate` (with a numeric `extracted_lowest`), `overall_rating`, `reviews`, `hotel_class`, `gps_coordinates`, `link`, and `property_token`. The skill computes cents per point and a verdict on top of the numeric `extracted_lowest` cash rate.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills).
- Authenticate with `apify login`, or set an `APIFY_TOKEN` environment variable.
- The award points cost per night: from the traveler's app for dynamic programs, or the Hyatt category for a fixed-chart lookup.

## The Actor

- Store page: https://apify.com/johnvc/google-hotels-search-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/google-hotels-search-scraper`
- Pricing: pay per page of results processed plus a small per-run setup fee (see `references/gotchas.md`).

## Run it with the Apify CLI

Pull the live cash rates for a program's properties in a city and date (brand-bias the query to the chain when it helps):

```bash
apify actors call "johnvc/google-hotels-search-scraper" -i '{"search_type":"search","q":"Marriott hotels in Chicago","check_in_date":"2026-10-15","check_out_date":"2026-10-16","adults":2,"currency":"USD"}' \
  --json \
  --user-agent apify-awesome-skills/apify-hotel-points-value \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-hotel-points-value`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/google-hotels-search-scraper`

Then ask, for example: "For Marriott in Chicago on Oct 15, what is the cash rate, and at 50,000 points a night is that a good use of my Bonvoy points?"

## Workflow

1. Gather the inputs: destination, dates, party, the loyalty program, and the points cost per night (or the Hyatt category). Confirm what you are missing.
2. Search the cash rates. Run `johnvc/google-hotels-search-scraper` for the location and dates. Brand-bias `q` to the chain (for example "Hilton hotels in Denver") or run a normal search and keep the rows whose `name` matches the program's brand family (`scripts/rewards.py "Hilton Honors"` returns the brand list).
3. Parse the cash rates. Flatten `properties`, keep `name`, `extracted_lowest` cash rate, `overall_rating`, `link`. For a large result, hand the saved file to a subagent (see `references/gotchas.md`).
4. Attach the points cost. For Hyatt, pass the category and let `scripts/points_value.py` read the fixed chart. For dynamic programs, pass the points the traveler sees, or estimate.
5. Compute and rank. Feed a `{program, rows}` JSON to `scripts/points_value.py --in rows.json`; it returns each row with `cents_per_point`, the baseline, and a `verdict`, sorted best value first.
6. Deliver. Present the ranked "where your points go furthest" table with the cash rate, points, cents per point, and verdict per property, and a one-line recommendation. Use `scripts/render_price_table.py` for a Markdown or email-ready table. Include the honest-limit note.

## Inputs

- Loyalty program name (maps via `scripts/rewards.py`).
- Destination, `check_in_date`, `check_out_date`, `adults`.
- Points cost per night (dynamic programs) or Hyatt `category` and `season`.
- Optional: `min_price`/`max_price`, `hotel_class`, `currency`, `gl`, `hl`.

## Cost guardrails

Pay per event: a per-run setup fee plus a fee per page of results processed (around $0.018 per page at BRONZE tier). A one-page search lands around $0.04. `max_pages` is the cost cap. See `references/gotchas.md`.

## Honest limits

- Cash rates are live; the points cost is not (you supply it, or Hyatt is looked up from the fixed chart).
- Cents per point is a yardstick, not a guarantee. Award stays can carry resort fees; cash stays earn points and status.
- It does not book, and it does not see your points balance.
- Baseline valuations are rough defaults; edit them in `scripts/points_value.py` for your own habits.
- Dynamic-program point costs change; confirm the number in the app before booking.

## Troubleshooting

See `references/gotchas.md` for empty results, currency defaults, and the subagent parse routine. See `references/award-values.md` for the baseline valuations and the Hyatt award chart. See `references/actor-index.md` for the Actor routing table.

## Bundled scripts

- `scripts/points_value.py`: cash rate plus points in, cents per point and a cash-or-points verdict out (single stay or a ranked batch; Hyatt chart built in).
- `scripts/rewards.py`: a program name in, its hotel brand family out (for filtering the search).
- `scripts/render_price_table.py`: rows in, a Markdown table and an email-ready HTML table out.

## Related travel skills and Actors

- Track a redemption over time and get alerted when it beats your threshold: the `apify-hotel-points-deal-tracker` skill.
- Plan the lodging or the whole trip: the `apify-plan-hotel-stays` and `apify-plan-a-trip` skills.
- Export raw hotel data: the `apify-scrape-hotel-prices` skill, built on https://apify.com/johnvc/google-hotels-search-scraper?fpr=9n7kx3&fp_sid=awesomeskills
