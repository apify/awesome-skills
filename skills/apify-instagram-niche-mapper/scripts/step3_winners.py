"""Step 3: label each shortlisted creator's reels as outlier / strong / rest.

Usage:
  python step3_winners.py --reels reels12.json --shortlist shortlist.txt --out-dir out \
      [--outlier-floor N | --step1-stats out/step1_stats.json] [--now 2026-11-05]

Outlier: plays >= 3x the creator's median AND >= outlier floor.
Strong:  share rate > the creator's median share rate AND plays >= 1.5x the creator's median.
Reels younger than 48h are set aside. Collapsed creators (newest 3 measurable reels
below 0.5x their median) are removed.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd

from common import creator_of, first_line, first_line_type, load_items, plays_of, to_ts

ap = argparse.ArgumentParser()
ap.add_argument("--reels", nargs="+", required=True)
ap.add_argument("--shortlist", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--outlier-floor", type=float)
ap.add_argument("--step1-stats")
ap.add_argument("--now")
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
now = pd.Timestamp(a.now, tz="UTC") if a.now else pd.Timestamp.now(tz="UTC")
if a.outlier_floor is None:
    a.outlier_floor = json.load(open(a.step1_stats))["suggested_outlier_floor"] if a.step1_stats else 10_000
shortlist = [l.strip() for l in open(a.shortlist) if l.strip() and not l.startswith("#")]

R = pd.DataFrame([dict(
    creator=creator_of(x), shortCode=x["shortCode"],
    url=x.get("url") or f"https://www.instagram.com/reel/{x['shortCode']}/",
    ts=x.get("timestamp"), plays=plays_of(x), shares=x.get("sharesCount"),
    likes=x.get("likesCount"), comments=x.get("commentsCount"), duration=x.get("videoDuration"),
    pinned=bool(x.get("isPinned")), caption=x.get("caption") or "",
) for x in load_items(a.reels) if x.get("shortCode")]).drop_duplicates(["creator", "shortCode"])
R = R[~R.pinned & R.creator.isin(shortlist)]
R["ts"] = to_ts(R.ts)
R["age_h"] = (now - R.ts).dt.total_seconds() / 3600
R["share_rate"] = R.shares / R.plays
R["first_line"] = R.caption.apply(first_line)
R["fl_len"] = R.first_line.str.len()
R["fl_type"] = R.first_line.apply(first_line_type)

status, rows = {}, []
for c in shortlist:
    g = R[R.creator == c].sort_values("ts", ascending=False).head(12)
    m = g[(g.age_h >= 48) & g.plays.notna()]
    if g.empty:
        status[c] = dict(status="no reels returned"); continue
    if m.empty:
        status[c] = dict(status="not yet measurable", reels=len(g)); continue
    med, msr = m.plays.median(), m.share_rate.median()
    newest3 = m.head(3).plays.median()
    if len(m) >= 6 and newest3 < 0.5 * med:
        status[c] = dict(status="collapsed – removed", reels=len(g), measurable=len(m),
                         median_plays=med, newest3_vs_median=newest3 / med); continue
    for _, x in m.iterrows():
        outlier = x.plays >= 3 * med and x.plays >= a.outlier_floor
        strong = pd.notna(x.share_rate) and x.share_rate > msr and x.plays >= 1.5 * med
        rows.append(dict(label="outlier" if outlier else "strong" if strong else "rest",
                         url=x.url, creator=c, posted=x.ts.strftime("%Y-%m-%d"), plays=int(x.plays),
                         lift=x.plays / med, shares=x.shares, share_rate=x.share_rate,
                         creator_median_share_rate=msr, likes=x.likes, comments=x.comments,
                         duration=x.duration, fl_type=x.fl_type, fl_len=x.fl_len,
                         first_line=x.first_line[:200]))
    labels = [r["label"] for r in rows if r["creator"] == c]
    status[c] = dict(status="tested", reels=len(g), measurable=len(m), median_plays=med,
                     newest3_vs_median=newest3 / med, outliers=labels.count("outlier"),
                     strong=labels.count("strong"),
                     steady=bool(labels.count("outlier") == 0 and 0.5 <= newest3 / med <= 1.5))

T = pd.DataFrame(rows)
S = pd.DataFrame(status).T.rename_axis("creator").reset_index()
S.to_csv(f"{a.out_dir}/creator_status.csv", index=False)
if T.empty:
    raise SystemExit("No measurable reels. Wait a few days and re-run.")
order = {"outlier": 0, "strong": 1, "rest": 2}
T = T.sort_values(["label", "plays"], key=lambda s: s.map(order) if s.name == "label" else -s)
T.round(4).to_csv(f"{a.out_dir}/reels_labeled.csv", index=False)
W = T[T.label != "rest"]
W.round(4).to_csv(f"{a.out_dir}/winners.csv", index=False)
open(f"{a.out_dir}/winner_urls.txt", "w").write("\n".join(W.url))

summary = T.groupby("label").agg(reels=("url", "count"), creators=("creator", "nunique"),
                                 median_share_rate=("share_rate", "median"),
                                 median_lift=("lift", "median"), median_first_line_len=("fl_len", "median"))
pd.set_option("display.width", 220)
print("Outlier floor:", a.outlier_floor)
print("\nCreator status:\n", S.status.value_counts().to_string())
print(S[S.status != "tested"].to_string(index=False))
print("\nSummary by label:\n", summary.round(4).to_string())
print("\nFirst-line type by label:\n", T.groupby("label").fl_type.value_counts().unstack(fill_value=0).to_string())
print("\nWinners per creator:\n", W.groupby(["creator", "label"]).size().unstack(fill_value=0).to_string())
print("\nSteady creators with no outliers:", ", ".join(S[S.get("steady") == True].creator))
print(f"\n{len(W)} winners -> {a.out_dir}/winner_urls.txt (total duration {W.duration.sum() / 60:.1f} min)")
