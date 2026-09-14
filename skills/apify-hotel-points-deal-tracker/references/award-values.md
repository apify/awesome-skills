# Award values and where the points cost comes from

The Google Hotels Actor returns the live CASH rate. The award cost in POINTS is not in Google Hotels, so this is how the skill gets it, and the baselines it judges value against. All numbers are rough defaults; edit `scripts/points_value.py` for your own habits.

## The metric

```
cents per point = nightly cash rate / points required * 100
```

Above the program baseline, points are the better deal; below it, pay cash. It is a yardstick, not a guarantee: award stays can still carry resort fees, and a cash stay earns points and status the number does not capture.

## Baseline valuations (cents per point)

| Program | Baseline | Points cost source |
|---------|----------|--------------------|
| Marriott Bonvoy | 0.7 | dynamic; from the app or an estimate |
| Hilton Honors | 0.5 | dynamic; from the app or an estimate |
| World of Hyatt | 1.7 | fixed award chart (below) |
| IHG One Rewards | 0.5 | dynamic; from the app |
| Wyndham Rewards | 0.9 | mostly flat tiers; from the app |
| Choice Privileges | 0.6 | from the app |
| Best Western Rewards | 0.6 | from the app |
| Accor Live Limitless | 2.0 | fixed cash conversion |

These are community-consensus rough values, not official. They only phrase the verdict; the cents-per-point number itself is exact from the live cash rate.

## World of Hyatt award chart (points per free night)

Hyatt is the one major program with a fixed published chart, so the skill looks the points up from the property category and season with no user input.

| Category | Off-peak | Standard | Peak |
|----------|----------|----------|------|
| 1 | 3,500 | 5,000 | 6,500 |
| 2 | 6,500 | 8,000 | 9,500 |
| 3 | 9,000 | 12,000 | 15,000 |
| 4 | 12,000 | 15,000 | 18,000 |
| 5 | 17,000 | 20,000 | 23,000 |
| 6 | 21,000 | 25,000 | 29,000 |
| 7 | 25,000 | 30,000 | 35,000 |
| 8 | 35,000 | 40,000 | 45,000 |

Verify the current chart and a property's category with Hyatt before booking; charts change.

## Dynamic programs (Marriott, Hilton, IHG)

Points cost moves with cash and is not published as a chart. Ask the traveler for the number they see in the app for the dates, or estimate from the cash rate. When estimating, say so in the output and tell them to confirm in the app before booking.

## Honest note to include in output

Cents per point is a decision aid, not a promise. It ignores resort fees on award stays, the points and status a paid stay earns, and whether an award room is even available. Present the verdict as a strong hint and tell the traveler to confirm availability and the points cost in their program.
