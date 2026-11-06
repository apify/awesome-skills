"""Step 2: score creators from their last 12 non-pinned reels (Reel Scraper output).

Usage:
  python step2_creators.py --reels reels12.json --topic-words "seo,aeo,google" --out-dir out \
      [--active-days 45] [--floor N] [--tier-a N] [--now 2026-11-05]

Floor and Tier A default to the 70th and 75th percentile of creator medians among
on-topic, active creators, so they scale to the niche.
"""
import argparse
import os

import numpy as np
import pandas as pd

from common import creator_of, load_items, non_latin_share, plays_of, to_ts, topic_regex

ap = argparse.ArgumentParser()
ap.add_argument("--reels", nargs="+", required=True)
ap.add_argument("--topic-words", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--active-days", type=int, default=45)
ap.add_argument("--floor", type=float)
ap.add_argument("--tier-a", type=float)
ap.add_argument("--now")
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
now = pd.Timestamp(a.now, tz="UTC") if a.now else pd.Timestamp.now(tz="UTC")
rx = topic_regex(a.topic_words)

items = [x for x in load_items(a.reels) if x.get("shortCode")]
failed = sorted({creator_of(x) for x in load_items(a.reels) if not x.get("shortCode")} - {None})
R = pd.DataFrame([dict(
    creator=creator_of(x), shortCode=x["shortCode"], fullName=x.get("ownerFullName"),
    ts=x.get("timestamp"), plays=plays_of(x), shares=x.get("sharesCount"),
    pinned=bool(x.get("isPinned")),
    text=(x.get("caption") or "") + " " + " ".join("#" + h for h in (x.get("hashtags") or [])),
) for x in items]).drop_duplicates(["creator", "shortCode"])
R = R[~R.pinned]
R["ts"] = to_ts(R.ts)
R["age_h"] = (now - R.ts).dt.total_seconds() / 3600
R["measurable"] = R.age_h >= 48
R["on_topic"] = R.text.str.contains(rx)

rows = []
for c, g in R.groupby("creator"):
    g = g.sort_values("ts", ascending=False).head(12)
    m = g[g.measurable & g.plays.notna()]
    med = m.plays.median() if len(m) else np.nan
    newest3 = m.head(3).plays.median() if len(m) >= 6 else np.nan
    # Old pinned hits sometimes come back unflagged: a reel far older than the rest is suspect.
    gaps = g.ts.diff(-1).dt.days.fillna(0)
    gap_warning = bool((gaps > 60).any() and len(g) >= 6)
    name = f"{c} {g.fullName.dropna().iloc[0] if g.fullName.notna().any() else ''}"
    rows.append(dict(
        username=c, fullName=g.fullName.dropna().iloc[0] if g.fullName.notna().any() else "",
        reels=len(g), measurable=len(m), median_plays=med,
        max_plays=m.plays.max() if len(m) else np.nan,
        top_share=(m.plays.max() / m.plays.sum()) if len(m) and m.plays.sum() else np.nan,
        newest3_vs_median=newest3 / med if med else np.nan,
        topic_share=round(100 * g.on_topic.mean()),
        name_match=bool(rx.search(name)),
        last_post=g.ts.max(), non_latin_caption_share=non_latin_share(g.text.tolist()),
        date_gap_warning=gap_warning,
    ))
C = pd.DataFrame(rows)
C["active"] = (now - C.last_post).dt.days <= a.active_days
C["topic_pass"] = (C.topic_share >= 40) | (C.name_match & (C.topic_share >= 25))
C["collapsed"] = C.newest3_vs_median < 0.5
C["one_hit"] = C.top_share > 0.6

base = C[C.topic_pass & C.active & C.median_plays.notna()].median_plays
floor = a.floor if a.floor is not None else float(base.quantile(0.70)) if len(base) else 0
tier_a = a.tier_a if a.tier_a is not None else float(base.quantile(0.75)) if len(base) else 0
C["passes"] = C.topic_pass & C.active & (C.median_plays >= floor) & ~C.one_hit
C["tier"] = np.where(~C.passes, "", np.where(C.median_plays >= tier_a, "A", "B"))
C["generalist"] = (~C.topic_pass & C.active & (C.topic_share >= 8) & (C.median_plays >= tier_a))
C["group"] = np.select([C.passes, C.generalist], ["candidate", "generalist"], "out")

out = C.sort_values(["group", "tier", "median_plays"], ascending=[True, True, False])
out["last_post"] = out.last_post.dt.strftime("%Y-%m-%d")
out.round(3).to_csv(f"{a.out_dir}/creators_scored.csv", index=False)

pd.set_option("display.width", 220)
print(f"Creators scored: {len(C)}   failed/empty: {len(failed)} {failed[:10]}")
print(f"Topic pass: {C.topic_pass.sum()}   active: {C.active.sum()}   both: {(C.topic_pass & C.active).sum()}")
print(f"Floor (p70): {floor:,.0f}   Tier A (p75): {tier_a:,.0f}   candidates: {C.passes.sum()}   "
      f"one-hit dropped: {(C.topic_pass & C.active & C.one_hit).sum()}")
cols = ["username", "tier", "median_plays", "topic_share", "measurable", "last_post",
        "collapsed", "newest3_vs_median", "top_share", "non_latin_caption_share"]
print("\nCandidates:\n", out[out.group == "candidate"][cols].round(2).to_string(index=False))
print("\nGeneralists:\n", out[out.group == "generalist"][cols].round(2).to_string(index=False))
gw = C[C.passes & C.date_gap_warning].username.tolist()
if gw:
    print("\nDate-gap warning (possible unflagged pinned reels; check the profile):", ", ".join(gw))
print(f"\nSaved {a.out_dir}/creators_scored.csv")
