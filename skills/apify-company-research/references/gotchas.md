# Company research: failure modes, field coverage, cost traps

## Registry search (`extractlyspace/company-registry-search`)

- At least one of `names` and `registryIds` is required. Neither gives an `invalid_input` row with an example. Limits: 20 names, 50 numbers.
- A name is searched in every selected registry (`countries`: `gb`, `fr`, `no`, `fi`, `cz`, `lei`). Narrow `countries` to the markets that matter; each extra registry can add up to `maxResultsPerSource` paid rows per name.
- A name search keeps a company only if every word of the query (ignoring accents, one-letter words and legal forms such as SA, Ltd, AS, Oy) starts a word of its name. Dropped matches are not charged. Short generic names return many rows; use the registry number once known.
- A nine-digit number can be a French SIREN and a Norwegian org.nr and returns one row for each that exists. UK numbers accept prefixes (`SC123456`) and short numbers are padded.
- `no_results`: `No company named "NAME" in REGISTRY.` One row for each name and registry. Fix: check spelling, search by number, or add the registry. With `activeOnly` the message says the companies found are not active; set `activeOnly` to false to see them.
- `not_found` (numbers): `No company with registry number NUMBER in REGISTRY.` Fix: check the number or search by name.
- `partial`: a registry did not answer, or GLEIF did not answer so `lei` is empty. The other rows are delivered. Run again later. The UK key is shared by all users of the Actor, so the UK part can be the one that fails under load.
- `unavailable`: UK lookups are not available in this build. The other registries still work.
- Only companies with a LEI are in GLEIF. A missing `lei` on a registry row means no LEI was found, not that the company does not exist.
- `legalForm` is written out where the registry has a code table (`Allmennaksjeselskap (ASA)`) and may be a registry code elsewhere (`3220`, `DKUW`). `industryCode` is the registry's own scheme: SIC in the UK, NAF in France, NACE in Norway and Czechia, TOL in Finland. UK search rows have no SIC code; a lookup by company number does.
- For sole traders, address, postal code and city are left empty on purpose.
- What it never returns: officers, directors, shareholders, beneficial owners, phones, emails, birth dates. If the user needs them, say that this skill cannot provide them.
- Not a credit check. `status` is `active`, `dissolved` or `unknown` (the registry does not say).
- Keep the source attribution lines of the registries when republishing the data; they are in the Actor's README.

## Jobs (`extractlyspace/company-jobs-scraper`)

- Best input: a job board URL (`https://jobs.lever.co/spotify`), then the company's website domain (`stripe.com`), then a plain name. A name is matched by the job board's company name; if several boards carry it, a free `not_found` row lists them with URLs. Send one of those URLs.
- `not_found` for a domain: the site answers but links no supported board, or no website answers at that address. Send the job board URL, or check the address.
- `unsupported`: Workday career sites currently answer automated requests with a bot check (since November 2026), and Greenhouse EU boards (`boards.eu.greenhouse.io`) are not supported. Report these companies as not covered; do not retry in a loop.
- `partial`: a board stopped answering. The jobs read so far are delivered. Run the same company again later.
- A page on another company's site (a directory profile) is not the company's own site. Send the company's own domain.
- At most 100 companies per run; the same board named twice is delivered once.
- Field coverage differs by hiring system. Country is missing for Greenhouse and Personio; salary is only present when the company publishes pay; `isRemote` is known for Greenhouse and Personio only when the location text says "remote". Consequences: `locations` with a country matches the job's country, else whole words of the location text, so a Greenhouse job in "Berlin" is not matched by "Germany". `remoteOnly` drops jobs of unknown remote status. `postedWithinDays` drops jobs without a posting date.
- `onlyNew`: the first run returns every open job up to the limit; later runs return only jobs not returned before. The Actor remembers them in a key-value store named `company-jobs-scraper-seen` in the caller's own Apify account. Use it for scheduled checks, not for a one-off question.
- Hiring signal reading: a count of open roles in a function is a signal, not proof of a budget. Report the roles and their posting dates, and let the user judge.
- Never returns recruiters, hiring managers or applicants. Descriptions have email addresses and clearly formatted phone numbers removed. `description` is cut at 20,000 characters.

