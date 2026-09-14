# Rungs 1 to 3 in detail: rate, fidelity, tokens

`SKILL.md` keeps each of these to a paragraph, because classification decides the outcome and remediation only carries it out. This is the detail you need once you already know which rung you are on.

## Rung 1: rate and IP spread

### Choosing `proxyRotation`

| Value | Rotates | Use when |
|---|---|---|
| `RECOMMENDED` (default) | evenly, drops blocked proxies | independent, stateless page fetches |
| `PER_REQUEST` | new proxy every request | the site bans an IP quickly and requests share no state |
| `UNTIL_FAILURE` | one proxy until it fails | **the flow carries state**: cookies, a cart, a search session, a token bound to an IP |

The common failure is a stateful flow running under `PER_REQUEST`: every request arrives from a new IP carrying a session issued to a different one, which looks far more suspicious than a steady crawler. Use `sessionPoolName` to keep sessions separate between runs that must not share state.

**Once residential works, the flow has probably become stateful.** A WAF that lets you through usually issues a persistence cookie on the way (`__cf_bm`, `BIGipServer…`, `incap_ses_…`). That cookie is bound to the address that earned it, so switch to `UNTIL_FAILURE` for the crawl rather than staying on the default rotation, and expect the first rotation after expiry to look like a fresh block.

### `maxRequestRetries` does not always cap how many times you touch the site

It bounds retries of a *request*; session-level errors rotate the session on a separate counter. Against a **host that never answers** this diverges badly: measured, `maxRequestRetries: 0` produced eleven upstream attempts and `retryCount: 10`. Against a host that answers, including one that answers `403`, the count matches what you asked for. Check `retryCount` when the target is unreachable rather than assuming.

### Verifying that a change did something

With one URL you have an outcome, not a rate, so say which single change moved it. Six identical requests to one challenged platform returned three clean pages and three refusals from the same pool in the same minute, which is what an unlucky single probe looks like from the inside. Only over a real sample does a difference in block rate mean anything, and only then does the "three rungs, no change" stop rule in `SKILL.md` apply. The sample size that makes the rate countable is in `gotchas.md`.

### Diagnosing on a budget

A diagnosis that needs more than one run per egress is usually asking the wrong question. Two patterns keep the spend flat:

- Put every URL you want to compare into one run's `startUrls` rather than starting a run per URL. The per-run overhead dominates at this size, and one run gives you a matrix instead of a list.
- Repeat one URL with distinct `uniqueKey` values when you need a rate rather than an outcome. Same target, one run, six data points.

## Rung 2: request fidelity

Reproduce what a real client sends, in the order it sends it.

- **Headers and their order.** A default HTTP client's header set is itself a fingerprint. `Accept`, `Accept-Language`, `Accept-Encoding`, `User-Agent` and `Referer` should form one plausible client, and the `Referer` chain should match the path a human would take. `curl -H` appends in the order you pass and cannot reproduce a browser's ordering, so it cannot test this rung at all: set the headers in the Actor's `preNavigationHooks`, where you are writing the request options object directly.
- **Cookies the site sets before the page you want.** Pass them via `initialCookies`, or collect them in `preNavigationHooks`.
- **Coherence.** Match `Accept-Language` to the proxy country. A US residential IP asking for `ru-RU` is a contradiction the edge can see, and the same applies to timezone and locale once a browser is involved.

**The boundary of this rung, stated honestly.** Below the header layer sits the TLS and HTTP/2 fingerprint: cipher ordering, extensions, ALPN, HTTP/2 SETTINGS. A default Go or Node client is distinguishable from Chrome there, and no header work fixes it. If the evidence points at that layer, the tool class is uTLS or curl-impersonate, neither of which is an Apify Actor, or you accept the cost and move to Rung 5.

## Rung 3: tokens and edge cookies from a legitimate flow

Many "blocks" are a missing credential the site issues earlier: a build id, a CSRF token, a search token, a signed URL with a TTL, or the edge cookies a WAF sets on first contact.

- Find where it is issued, request it the way the site does, then reuse it.
- Bind it to the session and the address that obtained it. A token replayed from another IP is a stronger bot signal than no token at all.
- Respect TTLs. Refresh on expiry rather than on every request.
- **If Step 2 saw a sensor script or edge cookies on an otherwise clean page, this is where they matter.** Carry them into Rung 4: the page was open, the API behind it usually is not.

**Where this rung stops.** A value the site hands to anyone who loads the page is a parameter, and it belongs here. A value issued to a person, or one that gates records the site does not otherwise publish, is a credential you do not own: that is Step 0, and the answer is to stop and say so. The test is in `SKILL.md` under Step 2.
