# Gotchas — apify-sports-probabilities-mcp

Cost guardrails and error recovery specific to this MCP server. For what each tool does, see [SKILL.md](../SKILL.md).

## Cost guardrails

This server is pay-per-event (`PAY_PER_EVENT`), billed per MCP tool call — not per row and not per backing-Actor run. Check the current per-event prices on [the Store page](https://apify.com/commodus67/sports-probabilities-mcp) before committing to a large batch; the approximate prices at the time this skill was written:

| Event | Triggered by | Approx. price | Why |
|---|---|---|---|
| `read-probabilities` | `get_team_probabilities`, `get_league_probabilities` | ~$0.05 | Usually served from cache (3h NFL/MLB/NHL/NBA, 6h soccer) |
| `market-comparison` | `compare_model_vs_market` | ~$0.10 | Reads the model cache plus a live Kalshi fetch |
| `scenario-simulation` | `run_scenario` | ~$0.25 | **Not cached** — always a fresh Monte Carlo run, the most expensive call |
| `probability-history` | `get_probability_history` | ~$0.05 | Reads an already-archived dataset, no simulation |

### Confirmation thresholds (suggested)

- A single `run_scenario` call (~$0.25) needs no special confirmation.
- A loop of `run_scenario` calls — e.g. sweeping one parameter across several values to chart sensitivity — adds up fast. Estimate the total (`$0.25 × number of calls`) and warn the user above **~$2**; get explicit confirmation above **~$10**.
- `get_league_probabilities` with a high `limit` still costs one `read-probabilities` event regardless of how many teams come back — no extra guardrail needed there.

## Common errors

| Error / symptom | Cause | Fix |
|---|---|---|
| MCP client reports a connection error | Client was configured with an ephemeral `*.runs.apify.net/mcp` URL instead of the permanent endpoint | Reconnect using `https://commodus67--sports-probabilities-mcp.apify.actor/mcp` |
| `get_team_probabilities` / `get_league_probabilities` for soccer returns nothing | `league` wasn't a recognized name or ESPN slug | Use one of the slugs listed in [actor-index.md](actor-index.md); league names like `"Premier League"` also resolve but an unmapped string returns no data rather than a fuzzy match |
| `compare_model_vs_market` for soccer returns no comparisons | No automatic Kalshi market exists for soccer league titles | Pass `marketProbabilities` yourself (e.g. derived from bookmaker odds) — this is expected, not a bug |
| `get_probability_history` returns an empty result | The named dataset was never archived — the backing Actor's run needs `archiveToNamedDataset` set for that to happen | Tell the user that history for that season/team wasn't recorded; this tool cannot reconstruct it after the fact |
| `run_scenario` takes noticeably longer than other calls | Expected — it's explicitly not reading the cache, it starts a fresh Monte Carlo simulation | Not an error; just slower and more expensive than a plain read |

## Actor-specific notes

### `commodus67/nfl-playoff-odds-api-monte-carlo-simulator` and the NBA/NHL equivalents

- Before enough games are played in a new season, these models blend in a prior from the previous season (shrunk toward .500) rather than starting from a flat 50/50 for every team — so don't expect uniform preseason numbers; if they ever do look suspiciously uniform across every team, that's the bug this prior was built to prevent, worth flagging back to the author rather than treating as normal.
- NHL and NBA seasons are named by the **year the season ends** — `season: 2027` for NHL/NBA means the 2026-27 season, which trips people up if they're used to NFL/MLB's convention of naming by the year it starts.

### `commodus67/football-soccer-monte-carlo-predictor`

- Resolves matches by a blended "strength gap" model, not goals-based Poisson — so its numbers aren't directly comparable in method to a Dixon-Coles single-match predictor, even where both exist for the same league.
- Not every one of the 17 leagues has comparably deep historical data; treat probabilities for thinner-history leagues as noisier, though the tool itself doesn't currently flag this.

### Kalshi market data (via `compare_model_vs_market`)

- Kalshi's taker fee (`feeRate` default 0.07) applies to the price actually paid, not the edge — a large edge on an expensive contract still pays a real fee. The tool's `netEVPerContract` already accounts for this; don't re-derive EV from the raw edge number.
- `cappedByPortfolioLimit: true` on a row with `hasValue: true` means there *is* a value disagreement, but the suggested stake is $0 because the portfolio-level exposure cap (`maxTotalExposurePct`, default 0.06) is already spent on better-edge rows. Don't read that as "no edge" — it's "edge exists, budget is allocated elsewhere."

For a polished gotchas example with more detailed error-recovery flows, see [apify/agent-skills ultimate-scraper gotchas](https://github.com/apify/agent-skills/blob/main/skills/apify-ultimate-scraper/references/gotchas.md).
