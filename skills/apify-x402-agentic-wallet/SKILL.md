---
name: apify-x402-agentic-wallet
description: Discover, pay for, and run any Apify Actor by paying USDC on Base over the x402 protocol with a Coinbase Agentic Wallet (awal) — no Apify account or API key. You buy one small, spend-capped prepaid Apify token, then run as many Actors as the request needs with it. Use when the user wants to use Apify tools without signing up, pay per use with crypto / USDC, set up an agentic wallet, mentions "x402", "awal", "agentic wallet", "Coinbase wallet", "pay with USDC", "no API key", or asks to pull live web data (social media, search, maps, marketplaces, news) while paying on-chain per use.
author: Martin Forejt
author_url: https://github.com/martinforejt
---

# Use Apify tools by paying with an agentic wallet (x402)

You are an agent with a Coinbase Agentic Wallet (`awal`). This lets you discover, pay for, and run any
of Apify's thousands of web-data and automation tools ("Actors") by paying USDC on Base over the
**x402** protocol — no Apify account or API key. Make **one** small payment to buy a prepaid,
spend-capped Apify token, then run as many Actors as the request needs with it.

For every request, run this loop: **discover an Actor → check its input + price → run it → read the
data → answer.** You need only `npx awal` and `curl` — read the raw JSON/markdown each command returns
yourself; don't pipe output through `python`, `jq`, or any other script. **This page is the only
instructions you need** — every `awal` command for this flow is below.

---

## About this page

This URL serves **this markdown playbook** — instructions for you, not an x402 payment endpoint.
`npx awal x402 details <this-url>` correctly returns `NO_PAYMENT_REQUIREMENTS`. Read the page with
`curl` (or your built-in fetch) and follow the steps below. Real x402 payments happen at
`agi.apify.com/protocols/x402/prepaid-tokens?amount=…&currency=usd` in Step 3.

---

## Start here — greet the user, then set up

Don't run anything yet. First introduce yourself and ask to begin. Say something like:

> I can pull live data from the web and run automations for you — social media, search engines, maps,
> marketplaces, news, and thousands of other sources — by paying tiny amounts of USDC for tools on
> Apify ("Actors"). No Apify account or API key needed; I pay per use from a crypto wallet (a Coinbase
> Agentic Wallet, over x402).
>
> To start I'll set up the wallet — I'll just need your email and a verification code. Then you can ask
> me for any web-data task. Want to begin? If so, what email should I use?

Only proceed when the user agrees. Don't mention funding amounts up front — only bring up the USDC + ETH
requirement if the wallet turns out to be empty or underfunded at Step 2.

## Step 1 — Authenticate the wallet

**Always ask the user for their email. Never guess it or take it from your environment/context** — wait
for them to tell you, even if you think you know it.

