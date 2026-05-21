#!/usr/bin/env python3
"""Build the unified prospect table from the Actor's datasets.

Reads campaign config + 4 Actor sidecar files; writes one row per WCC URL.

Usage:
  python3 scripts/build_prospects.py --config campaign.json

Reads:
  {base}.json            (main leads)
  {base}_serp.json       (Google + LLM-engine SERP results)
  {base}_wcc.json        (Website Content Crawler bodies)
  {base}_authors.json    (AI Web Scraper author results)
Writes:
  {base}_prospects.json
"""
import argparse
import json
import re
from collections import defaultdict
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

EDIT_RE = re.compile(r'editor|content|writer|managing|editorial|blog|copy|journalist|head of content|redaktor|šéfredaktor', re.I)
DEMOTE_RE = re.compile(r'\bceo\b|\bcfo\b|\bcto\b|\bcoo\b|founder|chief|\bvp\b|president|jednatel|majitel', re.I)
SENIORITY_RANK = {"head": 5, "director": 4, "vp": 3, "senior": 4, "manager": 3,
                  "c_suite": 1, "entry": 2, "intern": 1, None: 0, "": 0}

TRACKING_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
                   "fbclid", "gclid", "msclkid", "yclid", "ref", "ref_src"}

ENGINE_ORDER = [
    "Google Organic", "ChatGPT", "Gemini", "Copilot", "Perplexity",
    "Google AI Mode", "Google AI Overview",
]


def norm_domain(d: str) -> str:
    if not d:
        return ""
    d = d.replace("https://", "").replace("http://", "").rstrip("/")
    if d.startswith("www."):
        d = d[4:]
    return d.lower().split("/")[0]


def norm_url(u: str) -> str:
    if not u:
        return ""
    try:
        p = urlparse(u)
        host = p.netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if k.lower() not in TRACKING_PARAMS]
        new = p._replace(scheme="https", netloc=host, query=urlencode(q), fragment="")
        out = urlunparse(new)
        if out.endswith("/") and out.count("/") > 3:
            out = out[:-1]
        return out
    except Exception:
        return u


def url_domain(u: str) -> str:
    try:
        return norm_domain(urlparse(u).netloc)
    except Exception:
        return ""


def score_contact(c):
    title = c.get("jobTitle") or ""
    sen = c.get("seniority") or ""
    s = SENIORITY_RANK.get(sen, 0)
    if EDIT_RE.search(title):
        s += 100
    elif DEMOTE_RE.search(title):
        s -= 50
    if c.get("email"):
        s += 10
    return s


