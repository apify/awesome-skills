# Apify Actor Usage -- `apify/google-search-scraper`

The skill uses a single Actor for all six AI surfaces. Each AI surface is an add-on toggled on via a nested input object.

## Input schema (only the fields the skill sets)

| Field | Type | Skill default | Notes |
|-------|------|---------------|-------|
| `queries` | string | from `config.json:prompts` | One prompt per line. |
| `maxPagesPerQuery` | int | `1` | One page is enough to surface AI Overviews. |
| `resultsPerPage` | int | `10` | Default. |
| `countryCode` | string | from config, default `us` | ISO 3166-1 alpha-2. |
| `languageCode` | string | from config, default `en` | ISO 639-1. |
| `disableGoogleSearchResults` | bool | **must remain `false`** | AI Overviews ride alongside organic SERP results -- turning off SERP suppresses Overviews too. |
| `aiModeSearch` | object | `{ "enableAiMode": <user> }` | Google AI Mode add-on. |
| `chatGptSearch` | object | `{ "enableChatGpt": <user> }` | ChatGPT Search add-on. |
| `perplexitySearch` | object | `{ "enablePerplexity": <user> }` | Perplexity add-on. |
| `copilotSearch` | object | `{ "enableCopilot": <user> }` | Microsoft Copilot add-on. |
| `geminiSearch` | object | `{ "enableGemini": <user> }` | Google Gemini add-on. |

## Example input the runner constructs

```json
{
  "queries": "best web scraping tool\nhow to scrape Amazon prices\nApify vs Scrapy",
  "maxPagesPerQuery": 1,
  "countryCode": "us",
  "languageCode": "en",
  "aiModeSearch":     { "enableAiMode":     true  },
  "chatGptSearch":    { "enableChatGpt":    true  },
  "perplexitySearch": { "enablePerplexity": true  },
  "copilotSearch":    { "enableCopilot":    true  },
  "geminiSearch":     { "enableGemini":     true  }
}
```

## Expected dataset shape (per query, per page)

Each Actor dataset item represents one query result. Field names verified against a live run on 2026-05-18:

| Source | Top-level field | Answer text | Citations |
|--------|----------------|-------------|-----------|
| AI Overviews | `aiOverview` | `aiOverview.content` (often missing -- see below) | `aiOverview.sources[].url` |
| AI Mode | `aiModeResult` | `aiModeResult.text` | `aiModeResult.sources[].url` |
| ChatGPT Search | `chatGptSearchResult` | `chatGptSearchResult.text` | `chatGptSearchResult.sources[].url` |
| Perplexity | `perplexitySearchResult` | `perplexitySearchResult.text` | `perplexitySearchResult.sources[].url` (also `.citationUrls[]` as a flat fallback) |
| Copilot | `copilotSearchResult` | `copilotSearchResult.text` | `copilotSearchResult.sources[].url` |
| Gemini | `geminiSearchResult` | `geminiSearchResult.text` | `geminiSearchResult.sources[].url` |

Each entry under `sources[]` is an object with `url`, `title`, and `description` (or `snippet`) -- the runner preserves all three so the user can later inspect the metadata behind every citation.

### Parser fallbacks

The runner's `_block_text(...)` helper tries `text` first (the dominant key across all five working surfaces), then falls back to `content`, `answer`, `markdown`. `_block_citations(...)` tries `sources` / `citations` / `references` / `links` as arrays of objects, falling back to `citationUrls` as a flat URL list. If everything is missing, the row is written with `answer_text = "[no answer returned]"` and empty `citations[]`.

## Per-source cost flags

Pricing shifts -- check the Actor's [pricing tab](https://apify.com/apify/google-search-scraper) for current per-result rates. Disable any source the user does not care about (Step 1 of SKILL.md): each AI surface adds a per-result fee on top of the base SERP page price.

## What the runner ignores

- `customDataFunction`, `saveHtml`, `saveHtmlToKeyValueStore` -- not needed; the parser walks structured fields.
- `mobileResults` -- irrelevant for citation tracking.
- `forceExactMatch` -- never set; we want broad SERP behavior, not literal-quote matching.
