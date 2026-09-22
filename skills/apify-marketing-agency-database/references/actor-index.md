# Actor routing table: Clutch.co marketing agency database

The Actor `johnvc/clutch-agency-api` has three modes. This skill uses `directory`.
Pick the mode by the job:

| Job | Mode | Key inputs | Row type returned |
|-----|------|-----------|-------------------|
| Build the list of agencies in a category or location | `directory` | `directoryUrls`, `maxPagesPerDirectory`, `maxItems` | `listing` |
| Full record for specific companies you already know | `profiles` | `profileUrls`, `includeReviews`, `outputFormats` | `profile` (+ `review`) |
| Find companies by keyword, then pull them | `search` | `searchQueries` | `profile` |

For the full profile and reviews of a shortlist, use the companion skill
`apify-company-data-api`, which is shaped for that outcome. Feed it the
`profile_url` values this directory run returns.

## Directory URL patterns

Clutch has a page for most service and location combinations. Examples:

- `https://clutch.co/agencies/digital-marketing`
- `https://clutch.co/web-developers`
- `https://clutch.co/us/agencies/digital-marketing`
- `https://clutch.co/seo-firms`

Page 0 is the bare URL; deeper pages are handled internally, so you only set
`maxPagesPerDirectory`.

## Output views

- `companies` (Companies Overview): the listing columns.
- `reviews` (Client Reviews): used by profiles mode, not directory mode.

## Store and MCP

- Store page: https://apify.com/johnvc/clutch-agency-api?fpr=9n7kx3&fp_sid=awesomeskills
- Hosted MCP server: `https://mcp.apify.com/?tools=actors,docs,johnvc/clutch-agency-api`
- MCP docs: https://docs.apify.com/platform/integrations/mcp

## Related Actors in the portfolio

- Google Maps Places API: https://apify.com/johnvc/google-maps-places-api?fpr=9n7kx3&fp_sid=awesomeskills
- LinkedIn Company API: https://apify.com/johnvc/linkedin-company-api?fpr=9n7kx3&fp_sid=awesomeskills
- G2 Reviews API: https://apify.com/johnvc/g2-reviews-api?fpr=9n7kx3&fp_sid=awesomeskills
