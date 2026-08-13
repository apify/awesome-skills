---
name: apify-blocked-scrape-triage
description: Diagnose and recover a scrape that is blocked, throttled, or served empty or partial content, in cost order, before paying for a heavier Actor. Use when a run returns 0 items, when a site answers 403, 429 or a challenge page, when the HTML comes back empty or truncated, when a request fails with no response at all, when the page shows data in a browser that the Actor does not see, or when a scraper that worked yesterday suddenly returns nothing. Triggers - "I'm getting blocked", "403 from the site", "429 rate limited", "Cloudflare challenge", "scraper returns empty results", "connection reset", "page loads in my browser but not in the Actor", "do I need residential proxies", "should I switch to a browser", "my scraper broke overnight". Escalates in cost order - a cheaper published source first, then reachability, request rate and IP spread, request fidelity, session tokens, the site's own internal API, browser last.
author: Mikhail Koviazin
author_url: https://github.com/mikhail-koviazin
---

# Blocked scrape triage

A scrape came back wrong. Find out why before changing anything, then escalate in cost order. Most "blocks" are not bot detection, some are not even a live server, and the browser is the most expensive answer rather than the first one.

Work the steps in order. Step 0 ends more investigations than the whole ladder does.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via one of:
  - `apify login` (OAuth, if using the Apify CLI)
  - `APIFY_TOKEN` environment variable
  - Token from [Apify Console → Settings → Integrations](https://console.apify.com/settings/integrations)

## What a diagnosis is allowed to cost

**One DNS pair, one navigation per egress per host, then stop and conclude.** The unit is the host, not the organisation: one county published its records across three hostnames that refused a request in three different ways, and a budget spent on "the target" would have bought one of those three answers. The budget counts requests to hosts the target owns; looking something up on a third-party platform, a data catalogue or your own IP check is free. If you are four requests into one host and still cannot name the cause, you are no longer diagnosing, you are probing, and you should say what you know and what it would cost to learn more. One navigation means one page: a browser pulling forty subresources for that page is still one navigation, and a burst of repeated probes is not. The one exception worth spending on is the residential probe in Step 3, a single run that separates "your network" from "actually defended".

Sample before you commit to a fix, change one variable at a time, and remember that your diagnosis is traffic the target counts. Residential traffic and browser Actors are the two line items that surprise people.

**One variable includes time.** Measurements taken from one egress at 05:44 and from another at 05:57 differ by network *and* by half an hour, and a refusal that expired on its own is indistinguishable from one your second egress defeated. When you compare two egresses, interleave them inside the same minute. This bit a real investigation: three hosts looked like a clean "the network is the cause" result until the blocked egress was re-measured later and two of the three answers had changed.

## Know your own vantage point first

Two requests, both free, both about you rather than the target. Skipping them is how a problem with your own address becomes a proxy purchase.

**1. What your egress looks like from outside.** Not its class in the abstract, the actual address, network and country the site sees:

```bash
curl -s "http://ip-api.com/json/?fields=query,country,as,org,hosting"
```

That service is free for non-commercial use and rate limited, and it tells you where you stand in its own headers: a live call returned `X-Rl: 44` (calls left in the window) with `X-Ttl: 60` (seconds until reset). Read them rather than discovering the limit as a failure, and for anything regular use a source whose terms fit your use. When you only need the address, the country and which POP you land on, an endpoint with no such conditions does that much:

```bash
curl -s "https://www.cloudflare.com/cdn-cgi/trace"
```

Measured side by side from one egress: the trace returned `ip=64.176.60.193`, `loc=JP` and `colo=KIX`, while the first call added what the trace does not carry, `AS20473 The Constant Company` and `"hosting": true`. The ASN and the hosting flag are the parts that predict a refusal, so the cheaper endpoint is a supplement rather than a replacement.

`"hosting": true` means every WAF you meet has classified you before reading a single header of yours, and that a `403` from a public site is the expected answer rather than a surprise. **Egress** below means exactly this: the network your request leaves from, as the site sees it. Two egresses of the same class, a hosting IP and a datacenter proxy, are usually one data point to a WAF rather than two.

**Run this from every machine you are about to call a separate vantage point, and compare the addresses rather than the machines.** A laptop behind a VPN client and the VPN's own server are one egress, not two, and the check says so in one line. Measured: two machines a continent apart returned the same `query` address, so every "second opinion" taken from the laptop was the first opinion again. What did differ was the path: the same request that timed out after 30 seconds from the laptop reported `connect=0.000000s` from the server, which is a silent TCP drop rather than a slow host, and only the second form of the measurement says which one you have.

**2. Whether your DNS answers mean anything.** Resolve over DoH rather than UDP, against two providers:

```bash
curl -s -H "accept: application/dns-json" "https://dns.google/resolve?name=HOST&type=A"
curl -s -H "accept: application/dns-json" "https://cloudflare-dns.com/dns-query?name=HOST&type=A"
```

**If UDP answers hand back a non-routable address while DoH returns a real one, your own machine is answering, and the UDP answer is not evidence of anything.** The usual cause is not hostile: proxy clients in the Clash, mihomo and sing-box family default to fake-ip mode, where the client invents an address out of `198.18.0.0/15` so it can route by hostname rather than by IP. Addressing the query to `1.1.1.1` or `8.8.8.8` changes nothing, because the answer never leaves the machine. Observed on exactly such a setup: both UDP queries returned `198.18.5.101` for a host whose real addresses came back over DoH from those same two providers.

If you are on a VPN or proxy client at all, assume this until DoH says otherwise, and never report a host as dead on a UDP answer alone.

**DoH is the better witness here, not an infallible one.** On a corporate or container network with split-horizon DNS, an internal name resolves only through the local resolver, and DoH will answer NXDOMAIN for a host that exists for you; some networks also block DoH outright. The rule above is about public sites, where the public answer is the one that matters. If your target is internal, invert it: trust the local resolver and use DoH only to prove the name is not public.

## Step 0: is this data published somewhere cheaper

These checks cost at most one request each and they end the investigation outright. In a sweep of twenty-one public data sites, this section was the right answer more often than the entire ladder below. **That sample is public-sector and open-data heavy, where defences are rare and publication is common**, so read the ratio as an argument for checking cheaply first, not as a claim about the web at large: on commercial marketplaces and listing sites the balance moves the other way, and this section will end fewer of your investigations.

- **A deliberate publication of the same data.** An open data portal, an ArcGIS REST service, a bulk download page, a `.json` twin of the HTML route, `sitemap.xml`. A published feed is cheaper, more stable and more complete than anything you will scrape, and it often answers from an egress the main site is refusing.
- **A login you do not own, or a paywall.** Stop and say so.
- **Terms that forbid this collection.** Read the target page itself, not only `robots.txt`: assessment portals in particular tend to print the prohibition in the page body while `robots.txt` says nothing. Many sites publish no `robots.txt` at all, and its absence decides nothing either way. Where the terms forbid automated collection and a portal publishes the same records, the portal is not a workaround, it is the supported route.

**Find the portal rather than guessing at it.** Two families cover most public data, and both have a discovery step people skip because the URL template is easy to remember and useless without an id.

```bash
# Socrata: ask the federated catalog what a domain publishes, then fetch by id
curl -s "https://api.us.socrata.com/api/catalog/v1?domains=DOMAIN&q=TERM&limit=5"
curl -s "https://DOMAIN/resource/DATASET_ID.json?\$limit=5"

# ArcGIS: walk the directory instead of guessing a layer number
curl -s "https://HOST/arcgis/rest/services?f=json"
curl -s "https://HOST/arcgis/rest/services/FOLDER/SERVICE/MapServer?f=json"
curl -s "https://HOST/arcgis/rest/services/FOLDER/SERVICE/MapServer/LAYER/query?where=1%3D1&outFields=*&resultRecordCount=5&returnGeometry=false&f=json"
```

**A hostname that answers is still a guess, and the check is the content rather than the status.** The catalog endpoint above returns the whole federated catalog on *any* host, so a guessed portal name answered `200` with ten thousand results belonging to three other states, and the real portal returned the same rows. Asking the platform whether it knows the domain separated them in one request: `?domains=GUESSED_HOST` answered `{"error":"Domain not found: ..."}` for the guess and its own datasets for the real one. Generalised: **ask whether the records name the host you asked.** The same rule kills wildcard DNS, where every name in a zone resolves and none of them is a service.

**A hostname with no owner in it is usually a vendor serving hundreds of clients**, so the block belongs to the vendor rather than to the body whose data you want, and that body often publishes the records itself. Check the CNAME before assuming independence: four portals under four different government domains resolved to the same three addresses, each CNAME naming the same vendor, sharing one rate limit and one point of failure that the hostnames do not show.

## Step 1: did anything come back, and is the target still there

Everything after this step assumes a server answered you. Three failure classes produce no HTTP conversation at all, they are the cheapest things that can be wrong, and they are the most expensive to miss, because every rung below will fail identically against them at increasing cost.

| Symptom | What it usually is | Check |
|---|---|---|
| No status, no headers, no body; the client reports a DNS error | the hostname does not exist publicly | resolve it against **two public resolvers you did not configure** |
| TCP connects, then the TLS handshake fails | something in your own path is intercepting, or the name resolved to the wrong host | compare the resolved address across resolvers before touching the request |
| Connection refused or reset with no response | wrong port, dead host, or a network-level drop | as above, then check the site's current navigation |
| Your resolver returns an address in a private range, CGNAT (`100.64/10`) or `198.18.0.0/15` | **either** the name is not public, **or** your path intercepts transparently | the two-answer test below. Do not stop on the address alone |

**Resolve the way the pre-flight section says, over DoH, against two providers.** A local, corporate or captive resolver will happily answer for a name that does not exist publicly, and on an intercepted path it will do so in the name of whatever resolver you addressed. If two providers both return NXDOMAIN over DoH, the host does not exist and nothing below applies. One free query, and it can end the investigation.

**A non-routable answer is a question, not a verdict.** Transparent interception is common on corporate and VPN paths, and it works: your traffic still reaches the real origin.

| DoH answers | Your traffic | Meaning | Do |
|---|---|---|---|
| NXDOMAIN from both | nothing arrives | the host does not exist | stop, re-target |
| **a non-routable address, typically from `198.18.0.0/15`** | anything | **your own proxy client answered** (fake-ip mode), and the address says nothing about the host | re-resolve over DoH; if DoH gives a real address, use that and move on. If DoH agrees, treat DNS as unavailable and let a second egress decide |
| real address | nothing arrives, or the origin looks wrong | your path is breaking the connection | fix or bypass your path first, and do not blame the site |
| real address | real origin headers arrive (CDN POP ids, coherent `ETag`s across repeats) | **transparent interception that works** | **proceed**, and record this vantage point as confounded: any verdict now needs a second egress |

**An answer proves less than absence does.** NXDOMAIN proves the name is not public; a real address proves almost nothing, because behind a shared CDN a wildcard record answers for every name in the zone. Confirm a guessed hostname the way Step 0 describes, by asking whether the content names the host you asked.

**A verdict belongs to a host and a path together.** Measured on one vendor platform in the same minute from one egress: `robots.txt` answered `200` while `/` and `/sitemap.xml` answered `403`. The `200` came from the CDN's own managed copy of `robots.txt` and never reached the origin. Before recording "this host blocks us", fetch a second path as a control, and prefer one the CDN cannot be answering for.

**Then check the URL is still the one the site publishes.** The most ordinary cause of "I pulled nothing useful" is not a defence, it is a stale address. Sites move search, catalogues and APIs onto vendor platforms and leave the old hostname to rot for years. Open the site's own current navigation and confirm the path you are using is the one it links to today.

**Stop rule for this step.** If the host does not resolve, or the site no longer publishes that path, you are finished. There is nothing to unblock.

## Step 2: classify what came back

You are here only if a server answered. The single most expensive mistake now is reading every failure as "they detected me" and jumping to a browser with residential proxies. Match the symptom first, and **read the body before you read the status**.

| What came back | Most likely cause | Do NOT | Go to |
|---|---|---|---|
| 403, CDN error page, the edge **identified as Cloudflare** (`server: cloudflare`, `cf-ray`), **no** `cf-mitigated` header, and a blocked-page body rather than an interstitial | a rule that read your address or ASN. Nothing of yours was evaluated | change your client: a real browser can fail identically | Step 3, egress work |
| 403 or 503, interstitial body (`Just a moment...`), **`cf-mitigated` present**, CSP naming a challenge host | a managed challenge. The edge will admit a good client, and the check clears itself given seconds | escalate straight to a browser Actor, see Rung 5 for what that actually did | Rung 1, then Rung 5 |
| 403 from an edge that is **not** Cloudflare, or one you have not identified yet | unclassified. The Cloudflare marker cannot appear here, so its absence carries no information | read "no `cf-mitigated`" as "my address was judged" | name the vendor first, see below |
| 200, a full server-rendered page carrying a form with hidden state (`__VIEWSTATE`, `__EVENTVALIDATION`, a CSRF field), and no records | not a block and not a shell. The records are behind a POST you never issued | read the empty form as a defence, or send it to Rung 5 for a browser | the form test below |
| 403 with an XML or JSON error body from a storage service (`AccessDenied`, `RequestId`, `Server: AmazonS3` or equivalent) | **an object that does not exist.** Storage answers 403 rather than 404 for a missing key | shop for proxies | Step 1, the path is dead |
| 403 only after N successful requests | rate, or a session that aged out | rotate IPs blindly | Rung 1 |
| 429, often with `Retry-After` | explicit rate limit, and they are telling you the number | ignore the header | Rung 1 |
| A normal page plus an injected sensor script and edge cookies (`incap_*`, `__cf*`) set on the first hit | not a block. It is notice that the **API behind this page** is defended even though the page is not | assume the next layer is as open as this one | Rung 4, and carry those cookies (Rung 3) |
| 200, small body, a mount point and a JS bundle (`<div id="root">`, `/assets/index-*.js`) | a single-page app shell. The records arrive after load | assume blocking; assume the URL matters | Rung 4 |
| 200, a rendered site whose record links point at another domain | a brochure. The data was never on this host | keep parsing this host | Step 1, re-target |
| 200, tiny body, no scripts, a `<meta http-equiv="refresh">` or a `location` assignment | a redirect stub. The real page is one hop away | parse this body for records | follow the target, then re-classify |
| 200, a body of a few dozen bytes that **is** the refusal (`Invalid Password`, `Not authorized`, `Missing parameter`) | not a block and not a defence. An endpoint that wants arguments you did not send | treat the 200 as success, or send it to Rung 4: there is no JSON twin behind a CGI | the parameter test below |
| 200, small body, a stock server welcome page (`IIS Windows Server`, `Welcome to nginx`) | a bare host or the wrong virtual host, not the application | read it as the site's answer | Step 1, re-target |
| A 2xx that is not 200, especially `202` with a near-empty body | not a success. Often an edge answering for an origin that did not, and frequently the site has moved | treat 2xx as "it worked" | compare `loadedUrl` with what you asked for, then Step 1 |
| 200, but fewer items than the browser shows | pagination cap, API limit, or a logged-out view | assume blocking | Rung 4 |
| 200 titled `Page not found`, with full site chrome | a soft 404 | trust status, headers or size; only content shows it | Step 1, the path is dead |
| Worked yesterday, empty today, no error | the site changed markup or endpoints | escalate proxies | Rung 4, re-inspect |

**The first two rows are one status code and two different situations.** A hard block and a managed challenge both arrive as `403` from the same CDN vendor, they route in opposite directions, and the header separates them. Both were measured on the same afternoon from one egress: a government portal answered a plain HTTP client with a bare `403` and no `cf-mitigated`, a vendor platform answered the same client with `cf-mitigated: challenge` and `Just a moment...`. **Your diagnostic Actor cannot see either header until you unblind it**, and until then both arrive as an empty item. The one-line fix is in "Making refusals visible" below; apply it before using this table.

**Name the edge before you use its marker, because `cf-mitigated` is one vendor's header and absence is not evidence.** On any edge that is not Cloudflare the header cannot appear, so "no `cf-mitigated`" is guaranteed and tells you nothing, while the rule that reads it happily returns "your address was judged" for every one of them. Identify the vendor from what did arrive:

| Edge | What identifies it | What separates hard block from challenge there |
|---|---|---|
| Cloudflare | `server: cloudflare`, `cf-ray`. Measured on a refusal: 4,560-byte body, `Sorry, you have been blocked` | `cf-mitigated` first, then the body. Present means a managed challenge; absent **plus a blocked-page body** means your address. Absent **with an interstitial body** is still a challenge: custom rules and newer challenge widgets do not all set the header, so let the body overrule it |
| Akamai | `Server-Timing: ak_p`, `X-Reference-Error`, a body naming `errors.edgesuite.net`. Measured on a refusal: 384 bytes, `Access Denied`, and **no `Server` and no `Via` header at all** | not `cf-mitigated`, which never appears here. Treat the refusal as unclassified and let a second egress decide |
| anything else, or unidentified | whatever `Server`, `Via`, `X-Cache` and `Server-Timing` do carry | unknown. Say so, and route by the second egress rather than by an absent header |

**A refusal is a measurement, not a property of the site, and some refusals expire.** The Akamai refusal above carried `Server-Timing: cdn-cache; desc=HIT` on a `403` whose own `Cache-Control` said `max-age=0`, meaning the error object was served from the edge cache and never reached the origin. Thirty-eight minutes later the same URL from the same address answered `302` and then `200` with 81,337 bytes, three times running. Nothing about the requester had changed. This is not a promise that refusals dissolve: an ASN or geo rule in a firewall is stable for as long as someone leaves it there, and re-measuring only confirms it. The point is the asymmetry of cost. One repeat request is free and it either upgrades a single observation into a stable fact or saves you a proxy purchase against a refusal that was never about you.

**The parameter test, for an endpoint that answers 200 by refusing you.** A missing argument and a credential you do not own look identical in the response, and they end in opposite places: one is Rung 3, the other stops the investigation at Step 0. Decide by where the value comes from, not by what it is called.

- **The site itself hands it out** to anyone who loads the page: a district code in a public dropdown, a build id in the HTML, a token the page fetches before its first search, a guest login printed in the UI. That is a parameter of a public route. Take it the way the page does, Rung 3.
- **It is issued to a person**, or it gates records the site does not otherwise publish. That is a credential you do not own, whatever the field is named. **Stop and say so**, and never guess, rotate or construct one.
- **Unsure after one look at the page that issues it?** Treat it as the second case and go to Step 0 to look for a published copy of the data. A source that requires an account almost always has a bulk or catalogue route that does not.

**The form test, for a full page that carries a form instead of records.** Server-rendered forms with hidden state are the default shape of government and utility record systems, and a GET-only crawler receives a valid `200` from one forever, with no error and no records. This is not the SPA shell row: there is no mount point and no bundle, the page is large, and the data is one POST away rather than one XHR away.

1. **Issue the POST the form describes**, carrying every hidden field it hands you (`__VIEWSTATE`, `__VIEWSTATEGENERATOR`, `__EVENTVALIDATION` and friends) plus the search field, with a `Referer` of the form page.
2. **Read where the answer goes.** If the response is a redirect to a URL carrying your query in its parameters, you have the record address rather than a session.
3. **Then test that address cold**, in a fresh client with no cookies and no `Referer`. This is the step that decides the whole job.

Measured on a county assessor's system: the form page answered `200` with 5,316 bytes and a `__VIEWSTATE`; the POST answered `302` to `.../ParcelDetail.aspx?hdnParcel=<key>&hdnInstance=pcl7`; and a cold `curl` of that URL, no cookies, no `Referer`, default user agent, answered `200` with 38,817 bytes of the actual record. One of the two redirect parameters turned out to be optional, so **strip parameters one at a time before you build them into a crawl**. A key the system does not know answered `200` with 747 bytes reading `No record found`, which is a third outcome to record rather than an empty row to drop.

When the cold GET works, the crawl collapses to one request per key, no browser, no session, no postback: fetch the keys from whatever Step 0 turned up and go straight to record URLs.

**Separating a shell from a brochure**, since both are a `200` with no data and the advice is opposite. Do not ask where a human would go; a human really does use the SPA's host. **Ask the body.** A shell is small, has a single empty mount element, loads a JS bundle, and returns the *same bytes and the same `ETag`* for different record ids. A brochure is a full rendered page whose record links point at another domain. Shell means stay, go to Rung 4. Brochure means the target is wrong, return to Step 1.

**Compare the URL you asked for with the URL that answered**, every time. Redirect chains cross domains silently, and a site that moved hosts is the cheapest diagnosis to miss. On one sweep `loadedUrl` was the only field that revealed a county assessor had moved onto the city's domain, behind a `202` that looked like nothing at all.

**`loadedUrl` only exists on a request that completed, which is the case this skill is about.** While every egress is refused you have no redirect chain and no way to see that two hostnames are one site, so two refusals from two different CDN vendors read as two independent targets and double your apparent problem. Two ways out, both cheap: compare the CNAME chains, or wait for the first egress that answers and read `loadedUrl` there. Measured: a `.com` hostname refused by Cloudflare and a `.gov` hostname behind Akamai turned out to be one site, and the `loadedUrl` from the egress that was admitted said so in one field.

Write down which row you are in. Every later decision depends on it.

## Step 3: change one thing about who is asking

**Test A, different client, same egress.** Fetch the same URL with a client that has a different stack; a real desktop browser is ideal, since it differs from a script in headers, TLS and JS execution at once. **If you have no browser sharing your egress, this test is unavailable.** Say so rather than substituting something that is not the same comparison.

**Test B, different egress.** On Apify that is an Actor run, not a one-line curl: write an input file, write a `pageFunction`, call the Actor, take the dataset id from the response, fetch the items. Budget a few minutes and a sub-cent run. The ready-made input is in [references/diagnostic-run.md](references/diagnostic-run.md).

| Test A (other client, same egress) | Test B (same client, other egress) | What it means | Next |
|---|---|---|---|
| works | blocked | your request looks wrong, your network is fine | Rung 2 |
| blocked | works | your network is the problem, not your client | Rung 1, and you already have the fix |
| blocked | blocked | **not a verdict yet.** Read the next paragraph before concluding anything | Rung 1, residential probe |
| works | works, but no data in the HTML | not a block at all, the data is rendered or fetched separately | Rung 4 |

**Test A moves more often than people expect, and it is free.** Measured on a state assessment portal from one hosting egress: a default HTTP client got `403` and a real desktop Chrome on the same address got the full page, same minutes. The `403` was about the client, not the address, and every proxy in the world would have been the wrong purchase. That page then printed terms forbidding automated collection, which is a Step 0 answer and not a Rung 1 one.

**Two refusals are not a verdict, and this is where people abandon reachable sites.** A hosting IP and a datacenter proxy are the same class of address to a WAF, so refusing both is one fact, not two. Before calling a site defended, spend **exactly one run** on a residential egress in the country the site serves. If residential from the right country is also refused, the site is genuinely defended and "How this ends" applies.

**That probe is billed traffic, so it is the one step to ask about rather than perform.** Residential is charged by volume and this skill exists to prevent buying it reflexively; running it unattended, on someone's account, to satisfy a diagnosis is the same mistake at a smaller scale. State what the probe would cost and what it would settle, then run it once when the answer is yes. Everything before this point is free or sub-cent.

**And prefer a free vantage point to a paid one whenever you have both.** If you can issue a request from a second network yourself, a plain `curl` from there answers the same question as an Actor run, immediately and at no cost, and it shows you the things a crawler hides: whether TCP connected at all, the raw headers, the body before any parsing. Spend the run when your only second egress is the platform's.

**When two same-class egresses disagree, stop before you buy anything.** The rule above expects a hosting IP and a datacenter proxy to be judged alike. When they are not, the rule being applied is not about the class of network at all: it is about your specific address or its immediate neighbours, and the fix is another datacenter egress, which is cheap and probably already in your account. Residential is the wrong purchase here, and this is where the reflex costs the most for the least.

Measured on one county's hosts, one afternoon, two egresses of the same class:

| Host | Hosting IP | Datacenter proxy |
|---|---|---|
| the GIS service | no response at all, 30 s timeout | `200`, the service directory |
| the file download page | `403`, a 399-byte `Access Denied` | `200`, 75 KB, the real page |
| the API host | `403`, CDN error page, no `cf-mitigated` | not attempted |

Three refusal shapes from one county on one egress, and none of them from the other. Note also that this is Step 1's host-and-path rule again: a silent timeout, a CDN block and a short `Access Denied` are three different mechanisms, and reporting "the county blocks us" would have hidden all three.

**With Test B alone**, the normal case for an agent: **B blocked** means run the residential probe before deciding anything, **B returns a body with no data** means Rung 4 regardless of what A would have shown, and anything needing A is unresolved rather than guessed. B also changes the network *and* the client stack at once, so when the two disagree you cannot attribute it to either until you hold one constant.

**A single outcome is not a rate.** Six identical requests to one vendor platform, one run, returned three clean pages and three refusals from the same proxy pool. Draw conclusions from a sample. The four-request worked example behind this whole section, where the answer was the network and residential bought nothing, and the sample size that makes a block rate countable, are both in [references/gotchas.md](references/gotchas.md).

## The ladder

Enter it only if Step 2 or Step 3 sent you here. Classification decides; the ladder only remediates, cheapest rung first.

**Rungs 1 to 3 are remediation you will recognise**, and each is a paragraph rather than a page here, with the settings and the traps in [references/rungs-1-3.md](references/rungs-1-3.md):

1. **Rate and IP spread.** Lower `maxConcurrency`, honour `Retry-After`, and run the residential probe Step 3 already described, once. Choose `proxyRotation` deliberately, because a stateful flow under `PER_REQUEST` looks far more suspicious than a steady crawler.
2. **Request fidelity.** Make your headers, their order and the `Referer` chain form one plausible client, and match `Accept-Language` to the proxy country. `curl -H` cannot control header order, so set them in `preNavigationHooks`. Below headers sits the TLS and HTTP/2 fingerprint, which no header work fixes: that layer means uTLS or curl-impersonate, or Rung 5.
3. **Tokens and edge cookies from a legitimate flow.** A build id, a CSRF or search token, a signed URL, or the cookies a WAF sets on first contact. Take it the way the page does, bind it to the session and address that earned it, respect its TTL. If Step 2 saw a sensor script on an otherwise clean page, carry those cookies into Rung 4.

### Rung 4: the site's own internal API

The highest-leverage rung, and the one most often skipped. The public HTML is the most defended, most fragile and least complete surface a site has. All four routes below work without a browser, which is why this rung comes first:

1. **State embedded in the HTML you already downloaded.** `__NEXT_DATA__`, `window.__INITIAL_STATE__`, `<script type="application/json">`, JSON-LD. Zero extra requests.
2. **The JS bundle the shell loads.** For a plain React or Vue app with no embedded state, fetch the bundle named in the shell and grep it for path literals: `/api/`, `/v1/`, `.json`, a bare hostname. The endpoint the app calls is a string inside that file. One request per bundle.
3. **Sitemaps, feeds and `.json` twins** of `.html` routes.
4. **A hosted search provider.** Sites often front their catalogue with one, and its endpoint returns clean structured records.

With a browser, devtools filtered to XHR is faster than all of the above; it is listed last because it costs a browser, not because it is worse. Payoff for the rung: usually faster, cheaper per record, more stable across redesigns, and less defended. It often removes the blocking problem instead of working around it.

**The HTTP Actor will not fetch the endpoint you just found unless you tell it to.** `apify/cheerio-scraper` supports `text/html` and `application/xhtml+xml` and **skips every other content type**, which is exactly the JSON this rung exists to reach. The field that fixes it is:

```json
{ "additionalMimeTypes": ["application/json", "text/plain"] }
```

**Measured trap: that field is currently not accepted through the MCP `call-actor` tool at all**, and its error message sends you hunting in the wrong place. An array is rejected with `Validation errors: must be object`, the same array as a JSON string is rejected the same way, and an object is rejected with `must be array`, while the Actor's own build schema declares the field `"type": "array"`. Everything else in the diagnostic input goes through untouched, including `preNavigationHooks`, `maxRequestRetries: 0`, `maxConcurrency`, `pageLoadTimeoutSecs`, a `customData` object and a `pageFunction` full of backslashes, so this is one field rather than your escaping. Three ways past it, cheapest first:

- **Ask the endpoint for HTML.** An ArcGIS or Socrata service answers `f=html` or a browsable catalogue page with the same content, and that route measured `200` through the Actor on a host whose JSON form the Actor would have skipped. Good enough to diagnose, not what you want in production.
- **Fetch it with your own code.** A paginated JSON endpoint is a loop over `resultOffset`, not a crawl: there are no links to follow and no HTML to parse, so twenty lines beat any crawler Actor and the MIME question disappears.
- **Run the Actor from somewhere other than the MCP tool** if you have the Console or the CLI. Not tested here, so verify before you count on it.

### Rung 5: browser, last

**A browser is not automatically the stronger client.** Measured on one vendor platform, same URL, same proxy pool, one minute apart: the browser Actor got a hard block page while the plain HTTP Actor got a managed challenge twice and a clean `200` on the third request. Confirm a browser buys you something before you buy one. It costs about twelve times the HTTP Actor per page, and it demands approval of full account access in the Console before its first run, which stops an unattended flow dead.

**A Crawlee-based browser Actor will not wait out a challenge by default:** it aborts on the challenge's `403` before the page can clear, which is the one thing a browser was supposed to be for. Unblind it exactly as below, then wait for the interstitial to disappear inside your `pageFunction`. Numbers and the Chrome comparison: [references/gotchas.md](references/gotchas.md).

**Coherence rule.** Proxy country, `Accept-Language`, timezone and browser profile must agree. An incoherent profile is not stealth, it is a slower way to get blocked at browser prices.

## How this ends

Most investigations end without touching the ladder. All of these are finished results, not failures:

- **The cause is named and it is not a block.** A dead path, a stale URL, an SPA whose records come from an endpoint, data published in a feed. Write down the cause, the egresses you measured from, and the next concrete step.
- **The cause is named and it is a block you fixed.** Record which single change moved it.

Stop and tell the user when:

- The host does not resolve, the path is gone, or the data is not on this host. Re-target rather than unblock.
- The terms of the source forbid this collection. Say so at Step 0 rather than after a fix.
- **A hard block survives residential from the country the site serves.** That is the cheap stop, and it comes after one run rather than after a browser. A managed challenge is the other case: it earns one browser run first, because it is built to clear. On a Cloudflare edge `cf-mitigated` tells you which of the two you have; elsewhere, use the residential result itself as the discriminator rather than an absent header.
- Browser plus residential plus a coherent profile is still blocked. Cost per record now dominates; look for an official API, a data licence, or another source.
- Over a real sample, three rungs produced no change in block rate. The diagnosis is wrong, not the tooling.
- Cost per successful record exceeds what the record is worth. Compute it.
- The block is a login wall or a paywall.

Once a source is in production, track its failure rate and alert on it. A source that quietly degrades still produces something that looks like a dataset, and you want to hear about it from a graph rather than from a hole in the data.

## Actor routing

| User need | Actor ID | Tier | Best for |
|---|---|---|---|
| Plain HTML, no JS needed, cheapest per page | `apify/cheerio-scraper` | apify | Steps 1-3 and Rungs 1-4, the default starting point |
| Full browser, page function, Chrome | `apify/web-scraper` | apify | Rung 5, client-side rendering |
| Full browser with Playwright control | `apify/playwright-scraper` | apify | Rung 5, complex flows |
| Full browser with Puppeteer control | `apify/puppeteer-scraper` | apify | Rung 5, existing Puppeteer logic |
| Whole-site text extraction for AI pipelines | `apify/website-content-crawler` | apify | content harvesting, not field-level extraction |

Full table with the inputs that matter when blocked: [references/actor-index.md](references/actor-index.md).

## Calling Actors

**Through the Apify MCP server**, which is how an agent normally reaches the platform: `call-actor` with the Actor name and an input object, then `get-dataset-items` with the id from the reply. There is no input file and no shell redirection in this path, and the id you need is at **`storages.datasets.default.id`**, not `defaultDatasetId`. Do not paste the CLI's flags into MCP arguments; they are not parameters of these tools.

Two traps in that reply, both measured. The **item count is read while the run is still flushing and undercounts**: four runs on four different days reported `1` against six stored items, `4` against six, and `3` against four, so read the dataset before concluding how many items a run produced. And **`Validation errors: must be object` does not name the field it means, and its wording points away from the cause**: the same rejection appears for a valid array (`must be object`) and for an object in that same field (`must be array`). Do not go looking for your own escaping. Submit the small input from [references/diagnostic-run.md](references/diagnostic-run.md), which validates as a whole, then add fields one at a time; the known offender is `additionalMimeTypes`, see Rung 4.

**Through the CLI**, if you have one, the call takes an input file and the reply names its storages differently (`storage.defaultDatasetId`, not `storages.datasets.default.id`). Commands and flags: [references/actor-index.md](references/actor-index.md).

### Making refusals visible

**Your diagnostic goes blind on exactly the case you are diagnosing.** Crawlee treats 401, 403 and 429 as blocking and throws `Request blocked - received 403 status code.` before your `pageFunction` runs. The item reaches the dataset with **no fields of yours at all**: no status, no headers, no body, nothing to classify with. Both the HTTP Actors and the browser Actors do this, and the two rows Step 2 opens with are precisely the ones you cannot tell apart in that state.

Put this in `preNavigationHooks` and the refusal arrives as data instead:

```json
{
  "preNavigationHooks": "[async ({ session }) => { if (session) { const retire = session.retireOnBlockedStatusCodes.bind(session); session.retireOnBlockedStatusCodes = (code, extra) => { retire(code, extra); return false; }; } }]"
}
```

It still retires the blocked session, so the pool keeps rotating away from bad addresses, but it stops the throw, so the response reaches your code. Measured over six identical requests to a challenged platform, this took a run from three classified refusals out of six to six out of six, while the variant that skips the retire call sees everything and gets nothing through. The comparison table and the diagnostic `pageFunction` that uses it: [references/diagnostic-run.md](references/diagnostic-run.md).

**There is no fallback field to read instead, and this is worth stating because `#debug.statusCode` looks like one.** It is present on requests that completed, so a run full of `200`s will show it and give you the wrong impression of what you have. Measured on a run without the hook against a platform that refuses: two items, `#error: true`, `#debug.retryCount: 0`, and the entire field list was `#error`, `#debug.requestId`, `#debug.url`, `#debug.method`, `#debug.retryCount`, `#debug.errorMessages`. No status, no headers, no body. If you took the run without the hook, you have the fact that something failed and the message Crawlee threw, and you must re-run to classify.

**This is a diagnostic switch, not a crawl setting.** Take it out once you have classified the refusal, or your crawl will happily write challenge pages into your dataset as if they were records.

**Why a hook and not a setting.** Crawlee the library does expose this behaviour through session pool options, but you are not calling the library, you are filling in an Actor's input, and that input does not carry them. Measured against the published build schema of `apify/cheerio-scraper`: 30 input fields, and `sessionPoolOptions`, `blockedStatusCodes`, `additionalHttpErrorStatusCodes` and `gotOptions` are absent from all of them; the only session-related field is `sessionPoolName`. `preNavigationHooks` is the one field that hands you a live session object, which is why the fix lives there.

**It does reach into internals, so treat it as version-bound.** `retireOnBlockedStatusCodes` is a session method rather than a documented input, and an upgrade can rename or restructure it with no error on your side. The failure is silent and recognisable: refusals go back to arriving as items with no status and no headers, exactly as described above. Check that field before blaming the site. The setting people try first does not do this job, measured: `gotOptions.throwHttpErrors = false` left one classified refusal out of six, against six out of six with the hook.

## Troubleshooting

- **A target is missing from your dataset, or items arrive empty** → Crawlee threw before your code ran. Add the hook from "Making refusals visible", then classify.
- **403 and you cannot tell a hard block from a challenge** → name the edge first. On Cloudflare `cf-mitigated` decides it. On any other edge that header cannot appear, so its absence is not an answer and the refusal stays unclassified until a second egress speaks.
- **A refusal that will not reproduce an hour later** → a cached edge error or a rule that has since gone. Check for `cdn-cache` in `Server-Timing` on the refusal itself, and re-measure both egresses inside one minute before you conclude anything.
- **A 200 carrying a full page, a form and no records** → the form test in Step 2. Issue the POST, then check whether its redirect target answers a cold GET.
- **Your two vantage points return the same address** → they are one egress. Compare `query` from the egress check on each machine before treating them as independent.
- **Your resolver answers `198.18.x.x`** → your own proxy client in fake-ip mode, not the site. Re-resolve over DoH.
- **Your hosting IP is refused and a datacenter proxy is not** → your specific address, not its class. Change datacenter egress, do not buy residential.
- **A 200 whose whole body is `Invalid Password` or `Not authorized`** → a missing argument or a credential. Apply the parameter test in Step 2.
- **The JSON endpoint you found comes back empty through the Actor** → `apify/cheerio-scraper` skips non-HTML, and `additionalMimeTypes` is currently rejected through MCP whatever you encode it as. Ask the service for `f=html`, or fetch the endpoint with your own code.
- **No status, no headers, no body** → Step 1, and check your own vantage point first.
- **A non-routable address from your own resolver, but traffic works** → transparent interception. Proceed, mark the vantage point confounded, require Test B before any verdict.
- **0 items, run succeeded** → read `SDK_CRAWLER_STATISTICS_0`; a green run proves nothing.
- **403 with an XML body naming a storage service** → a missing object, not a defence. The path is dead.
- **403 from two datacenter or hosting egresses** → not a verdict. One residential run before you conclude.
- **A guessed portal hostname answers 200** → confirm the records name that host before building on it.
- **Intermittent 403, or a failure that takes the same number of seconds every time** → look at concurrency and at configured timeouts, not at fingerprints.
- Detailed traps and recovery: [references/gotchas.md](references/gotchas.md).
