---
name: apify-review-monitoring
description: "Pull and monitor customer reviews of companies and software products from Trustpilot and Capterra, then summarise complaints, praise and reply behaviour. Trustpilot takes review URLs from any country site or plain domains, reads past the 200-review limit without a login, and adds a free company row with TrustScore and star distribution. Capterra takes product URLs or plain product names and returns ratings, pros, cons, reviewer role, company size and vendor replies. Both support only-new monitoring, so a weekly schedule returns just the new reviews. Routes to heyitsgautham/trustpilot-reviews-scraper and heyitsgautham/software-reviews-scraper. Use when the user asks for Trustpilot reviews, a company's TrustScore, 1-star complaints, reviews mentioning refunds or delivery, competitor review comparisons, Capterra reviews of SaaS tools, or a weekly digest of new reviews. Pay per review, no start fee, and summary rows are free."
author: Gautham Krishna (heyitsgautham)
author_url: https://github.com/heyitsgautham
metadata:
  category: data-extraction
  keywords: "trustpilot, trustscore, reviews, review-monitoring, capterra, software-reviews, customer-feedback, complaints, competitor-analysis, reputation, voice-of-customer, apify"
---

# Review monitoring on Trustpilot and Capterra

Disclosure: the author of this skill built and owns both Actors it routes to (`heyitsgautham/trustpilot-reviews-scraper` and `heyitsgautham/software-reviews-scraper`).
They are pay-per-result Actors on Apify Store.
No referral or tracking parameters are used in this skill.

This skill turns "what do customers say about X" into rows the agent can count and quote, and then into a weekly feed of only the new reviews.

## Example prompts

Prompts this skill handles:

- "Pull the 1 and 2 star Trustpilot reviews for monzo.com and zalando.de from the last 3 months and group the complaints."
- "Compare the TrustScores and star splits of these five online shops." (a pasted list of domains)
- "Every Monday, send me new Capterra reviews of Asana, monday.com and ClickUp, with the cons."

Out of scope (the boundary):

- Google Maps, Yelp or Tripadvisor reviews of local businesses. Use a Google Maps or Tripadvisor reviews Actor from Apify Store instead.
- Reviewer identities or contact details. Neither Actor returns reviewer names, emails or phone numbers.

## Prerequisites

- Apify account ([sign up](https://apify.com)).
- Authentication through `apify login`, or an `APIFY_TOKEN` environment variable (Apify Console, Settings, Integrations).

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Reviews of a company, shop, bank, airline or app on Trustpilot | `heyitsgautham/trustpilot-reviews-scraper` | community | Consumer brands. Any Trustpilot country site, or a plain domain |
| Reviews of a B2B software product | `heyitsgautham/software-reviews-scraper` | community | SaaS tools on Capterra, by product URL or by name |
| A SaaS company's brand reputation | Both | community | Trustpilot for the company, Capterra for the product |

## Workflow

1. Get the businesses as domains (`monzo.com`) or Trustpilot URLs, and the software as Capterra URLs or names (`Asana`).
2. Agree the slice before running: star ratings, a date window, a keyword, and how many reviews per business.
   Default to `maxReviewsPerBusiness` 100 for a first look, and say so.
3. Run the Actor, then read rows by type.
   On Trustpilot, each business has one free company row with `trustScore`, `starDistribution`, `matchingReviews` and `reviewsReturned`, then one row per review.
   A business with no Trustpilot page comes back as a free row, not an error.
4. Summarise from the text fields: `title` and `text` on Trustpilot, `pros` and `cons` on Capterra.
   Quote reviews with their `reviewUrl` or date, and count themes rather than guessing them.
   `replyText` on Trustpilot and `vendorResponse` on Capterra show whether the company answers.
5. For a weekly feed, run the same input with `onlyNewSinceLastRun: true` on an Apify schedule (Console, Schedules, or the [schedules API](https://docs.apify.com/api/v2/schedules)).
   The first run returns the usual results and remembers them, and later runs return only reviews not returned before for the same business and filters.

## Run it with the Apify CLI

Check the live input schema and price first:

```bash
apify actors info "heyitsgautham/trustpilot-reviews-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

Recent 1 and 2 star reviews for a bank and a shop, one by domain and one from a country site:

```bash
apify actors call "heyitsgautham/trustpilot-reviews-scraper" -i '{"businesses":["monzo.com","https://de.trustpilot.com/review/www.zalando.de"],"stars":["1","2"],"datePeriod":"last3months","maxReviewsPerBusiness":200}' \
  --json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

Reviews that mention refunds, on Trustpilot's own search:

```bash
apify actors call "heyitsgautham/trustpilot-reviews-scraper" -i '{"businesses":["https://www.trustpilot.com/review/www.booking.com"],"keyword":"refund","maxReviewsPerBusiness":100}' \
  --json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

TrustScore comparison only, at almost no cost (one review each, company rows are free):

```bash
apify actors call "heyitsgautham/trustpilot-reviews-scraper" -i '{"businesses":["monzo.com","https://www.trustpilot.com/review/www.booking.com","https://www.trustpilot.com/review/www.amazon.com"],"maxReviewsPerBusiness":1}' \
  --json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

Newest Capterra reviews for three tools, by name:

```bash
apify actors call "heyitsgautham/software-reviews-scraper" -i '{"productNames":["Asana","monday.com","ClickUp"],"sortBy":"newest","maxReviewsPerProduct":50}' \
  --json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

The weekly feed shape, to save as a task and schedule:

```bash
apify actors call "heyitsgautham/trustpilot-reviews-scraper" -i '{"businesses":["monzo.com"],"onlyNewSinceLastRun":true}' \
  --json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

Read the rows back from a finished run:

```bash
apify datasets get-items <DATASET_ID> --format json \
  --user-agent apify-awesome-skills/apify-review-monitoring \
  2>/dev/null
```

## Cost

| Actor | Price per 1,000 reviews | Lowest tier (Gold) | Always free |
|---|---|---|---|
| `heyitsgautham/trustpilot-reviews-scraper` | $0.25 | $0.175 | Company rows, unknown domains, failed fetches |
| `heyitsgautham/software-reviews-scraper` | $1.00 | $0.70 | Failed URLs, missing products, unmatched names, products with no reviews, summary and comparison rows |

Check live prices with `apify actors info` before quoting them.

Cost and time traps:

- Trustpilot past 200 reviews per business reads many narrower filters, at about 4 to 5 requests per second. Large companies with tens of thousands of reviews take minutes each, so raise the run timeout or cap `maxReviewsPerBusiness`.
- `reviewerCountries` filters after reading, so a country with few reviewers ends early with few rows. That is expected, not a failure.

## Troubleshooting

- A free `invalid_input` row naming a topic: Trustpilot ignores topic IDs it does not know, so the Actor refuses to return unfiltered reviews. Use the IDs listed in the Actor's README, such as `refund`, `delivery_service` or `customer_service`.
- `moreBehindLogin: true` on a company row: Trustpilot hid the rest of that slice behind its login. Narrow the filters or accept the share returned, which `reviewsReturned` and `matchingReviews` show.
- A Capterra name returned the wrong product: pass the Capterra product URL instead of the name.
- To restart a feed, delete the key-value store `trustpilot-reviews-scraper-monitor` or `software-reviews-scraper-monitor` in the user's own Apify account.
