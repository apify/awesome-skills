# READMEs for the pair

An Actor without a README is not finished. The README is the Store page: SEO content, first impression, usage guide and support resource. Use H2 for main sections (they form the table of contents), H3 for subsections, no H1 (the Actor name is the H1). Put the most important information in the first 25%. Aim for 300+ words.

## Actor A (scraper)

Standard Apify structure:

1. **What does [Actor] do?** - 1-2 sentences, link to the source site, bold key terms, mention "API" where it fits.
2. **Why use it?** - use cases; scheduling, API access, integrations, monitoring.
3. **What data can it extract?** - table of the main fields (name, type, description).
4. **How to use it** - numbered steps, including setting up a schedule.
5. **How much does it cost?** - per the pricing model.
6. **Input** - point to the Input tab; explain `forceReprocess` (re-scrape everything, e.g. after a schema change) and the dedup behaviour.
7. **Output** - "You can download the dataset in various formats such as JSON, HTML, CSV, or Excel", a 2-item JSON example, and a note that records also accumulate in the named dataset `<name>` across runs, and that `enrichmentError` marks partial records.
8. **Tips** - schedule frequency vs cost, keeping `maxItems` low on first runs.
9. **FAQ, disclaimers, support** - the scraping/GDPR disclaimer below, the Issues tab, and a link to Actor B ("search these records as an API").

## Actor B (index / search)

Same structure, plus the API material a Standby Actor must document:

1. **What does [Actor] do?** - "Search N+ <records> by <filters> - as a one-off run or a real-time API."
2. **Why use it?** - no scraping on your side, always fresh (updated on schedule), pay only per result.
3. **What data can you get?** - field table (same fields as Actor A).
4. **How to search <records>** - two subsections:
   - **### Run it in Apify Console** - fill filters, start, download.
   - **### Call it as an API (Standby)** - endpoint, auth, example:
     ```bash
     curl -H "Authorization: Bearer <YOUR_APIFY_TOKEN>" \
       "https://<username>--<index-name>.apify.actor/search?sector=fintech&minAmount=1000000&limit=10"
     ```
     Document every query parameter (name, type, default, example), the response shape (`count`, `total`, `items`), the `400` error case, and that `GET /` is a health check. Mention the Swagger UI on the Standby tab.
5. **How much does it cost?** - price per `result` event, that only returned records are charged, and that `limit` caps the cost of one call (max 1000). Give a worked example ("100 results ≈ $X").
6. **Input** - the filters, matching the query parameters 1:1.
7. **Output** - JSON example of 2 records and of the Standby response wrapper.
8. **Data freshness** - how often the source is updated (Actor A's schedule).
9. **FAQ, disclaimers, support.**

Do **not** document `SOURCE_DATASET_ID` / owner tokens in the public README - that is the owner's setup, not the user's. Keep it in the repo's developer notes (or a `## Development` section if the Actor is private).

## Disclaimer template

> Our Actors are ethical and do not extract any private user data, such as email addresses, gender, or location. They only extract what the user has chosen to share publicly. We therefore believe that our Actors, when used for ethical purposes by Apify users, are safe. However, you should be aware that your results could contain personal data. Personal data is protected by the GDPR in the European Union and by other regulations around the world. You should not scrape personal data unless you have a legitimate reason to do so. If you're unsure whether your reason is legitimate, consult your lawyers.

## SEO and tone

- Keywords in H2/H3 ("How to search startup funding rounds", "Startup funding API"); "People Also Ask" style H3 questions in the FAQ.
- Developer-facing tone for the API section (code, parameters); plain language for the Console section.
- Emojis sparingly; compressed images; embed a YouTube URL if one exists.
- Reference READMEs: [Instagram Scraper](https://apify.com/apify/instagram-scraper), [Google Maps Scraper](https://apify.com/compass/crawler-google-places).
