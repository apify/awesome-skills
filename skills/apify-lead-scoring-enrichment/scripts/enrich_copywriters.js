#!/usr/bin/env node
// For each lead URL:
//   1. Google-search site:{domain} blog → apify/google-search-scraper
//   2. Extract author names from top blog posts → apify/ai-web-scraper
//      (with the get-author-name-from-blog-post example input)
//   3. Deduplicate authors, then resolve emails → scalelist/bulk-email-finder-dep
//
// Usage:
//   node --env-file=.env scripts/enrich_copywriters.js \
//     --input leads.csv --output enrichment.json \
//     [--results-per-domain 5]

import { parseArgs } from 'node:util';
import { readFileSync, writeFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { runActorAndGetItems, toCanonicalUrl, toDomain } from './apify_client.js';

const { values } = parseArgs({
    options: {
        input: { type: 'string' },
        output: { type: 'string' },
        'results-per-domain': { type: 'string', default: '5' },
    },
});

if (!values.input || !values.output) {
    console.error('Usage: enrich_copywriters.js --input <leads.csv> --output <enrichment.json>');
    process.exit(1);
}

const csvText = readFileSync(values.input, 'utf8');
const rows = parse(csvText, { columns: true, skip_empty_lines: true, trim: true });
if (!rows.length || !('company_url' in rows[0])) {
    console.error('Error: input CSV needs a "company_url" column.');
    process.exit(1);
}

const urls = [...new Set(rows.map((r) => toCanonicalUrl(r.company_url)).filter(Boolean))];
const perDomain = parseInt(values['results-per-domain'], 10) || 5;
console.error(`Copywriter hunt across ${urls.length} URLs, top ${perDomain} blog posts each.`);

const sidecar = Object.fromEntries(urls.map((u) => [u, { authors: [], blogPosts: [], emails: [] }]));

// ---- Step 1: Google search for blog posts on each domain.
console.error('→ Running apify/google-search-scraper for site:{domain} blog…');
const gssItems = await runActorAndGetItems(
    'apify/google-search-scraper',
    {
        queries: urls.map((u) => `site:${toDomain(u)} blog`).join('\n'),
        resultsPerPage: perDomain,
        maxPagesPerQuery: 1,
        countryCode: 'us',
        languageCode: 'en',
    },
    { sourceTag: 'copywriters_search', timeoutSec: 1200 },
);
console.error(`  google-search: ${gssItems.length} result buckets back.`);

// Map results back to their originating domain by matching the query.
const blogUrlsByDomain = {};
for (const bucket of gssItems) {
    const query = bucket.searchQuery?.term || bucket.searchQuery || '';
    const m = /site:([^\s]+)/i.exec(query);
    if (!m) continue;
    const domain = m[1].toLowerCase();
    const canon = toCanonicalUrl(domain);
    if (!canon || !(canon in sidecar)) continue;
    const results = bucket.organicResults || bucket.results || [];
    const links = results.map((r) => r.url).filter(Boolean).slice(0, perDomain);
    blogUrlsByDomain[canon] = links;
    sidecar[canon].blogPosts = links;
}

const allBlogUrls = Object.values(blogUrlsByDomain).flat();
if (!allBlogUrls.length) {
    console.error('No blog posts discovered — skipping author extraction and email lookup.');
    writeFileSync(values.output, JSON.stringify(sidecar, null, 2));
    process.exit(0);
}

// ---- Step 2: extract author names from blog posts.
console.error(`→ Running apify/ai-web-scraper on ${allBlogUrls.length} blog URLs…`);
const authorItems = await runActorAndGetItems(
    'apify/ai-web-scraper',
    {
        // Matches https://apify.com/apify/ai-web-scraper/examples/get-author-name-from-blog-post
        startUrls: allBlogUrls.map((u) => ({ url: u })),
        prompt: 'Extract the author name of this blog post. Return the full name only, no title or role. If no author is listed, return null.',
        schema: {
            type: 'object',
            properties: { author: { type: 'string' } },
            required: ['author'],
        },
        proxyConfiguration: { useApifyProxy: true },
    },
    { sourceTag: 'copywriters_author', timeoutSec: 1800 },
);
console.error(`  ai-web-scraper: ${authorItems.length} items back.`);

// apify/ai-web-scraper returns extracted values in `item.data` (array of
// strings or {name}-shaped objects), NOT `item.author`. Flatten to a list
// of candidate names per item, then keep only entries that look like a
// real first+last human name (drops "Session zero", "Login", single-word
// nav labels, etc.).
const looksLikeHumanName = (s) => {
    if (typeof s !== 'string') return false;
    const trimmed = s.trim();
    if (trimmed.length < 3 || trimmed.length > 60) return false;
    const parts = trimmed.split(/\s+/);
    if (parts.length < 2) return false;
    return parts.every((p) => /^[A-Z][A-Za-z''`\-.]{0,29}$/.test(p));
};
const authorsByDomain = {};
for (const item of authorItems) {
    const sourceUrl = item.url || item.startUrl;
    if (!sourceUrl) continue;
    const raw = item.data ?? item.author ?? item.result?.author ?? [];
    const candidates = (Array.isArray(raw) ? raw : [raw])
        .map((v) => (typeof v === 'string' ? v : v && (v.name || v.author)))
        .filter(Boolean)
        .map((s) => s.trim())
        .filter(looksLikeHumanName);
    if (!candidates.length) continue;
    for (const [canon, links] of Object.entries(blogUrlsByDomain)) {
        if (links.includes(sourceUrl)) {
            const set = (authorsByDomain[canon] = authorsByDomain[canon] || new Set());
            for (const name of candidates) {
                set.add(name);
                sidecar[canon].authors.push({ name, sourceUrl });
            }
            break;
        }
    }
}

const finderPairs = [];
for (const [canon, set] of Object.entries(authorsByDomain)) {
    for (const fullName of set) {
        const parts = fullName.split(/\s+/);
        if (parts.length < 2) continue;
        finderPairs.push({
            canon,
            firstName: parts[0],
            lastName: parts.slice(1).join(' '),
            domain: toDomain(canon),
        });
    }
}

if (!finderPairs.length) {
    console.error('No authors extracted with a first+last name — skipping email lookup.');
    writeFileSync(values.output, JSON.stringify(sidecar, null, 2));
    process.exit(0);
}

// ---- Step 3: email finder on (first_name, last_name, company_domain) triples.
console.error(`→ Running scalelist/bulk-email-finder-dep for ${finderPairs.length} authors…`);
let finderItems = [];
try {
    finderItems = await runActorAndGetItems(
        'scalelist/bulk-email-finder-dep',
        {
            leads: finderPairs.map(({ firstName, lastName, domain }) => ({
                first_name: firstName,
                last_name: lastName,
                company_domain: domain,
            })),
        },
        { sourceTag: 'copywriters_email', timeoutSec: 1200 },
    );
} catch (e) {
    console.error(`  bulk-email-finder-dep failed: ${e.message}. Continuing with no emails.`);
}
console.error(`  email-finder: ${finderItems.length} items back.`);

for (const item of finderItems) {
    const email = item.email || item.emailAddress;
    if (!email) continue;
    const domain = (item.company_domain || item.domain || '').toLowerCase();
    const first = (item.first_name || item.firstName || '').toLowerCase();
    const last = (item.last_name || item.lastName || '').toLowerCase();
    const match = finderPairs.find((p) => p.domain === domain && p.firstName.toLowerCase() === first && p.lastName.toLowerCase() === last);
    if (!match) continue;
    sidecar[match.canon].emails.push(email);
    const author = sidecar[match.canon].authors.find((a) => a.name.toLowerCase() === `${first} ${last}`);
    if (author) author.email = email;
}

for (const canon of Object.keys(sidecar)) {
    sidecar[canon].emails = [...new Set(sidecar[canon].emails)];
}

writeFileSync(values.output, JSON.stringify(sidecar, null, 2));
console.error(`Wrote ${values.output}. ${Object.values(sidecar).filter((v) => v.emails.length).length}/${urls.length} URLs have ≥1 copywriter email.`);
