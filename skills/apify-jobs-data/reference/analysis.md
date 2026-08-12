# Market & Salary Analysis — apify-jobs-data (Step 6)

Compute job-market statistics from the clean, normalized rows produced in Step 5.
**Every figure reports the share of postings it is computed from** — coverage is
mandatory, because field coverage varies by board and many postings omit salary.

## Input

The normalized rows (schema in [output-formats.md](output-formats.md)). A larger sample
makes the statistics meaningful — raise the result cap (anchor #4) for analysis runs,
and prefer the aggregator so the sample spans many boards.

## Aggregations

### Hiring demand
- Count of **distinct, de-noised** postings (ghosts and duplicates already removed —
  this is why de-noise matters: it's the difference between real demand and a board's
  inflated count).
- Break down by company (top employers hiring for the role), location, seniority, and
  `job_type`. Report **counts**, not just percentages.

### In-demand skills
- Take each posting's `skills` field where present; otherwise parse the JD text against
  a skill vocabulary (languages, frameworks, tools, certifications).
- Rank by frequency, reported as "X% of postings mention <skill> (N of M)".
- Distinguish must-have vs nice-to-have phrasing where the JD separates them.

### Salary distribution
- Use disclosed salary min / max / currency from the normalized rows.
- Normalize currency and period (annual vs monthly vs hourly) **before** aggregating;
  separate or drop rows you cannot normalize, and say how many.
- Report min / 25th / median / 75th / max, split by seniority and location where the
  sample supports it. Flag any cell with **< ~5 data points** as too thin to trust.
- **Coverage is mandatory:** "median €95k, from the 41% (52/126) of postings that
  disclosed a figure". Never present a salary statistic without the disclosed share.
- Optional cross-check: `memo23/glassdoor-scraper-ppr` salaries for the same role, to
  compare posted bands against Glassdoor estimates — label each source separately.
- **Cost-quality note:** disclosure is low, so do **not** scale the scrape just to
  harvest more disclosed salaries — that burns money for a few extra figures. When the
  posted sample is thin, lean on the Glassdoor benchmark (one cheap per-company call)
  instead of a mega-scrape. Scrape only as much as the demand/skills analysis needs.

### Remote / hybrid mix
- Share of postings remote / hybrid / on-site, from the normalized remote flag plus JD
  signals. Report coverage.

## Grounding rules

- Every number traces to scraped rows; state the N and the coverage share.
- A thin sample is a **finding**, not a gap to paper over — say "only 12 postings
  matched, too few for a reliable salary distribution" rather than computing a shaky
  median.
- Don't infer a trend from a single run — this skill takes one snapshot per run.

## Output

A short report: a demand headline, a top-skills table, a salary-distribution table
(each cell with its coverage), and the remote mix — every figure carrying its N. The
underlying normalized rows go to the file (export mode) so the user can re-aggregate
themselves. Rendering details: [output-formats.md](output-formats.md).