## Luma events (`extractlyspace/luma-events-scraper`)

- To list what one company hosts, give its Luma calendar page in `calendarUrls` (for example `https://lu.ma/llmlondon`). Event links go in `eventUrls`. `cities` returns events in and around a city, not by company; use it only when the question is about a place or topic.
- `categories` needs `cities`. Values: family, books, games, tech, food, ai, running, arts, climate, fitness, wellness, crypto.
- `no_results` with a calendar URL: the calendar has no upcoming events. Many company calendars are empty most of the year. Say so; do not widen to a city to fill the answer.
- `not_found`: the city, category or link does not exist on Luma. `invalid_input`: no source, `categories` without `cities`, a malformed date, or `dateFrom` after `dateTo`. Dates are `YYYY-MM-DD` and compared by UTC day.
- `partial`: one source could not be reached; the others are delivered.
- Cost trap: `includeOrganizerDetails` is on by default and adds $0.003 per event that has organizer data, three times the price of the event itself. Turn it off when only the event list is needed.
- Organizer data is the organizer's name, Luma page, website, public X, LinkedIn and Instagram links, and the host names shown on the public event page. `guestCount` is a public number. Guest lists, attendee data, emails and phone numbers are never returned, and addresses Luma shows only to registered guests are `null`.

## Google Sheets (`extractlyspace/google-sheets-sync`)

- Setup, once per sheet: share the sheet with `sheets-sync@monday-brief-507421.iam.gserviceaccount.com` (Editor to export, Viewer to import) and add a tab named `apify-<your Apify user id>` (it can be empty and hidden; the user id is in Apify Console under Settings). Without the tab the run returns `not_shared` and names the exact tab to add. Do not skip this by sharing the sheet publicly for export.
- A sheet that anyone with the link can view imports without either step if the URL has `#gid=` and `sheetName` is empty. Export never works that way.
- Do not name an ordinary tab `apify-<user id>`; that name is refused with `invalid_input`.
- Export needs exactly one of `datasetId` and `rows` (up to 1,000 rows). `upsert` needs `keyColumn`, and the key must be one of the written columns. Use the registry number (`registryId`) or `jobId` as the key.
- `append` after a timeout can write the same rows twice on a repeated run. Set `keyColumn` and rows already in the sheet are skipped.
- `replace` clears the tab first. If the spending limit cannot pay for every row, the tab is left unchanged; if Google's quota stops the run after the clearing, the tab can be left empty and the status row says so.
- Import returns every value as a string, including numbers and booleans. Empty cells are empty strings. An empty or repeated header cell becomes `column_3` or `name_2`.
- `not_found`: the spreadsheet, tab or dataset does not exist; the message lists the tabs of the sheet. `too_large`: the export would pass Google's limit of 10 million cells. `partial`: Google's quota ran out; what was written stays; run again in a minute.
- Never paste a Google credential or an Apify token into a sheet or a command. The Actor needs neither.

## Cost guardrails

- Registry: `names x registries x maxResultsPerSource x $0.002`.
- Jobs: `companies x maxJobsPerCompany x $0.0015` (x $0.0025 with `includeDescription`). Descriptions need one extra request per job on some systems; use them only for a short list.
- Luma: `maxEvents x $0.0045` with organizer details.
- Sheets: $0.00002 per row.
- A list of 100 companies through all four steps with the defaults can pass $10, almost all of it in jobs. Ask the user before running jobs for the whole list; run it on the shortlist.
- When the caller's spending limit is reached the run stops and adds a `limit_reached` row with the delivered count. Report it as a partial result.
