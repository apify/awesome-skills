# Actor routing table: Clutch.co company data

The Actor `johnvc/clutch-agency-api` has three modes. This skill uses `profiles`.
Pick the mode by the job:

| Job | Mode | Key inputs | Row type returned |
|-----|------|-----------|-------------------|
| Full record for specific companies you already know | `profiles` | `profileUrls` (URLs or slugs), `includeReviews`, `outputFormats` | `profile` (+ `review`) |
| Build the list of companies in a category or location | `directory` | `directoryUrls`, `maxPagesPerDirectory` | `listing` |
| Find companies by keyword, then pull them | `search` | `searchQueries` | `profile` |

For directory mode (collecting a whole agency list), use the companion skill
`apify-marketing-agency-database`, which is shaped for that outcome.

## Output views

- `companies` (Companies Overview): the profile and listing columns.
- `reviews` (Client Reviews): one row per verified review.

## Store and MCP

- Store page: https://apify.com/johnvc/clutch-agency-api?fpr=9n7kx3&fp_sid=awesomeskills
- Hosted MCP server: `https://mcp.apify.com/?tools=actors,docs,johnvc/clutch-agency-api`
- MCP docs: https://docs.apify.com/platform/integrations/mcp

## Related Actors in the portfolio

- LinkedIn Company API: https://apify.com/johnvc/linkedin-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- Crunchbase Company API: https://apify.com/johnvc/crunchbase-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- G2 Reviews API: https://apify.com/johnvc/g2-reviews-api?fpr=9n7kx3&fp_sid=awesomeskills
