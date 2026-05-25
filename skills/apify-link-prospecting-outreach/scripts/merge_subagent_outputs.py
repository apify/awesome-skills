#!/usr/bin/env python3
"""Merge sub-agent placement/email outputs back into the enriched rows.

Usage:
  python3 scripts/merge_subagent_outputs.py \
    --config campaign.json \
    --outputs-dir /tmp/placement_outputs

Each output file is /tmp/placement_outputs/row_<N>.json matching the row_index
the agent emitted. Schema per sub-agent output:
  {row_index, article_url, placement_strategy, placement_source_sentence,
   placement_with_link, placement_new_insertion, outreach_type,
   email_subject, email_body, skip_recommendation, notes}

Reads:  {base}_enriched.json
Writes: {base}_drafted.json
"""
import argparse
import json
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--outputs-dir", required=True)
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    base = cfg["base"]
    partnership = cfg.get("partnership_type", "")
    rows = json.load(open(f"{base}_enriched.json"))

    by_url = {}
    for fname in os.listdir(args.outputs_dir):
        if not fname.endswith(".json"):
            continue
        out = json.load(open(os.path.join(args.outputs_dir, fname)))
        url = out.get("article_url")
        if url:
            by_url[url] = out
    print(f"Loaded {len(by_url)} sub-agent outputs from {args.outputs_dir}")

    drafted = 0
    sub_skipped = 0
    not_drafted = 0

    for r in rows:
        if r["Outreach Status"] == "Skip":
            r.setdefault("Outreach Type", "")
            r.setdefault("Partnership Offer", "")
            r.setdefault("Placement Source Sentence", "-")
            r.setdefault("Placement With Link", "-")
            r.setdefault("Placement New Insertion", "-")
            r.setdefault("Suggested Email Copy", "")
            continue

        sub = by_url.get(r["Article URL"])
        if sub is None:
            r["Outreach Type"] = ""
            r["Partnership Offer"] = partnership
            r["Placement Source Sentence"] = "-"
            r["Placement With Link"] = "-"
            r["Placement New Insertion"] = "-"
            r["Suggested Email Copy"] = ""
            prior = r.get("Notes", "") or ""
            r["Notes"] = ("Placement: not-drafted (sub-agent not run for this row)"
                         + (f" | {prior}" if prior else ""))
            not_drafted += 1
            continue

        strategy = sub.get("placement_strategy", "")
        if strategy == "skip":
            r["Outreach Status"] = "Skip"
            prior = r.get("Notes", "") or ""
            reason = sub.get("skip_recommendation", "sub-agent recommended skip")
            r["Notes"] = f"SKIP (sub-agent review): {reason}" + (f" | {prior}" if prior else "")
            r["Outreach Type"] = ""
            r["Partnership Offer"] = ""
            r["Placement Source Sentence"] = "-"
            r["Placement With Link"] = "-"
            r["Placement New Insertion"] = "-"
            r["Suggested Email Copy"] = ""
            sub_skipped += 1
            continue

        r["Outreach Type"] = sub.get("outreach_type", "topical-niche-edit")
        r["Partnership Offer"] = partnership
        r["Placement Source Sentence"] = sub.get("placement_source_sentence", "-")
        r["Placement With Link"] = sub.get("placement_with_link", "-")
        r["Placement New Insertion"] = sub.get("placement_new_insertion", "-")

        subject = (sub.get("email_subject") or "").strip()
        body = (sub.get("email_body") or "").strip()
        r["Suggested Email Copy"] = f"Subject: {subject}\n\n{body}" if subject and body else ""

        parts = [f"Placement: {strategy}"]
        if sub.get("notes"):
            parts.append(sub["notes"])
        if r.get("Notes"):
            parts.append(r["Notes"])
        r["Notes"] = " | ".join(parts)
        drafted += 1

    out_path = f"{base}_drafted.json"
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False, default=str)
    print(f"Wrote {len(rows)} rows → {out_path}")
    print(f"  Drafted: {drafted} | Sub-agent skipped: {sub_skipped} | Not drafted: {not_drafted}")


if __name__ == "__main__":
    main()
