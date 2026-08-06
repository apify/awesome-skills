# Example scoring rules — split per source

Paste one block per source when the agent asks in Step 2. Only supply
blocks for sources you actually want to fetch — each block corresponds to
a `--enable-*` flag in Step 4. Keep each rule pointed at its own source
so the resulting `tech_score` / `content_score` / `metadata_score`
columns stay auditable.

## Tech-stack rules — evaluated against `scoring.json[url].tech`

```
+10 if the company uses Shopify or WooCommerce (we sell a Shopify integration).
+5  if the tech stack includes HubSpot, Marketo, or Segment (marketing-ops ICP).
+3  if the site uses a modern framework (Next.js, Nuxt, SvelteKit) → likely product-led.
-3  if no analytics or CDP is detected (likely too early-stage).
```

## Website-content rules — evaluated against `scoring.json[url].content`

```
+8 if the homepage describes a SaaS or platform business.
+3 if the homepage mentions "developers", "API", or "SDK" (technical buyer).
-5 if the homepage describes a services agency or consultancy (not our ICP).
-3 if the homepage is only in a language we don't sell in.
```

## Company-metadata rules — evaluated against `scoring.json[url].metadata`

```
+3 if industry is e-commerce, retail, or B2C.
+5 if the company has a LinkedIn presence (bigger operation).
-3 if company size is under 10 employees (too small to buy).
-5 if the domain is a personal blog or portfolio site.
```

Once the agent produces `tech_score`, `content_score`, `metadata_score`,
`score` (sum), and `outreach_hook` per lead, `merge_output.js` joins them
onto the enriched CSV. Sort descending by `score` and pitch the top of
the list first; scan the three sub-scores when a row surprises you.