```bash
npx -y awal auth login <email>  # emails the user a verification code
```
(`awal` needs no install — `npx` fetches and caches it on first use. The `-y` skips the first-run
download confirmation so a non-interactive agent doesn't hang. Use plain `npx awal` thereafter.)
Then **ask the user for the code** and verify it:
```bash
npx awal auth verify <code>
npx awal status                 # expect: Authenticated, logged in as <email>
```
The wallet is created on first login. If `status` isn't authenticated, repeat the login/verify pair.
`status` may print `auth verify <flow-id> <code>`; you only need `npx awal auth verify <code>` — the flow
ID is saved automatically from login. If any later command says **Not authenticated**, run `npx awal status`
and repeat Step 1.

## Step 2 — Check funding (two assets on Base: USDC + ETH)

```bash
npx awal balance --chain base --json   # need BOTH: USDC > $1 AND ETH > 0
npx awal address                 # get the wallet address if the user needs to fund it
```
If either asset is missing, share the address and ask the user to fund it on **Base**, then wait. To
make funding easy, fetch a scannable QR of the address:
```bash
curl -s "https://apify.com/api/wallet-qr?address=<wallet-address>"
```
**You MUST paste the command's entire raw output directly into your reply, verbatim, inside a code
block — every line, unchanged.** The output is a QR made of block characters; the user scans it with
their phone wallet to fund the address. Do NOT summarize it, describe it, replace it with the address
text, or drop any lines — if you don't print the actual characters, there is no QR to scan. Show the QR
first, then the funding instructions. Optionally open the wallet UI for Coinbase Onramp:
```bash
npx awal show   # opens the companion window; user can fund with card/Apple Pay/Coinbase
```

**⚠️ USDC alone is not enough — you need a little ETH for gas.** The `awal` wallet is a smart-contract
wallet that must be deployed on-chain before it can authorize any payment, and that one-time deployment
costs native ETH. With USDC but **0 ETH**, the first payment fails:
```
Failed to deploy wallet
... sender balance and deposit together is 0 but must be at least <n> to pay for this operation
```
The ETH must come from **outside** (exchange withdrawal on Base, or another wallet) — you can't swap
USDC for it, since a swap also needs gas. ~0.001 ETH is enough; the first payment then deploys the
wallet automatically. Apify payments themselves are gasless.

## Step 3 — Buy a prepaid Apify token (one x402 payment)

**Pause and ask the user to confirm before paying.** Tell them what you're about to do — e.g. "I'll pay
$1 of USDC over x402 to buy a spend-capped Apify token (expires in 14 days, non-refundable). Go ahead?"
— and only run the command once they say yes. **A task request alone is not consent** — wait for an
explicit "go ahead" (or similar). This is the moment people are here to see, so don't do it silently.

Put the amount in the **query string** so payment discovery picks it up (without `?amount=…&currency=usd`,
`x402 details` on the prepaid-tokens URL returns `NO_PAYMENT_REQUIREMENTS`):
```bash
npx awal x402 pay 'https://agi.apify.com/protocols/x402/prepaid-tokens?amount=1&currency=usd' \
  --max-amount 1000000 --json
```
`--max-amount` is a safety cap in USDC atomic units (`1000000` = $1.00). `awal` prints a spinner line
before the JSON; just read the JSON object that follows. On success:
```json
{"status":201,"data":{"token":"apify_api_...","remainingBalanceUsd":1,"expiresAt":"<+14 days>"}}
```
Keep the `token` for the session as your Apify API key (it's what `$TOKEN` refers to in the commands
below); never print or persist it. It's capped to what you paid, **expires in 14 days**, and unused
credit is **non-refundable** — buy only what you'll use.

> Fails with `currency must be "usd"` → params must be in the URL. Fails with `Failed to deploy wallet`
> → see the ETH note in Step 2. Fails with `authorized but rejected by server` / `REQUEST_FAILED` even
> when ETH is already present → wait a few seconds and **retry the same pay command once** before
> troubleshooting further (first-time smart-wallet payments can fail transiently).

## Step 4 — Handle the user's request

Ask what they want, then run the loop. The user can ask for **anything** — there's no fixed menu. Read
the JSON/markdown each command returns directly. The endpoints below cover most tasks; for anything
else (pagination, run options like memory/timeout, key-value stores), see the Apify API reference in
the Reference section.

**a. Discover an Actor** — search the Store with terms from the request:
```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.apify.com/v2/store?search=<url-encoded terms>&limit=5"
```
Read `data.items[]` and pick one by `username`/`name` (prefer high usage/ratings). The API id joins
them with a tilde: `username~name`. For a multi-source request, use one Actor per source.

**b. Inspect it** — fetch the Actor's docs page, which has the input fields, copy-paste example
inputs, and pricing all in one:
```bash
curl -s "https://apify.com/<username>/<name>.md"
```
Take an example input and adapt it to the request; read the Pricing section so you don't blow your cap
(small scrapes are often 1–2 cents; large jobs cost more — keep result limits modest). If an Actor accepts
an array of categories/tags, run **one value per Actor call** when you need several (e.g. `ai` then
`tech`) — a single call with multiple values may return only one category up to the per-run cap. Merge
and dedupe in your answer using stable `id` fields.

**c. Run it and read the results:**
```bash
curl -s -X POST "https://api.apify.com/v2/acts/<username~name>/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '<input-json>'
```
Then answer concisely. Watch for failures:
- Items with `requestErrorMessages`/`error` and no real fields = the target **blocked the scrape**.
  Retry once, else try another Actor. Never present a blocked/empty run as a result or fabricate data.
- `run-sync` times out ~5 min. For big jobs: `POST /v2/acts/<id>/runs`, poll
  `GET /v2/actor-runs/<runId>` until `SUCCEEDED`, then `GET /v2/datasets/<defaultDatasetId>/items`.
- **Verify the right entity** — a handle on one platform may be someone else on another; sanity-check
  follower count / verified badge.
- **Rank only on fields the Actor returns** — if attendance or popularity metrics are missing or zero,
  say so; don't treat `isSoldOut` or sparse metadata alone as proof something is "top" or "worth attending."

## Manage the balance
```bash
curl -s "https://agi.apify.com/prepaid-tokens/balance" -H "Authorization: Bearer $TOKEN"
```
When low, buy another token (Step 3) and switch to it.

## Guardrails
- Your spending cap is the token balance. Spend only what the task needs; check price before big jobs.
- You may run `auth login`/`auth verify` and buy a token yourself. **Never** run `send`, `trade`/`swap`,
  or otherwise move funds — ask the user first for anything beyond authenticating and buying credit.
- Never print or persist the token. Treat it like a live API key.
- If a run is blocked or empty, say so and try another Actor — never make up results.

## Reference
- **`awal` commands used in this flow** (all via `npx awal`; first run may need `npx -y awal`):
  `status`, `auth login <email>`, `auth verify <code>`, `balance --chain base --json`, `address`,
  `show`, `x402 pay <url> --max-amount <atomic-usdc> --json`
- **Apify API reference** (all endpoints — runs, datasets, key-value stores, pagination, run options):
  https://docs.apify.com/api/v2 — append `.md` to most doc pages for a machine-readable version. Index
  of all docs as `.md` links: https://docs.apify.com/llms.txt (don't fetch `llms-full.txt`, it's ~43 MB).
- Apify x402: https://docs.apify.com/platform/integrations/x402
- AGI endpoint: https://agi.apify.com (machine docs at `/AGENTS.md`, `/llms.txt`)
- `awal` CLI docs (optional, for edge cases): https://docs.cdp.coinbase.com/agentic-wallet/cli/welcome
- Verified on `awal` v2.12.0 on Base (any recent version should work). Check with `npx awal --version`.
