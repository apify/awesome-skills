---
name: apify-dependency-health-check
description: Use when the user asks to check a dependency list before a release or audit, to find abandoned, yanked or unlicensed packages, to confirm a package name an AI assistant suggested really exists, or to build a licence and repository table for a Rust, Go, Java, .NET, PHP or Ruby project. Covers crates.io, Go modules, Maven Central, NuGet, Packagist and RubyGems. Returns plain rule flags per package, not a score. Does not cover npm or PyPI.
author: leadharbor
author_url: https://apify.com/leadharbor
metadata:
  category: developer-tools
  keywords: "dependency check, package health, abandoned packages, yanked, deprecated, licence audit, crates, go modules, maven, nuget, packagist, rubygems, hallucinated package, slopsquatting"
---

# Dependency health check with Apify

Check whether packages exist, how old their latest release is, whether the registry marks them yanked or deprecated, and which licence and repository the registry lists. One dataset row per package, six registries.

Disclosure: the routed Actor `leadharbor/package-registry-health` is built by this skill's author and is paid (pay per event).

## Example prompts

Prompts this skill handles:

- "Here is our Cargo.lock and go.mod. Which dependencies have not shipped in two years or are yanked?"
- "Before I add `swiftmailer/swiftmailer` and `rubygems:nokogiri`, do these packages exist and are they maintained?"
- "Make me a spreadsheet of licences and repository URLs for these 40 NuGet and Maven packages."

Out of scope (the boundary):

- "Scan my npm or PyPI dependencies." npm and PyPI are not covered by this Actor. Say so and do not substitute a guess.
- "Is this package safe or free of vulnerabilities?" The Actor reports registry metadata only. It does not scan code or CVEs, and a quiet package can still be fine.

## Prerequisites

- Apify account ([sign up](https://apify.com))
- Authentication via `apify login` or the `APIFY_TOKEN` environment variable (never put a token in a URL)

## Workflow

1. **Normalise the list.** Turn each dependency into `ecosystem:name`. Ecosystems: `crates`, `go`, `maven`, `nuget`, `packagist`, `rubygems`. Go uses the module path (`go:github.com/google/uuid`), Maven uses `groupId:artifactId` without a version, Packagist uses `vendor/package`. Drop npm and PyPI entries and tell the user they were skipped. Up to 1000 packages per run.
2. **Fetch the live input schema** before building input; do not rely on this file for field names:

       apify actors info "leadharbor/package-registry-health" --input --json \
         --user-agent apify-awesome-skills/apify-dependency-health-check 2>/dev/null

3. **Estimate and confirm cost** when the list is larger than about 500 packages. See Cost below. Crates are slow by design (about 1.1 s per crate).
4. **Run it** (see the command below), then read the rows.
5. **Report per package.** Read `status` first. Only `ok` rows have registry data; list `not_found` rows as "does not exist" and `error` rows as "could not be checked, retry". Group the `ok` rows by `flags`. Sort by `position` to keep the user's order.

## Actor routing

| User need | Actor ID | Tier | Best for |
|-----------|----------|------|----------|
| Existence, latest version, release age, yanked or deprecated, licence, repository, downloads across six registries | `leadharbor/package-registry-health` | community | Dependency audits, release checks, AI-suggested package names |

`Tier` = `apify` (Apify-maintained, prefer) or `community` (third-party).

## Calling the Actor

    apify actors call "leadharbor/package-registry-health" \
      -i '{"packages": ["crates:fastrand", "go:github.com/google/uuid", "maven:com.google.guava:guava", "nuget:Serilog", "packagist:swiftmailer/swiftmailer", "rubygems:rake"]}' \
      --json \
      --user-agent apify-awesome-skills/apify-dependency-health-check \
      2>/dev/null

Fetch the rows:

    apify datasets get-items DATASET_ID --format json \
      --user-agent apify-awesome-skills/apify-dependency-health-check 2>/dev/null

The same input works through the Apify MCP connector (<https://mcp.apify.com>) or any MCP client.

## Output fields

Every row has the same keys: `status` (`ok`, `not_found`, `error`, `invalid_input`), `exists` (`true`, `false`, or `null` when unknown), `latestVersion`, `latestReleaseDate`, `daysSinceRelease`, `deprecatedOrYanked` (`null` when the registry data could not be read, and always `null` for RubyGems), `deprecationNote`, `license`, `licenseSpdx`, `repositoryUrl`, `homepageUrl`, `downloads` (`null` for Go and Maven), `flags`, `warnings`, `source`, `error`, `errorKind`, `position`, `input`, `checkedAt`.

`flags` are plain rules, not a health score: `no-release-in-24-months`, `latest-version-yanked-or-deprecated`, `license-missing`, `repository-missing`, `no-listed-version`. Quote the flag and the field behind it; do not invent a verdict.

## Cost

Pay per event: `package-checked`, $0.0008 per package at the free-plan price (lower on paid Apify plans; read the live price from the Store page). Only definite answers are charged: `ok` and `not_found` rows. `error` rows, `invalid_input` rows and duplicates are not charged. Example: 250 packages with 240 found, 6 missing and 4 timeouts is 246 charged, about $0.20.

## Troubleshooting

- `errorKind: registry_unavailable`: the registry failed repeatedly and the rest of its packages were skipped. Re-run only those packages later.
- `errorKind: rate_limited` or `timeout`: retry just the failed rows; they were not charged.
- `invalid_input`: the entry was not `ecosystem:name`. Fix the spelling or the ecosystem prefix.
- Go rows never raise `license-missing` and have `licenseSpdx: null`, because the Go proxy serves no licence data. Say "not available", not "no licence".
- For cost guardrails and recovery details, see [references/gotchas.md](references/gotchas.md).
