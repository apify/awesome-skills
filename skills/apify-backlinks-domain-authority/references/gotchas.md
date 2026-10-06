# Cost guardrails and error recovery: backlinks and domain authority

## Confirm live prices before a batch

Prices can change. Read them from the live Actor rather than trusting a copied number:

```bash
apify actors info "crawlplant/link-gap-finder" --json \
  --user-agent apify-awesome-skills/apify-backlinks-domain-authority \
  2>/dev/null
```

The newest entry in `pricingInfos` lists each event under `pricingPerEvent.actorChargeEvents`, with a price per Apify
plan tier (`FREE`, `BRONZE`, `SILVER`, `GOLD`). Quote the tier that matches the user's plan, or `FREE` when unknown.

## Cost model

- Pay per event, platform usage included. Each row type has one price; the only other charge is a $0.00005 start fee.
- Around $1 per 1,000 domain profiles, $1.50 per 1,000 history rows, $2 per 1,000 referring-domain, outlink or change rows,
  $4 per 1,000 link-gap prospects, $5 per 1,000 similar sites (Free plan list prices).
- Rows left out by `minAuthority` are not charged. Filtering server-side is cheaper than filtering after download.
- `maxItems` caps the whole run. In link modes, rows = domains x `maxReferrersPerDomain` (for `changes`: up to twice that,
  gained plus lost) until `maxItems` stops it.

Rule of thumb for confirmation: mention cost under about $5, warn over about $5, get explicit sign-off over about $20.
Always phrase as "around $X".

## Guardrails

1. Start small: one or two domains and `maxItems` of 10-20. Check the row shape before a wide batch.
2. Referring-domain lists explode for big sites: bbc.co.uk has about 250,000 referring domains. Always set
   `maxReferrersPerDomain` and `maxItems`, and use `minAuthority` (30-50) for outreach lists.
3. Link gap with 20 competitors and a deep comparison can return thousands of prospects. Cap `maxItems` at the number of
   sites the user can actually contact.
4. Keep `excludeHubs` on for outreach: hubs link to everyone and are not realistic prospects.
5. History back to 2018 is up to 60 rows per domain. Ask how far back the user needs before raising `historyReleases`.

## Error recovery

- `ccStatus: "not-in-graph"`, `openAuthority: 0`: no links to the domain in the crawled sample. Report it as "no
  measurable link authority", not as a failed lookup.
- `ccStatus: "below-scan-depth"` with `openAuthorityMax`: only in `history` mode or with an older `graphRelease`, for
  domains outside the searched top N. The domain's score is at most `openAuthorityMax`.
- Empty link-mode result: check that the domain is spelled right and has referring domains in a `profiles` run first
  (`ccReferringDomains`). A domain with 0 there has nothing to list.
- A `linkGap` run without `yourDomain` fails at once with "linkGap mode needs yourDomain": pass the user's site there and
  the competitors in `domains`.
- Before retrying, check the original run's status so a lost response does not trigger a second paid run:

```bash
apify runs info <RUN_ID> --json \
  --user-agent apify-awesome-skills/apify-backlinks-domain-authority \
  2>/dev/null
```
