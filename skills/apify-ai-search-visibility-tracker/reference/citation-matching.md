# Citation and Mention Matching

Two independent matchers run on every (prompt x source) cell. An entity can be `cited: true, mentioned: false` (linked but unnamed) or `cited: false, mentioned: true` (named but not linked).

## URL citation matching -- registrable domain

Compare the **registrable domain** of every cited URL to the entity's domain. `https://blog.apify.com/x` counts as a citation for `apify.com`; `https://github.com/apify/x` does **not** (registrable domain is `github.com`).

The runner uses `tldextract` if installed (handles multi-part TLDs like `.co.uk` correctly):

```python
import tldextract
def registrable(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}".lower()
```

Stdlib fallback (covers ~99% of cases, misses some multi-part TLDs):

```python
from urllib.parse import urlparse
def registrable_fallback(url):
    host = (urlparse(url).hostname or "").lower()
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host
```

URLs without a scheme get `https://` prepended before parsing. IDN domains should be normalised to ASCII (`xn--...`) before comparing.

## Brand-name mention matching -- word boundary

Match surface forms against the answer text with `\b<form>\b`, case-insensitive:

```python
import re
def mentions(text, surface_forms):
    return any(
        re.search(r"\b" + re.escape(f) + r"\b", text, flags=re.IGNORECASE)
        for f in surface_forms if f
    )
```

`\b` anchors prevent `Apify` from matching `Apifying` or `Happify`. For multi-word brands (`Open AI`), pass each surface form literally (`["OpenAI", "Open AI"]`). `re.escape` handles punctuation (`O'Reilly`, `Yahoo!`) correctly.

## Test matrix

| Citation URL | Brand domain | `cited` |
|---|---|---|
| `https://apify.com/store` | `apify.com` | true |
| `https://blog.apify.com/x` | `apify.com` | true |
| `https://APIFY.COM/x` | `apify.com` | true |
| `https://github.com/apify/x` | `apify.com` | false |
| `https://apifyclone.com/x` | `apify.com` | false |

| Answer text | Surface form | `mentioned` |
|---|---|---|
| `Use Apify for scraping` | `Apify` | true |
| `apify is great` | `Apify` | true |
| `See apify.com/docs` | `Apify` | true |
| `When apifying data` | `Apify` | false |
| `Happify the user` | `Apify` | false |
