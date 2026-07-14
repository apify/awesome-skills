# Kick Data Scraper input modes

Use one mode per Actor run. The current public Actor schema remains authoritative.

## Known channels

Use `channels` for exact Kick usernames. Normalize profile URLs to slugs and remove duplicates before running.

```json
{
  "mode": "channels",
  "channelSlugs": ["xqc", "trainwreckstv", "asmongold"]
}
```

`maxItems` is ignored in this mode. Cost and result count depend on the supplied unique slugs.

## Keyword search

Use `search` for topics, creator names, games, or phrases.

```json
{
  "mode": "search",
  "searchKeywords": "poker",
  "maxItems": 25
}
```

`searchKeywords` is one string. Search may return fewer results than `maxItems`.

## Category research

Use `category` for one or more Kick category slugs.

```json
{
  "mode": "category",
  "categorySlugs": ["just-chatting", "irl"],
  "categorySort": "recommended",
  "categoryLanguages": ["en"],
  "maxItems": 50
}
```

Supported category sorts:

- `recommended`
- `viewers_high_to_low`
- `viewers_low_to_high`

Use category slugs from Kick URLs, not display labels.

## Live discovery

Use `livestreams` for channels that are live at run time.

```json
{
  "mode": "livestreams",
  "livestreamSort": "viewers_high_to_low",
  "livestreamLanguages": ["en"],
  "livestreamTags": ["gaming", "casual", "gta"],
  "maxItems": 100
}
```

Supported live sorts:

- `recommended`
- `viewers_high_to_low`
- `viewers_low_to_high`

Language filters use short language codes such as `en` or `bg`.

Tags are exact values with no spaces, no empty strings, and no values over 20 characters. Use `search` for a phrase such as `CS GO`.

## Discovery limits

`maxItems` defaults to 100 and has a hard maximum of 1000 for search, category, and livestream discovery. Start with 10–25 for exploratory work and increase only when the user's question requires it.

The Actor may ignore invalid filter values and warn about them. Validate values before paying for a run, then inspect result provenance to confirm the intended filter was applied.
