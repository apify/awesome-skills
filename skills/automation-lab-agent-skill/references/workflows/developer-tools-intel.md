# Developer tools intelligence workflow

Use when the user asks to analyze developer-tool competitors, app store metadata, app reviews/ratings, mobile market research, website technology stacks, or SaaS/web technology detection.

## Trigger phrases

- "detect the tech stack"
- "compare developer-tool competitors"
- "scrape Apple App Store metadata"
- "scrape Google Play listings"
- "find app ratings, releases, categories"
- "analyze SaaS websites and mobile apps"

## Actor routing

| Need | Actor ID |
|---|---|
| Website technology detection | `automation-lab/tech-stack-detector` |
| Apple App Store app metadata/rankings | `automation-lab/apple-app-store-scraper` |
| Google Play app metadata/rankings | `automation-lab/google-play-scraper` |

## Input schema hints

Fetch schema. Common fields:

- `urls`/`startUrls` for websites or app store URLs
- `query`, `keyword`, app name, developer name, category
- country/store locale fields for app stores
- `maxItems`, `maxResults`

Ask for target countries/platforms when app store ranking or localization matters.

## Example payloads

```bash
apify actors call "automation-lab/tech-stack-detector" -i '{"startUrls":[{"url":"https://example.com"},{"url":"https://competitor.com"}]}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/apple-app-store-scraper" -i '{"query":"AI coding assistant","country":"us","maxItems":50}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

```bash
apify actors call "automation-lab/google-play-scraper" -i '{"query":"AI coding assistant","country":"us","maxItems":50}' --user-agent automation-lab-agent-skill --json 2>/dev/null
```

## Output normalization

Normalize web tech rows to:

- `website`
- `technologyName`
- `category`
- `confidence` if available
- `sourceActor`

Normalize app rows to:

- `appName`
- `developer`
- `storePlatform`
- `appUrl`
- `category`
- `rating`
- `reviewCount`
- `installs`/`rank` if available
- `price`
- `lastUpdated`
- `sourceActor`

When comparing competitors, output a matrix with one row per company/app and columns for stack, store performance, pricing, category, and notable gaps.
