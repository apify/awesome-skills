---
name: apify-sports-probabilities-mcp
description: Get playoff, title, division, wild-card or relegation probabilities for an NFL, MLB, NHL, NBA or soccer team or league, re-run the Monte Carlo under different assumptions, read an archived season's probability history, and compare the model against live Kalshi prediction-market prices to find the edge. Use when a user asks things like "what are the Chiefs' playoff odds", "rank the Premier League by title probability", "where does the model disagree with the market on NBA title odds", "how would higher home-field advantage change the AFC playoff picture", or "show how the Dodgers' World Series odds moved over the season". Backed by Sports Probabilities MCP, a live remote MCP server — not a scraping Actor you run yourself.
author: Elio Liberatore
author_url: https://github.com/commodus67
metadata:
  category: data-extraction
  keywords: "sports probabilities, playoff odds, monte carlo simulation, nfl, mlb, nhl, nba, soccer, win probability, model vs market, kalshi, prediction markets, mcp server, remote mcp"
---

# Sports Probabilities MCP

Get Monte Carlo playoff/title/relegation probabilities for the NFL, MLB, NHL, NBA and 17 soccer leagues, and see where those probabilities disagree with live Kalshi prediction-market prices — all through one hosted MCP server, no scraping or Actor runs required on your side.

**Disclosure:** this skill routes exclusively to `sports-probabilities-mcp`, an Apify Actor/MCP server built and owned by the author (Elio Liberatore / `commodus67`), which in turn calls four other paid Actors the author also owns and built (`football-soccer-monte-carlo-predictor`, `mlb-playoff-odds-monte-carlo`, `nfl-playoff-odds-api-monte-carlo-simulator`, `nhl-playoff-odds-monte-carlo`, `nba-playoff-odds-monte-carlo`). All five charge pay-per-event on the Apify platform; the author has a direct financial interest in their use. No affiliate/referral links are used anywhere in this skill.

## What this skill does (and what it deliberately does not)

This skill answers questions with **model output and market-comparison math** — simulated probabilities, Monte Carlo re-runs under different assumptions, and the net edge/EV/Kelly-stake math against live Kalshi prices. Every tool response, and this skill, treats that output as **research, never as betting advice**: it reports what the model and the market say, not what to do about it. If a user asks "should I bet on X", answer with the model's number and the market's number and stop there — don't turn edge into a recommendation.

## Example prompts

Prompts this skill handles:

- "What are the Kansas City Chiefs' playoff odds right now?"
- "Rank the Premier League by title probability, most likely first."
- "Where does the model disagree most with Kalshi on NFL playoff odds?"
- "Re-run the NBA simulation with higher home-court advantage — who gains the most?"
- "How did the Dodgers' World Series odds move over the 2026 season?" (only works if that run was archived — see Workflow step 4)

Out of scope (the boundary):

- "Should I bet on the Chiefs to make the playoffs?" — this skill reports the model's probability and the market's price, with the net edge after fees; it does not tell anyone whether to place a bet. Say so and give the numbers instead.
- "Scrape me the box score / play-by-play for last night's game" — this MCP has no play-by-play or box-score data, only season-long Monte Carlo probabilities. Point to a dedicated sports-data-scraping Actor on the Apify Store instead.

## Prerequisites

