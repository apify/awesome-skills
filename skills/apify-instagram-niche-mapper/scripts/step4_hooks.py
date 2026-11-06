"""Step 4 helper: join transcripts to winners and pre-fill fields for the hook review.

Usage:
  python step4_hooks.py --transcripts transcripts.json --winners out/winners.csv --out-dir out

Writes out/hooks_review.csv with first spoken sentence, a script-based language hint and a
suggested hook location. Claude confirms language and hook location by reading the rows,
then adds the pattern column.
"""
import argparse
import re

import pandas as pd

from common import COMMENT_CTA, first_line, load_items, non_latin_share

ap = argparse.ArgumentParser()
ap.add_argument("--transcripts", nargs="+", required=True)
ap.add_argument("--winners", required=True)
ap.add_argument("--out-dir", required=True)
a = ap.parse_args()

W = pd.read_csv(a.winners)
W["shortCode"] = W.url.str.rstrip("/").str.split("/").str[-1]
tr = {}
for x in load_items(a.transcripts):
    if x.get("shortCode"):
        t = x.get("transcript")
        tr[x["shortCode"]] = dict(transcript=t if isinstance(t, str) else "",
                                  caption=x.get("caption") or "",
                                  shares_now=x.get("sharesCount"))

def first_sentence(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    return re.split(r"(?<=[.?!])\s", t)[0][:200] if t else ""

def hook_location(caption_line, transcript):
    if len((transcript or "").split()) < 5:
        return "caption only"
    words = len(caption_line.split())
    if not caption_line or words < 4 or COMMENT_CTA.search(caption_line[:120]):
        return "speech only"
    return "caption + speech"

W["transcript"] = W.shortCode.map(lambda s: tr.get(s, {}).get("transcript", ""))
W["caption_first_line"] = W.shortCode.map(lambda s: first_line(tr.get(s, {}).get("caption", ""))).fillna(W.first_line)
W["first_spoken"] = W.transcript.apply(first_sentence)
W["has_speech"] = W.transcript.str.split().str.len().fillna(0) >= 5
W["speech_non_latin_share"] = W.transcript.apply(lambda t: non_latin_share([t]))
W["suggested_hook_location"] = [hook_location(c, t) if sc in tr else "MISSING – re-run transcript"
                                for sc, c, t in zip(W.shortCode, W.caption_first_line, W.transcript)]
W["speech_language"] = ""   # Claude fills: e.g. English / Hindi / none
W["keep"] = ""              # Claude fills: yes / no
W["pattern"] = ""           # Claude fills after grouping
missing = W[~W.shortCode.isin(tr)].shortCode.tolist()

cols = ["url", "creator", "label", "plays", "lift", "shares", "share_rate", "has_speech",
        "speech_non_latin_share", "speech_language", "keep", "suggested_hook_location", "pattern",
        "caption_first_line", "first_spoken", "duration", "transcript"]
W[cols].to_csv(f"{a.out_dir}/hooks_review.csv", index=False)
print(f"{len(W)} winners, {len(missing)} without transcript data {missing}")
got = W.shortCode.isin(tr)
print(f"With speech: {(W.has_speech & got).sum()}   no speech: {(~W.has_speech & got).sum()}")
print("Likely non-Latin speech (>30% non-Latin letters):", (W.speech_non_latin_share > 0.3).sum())
print(W.suggested_hook_location.value_counts().to_string())
for _, x in W.iterrows():
    print(f"\n[{x.shortCode}] {x.creator} {x.label} plays={x.plays} lift={x.lift:.1f} "
          f"SR={x.share_rate:.2%} | {x.suggested_hook_location}")
    print("  CAP:", re.sub(r"\s+", " ", x.caption_first_line)[:140])
    print("  SAY:", re.sub(r"\s+", " ", x.transcript)[:220])
