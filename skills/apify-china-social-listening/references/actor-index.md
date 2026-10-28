# Actor index — China social listening

| Actor | ID / name | Modes (high level) | Example tasks (Store) |
|-------|-----------|--------------------|------------------------|
| Weibo Scraper | `dheerajitbhu/weibo-scraper` | hot_search, search, comments, user_profile | hot-search-tracker, brand-mentions, post-comments-export, user-profile-data |
| Douban Scraper | `dheerajitbhu/douban-scraper` | search, comments, reviews, chart, subject | movie-ratings, book-ratings, short-comments, now-showing, top250-movies, book-reviews, movie-reviews |
| WeChat Articles | `dheerajitbhu/wechat-articles-scraper` | search (+ optional full article) | article-search, full-article-text, brand-monitoring |
| Bilibili Scraper | `dheerajitbhu/bilibili-scraper` | search, comments, popular, user_profile | video-search, comments-export, trending-videos, creator-stats |

Fetch live input schema before building inputs:

```bash
apify actors info "dheerajitbhu/douban-scraper" --input --json \
  --user-agent apify-awesome-skills/apify-china-social-listening 2>/dev/null
```
