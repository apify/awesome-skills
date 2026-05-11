# Pre-delivery Verification Checklist

Run this audit on every claim before presenting the final report.

## Audit Steps

1. **Source audit** — Every factual statement has a source URL? If not, find it in scraped data or remove the claim.
2. **Data-back check** — Every insight traces to specific data points. "Weak SEO" must be backed by "absent from top 10 for [keyword] — [URL]". Insight without data = opinion — trace back or remove.
3. **Contradiction scan** — Claims across modules contradict? (e.g., snapshot says "strong support" but G2 shows complaints). Flag and explain, don't hide.

## Confidence Labeling

Mark each major finding:

| Level | Definition |
|---|---|
| **High** | Scraped from primary source (company website, official docs). Marketing claims — treat critically but data point is authoritative |
| **Medium** | Confirmed by 2+ independent third-party sources (G2 + Capterra + Reddit = pattern) |
| **Low** | Single third-party source. Signal, not fact |

| Source Type | Examples |
|---|---|
| **Primary** | Company's own domain, official docs, press releases |
| **Verified third-party** | G2, Capterra, Gartner (verified users) |
| **Unverified third-party** | Blogs, analyst posts, news, Reddit |
| **Aggregator** | SimilarWeb, Crunchbase, LinkedIn (modeled data — directional, not exact) |

**Label format**: `[Confidence | Source]` — e.g., "500+ connectors [High | Primary — fivetran.com/connectors]"

**No inferences in reports.** Untraceable claims must be removed.
