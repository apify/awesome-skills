# Gate, rank, and deliver

## Gate first (drop or set aside)

Check every candidate row against the confirmed signature before ranking anything.

1. **Job family.** Drop rows outside the family: a "Member of Technical Staff (DevOps)" is not an AI researcher, and a "PhD Research Scientist Intern" is not a mid-senior hire.
2. **Level.** Allow one step up or down. When the title is ambiguous, read the years and scope in the description.
3. **Location rule.**
   - Google Jobs treats a city as a region hint. A "Denver, CO" search returned rows 100 to 200 miles away, so measure the distance yourself.
   - A bare "Remote" is region-unverified. Keep it, but list it in its own group under the in-area rows.
   - Honor hard gates such as US citizenship.
4. **Agency and contract reposts.** Set these aside as "agency" rather than ranking them.
5. **The exemplar itself.** Exclude its own requisition and its reposts.

Rows that fail the gate on family or level go into a short "adjacent" list. Never quietly mix them into the ranking.

## Rank what survives

Read each posting's full text. A keyword count is not enough: a skill named once in a benefits list does not count.

1. **Must-have overlap:** how many of the signature's must-haves the posting actually requires.
2. **Status:** "open on employer's board" ranks above "aggregator only" when overlap is equal.
3. **Recency:** newer first, from the board's own posted date when available. Open is not the same as fresh: boards keep evergreen requisitions live for months (a Cohere posting first published in 2024-11 was still listed in testing). Show the posted date and mark anything older than 90 days "long-running".
4. **Pay overlap:** only when both the exemplar and the row state a range. A missing range is unknown, never a mismatch.

Give each row one reason that quotes or paraphrases the posting, for example "requires reward models and RL post-training, same as your exemplar".

## Deliverable

Start with one coverage line:

> Searched Google Jobs (N pages), LinkedIn similar jobs (N), Ashby (N employers matched), and Workday (N sites). N raw rows; N passed the gate; N duplicates removed; N shown. N are confirmed open on the employer's board. Failed: (names, or none). Cost $X (run ids below).

Then a table of up to 10 rows:

| # | Title | Company | Location | Why similar | Status | Posted | Apply |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | one line | Open on employer's board (R-0407372) | 4 days | employer link |

After the table:

- **Remote, region unverified:** rows that only say "Remote", as their own short list.
- **Adjacent:** the rows that failed the family or level gate, in case the user wants to widen the search.
- **Agency:** staffing and contract reposts, if the user wants them.
- **Failed sources:** each one named, with what was tried. A source that returned zero while the others returned rows is failed until a control query proves otherwise.
- **Run ids and cost:** every run, with its cost.
- **Handoffs:** offer `apify-jobs-data` for resume fit and `apify-job-boards` for daily alerts.

Never invent a posting, a salary, a date, or an id. Leave missing fields blank.
