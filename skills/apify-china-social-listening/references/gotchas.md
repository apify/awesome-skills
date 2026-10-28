# Gotchas — China social listening

## Cost

- Always set `maxChargeUsd` (start at `1` for trials).
- Douban: first 20 rows free on search/comments/reviews when that mode’s limit ≤ 50; charts bill from row 1.
- Prefer example tasks with modest limits before large backfills.

## Keywords

- Prefer Chinese queries for Weibo / WeChat / Douban / Bilibili.
- Brand packs: run one task per common spelling (CN + EN) rather than one mixed query.

## Platform norms

- Never promote a scraper on the platform it scrapes (e.g. don’t pitch Weibo scraping on Weibo/X inappropriately).
- Public data only — respect each site’s terms and the user’s compliance needs.

## Failures

- `incomplete` / error rows → shrink batch, retry once, then report the Actor run URL.
- Don’t invent rows if the dataset is empty — say so and suggest an alternate Actor/mode.
