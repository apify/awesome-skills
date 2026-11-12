# Exemplar and role signature

The exemplar is the one job the user loves. Everything downstream is measured against it, so read it once, carefully, before spending anything.

## Resolve the exemplar

- **LinkedIn job URL:** LinkedIn job search in job mode, with the URL in `jobUrls`.
  - The row carries the full description, the seniority, any salary, and two seed lists: `similarJobs` (about 27 on a typical posting) and `peopleAlsoViewed` (about 10). Both are jobs, not people.
  - `similarSearches` is usually off-family noise. Ignore it.
  - `fromCache: true` is normal. Records are reused for up to 7 days, and there is no input that forces a fresh read. Use the text, but never use the row as proof the job is open.
- **Ashby, Greenhouse, JazzHR or iCIMS job URL:** pass the URL to that board's Actor. These accept a single job URL and return the posting.
- **Workday or Oracle job URL:** these expand a job URL to the whole site. Use the site URL with the job title as the text filter and a small per-site cap, then pick the matching requisition.
- **Any other URL, or a page that cannot be read:** ask for the pasted text.
- **Pasted text:** use it as given. If the posting has expired, ask for the text; never rebuild a description from a title.

## Build the signature

Write it as one short block and wait for the user to confirm or edit it.

- **Title family and variants.**
  - Keep 2 or 3 variants inside one job family. "Member of Technical Staff, AI Researcher" gives "AI research engineer" and "research scientist, evaluations".
  - A variant never crosses into a different function. "Product Manager" is not "Product Marketing Manager", and a clinical "Nurse Manager" is not a staffing "Travel Nurse RN".
- **Level.** One step up or down at most. Read it from the stated years and scope, not only the title: "5+ years", "Mid-Senior", "owns the roadmap". Interns and new-grad roles never match a senior exemplar.
- **Must-haves.**
  - Up to 5, taken from the requirements section: "Strong Python skills", "reward models, automated verifiers, graders".
  - Ignore the boilerplate (benefits, equal-opportunity text, data-processing notices).
- **Domain.** The industry or problem space, in a few words, for example "frontier AI evaluations for regulated industries".
- **Location rule.**
  - Record the city and an acceptable distance, or "remote in country X".
  - Record any hard gate the posting states, such as US citizenship or a clearance. A posting that requires US citizenship rules out roles that are only open abroad.
- **Pay floor.** Use the user's figure if they give one. Otherwise note the exemplar's range ("$250,000-400,000 + equity") as context, not as a filter.
- **Recency window.** Default to the last 30 days, or 7 for fast-moving tech roles.

## Example (from a live run)

Exemplar: "Member of Technical Staff, AI Researcher (New Stealth Startup)", Red Cell Partners, United States, Mid-Senior, posted 21 hours earlier.

- **Family:** AI research engineering. Variants: "AI research engineer", "member of technical staff AI researcher".
- **Level:** mid-senior, 5+ years.
- **Must-haves:** Python; model evaluations and benchmarks; RL and post-training; reward models, verifiers and graders; AI agents.
- **Domain:** AI evaluations for healthcare and government.
- **Location:** United States. Citizenship required, so drop roles that are only open in Paris, Poland or India.
- **Pay context:** $250,000-400,000 plus equity. **Recency:** 7 days.

Turn the signature into inputs only after the user confirms it. Each title variant becomes one bounded Google Jobs page. The title keywords and location keywords become the sweep filters (see join-and-verify.md).
