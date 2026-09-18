# Gotchas: what the field notes say, and what they cost

Every item here was observed on a live public source, not reasoned from documentation. Where a claim is inference rather than measurement, it says so. Anything already stated in `SKILL.md` is not repeated here.

## Diagnosis

### Record where you tested from, every time

A block is a statement about a pair: your request **and** your path to the site. The same URL can answer a residential connection and refuse a hosting IP in the same second. A note that says "the site blocks scrapers" and does not say which network it was tested from cannot be reused by anyone, including its author a month later.

Minimum to write down, and the first two matter more than people expect:

1. **Which resolver answered, and what it said.** Not your configured one alone: a local, corporate or captive resolver can answer for a name that does not exist publicly.
2. **Whether the returned address is routable.** Private ranges, CGNAT (`100.64/10`) and the RFC 2544 benchmarking range `198.18.0.0/15` mean you are looking at your own path, not the site's.
3. Egress IP and country.
4. Whether the egress ASN is residential, mobile or hosting.

Recording only 3 and 4 is how a diagnosis goes wrong quietly. A real case: a host that failed with a TLS error resolved locally to `198.18.4.138`, a bogon, while two public resolvers returned NXDOMAIN. The note written from fields 3 and 4 alone reads "hosting IP in Japan, blocked" and points the next reader at geo and ASN reputation. The host simply did not exist.

### Verdicts of "not blocked" need a second egress too

Everyone knows a single "blocked" result is provisional. A single **clean** result is provisional in the same way, and more dangerously, because nobody re-checks good news. If your own path is confounded at all, and transparent interception is enough to confound it, a local `200` is not evidence that the site is open.

### Connection-level failures leave a different artefact

When there is no response, the usual advice to keep the raw response does not apply. Keep these instead, because they are what the diagnosis is made from:

- the answer from each resolver you asked, including which one, and the returned address;
- whether TCP connected, and how long that took, separately from what failed afterwards;
- the exact client error string, since "connection reset", "connection refused" and "TLS handshake failed" point at three different layers.

### Block rate, and when you are allowed to use the words

**Block rate** is refused requests divided by attempted requests, over a sample large enough to mean something: at least twenty requests to the same source. **On a single URL there is no block rate, only an outcome.** Say "it worked" or "it did not" and do not dress one request as a measurement. The "three rungs with no change" stop rule below is a statement about a rate, so it does not apply until you have one.

### A CDN error page is not the site's opinion of you

A generic edge error (`Request blocked`, `Access Denied`, a bare `403` with the CDN named in `Server` or `Via`) is produced before the origin sees the request. It carries no information about your headers, your fingerprint or your behaviour, because nothing of yours was evaluated beyond the network. Treating it as bot detection sends you up the whole ladder against a rule that only reads an address.

Observed on a large US county assessor site fronted by a CDN, four requests to one URL:

| Egress | Client | Result |
|---|---|---|
| hosting provider, non-US | default HTTP client | `403`, CDN error page |
| same IP | live desktop Chrome | `403`, identical |
| Apify Proxy, **datacenter** | Cheerio, no browser, no JS | **`200`, full page, first attempt** |
| Apify Proxy, **residential**, US | Cheerio, no browser, no JS | `200`, byte-identical to the row above |

Rows one and two say "not my client": a real browser failed exactly like the script, in the same second. Row three says "not datacenter addresses as a class" either, because the request that succeeded came from a datacenter and was the least browser-like client in the table. What was left was the specific network rows one and two went out on. Row four is the expensive lesson: residential bought nothing here, so it is a probe to run once rather than a setting to adopt.

**Do not predict the result of that test from this one.** The same pair of clients on a state assessment portal, from the same kind of hosting egress, gave the opposite answer: `403` to the HTTP client and the full page to Chrome, in the same minutes. Both sites are `403` behind the same CDN vendor, and only running Test A tells you which of the two you are looking at.

### The browser was the worse client, measured three ways

On one vendor platform behind a managed challenge, in the same fifteen minutes:

| Client and egress | Answer |
|---|---|
| HTTP Actor, Apify datacenter proxy | `cf-mitigated: challenge` twice, then a clean `200` with the real page |
| Browser Actor, same proxy pool, one minute later | hard block page, no `cf-mitigated` |
| Desktop Chrome, hosting egress that the HTTP client had been challenged from | sat through "Verifying you are human", then loaded the real page |

Three things follow. Escalating to a browser can move you from a passable challenge to a hard refusal, so it is not a strictly stronger client. A managed challenge really does clear itself for an ordinary browser, so the challenge class is worth one browser run. And a Crawlee browser Actor never reaches that point unless unblinded, because it aborts on the challenge's `403` before the page can clear: three requests, three empty error items.

Cost of the comparison: `0.0011` compute units for three requests through the HTTP Actor against `0.0131` through the browser Actor, roughly twelve times, before proxy traffic.

### A soft 404 is not a block

A `200` can carry full site chrome, correct headers, a plausible size, and a body that says the page does not exist. Only the content distinguishes it. A crawler counts it as a success, and a diff against an earlier capture reports a page that changed rather than a link that died.

### Your own client's failure looks exactly like the site's

A script that throws while formatting a result writes the same "error" into your notes as a site that refused you. In one sweep a target was recorded as failing when the fault was a string operation in the probe. Before adding a refusal to a journal, confirm the request actually left the machine.

This happens inside Actors too, and the item looks identical to a block. A `pageFunction` that called `response.status()` on an Actor whose response object exposes `status` as a plain property produced `#error: true` items reading `TypeError: response.status is not a function`, which is a bug in the probe and not an opinion of the site. Read `#debug.errorMessages` before recording anything: a refusal names a status code, your own bug names your own code.

### The diagnosis is traffic too

A burst of probes is a pattern the target counts, and the answer can move under you while you measure. Prefer one run carrying every URL you want to compare over one run per URL, keep repeats deliberate, and when a source's answer changes mid-investigation, check your own request volume before concluding the site escalated against you.

## Cost

- A browser costs one to two orders of magnitude more per page than an HTTP request. Rung 5 is a budget decision, not a technical preference.
- Residential proxy traffic is billed by volume. Run it once as a probe when two same-class egresses have refused; adopt it for a whole crawl only after it has proved to be the variable that mattered. On one site it changed a `403` into a full page; on another it returned a byte-identical page for more money.
- Change one variable at a time: group, then country. Two changes at once buy an improvement you cannot attribute or reproduce.
- Sample before scaling: a handful of URLs, confirm the outcome moved, then run the full set. Confirm with the user before any run whose estimated cost is significant.

## Recovery

- **Track failure rate per source and alert on it.** A source that quietly degrades from 2% to 60% failures produces a dataset that still looks like a dataset. You want to hear about it from a graph, not from a hole in the data.
- **Keep the raw response of the first failure.** Status, headers, first kilobyte of the body. Every diagnosis above is made from that artefact, and it is gone by the time anyone asks.
- **Three rungs with no change means the diagnosis is wrong**, not that the tooling is weak. Go back to the classification table. This only applies over a real sample; on a single URL there is no rate to compare.
