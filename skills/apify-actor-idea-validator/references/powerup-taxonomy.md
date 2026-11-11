# Powerup taxonomy

Canonical labels for Apify Store "powerups" — the user-facing feature toggles an Actor's input schema exposes. The skill normalises every candidate toggle it sees against this list so the same capability isn't double-counted under three different names.

## How to use

1. For each candidate toggle from an Actor's input schema (step M3 of [market-research.md](market-research.md)), check whether its meaning — read from `title` + `description`, not the field name — matches a **canonical label** below.
2. If it does, record the canonical label.
3. If it doesn't, keep the Actor-local label verbatim and mark it `(unmapped)`.
4. When the same `(unmapped)` label has appeared in **3 or more Actors** across runs, promote it: add a new row here with the field-name patterns that typically carry it.

Match on meaning, not strings. "Return AI overview snippet" and "Scrape SGE results" are both **AI search visibility** even though neither field is named that.

## Canonical labels (seed)

| Canonical label | Field-name patterns (examples) | Synonyms to watch for |
|---|---|---|
| AI search visibility | `includeAiOverviews`, `includeAiMode`, `scrapeAiOverview`, `sgeSnippets`, `aiAnswers` | AI overview, SGE snippet, AI mode results, generative answers |
| Business leads enrichment | `includeBusinessLeads`, `extractBusinessInfo`, `enrichLeads`, `companyDetails` | Lead enrichment, B2B contact enrichment, company data append |
| Link prospecting | `linkProspecting`, `backlinks`, `outboundLinks`, `linkOpportunities` | Backlink discovery, outreach prospecting, link-building targets |
| Full website content | `fetchFullWebsiteContent`, `fullPageContent`, `includePageContent`, `scrapeLinkedPages` | Deep page crawl, full body text, full HTML |
| Paid result extraction | `scrapePaidResults`, `includeAds`, `extractAds`, `sponsoredResults` | Sponsored results, ads block, PPC listings |
| Reviews extraction | `scrapeReviews`, `includeReviews`, `maxReviews`, `reviewsCount` | User reviews, star ratings detail, testimonials |
| Contact info enrichment | `includeEmails`, `extractEmails`, `scrapePhones`, `contactDetails` | Email finder, phone scraping, contact page scrape |
| Screenshot capture | `takeScreenshot`, `includeScreenshots`, `captureScreenshot` | Page screenshot, element screenshot, visual capture |
| PDF / document export | `exportPdf`, `renderPdf`, `includePdf`, `savePdf` | PDF rendering, document download, printable export |
| Scheduling / cron | `schedule`, `cronExpression`, `runEvery`, `recurring` | Recurring runs, scheduled triggers |
| Webhook delivery | `webhookUrl`, `webhookTargets`, `onFinishWebhook`, `notifyWebhook` | Push to webhook, callback URL, pipeline trigger |
| Media download | `downloadImages`, `downloadMedia`, `saveVideos`, `includeImages` | Image downloader, video grab, media persistence |
| Geo-targeting | `country`, `region`, `locationQuery`, `geo`, `countryCode` | Country filter, regional restriction, geo-fencing |
| Language filtering | `language`, `languageCode`, `locale`, `hl` | Locale filter, hl param, language restriction |
| Sentiment / AI classification | `sentimentAnalysis`, `classifyContent`, `topicDetection`, `includeSentiment` | Sentiment tagging, content classifier, topic extraction |
| Social-profile enrichment | `includeProfileDetails`, `enrichProfile`, `socialLinks`, `profileStats` | Follower counts, bio extraction, social profile append |
| Structured data extraction | `extractJsonLd`, `includeSchemaOrg`, `microdata`, `structuredData` | JSON-LD, schema.org, microdata |
| HTML / markdown export | `outputFormat`, `includeHtml`, `markdown`, `outputMarkdown` | Raw HTML, Markdown render, text-only output |
| Custom proxy / anti-bot bypass | `useResidentialProxy`, `bypassCloudflare`, `antibot`, `stealth` | Residential IPs, anti-bot bypass, CF challenge solver |
| Screenshot OCR / vision | `ocr`, `extractText`, `visionModel`, `imageToText` | OCR, image-to-text, screenshot parsing |

## Plumbing — NEVER label as powerups

These fields show up in almost every Actor and are infrastructure, not user-value features. Drop them silently during candidate extraction (step M3).

- `proxyConfig`, `proxy`, `proxyUrls`
- `debug`, `verbose`, `logLevel`
- `maxRequests`, `maxRequestsPerCrawl`, `maxConcurrency`, `minConcurrency`, `maxRequestRetries`, `maxRequestsPerMinute`
- `timeout`, `requestTimeout`, `navigationTimeout`, `pageLoadTimeout`
- `retries`, `retryOnBlocked`
- `headful`, `headless`, `useChrome`
- `maxItems`, `maxResults` (when a plain limit, not an enriched toggle)
- `startUrls`, `urls`, `query`, `search` (these are the primary input, not a toggle)
- `datasetId`, `keyValueStoreId`, `requestQueueId`
- `inputSchemaVersion`, `apifyProxyGroups`
- `userAgent`, `customHeaders`
- Pagination plumbing: `pageCount`, `resultsPerPage`, `pagination.*`

An enum of output formats (`outputFormat: ['json','csv','html']`) IS a powerup (HTML / markdown export). A plain `format: 'json' | 'csv'` without richer alternatives is plumbing — drop it.