def email_verification_status(contact):
    if not contact:
        return "-"
    ev = contact.get("emailVerification") or {}
    result = (ev.get("result") or "").lower()
    return {
        "ok": "verified", "valid": "verified", "invalid": "invalid",
        "catch-all": "catch-all", "catch_all": "catch-all", "catchall": "catch-all",
        "risky": "risky", "unknown": "unknown",
    }.get(result, result or "-")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = json.load(open(args.config))
    base = cfg["base"]
    own_domains = set(cfg.get("own_domains", []))
    brand_aliases = cfg.get("brand", {}).get("aliases") or [cfg.get("brand", {}).get("name", "")]
    brand_aliases = [a for a in brand_aliases if a]

    leads = json.load(open(f"{base}.json"))
    serp = json.load(open(f"{base}_serp.json"))
    wcc = json.load(open(f"{base}_wcc.json"))
    authors = json.load(open(f"{base}_authors.json"))

    # Dedupe leads
    seen = set()
    dedup_leads = []
    for l in leads:
        k = l.get("personId") or l.get("email") or f"{l.get('firstName')}-{l.get('lastName')}-{l.get('domain')}"
        if k in seen:
            continue
        seen.add(k)
        dedup_leads.append(l)
    print(f"Leads: {len(leads)} → {len(dedup_leads)} after dedupe")

    # Index leads by domain + URL
    leads_by_domain = defaultdict(list)
    leads_by_url = defaultdict(list)
    for l in dedup_leads:
        d = norm_domain(l.get("domain", ""))
        if d:
            leads_by_domain[d].append(l)
        for s in (l.get("source_url") or []):
            u_norm = norm_url(s.get("url", ""))
            if u_norm:
                leads_by_url[u_norm].append(l)

    # Authors by URL
    authors_by_url = {}
    for a in authors:
        u_norm = norm_url(a.get("url", ""))
        data = a.get("data") or {}
        authors_by_url[u_norm] = {
            "authorName": data.get("authorName"),
            "publishDate": data.get("date"),
            "postName": data.get("postName"),
        }

    # SERP + engine attribution
    serp_lookup = {}
    engines_by_url = defaultdict(set)
    keyword_per_run = (serp[0].get("searchQuery", {}).get("term", "") if serp else "")

    for entry in serp:
        kw = (entry.get("searchQuery") or {}).get("term", "")
        for r in entry.get("organicResults") or []:
            u = norm_url(r.get("url", ""))
            if not u:
                continue
            engines_by_url[u].add("Google Organic")
            existing = serp_lookup.get(u)
            if not existing or (r.get("position", 999) < existing["position"]):
                serp_lookup[u] = {
                    "position": r.get("position"),
                    "title": r.get("title"),
                    "lastUpdated": r.get("lastUpdated"),
                    "keyword": kw,
                }
        for field, label in (
            ("aiModeResult", "Google AI Mode"),
            ("aiOverviewResult", "Google AI Overview"),
            ("perplexitySearchResult", "Perplexity"),
            ("chatGptSearchResult", "ChatGPT"),
            ("geminiSearchResult", "Gemini"),
            ("copilotSearchResult", "Copilot"),
        ):
            block = entry.get(field) or {}
            for src in (block.get("sources") or block.get("citationUrls") or []):
                u = src.get("url", "") if isinstance(src, dict) else (src if isinstance(src, str) else "")
                u_norm = norm_url(u)
                if u_norm:
                    engines_by_url[u_norm].add(label)

    # WCC by URL (canonical row list)
    wcc_by_url = {}
    for w in wcc:
        u_norm = norm_url(w.get("url", ""))
        if not u_norm:
            continue
        wcc_by_url[u_norm] = {
            "original_url": w.get("url"),
            "text": w.get("text") or "",
            "markdown": w.get("markdown") or "",
            "metadata": w.get("metadata") or {},
        }

    rows = []
    for u_norm, wcc_entry in wcc_by_url.items():
        original_url = wcc_entry["original_url"]
        domain = url_domain(original_url)
        if not domain:
            continue

        engine_set = engines_by_url.get(u_norm, set())
        engines = [e for e in ENGINE_ORDER if e in engine_set]

        s = serp_lookup.get(u_norm, {})
        wcc_text = wcc_entry["text"]
        wcc_meta = wcc_entry["metadata"]

        # Brand mention: source_url[].brand_mentioned_in_source OR body-level match against any alias
        brand_mentioned = False
        for l in leads_by_url.get(u_norm, []):
            for sl in (l.get("source_url") or []):
                if norm_url(sl.get("url", "")) == u_norm and sl.get("brand_mentioned_in_source"):
                    brand_mentioned = True
        if brand_aliases and any(re.search(r'\b' + re.escape(a) + r'\b', wcc_text, re.I) for a in brand_aliases):
            brand_mentioned = True

        # Author cascade: ai-web-scraper → wcc metadata.author → openGraph → jsonLd Person
        author_entry = authors_by_url.get(u_norm, {})
        article_author = author_entry.get("authorName")
        author_source = "searchAuthorName" if article_author else None
        if not article_author and wcc_meta.get("author"):
            article_author = wcc_meta["author"]
            author_source = "metadata.author"
        if not article_author:
            og = (wcc_meta.get("openGraph") or {}).get("article:author") if isinstance(wcc_meta.get("openGraph"), dict) else None
            if og:
                article_author = og
                author_source = "openGraph"
        if not article_author and wcc_meta.get("jsonLd"):
            try:
                for item in wcc_meta["jsonLd"]:
                    if isinstance(item, dict) and item.get("@type") == "Person" and item.get("name"):
                        article_author = item["name"]
                        author_source = "jsonld"
                        break
            except Exception:
                pass
        if not article_author:
            article_author = "Not found"
            author_source = "not found"

        article_title = s.get("title") or wcc_meta.get("title") or author_entry.get("postName") or "Not found"
        publish_date = (wcc_meta.get("publishedAt") or wcc_meta.get("publishedTime")
                        or s.get("lastUpdated") or author_entry.get("publishDate") or "Not found")

        # Contact pick: URL-level match first, then domain-level fallback
        url_leads = leads_by_url.get(u_norm, [])
        cs = sorted(url_leads or leads_by_domain.get(domain, []), key=score_contact, reverse=True)
        contact = cs[0] if cs else None
        alternates = cs[1:] if len(cs) > 1 else []

        row = {
            "Article URL": original_url,
            "Domain": domain,
            "Article Title": article_title,
            "Article Author": article_author,
            "Author Source": author_source,
            "Publish Date": publish_date,
            "SERP Position": s.get("position") if s.get("position") is not None else "-",
            "Source Engines": ", ".join(engines) if engines else "-",
            "Keyword": keyword_per_run,
            "Keywords List": [keyword_per_run] if keyword_per_run else [],
            "Brand Mentioned": brand_mentioned,
            "Has Backlink": False,  # set below from WCC outbound links
            "Contact Full Name": (f"{contact.get('firstName','')} {contact.get('lastName','')}".strip()
                                  if contact else "Not found"),
            "Contact Job Title": (contact.get("jobTitle") if contact else "Not found") or "Not found",
            "Department": (contact.get("departments") or ["-"])[0] if contact else "-",
            "Seniority": (contact.get("seniority") if contact else "") or "-",
            "Contact Email": (contact.get("email") if contact else "Not found") or "Not found",
            "Email Verification": email_verification_status(contact),
            "Contact LinkedIn": (contact.get("linkedinProfile") if contact else "") or "",
            "Company": (contact.get("companyName") if contact else "") or domain,
            "Alternate Contacts": [
                f"{a.get('firstName','')} {a.get('lastName','')} ({a.get('jobTitle','')}, {a.get('email','no-email')})"
                for a in alternates[:3]
            ],
            "WCC Text": wcc_text,
            "WCC OutboundLinks": [],
        }
        rows.append(row)

    # Outbound links + Has-Backlink
    LINK_RE = re.compile(r'\[([^\]]*)\]\((https?://[^)]+)\)')
    for r in rows:
        wcc_entry = wcc_by_url.get(norm_url(r["Article URL"]), {})
        md = wcc_entry.get("markdown", "")
        links = []
        for m in LINK_RE.findall(md or ""):
            anchor, link_url = m
            dom = url_domain(link_url)
            if not dom or dom == r["Domain"]:
                continue
            links.append({"anchor": anchor.strip(), "url": link_url, "domain": dom})
            if dom in own_domains:
                r["Has Backlink"] = True
        r["WCC OutboundLinks"] = links
        r["WCC OutboundLinkCount"] = len(links)

    out_path = f"{base}_prospects.json"
    with open(out_path, "w") as f:
        json.dump(rows, f, indent=2, default=str)
    print(f"Wrote {len(rows)} prospect rows → {out_path}")

    no_contact = sum(1 for r in rows if r['Contact Email'] == 'Not found' and r['Contact Full Name'] == 'Not found')
    print(f"  No contact: {no_contact} | Brand mention: {sum(1 for r in rows if r['Brand Mentioned'])} | Backlink: {sum(1 for r in rows if r['Has Backlink'])}")
    domains = sorted({r['Domain'] for r in rows})
    print(f"  Unique domains: {len(domains)}")


if __name__ == "__main__":
    main()
