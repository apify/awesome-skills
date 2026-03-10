# Awesome Apify Skills

Community collection of Apify agent skills for web scraping, data extraction, and automation. Works with Claude Code, Cursor, Codex, Gemini CLI, and other AI coding assistants.

> For the official consolidated Apify plugins, see [apify/agent-skills](https://github.com/apify/agent-skills).

## Available skills

<!-- BEGIN_SKILLS_TABLE -->
| Name | Description | Documentation |
|------|-------------|---------------|
| `apify-audience-analysis` | Understand audience demographics, preferences, behavior patterns, and engagement quality across Facebook, Instagram, YouTube, and TikTok | [SKILL.md](skills/apify-audience-analysis/SKILL.md) |
| `apify-brand-reputation-monitoring` | Track reviews, ratings, sentiment, and brand mentions across Google Maps, Booking.com, TripAdvisor, Facebook, Instagram, YouTube, and TikTok | [SKILL.md](skills/apify-brand-reputation-monitoring/SKILL.md) |
| `apify-competitor-intelligence` | Analyze competitor strategies, content, pricing, ads, and market positioning across Google Maps, Booking.com, Facebook, Instagram, YouTube, and TikTok | [SKILL.md](skills/apify-competitor-intelligence/SKILL.md) |
| `apify-content-analytics` | Track engagement metrics, measure campaign ROI, and analyze content performance across Instagram, Facebook, YouTube, and TikTok | [SKILL.md](skills/apify-content-analytics/SKILL.md) |
| `apify-ecommerce` | Scrape e-commerce data for pricing intelligence, customer sentiment, product research, quality analysis, and supply chain monitoring across Amazon, Walmart, eBay, IKEA, and 50+ marketplaces | [SKILL.md](skills/apify-ecommerce/SKILL.md) |
| `apify-influencer-discovery` | Find and evaluate influencers for brand partnerships, verify authenticity, and track collaboration performance across Instagram, Facebook, YouTube, and TikTok | [SKILL.md](skills/apify-influencer-discovery/SKILL.md) |
| `apify-lead-generation` | Generate B2B/B2C leads by scraping Google Maps, websites, Instagram, TikTok, Facebook, LinkedIn, YouTube, and Google Search using Apify Actors | [SKILL.md](skills/apify-lead-generation/SKILL.md) |
| `apify-market-research` | Analyze market conditions, geographic opportunities, pricing, consumer behavior, and product validation across Google Maps, Facebook, Instagram, Booking.com, and TripAdvisor | [SKILL.md](skills/apify-market-research/SKILL.md) |
| `apify-trend-analysis` | Discover and track emerging trends across Google Trends, Instagram, Facebook, YouTube, and TikTok to inform content strategy | [SKILL.md](skills/apify-trend-analysis/SKILL.md) |
<!-- END_SKILLS_TABLE -->

## Installation

> For the official consolidated Apify plugins, see [apify/agent-skills](https://github.com/apify/agent-skills).

```bash
# Add the marketplace
/plugin marketplace add apify/awesome-apify-skills

# Install a skill
/plugin install apify-lead-generation@awesome-apify-skills
```

### Cursor / Windsurf

Add to your project's `.cursor/settings.json` or use the same Claude Code plugin format.

### Codex / Gemini CLI

Point your agent to the `agents/AGENTS.md` file which contains skill descriptions and paths:

```bash
# Gemini CLI uses gemini-extension.json automatically
# For Codex, reference agents/AGENTS.md in your configuration
```

### Other AI tools

Any AI tool that supports Markdown context can use the skills by pointing to:
- `agents/AGENTS.md` - auto-generated skill index
- `skills/*/SKILL.md` - individual skill documentation

## Prerequisites

1. **Apify account** - [apify.com](https://apify.com)
2. **API token** - get from [Apify Console](https://console.apify.com/account/integrations), add `APIFY_TOKEN=your_token` to `.env`
3. **Node.js 20.6+**
4. **[mcpc CLI](https://github.com/apify/mcp-cli)** - `npm install -g @apify/mcpc`

## Pricing

Apify Actors use pay-per-result pricing. Check individual Actor pricing on the [Apify platform](https://apify.com).

## Contributing

1. Fork this repository.
2. Create your skill in `skills/your-skill-name/`.
3. Add `SKILL.md` with proper frontmatter:
   ```yaml
   ---
   name: your-skill-name
   description: What your skill does and when to use it
   ---
   ```
4. Add entry to `.claude-plugin/marketplace.json`.
5. Submit a pull request.

## Support

- [Apify Documentation](https://docs.apify.com)
- [Apify Discord](https://discord.gg/jyEM2PRvMU)
