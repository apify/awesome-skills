"""Step 1: merge Popular-search and hashtag reels, clean them, and report niche stats.

Usage:
  python step1_reels.py --inputs popular.json hashtag.json --topic-words "seo,aeo,google" \
      --out-dir out [--months 12] [--exclude exclude.txt] [--include include.txt] [--now 2026-11-05]

Run it once, review out/step1_review.csv by eye, write the shortCodes to drop into
exclude.txt (and topic-matching misses to keep into include.txt), then run it again.
"""
import argparse
import json
import os

import numpy as np
import pandas as pd

from common import (COMMENT_CTA, load_items, original_audio, plays_of, query_of,
                    to_ts, topic_regex)

ap = argparse.ArgumentParser()
ap.add_argument("--inputs", nargs="+", required=True)
ap.add_argument("--topic-words", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--months", type=int, default=12)
ap.add_argument("--exclude")
ap.add_argument("--include")
ap.add_argument("--now")
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
now = pd.Timestamp(a.now, tz="UTC") if a.now else pd.Timestamp.now(tz="UTC")

rows, errors = [], []
for x in load_items(a.inputs):
    if x.get("error") or not x.get("shortCode"):
        errors.append(query_of(x) or x.get("inputUrl"))
        continue
    src = "hashtag" if "/tags/" in (x.get("inputUrl") or "") else "popular"
    rows.append(dict(
        shortCode=x["shortCode"], url=f"https://www.instagram.com/reel/{x['shortCode']}/",
        source=src, query=query_of(x), timestamp=x.get("timestamp"),
        owner=x.get("ownerUsername"), ownerFullName=x.get("ownerFullName"),
        plays=plays_of(x), likes=x.get("likesCount"), comments=x.get("commentsCount"),
        shares=x.get("sharesCount"), duration=x.get("videoDuration"),
        original_audio=original_audio(x),
        hashtags=" ".join(x.get("hashtags") or []), caption=(x.get("caption") or "").replace("\r", " "),
    ))
if not rows:
    raise SystemExit("No reels in the inputs.")
df = pd.DataFrame(rows)
raw = len(df)
df["ts"] = to_ts(df.timestamp)
df = (df.sort_values("plays", ascending=False)
        .groupby("shortCode", as_index=False)
        .agg({**{c: "first" for c in df.columns if c not in ("shortCode", "source", "query")},
              "source": lambda s: "+".join(sorted(set(s))),
              "query": lambda s: "|".join(sorted(set(s)))}))
unique = len(df)

cut = now - pd.DateOffset(months=a.months)
df["recent"] = df.ts >= cut
rx = topic_regex(a.topic_words)
# Match on caption text first. Hashtags count only if they aren't the tag that found the reel:
# a reel pulled from #aeo always carries #aeo, whatever it is about.
src_tags = {q.lower() for q in df["query"].str.split("|").explode()}
df["text_match"] = df.caption.str.replace(r"#\S+", " ", regex=True).str.contains(rx)
df["tag_match"] = df.hashtags.apply(
    lambda h: bool(rx.search(" ".join("#" + t for t in h.split() if t.lower() not in src_tags))))
df["topic_match"] = df.text_match | df.tag_match

def read_list(p):
    if not p or not os.path.exists(p):
        return set()
    return {l.strip() for l in open(p) if l.strip() and not l.startswith("#")}

exc, inc = read_list(a.exclude), read_list(a.include)
df["on_topic"] = (df.topic_match & ~df.shortCode.isin(exc)) | df.shortCode.isin(inc)

# Per-query yield: which terms are worth keeping next time
_q = df[df.recent].assign(q=df["query"].str.split("|")).explode("q").reset_index(drop=True)
per_q = _q.groupby("q").agg(recent=("shortCode", "size"), on_topic=("on_topic", "sum"))
per_q["median_plays_on_topic"] = [_q[(_q.q == q) & _q.on_topic].plays.median() for q in per_q.index]
per_q["pct_on_topic"] = (100 * per_q.on_topic / per_q.recent).round()

# Review file: everything recent the topic check is unsure about, plus the top results
r = df[df.recent].sort_values("plays", ascending=False)
review = pd.concat([r.head(30), r[~r.text_match].head(120)]).drop_duplicates("shortCode")
review[["shortCode", "url", "query", "plays", "owner", "text_match", "tag_match", "on_topic", "caption"]].assign(
    caption=lambda d: d.caption.str.replace(r"\s+", " ", regex=True).str[:200]
).to_csv(f"{a.out_dir}/step1_review.csv", index=False)

c = df[df.recent & df.on_topic].copy()
bins = [0, 15, 30, 45, 60, 90, 10_000]
labels = ["<15s", "15-30s", "30-45s", "45-60s", "60-90s", "90s+"]
c["len_bucket"] = pd.cut(c.duration, bins, labels=labels)
c["comment_cta"] = c.caption.str.contains(COMMENT_CTA)
by_len = c.groupby("len_bucket", observed=False).plays.agg(
    reels="count", median="median", p90=lambda s: s.quantile(0.9)).reset_index()
by_len_nonpop = c[c.source != "popular"].groupby("len_bucket", observed=False).plays.agg(
    reels="count", median="median").reset_index()

authors = c.groupby("owner").agg(reels=("shortCode", "count"), total_plays=("plays", "sum"),
                                 median_plays=("plays", "median"), best_plays=("plays", "max"),
                                 fullName=("ownerFullName", "first")).reset_index()

stats = dict(
    raw_rows=raw, unique_reels=unique, failed_queries=sorted({e for e in errors if e}),
    within_months=int(df.recent.sum()), dropped_old=int((~df.recent).sum()),
    dropped_old_popular=int((~df.recent & df.source.str.contains("popular")).sum()),
    on_topic=int(len(c)), dropped_off_topic=int(df.recent.sum() - len(c)),
    median_plays=float(c.plays.median()), p90_plays=float(c.plays.quantile(0.9)),
    max_plays=float(c.plays.max()),
    original_audio_share=float(c.original_audio.eq(True).mean()),
    median_plays_original_audio=float(c[c.original_audio == True].plays.median()),
    median_plays_music=float(c[c.original_audio == False].plays.median()),
    comment_cta_share=float(c.comment_cta.mean()),
    authors=int(len(authors)), authors_once_share=float((authors.reels == 1).mean()),
    suggested_outlier_floor=float(round(c.plays.median() / 2, -2)),
)
json.dump(stats, open(f"{a.out_dir}/step1_stats.json", "w"), indent=2)

c.sort_values("plays", ascending=False)[
    ["url", "timestamp", "owner", "ownerFullName", "plays", "likes", "comments", "shares",
     "duration", "len_bucket", "original_audio", "comment_cta", "source", "query", "hashtags", "caption"]
].to_csv(f"{a.out_dir}/reels_clean.csv", index=False)
authors.sort_values("total_plays", ascending=False).to_csv(f"{a.out_dir}/authors.csv", index=False)
with open(f"{a.out_dir}/authors.txt", "w") as f:
    f.write("\n".join(authors.owner.dropna()))

pd.set_option("display.width", 200)
print(json.dumps(stats, indent=2))
print("\nPer-query yield (last", a.months, "months):\n", per_q.to_string())
print("\nPlays by length:\n", by_len.to_string(index=False))
print("\nPlays by length, excluding Popular-only reels:\n", by_len_nonpop.to_string(index=False))
print("\nTop authors by plays:\n", authors.sort_values("total_plays", ascending=False).head(10).to_string(index=False))
print("\nTop authors by appearances:\n",
      authors.sort_values(["reels", "total_plays"], ascending=False).head(10).to_string(index=False))
print(f"\nReview file: {a.out_dir}/step1_review.csv  ({len(review)} rows)")
