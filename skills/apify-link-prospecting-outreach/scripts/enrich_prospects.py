#!/usr/bin/env python3
"""Merge Ahrefs results, run the 11-rule skip pass, assign Why-tags and Prospect Tier.

Usage:
  python3 scripts/enrich_prospects.py --config campaign.json

Reads:
  {base}_prospects.json
  {base}_ahrefs_domain.json   ({domain: {dr, refdomains}})
  {base}_ahrefs_page.json     ({url: {org_traffic, ...}})
Writes:
  {base}_enriched.json
"""
import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlparse

ADVERSARIAL_TOKENS = [
    "vs", "versus", "alternative to", "alternatives to", "compared to",
    "compared with", "instead of", "better than", "worse than",
    "pros and cons", "comparison", "review of",
    # Czech / German equivalents commonly seen on EU comparison pages
    "srovnání", "alternativa k", "místo", "lepší než", "horší než", "recenze",
    "vergleich",
]

SUBDOMAIN_PREFIXES_SKIP = {
    "developers", "docs", "support", "helpcenter", "legacy",
    "dsarequests", "connectivity", "community",
}

PATH_PATTERNS_SKIP = [
    r"/api-docs/", r"/reference/", r"/marketplace/", r"/extensions/",
    r"/profile/", r"/users/", r"/free-tools/", r"/spec/",
    r"/content/privacy", r"/content/terms", r"/content/dma",
    r"/content/how_we_work", r"/legal/", r"/_redirects", r"/sitemap",
    r"/eshop/", r"/produkt/", r"/product/", r"/kosik/", r"/cart/",
]

VENDOR_PRODUCT_PATTERNS = [
    r"-scraper\.php$", r"-scraping\.php$",
    r"-data-scraper\.", r"-data-scraping\.",
    r"/bots/", r"/detail/",
]


def norm_domain(d: str) -> str:
    if not d:
        return ""
    d = d.replace("https://", "").replace("http://", "").rstrip("/")
    if d.startswith("www."):
        d = d[4:]
    return d.lower().split("/")[0]


