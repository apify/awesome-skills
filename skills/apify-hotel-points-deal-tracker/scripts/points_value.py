#!/usr/bin/env python3
"""Turn a live cash rate into a cash-or-points verdict for a hotel stay.

The Google Hotels Actor returns the live CASH rate. A points traveler knows
(or can look up) the AWARD cost in points. This helper does the division that
decides the stay:

    cents per point = nightly cash rate / points required * 100

then compares it to the program's rough baseline value and says use points,
pay cash, or toss-up. It runs one stay at a time, or a batch of rows from a
search so it can rank where your points go furthest.

Honest limits (say these in the output):
- Cash rates are live from the Actor; the POINTS cost is not. For dynamic
  programs (Marriott, Hilton, IHG) pass the points you see in the app, or let
  the tool estimate from the cash rate. For World of Hyatt the award chart is
  fixed, so pass a category and the tool looks the points up itself.
- Cents per point is the standard yardstick, not a guarantee. Award stays can
  still carry resort fees, and cash stays earn points and status credit that a
  simple per-point number does not capture. Treat the verdict as a strong hint.

Stdlib only.

Usage:
  # single stay, points known
  python3 points_value.py --program "Marriott Bonvoy" --cash 412 --points 50000
  # single Hyatt stay, points looked up from the fixed chart
  python3 points_value.py --program "World of Hyatt" --cash 400 --category 4 --season standard
  # batch: rank a search by value
  python3 points_value.py --in rows.json --out ranked.json
  # list what the tool knows
  python3 points_value.py --list
"""

import argparse
import json
import sys

# Rough baseline valuations, cents per point. Community consensus, not gospel;
# edit for your own redemption habits. Used only to phrase the verdict.
PROGRAM_BASELINES = {
    "Marriott Bonvoy": 0.7,
    "Hilton Honors": 0.5,
    "World of Hyatt": 1.7,
    "IHG One Rewards": 0.5,
    "Wyndham Rewards": 0.9,
    "Choice Privileges": 0.6,
    "Best Western Rewards": 0.6,
    "Accor Live Limitless": 2.0,
}

# World of Hyatt is the one major program with a FIXED published award chart,
# so points cost is knowable without the user. Points per free night by
# category and season. (Standard chart; verify against Hyatt before booking.)
HYATT_AWARD_CHART = {
    1: {"off": 3500,  "standard": 5000,  "peak": 6500},
    2: {"off": 6500,  "standard": 8000,  "peak": 9500},
    3: {"off": 9000,  "standard": 12000, "peak": 15000},
    4: {"off": 12000, "standard": 15000, "peak": 18000},
    5: {"off": 17000, "standard": 20000, "peak": 23000},
    6: {"off": 21000, "standard": 25000, "peak": 29000},
    7: {"off": 25000, "standard": 30000, "peak": 35000},
    8: {"off": 35000, "standard": 40000, "peak": 45000},
}

# lowercase alias -> canonical program name
ALIASES = {
    "marriott": "Marriott Bonvoy", "bonvoy": "Marriott Bonvoy",
    "hilton": "Hilton Honors", "honors": "Hilton Honors",
    "hyatt": "World of Hyatt",
    "ihg": "IHG One Rewards",
    "wyndham": "Wyndham Rewards",
    "choice": "Choice Privileges",
    "best western": "Best Western Rewards",
    "accor": "Accor Live Limitless", "all": "Accor Live Limitless",
}


def canonical_program(name):
    if not name:
        return None
    q = name.strip().lower()
    if q in (k.lower() for k in PROGRAM_BASELINES):
        for k in PROGRAM_BASELINES:
            if k.lower() == q:
                return k
    for alias, prog in ALIASES.items():
        if alias in q:
            return prog
    return None


def hyatt_points(category, season="standard"):
    cat = int(category)
    season = (season or "standard").lower()
    if cat not in HYATT_AWARD_CHART:
        return None
    return HYATT_AWARD_CHART[cat].get(season, HYATT_AWARD_CHART[cat]["standard"])


def cents_per_point(cash_rate, points_required):
    try:
        cash = float(cash_rate)
        pts = float(points_required)
    except (TypeError, ValueError):
        return None
    if pts <= 0:
        return None
    return round(cash / pts * 100.0, 3)


def verdict(program, cpp):
    """USE POINTS / PAY CASH / TOSS-UP vs the program baseline."""
    if cpp is None:
        return "UNKNOWN", None
    base = PROGRAM_BASELINES.get(program)
    if base is None:
        return "NO BASELINE", None
    if cpp >= base * 1.1:
        return "USE POINTS", base
    if cpp <= base * 0.9:
        return "PAY CASH", base
    return "TOSS-UP", base


def evaluate_row(program, row):
    """row: {name, cash_rate, points?|category?,season?}. Returns enriched row."""
    pts = row.get("points")
    if pts is None and program == "World of Hyatt" and row.get("category") is not None:
        pts = hyatt_points(row["category"], row.get("season", "standard"))
    cpp = cents_per_point(row.get("cash_rate"), pts)
    v, base = verdict(program, cpp)
    out = dict(row)
    out["points_used"] = pts
    out["cents_per_point"] = cpp
    out["baseline_cpp"] = base
    out["verdict"] = v
    return out


def main():
    ap = argparse.ArgumentParser(description="Cash-or-points verdict from a live cash rate.")
    ap.add_argument("--program")
    ap.add_argument("--cash", type=float)
    ap.add_argument("--points", type=float)
    ap.add_argument("--category", type=int, help="World of Hyatt category 1-8")
    ap.add_argument("--season", default="standard", choices=["off", "standard", "peak"])
    ap.add_argument("--in", dest="infile", help="Batch JSON: {program, rows:[{name,cash_rate,points|category,season}]}")
    ap.add_argument("--out", dest="out")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        print("Program baselines (cents per point):")
        for k, v in PROGRAM_BASELINES.items():
            print("  %-24s %.2f" % (k, v))
        print("\nWorld of Hyatt is the only fixed award chart (pass --category 1-8).")
        return

    if args.infile:
        data = json.load(open(args.infile))
        program = canonical_program(data.get("program"))
        rows = [evaluate_row(program, r) for r in data.get("rows", [])]
        rows.sort(key=lambda r: (r["cents_per_point"] is None, -(r["cents_per_point"] or 0)))
        result = {"program": program, "baseline_cpp": PROGRAM_BASELINES.get(program), "rows": rows}
        if args.out:
            json.dump(result, open(args.out, "w"), indent=2)
            print("Wrote %s (%d rows, best value first)" % (args.out, len(rows)))
        else:
            print(json.dumps(result, indent=2))
        return

    program = canonical_program(args.program)
    if program is None:
        print(json.dumps({"error": "unknown or missing --program; run --list", "query": args.program}))
        return
    pts = args.points
    if pts is None and program == "World of Hyatt" and args.category is not None:
        pts = hyatt_points(args.category, args.season)
    cpp = cents_per_point(args.cash, pts)
    v, base = verdict(program, cpp)
    print(json.dumps({
        "program": program, "cash_rate": args.cash, "points": pts,
        "cents_per_point": cpp, "baseline_cpp": base, "verdict": v,
        "note": "cents per point is a yardstick, not a guarantee; award stays can carry resort fees and cash stays earn points and status.",
    }, indent=2))


if __name__ == "__main__":
    main()
