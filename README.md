# Awesome Apify Skills

Community collection of specialized [Apify](https://apify.com) agent skills for AI coding assistants like [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Cursor](https://cursor.com).

Each skill provides domain-specific prompts and pre-configured Apify Actor workflows for common data extraction use cases.

> For the official consolidated Apify plugins, see [apify/marketplace](https://github.com/apify/marketplace).

## Skills

| Skill | Description |
|-------|-------------|
| **apify-lead-generation** | Generate B2B/B2C leads from Google Maps, Instagram, TikTok, Facebook, LinkedIn, YouTube, and Google Search |
| **apify-brand-reputation-monitoring** | Track reviews, ratings, sentiment, and brand mentions across Google Maps, Booking.com, TripAdvisor, and social media |
| **apify-competitor-intelligence** | Analyze competitor strategies, content, pricing, ads, and market positioning |
| **apify-market-research** | Analyze market conditions, geographic opportunities, pricing, and consumer behavior |
| **apify-influencer-discovery** | Find and evaluate influencers, verify authenticity, and track collaboration performance |
| **apify-trend-analysis** | Discover and track emerging trends across Google Trends and social platforms |
| **apify-content-analytics** | Track engagement metrics, measure campaign ROI, and analyze content performance |
| **apify-audience-analysis** | Understand audience demographics, preferences, behavior patterns, and engagement quality |
| **apify-ecommerce** | Scrape e-commerce data from Amazon, Walmart, eBay, IKEA, and 50+ marketplaces |

## Prerequisites

1. **Apify account** - Sign up at [apify.com](https://apify.com)
2. **Apify API token** - Get yours at [console.apify.com/account/integrations](https://console.apify.com/account/integrations)
3. **mcpc** - Install the Apify MCP connector:
   ```bash
   npm install -g @anthropic-ai/claude-code
   npx @anthropic-ai/claude-code /install-marketplace https://github.com/anthropics/awesome-apify-skills
   ```

Set your API token:
```bash
export APIFY_TOKEN=your_token_here
```

## Installation

### Claude Code

```bash
claude /install-marketplace https://github.com/anthropics/awesome-apify-skills
```

Then install individual skills:
```bash
claude /install apify-lead-generation
```

### Cursor

Copy the desired skill directory from `skills/` into your project's `.cursor-plugin/skills/` directory.

## Structure

```
skills/
├── apify-lead-generation/
│   ├── SKILL.md              # Skill instructions and Actor configurations
│   └── reference/scripts/    # Helper scripts (run_actor.js, etc.)
├── apify-brand-reputation-monitoring/
├── apify-competitor-intelligence/
├── apify-market-research/
├── apify-influencer-discovery/
├── apify-trend-analysis/
├── apify-content-analytics/
├── apify-audience-analysis/
└── apify-ecommerce/
```

## Contributing

Contributions are welcome! To add a new skill:

1. Fork this repository
2. Create a new skill directory under `skills/`
3. Include a `SKILL.md` with Actor configurations and usage instructions
4. Add helper scripts in `reference/scripts/`
5. Update `marketplace.json` with the new skill entry
6. Submit a pull request

## License

ISC