- An Apify account ([sign up](https://apify.com)) — the server is itself an Apify Actor running in Standby mode, and it bills per call via Apify's pay-per-event system.
- Authentication, by whichever your MCP client supports:
  - **OAuth (recommended):** the server advertises OAuth; an OAuth-aware MCP client (e.g. Claude's own connector UI) detects this automatically — just click Connect and authorize with your Apify account.
  - **Bearer token (manual clients):** an Apify API token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations), sent as `Authorization: Bearer <APIFY_TOKEN>`.

## Workflow

1. **Connect your MCP client directly to the hosted server** — this is a remote MCP server, not a scraping Actor you invoke through the CLI. Endpoint: `https://commodus67--sports-probabilities-mcp.apify.actor/mcp` (streamable HTTP). See [Calling interfaces](#calling-interfaces) for the one case where you'd go through an Actor call instead.
2. **Pick the tool that matches the question** — see the table below. Most questions need exactly one call.
3. **Build the input.** `sport` is always `nfl`, `mlb`, `nhl`, `nba` or `soccer`; soccer additionally needs `league` (a name like `"Premier League"` or an ESPN slug like `esp.1` — see [references/actor-index.md](references/actor-index.md) for the list). `season` only matters for backtesting a past year (NHL/NBA seasons are named by the year they *end*, so `2027` means the 2026-27 season).
4. **For a market question**, call `compare_model_vs_market` (NFL/MLB/NHL/NBA pull Kalshi automatically; for soccer, or to compare against a bookmaker instead of Kalshi, pass your own prices via `marketProbabilities`). It returns, per team, the model probability, the market probability, the edge, and — on the better side of the contract — the fee-aware net EV and a quarter-Kelly suggested stake capped by `maxPerPositionPct`/`maxTotalExposurePct`. Present this as the model's disagreement with the market, not as a trade to make.
5. **For "what if" questions**, use `run_scenario` — it starts a fresh simulation under changed parameters (home-field advantage, how hard a short record regresses to .500, point/run-differential weight, model uncertainty) and is explicitly not reading the cache, so expect it to take longer and cost more than a plain read.
6. **For historical trends**, use `get_probability_history` — it only returns probabilities that were actually archived (the source Actors need `archiveToNamedDataset` set on their runs). If the user asks about a season nobody archived, say so; this tool can't reconstruct history that was never recorded.

## Tool reference

| Tool | Use for | Required params | Notes |
|---|---|---|---|
| `get_team_probabilities` | One team's playoff/title/division/seeding/relegation odds and projected finish | `sport`, `team` | `league` required for soccer; `season` only for backtesting |
| `get_league_probabilities` | Whole league ranked by a probability instead of by standings | `sport` | `metric` picks the ranking (see table below); `order: ascending` for relegation |
| `compare_model_vs_market` | Where the model and Kalshi (or your own prices) disagree, with fee-aware edge and a suggested stake | `sport` | Returns `hasValue: false` rows too — that's not an error, it means the edge is below `minEdge` (default 0.05) |
| `run_scenario` | Re-simulate under different model assumptions | `sport`, `parameters` | Fresh simulation, not cached — costs the most (`scenario-simulation` event, see pricing below) |
| `get_probability_history` | Read an archived season's probability movement | `datasetName` | Only returns what was actually archived; `team` optional to narrow to one |

`metric` options for `get_league_probabilities`: NFL/MLB → `playoff`, `division`, `wildCard`, `topSeed`; NHL → the same plus `bestRecord`; NBA → `playoff`, `playIn`, `topSix`, `division`, `bestRecord`, `conferenceFinals`, `conference`, `title`; soccer → `title`, `top4`, `qualify`, `playoff`, `relegation`.

## Actor routing

The server doesn't reimplement the Monte Carlo — it calls one of five Actors (via `Actor.call`, server-side, with the server owner's own token) depending on `sport`, caches the result, and returns the model's output through a unified tool shape. The full table with pricing notes lives in [references/actor-index.md](references/actor-index.md); condensed:

| `sport` value | Actor ID | Tier | Coverage |
|---|---|---|---|
| `nfl` | `commodus67/nfl-playoff-odds-api-monte-carlo-simulator` | community | All 32 NFL teams |
| `mlb` | `commodus67/mlb-playoff-odds-monte-carlo` | community | All 30 MLB teams |
| `nhl` | `commodus67/nhl-playoff-odds-monte-carlo` | community | All 32 NHL teams |
| `nba` | `commodus67/nba-playoff-odds-monte-carlo` | community | All 30 NBA teams |
| `soccer` | `commodus67/football-soccer-monte-carlo-predictor` | community | 17 leagues (pass `league`) |

`Tier` = `community` for every row — all five are independently built by the same author as this MCP server, not Apify-maintained.

## Pay-per-event pricing

The server itself bills per call, separately from whatever the backing Actor would cost run directly — you never pay the backing Actor's price twice:

| MCP event | Triggered by | Approx. price |
|---|---|---|
| `read-probabilities` | `get_team_probabilities`, `get_league_probabilities` | ~$0.05/call |
| `market-comparison` | `compare_model_vs_market` | ~$0.10/call |
| `scenario-simulation` | `run_scenario` | ~$0.25/call (uncached, full re-simulation) |
| `probability-history` | `get_probability_history` | ~$0.05/call |

Prices are set by the Actor owner on the Apify Store and can change — always treat the number above as approximate and check [the Store page](https://apify.com/commodus67/sports-probabilities-mcp) for the current figure before committing a user to a large batch of calls. See [references/gotchas.md](references/gotchas.md) for cost guardrails on batched or scenario-heavy usage.

## Calling interfaces

**Option A — connect directly as an MCP client (recommended, and the only way to get the unified tool shape and the Kalshi comparison math):**

Point your MCP client at:

```
https://commodus67--sports-probabilities-mcp.apify.actor/mcp
```

Streamable HTTP, OAuth-capable. This is the normal path for everything in this skill.

**Option B — Apify MCP connector, calling a backing Actor directly:**

If you only need one sport's raw simulation rows and don't need the market comparison or the unified shape, the hosted connector at [mcp.apify.com](https://mcp.apify.com) can run one of the five Actors in the table above directly via its own Actor-calling tools. You lose the cross-sport unified tools and the Kalshi edge math this way — prefer Option A unless you have a specific reason not to.

**Option C — Apify CLI, same caveat as Option B:**

    apify actors call commodus67/nfl-playoff-odds-api-monte-carlo-simulator \
      --input '{"season": 2026}' \
      --user-agent apify-awesome-skills/apify-sports-probabilities-mcp \
      --json 2>/dev/null

This runs the backing Actor directly and returns its raw dataset rows — not through the MCP server, so no caching and no market comparison. Use Option A for anything this skill's example prompts cover.

## Troubleshooting

- **"Connection error — could not connect to a valid MCP server"** — almost always means the client was configured with a *run-specific* URL (`*.runs.apify.net/mcp`), which dies when that run ends. Reconnect using the permanent endpoint above, not a URL copied from a live-run view.
- **`compare_model_vs_market` returns many rows with `hasValue: false`** — not an error. It means the model and the market agree closely enough that the edge is under the `minEdge` threshold (default 0.05); only rows with `hasValue: true` are worth surfacing as a disagreement.
- **A team's early-season numbers look suspiciously close to 50/50 across the board** — expected before enough games are played for the current season's record to carry weight; the model blends in a shrunk prior from the previous season, so this should resolve itself after a few weeks, not stay flat all season.
- **Soccer call fails or returns nothing** — check that `league` is one of the supported ESPN slugs or names; an unmapped league string returns no data rather than guessing. See [references/actor-index.md](references/actor-index.md) for the list.
- For detailed cost guardrails and confirmation thresholds before running `run_scenario` in a loop, see [references/gotchas.md](references/gotchas.md).
