# Actor index — apify-sports-probabilities-mcp

Full routing table. `sports-probabilities-mcp` is a Standby MCP server that calls one of these five Actors server-side (with the server owner's own Apify token) depending on the `sport` parameter, caches the result (3h for NFL/MLB/NHL/NBA, 6h for soccer), and returns it through a unified tool shape. All five Actors — and the MCP server itself — are built and owned by the same author (`commodus67` / Elio Liberatore); see the disclosure line in [SKILL.md](../SKILL.md).

| `sport` value | Actor ID | Tier | Teams/leagues | Notes |
|---|---|---|---|---|
| `nfl` | `commodus67/nfl-playoff-odds-api-monte-carlo-simulator` | community | All 32 NFL teams | Blends current-season point differential with a shrunk prior from the previous season so early-season odds aren't flat 50/50 |
| `mlb` | `commodus67/mlb-playoff-odds-monte-carlo` | community | All 30 MLB teams | Also backs the `mlb-value-bets-vs-live-kalshi-prices` task on the Apify Store — same engine, same model used here |
| `nhl` | `commodus67/nhl-playoff-odds-monte-carlo` | community | All 32 NHL teams | Seasons named by the year they end (e.g. `2027` = 2026-27) |
| `nba` | `commodus67/nba-playoff-odds-monte-carlo` | community | All 30 NBA teams | Seasons named by the year they end, same convention as NHL |
| `soccer` | `commodus67/football-soccer-monte-carlo-predictor` | community | 17 leagues via ESPN slugs (`eng.1`, `esp.1`, `ita.1`, `ger.1`, `fra.1`, `ned.1`, `por.1`, `tur.1`, `bel.1`, `sco.1`, `bra.1`, `mex.1`, `arg.1`, `col.1`, `usa.1`, plus Austrian Bundesliga `aut.1`) | Resolves match outcomes by a "strength gap" model (blended standings + historical seasons), not a goals-based Poisson model — a different method from Dixon-Coles single-match predictors |

`Tier` = `community` for every row because all five are independently built by this MCP server's own author, not Apify-maintained. None are deprecated as of this writing.

## Market-comparison source

`compare_model_vs_market` pulls live prices from **Kalshi's public API** (no key required) for NFL/MLB/NHL/NBA:

| Sport | Kalshi series | Notes |
|---|---|---|
| NFL | `KXNFLPLAYOFF` | 32 contracts, one per team |
| MLB | `KXMLBPLAYOFFS` | Non-exclusive, 12-slot playoff field |
| NHL | `KXNHLPLAYOFF` | Non-exclusive, `targetSum` set to the number of playoff slots |
| NBA | `KXNBAPLAYOFF` | Same pattern as NHL |

Soccer has no reliable Kalshi league-title market, so `compare_model_vs_market` for `sport: soccer` expects the caller to supply `marketProbabilities` directly (e.g. from a bookmaker's implied odds) rather than pulling anything automatically.

## How to extend

This routing table only changes if the author adds a sixth sport to the MCP server itself (the mapping lives in the server's own `src/leagues.js`, not in this skill). If you're searching for a *different* Actor to solve a sports-data problem these five don't cover (play-by-play, box scores, live in-game odds), search the Store instead of assuming one of these fits:

    apify actors search "KEYWORDS" --json --limit 20 \
      --user-agent apify-awesome-skills/apify-sports-probabilities-mcp 2>/dev/null