def parse_date(s):
    if not s or s == "Not found":
        return None
    if isinstance(s, datetime):
        return s.replace(tzinfo=timezone.utc) if s.tzinfo is None else s
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d", "%b %d, %Y", "%d %b %Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(str(s), fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def tier_function(goal):
    """Return a callable(dr, page_traffic) -> 'A'|'B'|'C' for the given goal."""
    goal_norm = (goal or "").lower()

    def topical(dr, pt):
        if dr is None:
            return "C"
        if dr >= 50 and (pt or 0) >= 300:
            return "A"
        if 30 <= dr < 50 or 50 <= (pt or 0) < 300:
            return "B"
        return "C"

    def max_volume(dr, pt):
        if dr is None:
            return "C"
        if dr >= 30 and (pt or 0) >= 100:
            return "A"
        if 15 <= dr < 30 or 20 <= (pt or 0) < 100:
            return "B"
        return "C"

    def by_dr(a_min, b_min):
        def fn(dr, _pt):
            if dr is None:
                return "C"
            if dr >= a_min:
                return "A"
            if dr >= b_min:
                return "B"
            return "C"
        return fn

    if "topical authority" in goal_norm or "custom" in goal_norm or not goal_norm:
        return topical
    if "maximum link volume" in goal_norm:
        return max_volume
    if "recover unlinked brand mentions" in goal_norm:
        return by_dr(40, 20)
    if "replace competitor links" in goal_norm:
        return by_dr(50, 30)
    return topical


def detect_resource_page(row):
    if row["WCC OutboundLinkCount"] < 10:
        return False
    title = (row["Article Title"] or "").lower()
    return bool(re.search(
        r'\b(best|top \d|top-\d|nejlepší|nejlepsi|list|listicle|roundup|tools|resources|guide to|alternatives?|průvodce|seznam)\b',
        title))


def detect_links_to_competitor(row, competitor_domains):
    for link in row["WCC OutboundLinks"]:
        if link["domain"] in competitor_domains:
            return link["domain"]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    base = cfg["base"]
    goal = cfg.get("goal", "Topical authority links to specific URL")
    today = parse_date(cfg.get("today")) or datetime.now(tz=timezone.utc)
    own_domains = set(cfg.get("own_domains", []))
    competitor_domains = set(cfg.get("competitor_domains", []))
    already_pitched = set(cfg.get("already_pitched_domains", []))
    category_kw = set(k.lower() for k in cfg.get("category_keywords", []))
    subject_kw = set(k.lower() for k in cfg.get("subject_keywords", []))
    brand_aliases = cfg.get("brand", {}).get("aliases") or [cfg.get("brand", {}).get("name", "")]
    brand_aliases = [a for a in brand_aliases if a]

    rows = json.load(open(f"{base}_prospects.json"))
    ahrefs_dom = json.load(open(f"{base}_ahrefs_domain.json"))
    ahrefs_page = json.load(open(f"{base}_ahrefs_page.json"))

    tier_fn = tier_function(goal)
    brand_re = re.compile(r'\b(' + '|'.join(re.escape(a) for a in brand_aliases) + r')\b', re.I) if brand_aliases else None

    for r in rows:
        domain = r["Domain"]
        url = r["Article URL"]

        d = ahrefs_dom.get(domain)
        r["Domain DR"] = d["dr"] if d else "-"
        r["Referring Domains"] = d["refdomains"] if d else "-"
        p = ahrefs_page.get(url)
        r["Page Traffic"] = p["org_traffic"] if p else "-"

        dr_val = d["dr"] if d else None
        pt_val = p["org_traffic"] if p else None
        r["Prospect Tier"] = tier_fn(dr_val, pt_val) if d else "-"

        skip_reason = None
        notes = []

        if domain in own_domains:
            skip_reason = "Own domain leak"
        elif domain in competitor_domains:
            skip_reason = "Competitor domain (user-excluded)"

        if not skip_reason and domain in already_pitched:
            skip_reason = "Already pitched in prior campaign"

        pd = parse_date(r["Publish Date"])
        if not skip_reason and pd and (today - pd).days / 365.25 > 5:
            skip_reason = f"Stale content (published {pd.strftime('%Y-%m-%d')}, >5 years old)"

        if not skip_reason:
            url_lc = url.lower()
            try:
                host = urlparse(url).netloc.lower()
                if host.startswith("www."):
                    host = host[4:]
                first_part = host.split(".")[0]
            except Exception:
                first_part = ""
            if first_part in SUBDOMAIN_PREFIXES_SKIP:
                skip_reason = f"Doc/policy subdomain ({first_part}.*)"
            elif any(re.search(pat, url_lc) for pat in PATH_PATTERNS_SKIP):
                m = next(pat for pat in PATH_PATTERNS_SKIP if re.search(pat, url_lc))
                skip_reason = f"Non-editorial URL pattern ({m})"
            elif any(re.search(pat, url_lc) for pat in VENDOR_PRODUCT_PATTERNS):
                m = next(pat for pat in VENDOR_PRODUCT_PATTERNS if re.search(pat, url_lc))
                skip_reason = f"Vendor product page URL pattern ({m})"

        if not skip_reason and len((r.get("WCC Text") or "").split()) < 400:
            skip_reason = "Page body <400 words (likely not editorial)"

        if not skip_reason and re.search(r'/forum/|/thread/|/comments?/|/answers?/|/q/|/topic/|/discussion/|/diskuse/', url.lower()):
            skip_reason = "UGC / forum page"

        if not skip_reason and (category_kw or subject_kw):
            body_lc = (r.get("WCC Text") or "").lower()
            cat_hit = any(kw in body_lc for kw in category_kw)
            subj_hit = any(kw in body_lc for kw in subject_kw)
            if not cat_hit and not subj_hit:
                skip_reason = (f"Article isn't in user's category or subject — no match for any "
                               f"category {sorted(category_kw)} or subject {sorted(subject_kw)}")

        if not skip_reason and r["Brand Mentioned"] and brand_re:
            body = r.get("WCC Text") or ""
            body_lc = body.lower()
            for m in brand_re.finditer(body):
                start, end = max(0, m.start() - 100), min(len(body), m.end() + 100)
                window = body_lc[start:end]
                for token in ADVERSARIAL_TOKENS:
                    pattern = r'\b' + re.escape(token) + r'\b' if len(token) <= 12 else re.escape(token)
                    if re.search(pattern, window):
                        skip_reason = (f"Adversarial mention (likely competitor comparison page — "
                                       f"'{token}' appears near brand mention; won't link)")
                        break
                if skip_reason:
                    break

        if not skip_reason:
            no_contact = r["Contact Email"] == "Not found" and r["Contact Full Name"] == "Not found"
            no_author = r["Article Author"] in ("Not found", None, "")
            if no_contact and no_author:
                skip_reason = "No contact and no author found"

        if not skip_reason:
            ev = (r.get("Email Verification") or "").lower()
            if ev == "invalid":
                # Try alternates before skipping
                alt_has_email = any("no-email" not in a.lower() for a in (r.get("Alternate Contacts") or []))
                if alt_has_email:
                    notes.append(f"Primary email invalid — alternate contact has an email, prefer alternate")
                else:
                    skip_reason = "Email failed verification (invalid address) and no alternates with email"
            elif ev in ("catch-all", "risky", "unknown"):
                notes.append(f"Email verification = {ev}")

        if not skip_reason and r["Contact Email"] == "Not found" and r["Contact Full Name"] != "Not found":
            notes.append(f"No email found for {r['Contact Full Name']}")

        # Why-This-Prospect tags
        why_tags = []
        if r["Brand Mentioned"] and not r["Has Backlink"]:
            why_tags.append("Mentions brand, no backlink")
        cl = detect_links_to_competitor(r, competitor_domains)
        if cl:
            why_tags.append(f"Links to competitor ({cl})")
        if detect_resource_page(r):
            why_tags.append("Resource / roundup page")
        serp = r["SERP Position"]
        if isinstance(serp, int) and 1 <= serp <= 3:
            why_tags.append(f"Top-3 SERP for {r['Keyword']}")
        if pd:
            age = (today - pd).days / 365.25
            if 2 <= age <= 5:
                why_tags.append(f"Outdated content (published {pd.strftime('%Y-%m-%d')})")
        if r["Has Backlink"]:
            why_tags.append("Already links to brand — low priority")

        priority_lookup = {
            "Mentions brand, no backlink": 1,
            "Already links to brand — low priority": 2,
        }
        def sort_key(t):
            if t in priority_lookup:
                return priority_lookup[t]
            if t.startswith("Links to competitor"):
                return 3
            if t == "Resource / roundup page":
                return 4
            if t.startswith("Top-3 SERP"):
                return 5
            if t.startswith("Outdated content"):
                return 6
            return 99
        r["Why This Prospect"] = ", ".join(sorted(why_tags, key=sort_key)[:2]) if why_tags else "-"

        if skip_reason:
            r["Outreach Status"] = "Skip"
            notes.insert(0, f"SKIP: {skip_reason}")
        else:
            r["Outreach Status"] = "Not started"
        if r.get("Alternate Contacts"):
            notes.append(f"Alternate contacts: {'; '.join(r['Alternate Contacts'])}")
        r["Notes"] = " | ".join(notes) if notes else ""

    out_path = f"{base}_enriched.json"
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2, default=str)
    print(f"Wrote {len(rows)} enriched rows → {out_path}")

    total = len(rows)
    skipped = sum(1 for r in rows if r["Outreach Status"] == "Skip")
    print(f"\nTotal: {total}  Active: {total - skipped}  Skipped: {skipped}")

    tier_counts = Counter(r["Prospect Tier"] for r in rows if r["Outreach Status"] != "Skip")
    print("Active tier breakdown:")
    for t in ("A", "B", "C", "-"):
        if tier_counts[t]:
            print(f"  Tier {t}: {tier_counts[t]}")

    skip_counts = Counter()
    for r in rows:
        if r["Outreach Status"] == "Skip":
            m = re.search(r'SKIP: ([^|]+)', r["Notes"])
            if m:
                skip_counts[m.group(1).strip()] += 1
    print("Skip reasons:")
    for reason, n in skip_counts.most_common():
        print(f"  {n}× {reason}")


if __name__ == "__main__":
    main()
