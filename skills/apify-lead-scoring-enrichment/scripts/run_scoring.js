#!/usr/bin/env node
// Batches all lead URLs into per-Actor calls (tech, content, metadata) and
// writes a per-URL sidecar keyed by canonical https://domain.
//
// Usage:
//   node --env-file=.env scripts/run_scoring.js \
//     --input leads.csv --output scoring.json \
//     [--enable-tech] [--enable-content] [--enable-metadata] \
//     [--content-crawl-depth 0]
//
// At least one --enable-* flag must be set.

import { parseArgs } from 'node:util';
import { readFileSync, writeFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { runActorAndGetItems, toCanonicalUrl, toDomain } from './apify_client.js';

const { values } = parseArgs({
    options: {
        input: { type: 'string' },
        output: { type: 'string' },
        'enable-tech': { type: 'boolean', default: false },
        'enable-content': { type: 'boolean', default: false },
        'enable-metadata': { type: 'boolean', default: false },
        'content-crawl-depth': { type: 'string', default: '0' },
    },
});

if (!values.input || !values.output) {
    console.error('Usage: run_scoring.js --input <leads.csv> --output <scoring.json> [--enable-tech] [--enable-content] [--enable-metadata]');
    process.exit(1);
}
if (!values['enable-tech'] && !values['enable-content'] && !values['enable-metadata']) {
    console.error('Error: at least one of --enable-tech, --enable-content, --enable-metadata is required.');
    process.exit(1);
}

const csvText = readFileSync(values.input, 'utf8');
const rows = parse(csvText, { columns: true, skip_empty_lines: true, trim: true });
if (!rows.length) {
    console.error(`Error: no rows in ${values.input}`);
    process.exit(1);
}
if (!('company_url' in rows[0])) {
    console.error(`Error: input CSV is missing the required "company_url" column. Found: ${Object.keys(rows[0]).join(', ')}`);
    process.exit(1);
}

const urls = [...new Set(rows.map((r) => toCanonicalUrl(r.company_url)).filter(Boolean))];
const domains = [...new Set(urls.map(toDomain))];
console.error(`Loaded ${rows.length} leads → ${urls.length} unique URLs.`);

const sidecar = Object.fromEntries(urls.map((u) => [u, {}]));

function upsertByUrl(actorItems, urlPicker, key) {
    for (const item of actorItems || []) {
        const raw = urlPicker(item);
        const canon = toCanonicalUrl(raw);
        if (!canon || !(canon in sidecar)) continue;
        sidecar[canon][key] = item;
    }
}

if (values['enable-tech']) {
    console.error(`→ Running builtwith/builtwith-official-technology-scraper for ${domains.length} domains…`);
    const items = await runActorAndGetItems(
        'builtwith/builtwith-official-technology-scraper',
        { startDomains: domains },
        { sourceTag: 'tech', timeoutSec: 900 },
    );
    upsertByUrl(items, (it) => it.url || it.domain || it.website || it.startDomain, 'tech');
    console.error(`  tech: ${items.length} items back.`);
}

if (values['enable-content']) {
    const depth = parseInt(values['content-crawl-depth'], 10);
    console.error(`→ Running apify/website-content-crawler (maxCrawlDepth=${depth})…`);
    const items = await runActorAndGetItems(
        'apify/website-content-crawler',
        {
            startUrls: urls.map((u) => ({ url: u })),
            maxCrawlDepth: depth,
            maxCrawlPages: Math.max(urls.length, urls.length * (depth + 1)),
            crawlerType: 'playwright:firefox',
            saveMarkdown: true,
        },
        { sourceTag: 'content', timeoutSec: 1800 },
    );
    upsertByUrl(items, (it) => it.url || it.loadedUrl, 'content');
    console.error(`  content: ${items.length} items back.`);
}

if (values['enable-metadata']) {
    console.error(`→ Running vdrmota/contact-info-scraper for ${urls.length} URLs…`);
    const items = await runActorAndGetItems(
        'vdrmota/contact-info-scraper',
        {
            startUrls: urls.map((u) => ({ url: u })),
            maxDepth: 1,
            maxRequests: urls.length * 2,
        },
        { sourceTag: 'metadata', timeoutSec: 1800 },
    );
    upsertByUrl(items, (it) => it.url || it.domain, 'metadata');
    console.error(`  metadata: ${items.length} items back.`);
}

writeFileSync(values.output, JSON.stringify(sidecar, null, 2));
console.error(`Wrote ${values.output} (${Object.keys(sidecar).length} URLs).`);
