# Join the lanes and confirm what is open

Aggregators give breadth; employers' own boards give truth. A row is "open" only when an employer board returned it in this run.

## Where confirmed rows come from (in order of yield)

1. **LinkedIn seeds to Ashby.**
   - Take the employers in the exemplar's `similarJobs` and `peopleAlsoViewed`.
   - Run them through the Ashby Actor's `companies` input (company names are matched to boards), with the signature's `titleKeywords`.
   - In testing, 12 of 37 employers resolved, and all 12 had the exact titles live. The rest use other systems; their rows stay "aggregator only" unless another route below confirms them.
2. **Lane A employers to Workday, Oracle or iCIMS.**
   - For each strong Google Jobs or LinkedIn row, normalize the employer to the parent organization ("AdventHealth University" is AdventHealth).
   - Resolve it with the Workday career-sites Actor, the Oracle Actor's `companies`, or iCIMS `companies`.
   - Then pull with `searchText` (Workday, Oracle) or `keywords` (iCIMS) set to the row's title words, and a small `maxJobsPerSite`.
   - In testing, a Google Jobs row reached only through aggregator links was matched to AdventHealth's Workday requisition R-0407372, posted 4 days earlier, for half a cent.
3. **Title sweeps for employers lane A never showed.**
   - Ashby and Greenhouse sweep their largest boards when `companies` is empty. JazzHR searches its whole platform.
   - Always pass the signature's location keywords and a per-employer cap. Without them, 18 of 40 billed rows were in the wrong country, and two employers filled 22 of 40 slots.
4. **Google Jobs apply links.**
   - When an `apply_options` link points at a routed board, fetch that job directly.
   - This happened on 1 of 30 rows in testing, so treat it as a bonus, not a strategy.

## Matching a row to the employer's board

- **Strong match:** the employer board returns the same title (normalized for case and punctuation) at the same location or facility. Keep the board's own id (`jobReqId`, `requisitionId`, `id`) and its apply URL.
- **Location wording differs by board.** Workday often gives a facility name ("ADVENTHEALTH LITTLETON") rather than a city and state. Compare against the facility's city before calling a mismatch.
- **Several titles match:** keep the one at the exemplar's location, and list the others as related openings at that employer.

## Labels

- **Open on employer's board:** returned by the board in this run. Show the board id and the posted date.
- **Likely closed:** the board answered with jobs for that employer, but not this title. Say what the board did show instead.
- **Aggregator only:** no routed board covers this employer, or the lookup failed. It may still be open; say so plainly.
- **Agency:** a staffing-agency or travel-contract repost ("Travel Nurse RN - Nurse Manager - $1,984 to $2,137 per week"). Keep these out of the ranked list and offer them separately.

## Dedupe

- Decode each Google Jobs `job_id`. It is base64 JSON holding `htidocid` plus the title and company. Key listings on `htidocid`, because the raw `job_id` embeds the search and differs between queries for the same listing.
- One requisition can still appear twice under different `htidocid` values when it comes through two boards; in testing, the same nursing job arrived via Indeed and via Glassdoor. Use company plus title plus location to flag "possible duplicate", and merge only when an employer-board id ties the two rows together.
- Across lanes, a Google Jobs or LinkedIn row and an employer-board row merge when the board confirms the match above. The merged row keeps the board's apply URL.
