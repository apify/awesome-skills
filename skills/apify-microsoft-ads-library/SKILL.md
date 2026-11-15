---
name: apify-microsoft-ads-library
description: Research ads that advertisers ran on Microsoft Advertising (Bing, MSN, Outlook and partner sites) in the European Economic Area, from Microsoft's public Ad Library (its EU Digital Services Act ad repository). Use for "Bing ads of <competitor>", "Microsoft ads library", "ads on Bing in Germany", "which Bing ads mention <keyword>", "monitor a competitor's new Bing ads", "impressions and targeting of a Bing ad". EEA ads only.
author: Fetchwright
author_url: https://github.com/Fetchwright
metadata:
  category: data-extraction
  keywords: "microsoft ads, bing ads, ad library, ads transparency, dsa ad repository, competitor ads, eea, advertising research, ad monitoring"
---

# Microsoft (Bing) Ads Library research

Find, filter and monitor the ads an advertiser ran on Microsoft Advertising in the EEA, with dates, impression ranges, impression share by country and targeting, from Microsoft's public Ad Library.

Disclosure: the routed Actor `fetchwright/microsoft-ads-library-scraper` is built by the skill author and is paid per event (per ad saved; see its Pricing tab).

## Example prompts

Prompts this skill handles:

- "Show me the Bing ads Booking.com ran in Germany last month, with impressions."
- "Which advertisers run Microsoft ads that mention 'DJ booking' in Norway?"
- "Alert me in Slack when a competitor starts a new Bing ad."

Out of scope (the boundary):

- "Show Bing search ads in the United States": Microsoft's library covers EEA ads only. For Google ads use the `apify-ads-intelligence` skill (Google Ads Transparency Center); there is no public US library for Bing ads.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login`, the `APIFY_TOKEN` environment variable, or a token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## Workflow

1. Identify the advertiser(s) by the name Microsoft's library lists, usually the legal name (e.g. "Booking.com B.V."), or take keyword(s) when the user asks by topic.
2. Fetch the input schema (command under "Calling the Actor") and build the input: `advertisers` and/or `keywords`, optional `countries` (EEA codes), `dateFrom`/`dateTo`, `maxAdsPerAdvertiser`, and `includeDetails: true` when dates, impressions or targeting are needed.
3. Estimate cost before large runs: the run charges per ad saved, capped by `maxAdsPerAdvertiser` times the advertisers or keywords; confirm with the user above a few thousand ads.
4. Run, then deliver: ads count per advertiser, headline examples, the dataset link, and the caveats below.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Ads of named advertisers on Microsoft Advertising (EEA) | `fetchwright/microsoft-ads-library-scraper` (`advertisers: [...]`) | community | competitor ad research |
| Ads mentioning a keyword, any advertiser (EEA) | `fetchwright/microsoft-ads-library-scraper` (`keywords: [...]`, no advertisers) | community | topic or market scans |
| One row per advertiser account (country, verified, ad count) | `fetchwright/microsoft-ads-library-scraper` (`resultType: "advertisers"`) | community | quick "do they advertise on Bing" checks |
| New ads only, on a schedule, with a Slack/Discord alert | `fetchwright/microsoft-ads-library-scraper` (`onlyNewAds: true`, `monitorName`, `notifyWebhookUrl`) | community | competitor monitoring |

## Calling the Actor (Apify CLI)

    apify actors call "fetchwright/microsoft-ads-library-scraper" \
      -i '{"advertisers":["Booking.com B.V."],"countries":["DE"],"maxAdsPerAdvertiser":30,"includeDetails":true}' \
      --json \
      --user-agent apify-awesome-skills/apify-microsoft-ads-library \
      2>/dev/null

    # Input schema
    apify actors info "fetchwright/microsoft-ads-library-scraper" --input --json \
      --user-agent apify-awesome-skills/apify-microsoft-ads-library 2>/dev/null

    # Results
    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-microsoft-ads-library 2>/dev/null

The Apify MCP connector (<https://mcp.apify.com>) can call the same Actor with the same input.

## Troubleshooting

- **No ads for a US company:** the library holds EEA ads only; ask for EEA countries or use the Google route.
- **A name matches several accounts:** `maxAdvertisersPerName` sets how many to read, exact match first; an advertiser page link or numeric ID is unambiguous.
- **About 1,000 ads per search is Microsoft's limit:** set `splitByCountry: true` to read a large list country by country.
- **Dates, impressions and targeting are empty:** they need `includeDetails: true` (one extra lookup per ad, no extra charge). The Actor paces every Microsoft request about 15-25 seconds apart, so 30 ads with details take roughly 10-12 minutes; tell the user before large detail runs.
- **The run stopped early with "Microsoft refused this run":** Microsoft returned a block page. The Actor stops quietly and charges only the ads it saved; try again later rather than immediately.
- Microsoft's data can lag 1 to 3 days; Microsoft does not publish an ad format, so none is reported.
