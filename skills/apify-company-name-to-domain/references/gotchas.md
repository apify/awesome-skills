# Cost guardrails and error recovery: company name to domain

## Confirm live prices before a batch

Prices can change. Read them from the live Actors rather than trusting a copied number:

```bash
apify actors info "datagleaner/company-domain-finder" --json \
  --user-agent apify-awesome-skills/apify-company-name-to-domain \
  2>/dev/null

apify actors info "datagleaner/website-contact-details-scraper" --json \
  --user-agent apify-awesome-skills/apify-company-name-to-domain \
  2>/dev/null
```

If the metadata JSON cannot be parsed, use `apify api` to GET `/v2/acts/datagleaner~company-domain-finder`, with the same skill user-agent in the `User-Agent` header. Read the `pricingInfos` records; keep authentication in the CLI or an `Authorization: Bearer` header, never in the URL.

## Cost model

- Both Actors are pay per event with no start fee. A run that finds nothing costs almost nothing.
- Domain finder: one charge per company whose website is found at or above `minConfidence`. Raising `minConfidence` lowers both the bill and the number of rows.
- Contacts scraper: one charge per website with at least one email on the site's own domain. No-email, unreachable and robots-blocked sites are free.
- Duplicate names in the input are looked up, and billed, again. De-duplicate before the run.
- Estimate before a big run: names x expected hit rate x domain price, plus found sites x expected email rate x contacts price. Hit rates are high for well-known companies and lower for small local businesses; run 20 names from the user's own list first and use that rate.

Rule of thumb for confirmation: mention cost under about $5, warn over about $5, get explicit sign-off over about $20. Always phrase as "around $X".

## Guardrails

1. Test 3 to 5 names first and look at the row shape and the confidence spread.
2. Send the whole list as one run. Thousands of one-name runs each pay start-up time and are slower in total.
3. Set a run timeout that fits the list (budget up to about 2 seconds per name for the domain finder) and a **Max total charge** for anything large.
4. Keep `findContacts` off when the user only asked for domains.

## Error recovery

- `found: false` is a result, not an error: the row shows `alternatives` and why nothing passed. Add a location or industry hint and rerun only those names.
- A run that times out still keeps every row it finished. Read the dataset, then send only the missing names in a second run.
- A contacts row with `status: unreachable` means the site refused or failed for plain HTTP clients. It is not retried through other IPs and is not billed.
- Before retrying a run whose start response was lost, list the Actor's recent runs and recover the existing one, so an uncertain response does not trigger a second paid run.
