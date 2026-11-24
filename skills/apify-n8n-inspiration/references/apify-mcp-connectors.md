# Apify MCP connectors — supported services

Source: https://docs.apify.com/integrations/mcp-connectors

Last checked: 2026-10-28. Re-fetch the doc before you rely on this list — Apify adds connectors.

| Service | n8n node `name` patterns to match | Notes |
|---------|-----------------------------------|-------|
| Notion | `n8n-nodes-base.notion`, `n8n-nodes-base.notionTrigger`, `@n8n/n8n-nodes-langchain.toolNotion` | Most common hits: database page creation, append block, search. |
| Slack | `n8n-nodes-base.slack`, `n8n-nodes-base.slackTrigger` | Posts to channel, DMs, slash-command triggers. |
| GitHub | `n8n-nodes-base.github`, `n8n-nodes-base.githubTrigger` | Issues, PRs, releases, webhook-driven workflows. |
| Sentry | `n8n-nodes-base.sentryIo` | Event ingestion. Less common in community templates. |
| Supabase | `n8n-nodes-base.supabase` | Row insert / select / update. |

**Google and Microsoft Entra** appear on the doc page but only as OAuth providers you register your own app with — they are **not** currently exposed as MCP connectors. Treat Gmail, Google Sheets, Google Drive, Google Calendar, Outlook, OneDrive, Microsoft Teams etc. as *not yet supported* for bucket 3, and route them to the "Other / mixed" bucket.

## When a new connector launches

Add it here with the matching `name` patterns and update the `Last checked` date. The classification step in SKILL.md reads this file every run, so a one-line addition is enough.
