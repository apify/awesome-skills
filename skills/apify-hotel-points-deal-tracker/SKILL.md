---
name: apify-hotel-points-deal-tracker
description: Track hotel cash rates on a schedule and get told the moment a points redemption becomes a good deal. You set target properties or a city, the loyalty program (Marriott Bonvoy, Hilton Honors, World of Hyatt, IHG, and more), and a cents-per-point threshold; it re-checks the live cash rate with the Apify Google Hotels Search Scraper (johnvc/google-hotels-search-scraper), divides by the award points cost, and flags when the value crosses your threshold so you book the award at the right time. Use when someone wants to monitor hotel points value over time, get an alert when points beat cash, track award deals, watch a Marriott or Hilton or Hyatt redemption, or know when to book a points stay. Pairs with apify-hotel-points-value for the one-time calculation.
author: John Cole
author_url: https://github.com/johnisanerd
license: MIT
metadata:
  version: "1.0"
  keywords: "hotel points deal tracker, award value alert, points redemption tracker, when to book points, monitor hotel points value, marriott points deal, hilton points alert, hotel price monitoring, google hotels, apify"
---

# Hotel Points Deal Tracker: alert me when points beat cash

A redemption is only a good deal when the cash rate is high relative to the fixed points cost. That moves day to day. This skill watches the live cash rate for the stays you care about on a schedule, divides by the award points cost to get cents per point, and flags the moment the value crosses the threshold you set, so you burn points when they are worth the most.

## When to use this skill

- Someone wants to monitor a points redemption over time, not just check it once.
- They want an alert when a Marriott, Hilton, or Hyatt award becomes a good deal (cash rate up, fixed points cost unchanged).
- They are holding points for a trip and want to know the right week to book.
- They want a running record of a property's cash rate and its cents-per-point so they can spot a spike.

Not for: a one-time cash-or-points check (use `apify-hotel-points-value`), booking the award (you book in your program), or pulling your points balance.

## How it works

The value of an award stay is `cash rate / points required * 100` in cents per point. The points cost is fixed for World of Hyatt (a published award chart) and moves slowly for dynamic programs, while the CASH rate swings with demand. So the signal is the cash rate: when it rises above `threshold cents per point * points`, the redemption clears your bar.

The Google Hotels Actor supplies the live cash rate, and Apify runs it on a schedule and stores each result, which gives you both the alert and the history. The points cost comes from the Hyatt chart or from the number you provide for a dynamic program.

## Prerequisites

- Apify account (sign up at https://apify.com?fpr=9n7kx3&fp_sid=awesomeskills); `apify login` or an `APIFY_TOKEN`.
- The award points cost per night (from the app for dynamic programs, or the Hyatt category).
- A cadence (weekly is typical) and a cents-per-point threshold (for example, alert when Marriott clears 0.8 cents).

## The Actor

- Store page: https://apify.com/johnvc/google-hotels-search-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/google-hotels-search-scraper`
- Scheduling and pay-per-event pricing: see `references/gotchas.md`.

## Run it with the Apify CLI

Re-check the cash rate for a tracked property and date (run this on a schedule):

```bash
apify actors call "johnvc/google-hotels-search-scraper" -i '{"search_type":"search","q":"Grand Hyatt New York","check_in_date":"2026-12-20","check_out_date":"2026-12-21","adults":2,"currency":"USD"}' \
  --json \
  --user-agent apify-awesome-skills/apify-hotel-points-deal-tracker \
  2>/dev/null
```

Every call carries the three flags this repo expects: `--json`, `--user-agent apify-awesome-skills/apify-hotel-points-deal-tracker`, and `2>/dev/null`.

## Run it from Claude or another AI agent (MCP)

The Actor is MCP-ready. Add the hosted server URL:

`https://mcp.apify.com/?tools=actors,docs,johnvc/google-hotels-search-scraper`

Then ask: "Watch the Grand Hyatt for my dates and tell me when a free-night award clears 2 cents per point."

## Workflow

1. Set the target and the bar. Capture the property or city, dates, the program, the points cost per night (or Hyatt category), the cadence, and the cents-per-point threshold that means "book it".
2. Schedule the cash-rate check. Configure an Apify schedule to run the search on your cadence and keep each dataset, so you build a rate history. See `references/gotchas.md` for scheduling.
3. Score each run. On each result, pull the numeric `extracted_lowest` cash rate and run `scripts/points_value.py` with the points cost to get the cents per point and the verdict.
4. Alert on a crossing. When a run's cents per point rises to or above the threshold (or the verdict flips to use points), surface it as the "book now" signal, with the cash rate, points, and value.
5. Keep the history. Track the cents-per-point series over runs so the traveler can see the trend and time the booking. `scripts/render_price_table.py` renders a snapshot or a history table.

## Inputs

- Target property or city, `check_in_date`, `check_out_date`, `adults`.
- Loyalty program, and points cost per night (or Hyatt `category`/`season`).
- Cadence (for example weekly) and a cents-per-point threshold.

## Cost guardrails

Each scheduled run is pay per event, roughly $0.04 for a one-page check. A weekly check on a handful of properties is a few cents a month. Keep the property list and `max_pages` tight; see `references/gotchas.md`.

## Honest limits

- Cash rates are live; the points cost is supplied or read from the Hyatt chart.
- Cents per point is a yardstick, not a guarantee; award stays can carry resort fees, and cash stays earn points and status.
- Award availability itself is not in Google Hotels; a good value does not guarantee an award room is open, so confirm in the program before you count on it.
- It does not book, and it does not see your points balance.

## Troubleshooting

See `references/gotchas.md` for scheduling, empty results, and the parse routine. See `references/award-values.md` for baselines and the Hyatt chart. See `references/actor-index.md` for the Actor routing table.

## Bundled scripts

- `scripts/points_value.py`: cash rate plus points in, cents per point and a verdict out; scores each scheduled run.
- `scripts/rewards.py`: a program name in, its hotel brand family out.
- `scripts/render_price_table.py`: rows in, a Markdown table and an email-ready HTML table out.

## Related travel skills and Actors

- The one-time calculation: the `apify-hotel-points-value` skill.
- Scheduled cash-rate monitoring in general: the `apify-hotel-price-monitoring` skill, built on https://apify.com/johnvc/google-hotels-search-scraper?fpr=9n7kx3&fp_sid=awesomeskills
- Plan the lodging or the whole trip: the `apify-plan-hotel-stays` and `apify-plan-a-trip` skills.
