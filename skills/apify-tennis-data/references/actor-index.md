# Actor routing table: tennis data

Four Actors on the same match history. `crawlplant/flashscore-tennis` has every mode; the other three are
single-purpose listings with simpler inputs and defaults suited to their job. All are `community` tier (third-party,
built by this skill's author).

## crawlplant/flashscore-tennis

| Job | `mode` | Key inputs | `recordType` |
|-----|--------|-----------|--------------|
| Matches of days, past or up to ~2 days ahead | `matches` (default) | `dateFrom`, `dateTo`, `tours`, `status`, `players`, `tournaments`, `surfaces` | `match` |
| In play now | `live` | filters as above | `match` |
| Specific matches, any date | `matchIds` | `matchIds` (8-character ids or match URLs) | `match` |
| A player's career, newest first | `players` | `playerUrls` | `match` |
| A tournament edition with rounds | `tournaments` | `tournamentUrls`, `years` | `match` |
| Player profiles | `playerProfiles` | `playerUrls` | `player` |
| Player statistics | `playerStats` | `playerUrls`, `statsSplitBy` (`season`, `surface`, `tour`, `opponentRank`, `none`) | `playerStats` |
| Head-to-head | `h2h` | `playerUrls` in pairs | `h2h` |
| Elo list | `elo` | `eloTour` (`atp`, `wta`), `eloSurface` (`all`, `hard`, `clay`, `grass`, `carpet`), `maxItems` | `elo` |
| Rankings | `rankings` | `rankingLists` (`atp`, `wta`, `atp-race`, `wta-race`, `atp-doubles`, `wta-doubles`), `rankingDate` | `ranking` |
| Seasons in Sackmann's columns | `sackmann` | `years`, `tours` | Sackmann row |

Data switches for match rows: `includeOdds` (default true), `oddsCountry` (`GB` default: about 20 bookmakers; `DE`,
`PL`, `US`, `AU`...), `oddsMarkets` (`match-winner` or `all` for set, games, handicap and correct-score markets),
`includeH2H` (true), `includeStatistics` (true), `includePointByPoint` (false), `includeRankings` (true). Filters:
`tours` (`atp`, `wta`, `challenger-men`, `challenger-women`, `itf-men`, `itf-women`, `teams`, `other`; empty = all),
`matchType` (`singles` default, `doubles`, `all`), `status`, `sortBy` (`tour`, `time`), `maxItems` (100).

Example inputs (tested):

- Elo on clay, women: `{"mode":"elo","eloTour":"wta","eloSurface":"clay","maxItems":10}`
- Statistics by surface: `{"mode":"playerStats","playerUrls":["Iga Swiatek"],"statsSplitBy":"surface"}`
- Profile: `{"mode":"playerProfiles","playerUrls":["Coco Gauff"]}`
- Live scores without odds or form: `{"mode":"live","includeOdds":false,"includeH2H":false,"maxItems":3}`
- Last week's finished matches with closing odds:
  `{"mode":"matches","dateFrom":"-7","dateTo":"yesterday","status":"finished","includeH2H":false,"maxItems":3000}`

## crawlplant/tennis-match-history

A player's career, newest first. Inputs: `playerUrls` (names or player URLs), `players` (opponent name contains, for a
head-to-head list), `surfaces`, `tournaments`, `tours` (default leaves out exhibitions and juniors), `matchType`,
`status` (`finished` default; `scheduled` for the next matches), `includeStatistics`, `maxItems` (200).

## crawlplant/tennis-point-by-point

Match rows with `pointByPoint[]`. `mode`: `matches` (`dateFrom` defaults to `yesterday`), `matchIds`, `tournaments`
(`tournamentUrls`, `years`), `players` (`playerUrls`). `tours` defaults to `atp`, `wta`; `status` to `finished`
(`live` gives the points so far); `maxItems` (20). For point-by-point together with odds and form in one run, use
flashscore-tennis with `"includePointByPoint": true`.

## crawlplant/tennis-match-dataset

Played singles in Sackmann's columns. Inputs: `years` (from 1990; empty = `dateFrom` / `dateTo` or this season so far),
`tours` (`atp` default; `wta`, `challenger-men`, `challenger-women`, `itf-men`, `itf-women`; empty = ATP and WTA),
`maxItems` (1000). Weekly refresh: `{"years":[],"dateFrom":"-7","dateTo":"today","tours":["atp","wta"],"maxItems":5000}`
and upsert on `match_id`.

## Store and MCP

- https://apify.com/crawlplant/flashscore-tennis
- https://apify.com/crawlplant/tennis-match-history
- https://apify.com/crawlplant/tennis-point-by-point
- https://apify.com/crawlplant/tennis-match-dataset
- Hosted MCP server: `https://mcp.apify.com/?tools=actors,docs,crawlplant/flashscore-tennis` (add the others
  comma-separated). Docs: https://docs.apify.com/platform/integrations/mcp
