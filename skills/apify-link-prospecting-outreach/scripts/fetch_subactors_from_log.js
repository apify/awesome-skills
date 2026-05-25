#!/usr/bin/env node
/**
 * For apify/link-prospecting-tool runs where the parent no longer writes
 * SUB_ACTOR_RESULTS, parse the run log for sub-Actor runIds and download
 * each sub-Actor's default dataset.
 *
 * Usage:
 *   node --env-file=.env scripts/fetch_subactors_from_log.js \
 *     --run-id <runId> \
 *     --base YYYY-MM-DD_<short-name>_outreach
 *
 * Writes (when found):
 *   <base>_serp.json     — apify.google-search-scraper default dataset
 *   <base>_wcc.json      — apify.website-content-crawler default dataset
 *   <base>_authors.json  — apify.ai-web-scraper default dataset
 *   <base>_subruns.json  — index of detected sub-Actor runs
 */
import { parseArgs } from 'node:util';
import { writeFileSync } from 'node:fs';

const token = process.env.APIFY_TOKEN;
if (!token) { console.error('APIFY_TOKEN missing'); process.exit(1); }

const { values } = parseArgs({
    options: {
        'run-id': { type: 'string' },
        base: { type: 'string' },
    },
});
if (!values['run-id'] || !values.base) {
    console.error('Usage: --run-id <id> --base <prefix>');
    process.exit(1);
}
const runId = values['run-id'];
const base = values.base;

const h = { 'User-Agent': 'link-prospecting-skill/fetch-subactors/1.0' };

console.log(`Fetching log for run ${runId}...`);
const logResp = await fetch(
    `https://api.apify.com/v2/actor-runs/${runId}/log?token=${encodeURIComponent(token)}`,
    { headers: h },
);
const log = await logResp.text();

// Parse "[apify.<actor-name> runId:<id>]" markers from the log
const subActorRe = /\[apify\.([a-z0-9-]+) runId:([A-Za-z0-9]+)\]/g;
const seen = new Map();
let m;
while ((m = subActorRe.exec(log)) !== null) {
    const actorSlug = m[1];
    const subRunId = m[2];
    const key = `${actorSlug}:${subRunId}`;
    if (!seen.has(key)) {
        seen.set(key, { actorSlug, subRunId });
    }
}

const subRuns = Array.from(seen.values());
console.log(`Detected ${subRuns.length} unique sub-Actor run(s):`);
for (const s of subRuns) {
    console.log(`  apify.${s.actorSlug} runId=${s.subRunId}`);
}

// Resolve each sub-Actor's default dataset
async function getRunDetails(id) {
    const r = await fetch(
        `https://api.apify.com/v2/actor-runs/${id}?token=${encodeURIComponent(token)}`,
        { headers: h },
    );
    if (!r.ok) {
        console.warn(`Could not get details for sub-run ${id}: ${r.status}`);
        return null;
    }
    return (await r.json()).data;
}

async function fetchDataset(datasetId) {
    const r = await fetch(
        `https://api.apify.com/v2/datasets/${datasetId}/items?token=${encodeURIComponent(token)}&format=json`,
        { headers: h },
    );
    if (!r.ok) {
        console.warn(`Could not fetch dataset ${datasetId}: ${r.status}`);
        return [];
    }
    return r.json();
}

const SUFFIX_MAP = {
    'google-search-scraper': 'serp',
    'website-content-crawler': 'wcc',
    'ai-web-scraper': 'authors',
    // 'contact-info-scraper': folded into main leads — skip
};

const indexEntries = [];
for (const s of subRuns) {
    const details = await getRunDetails(s.subRunId);
    if (!details) continue;
    const dsId = details.defaultDatasetId;
    const status = details.status;
    indexEntries.push({
        actorSlug: s.actorSlug,
        subRunId: s.subRunId,
        status,
        defaultDatasetId: dsId,
        itemCount: null,
    });

    const suffix = SUFFIX_MAP[s.actorSlug];
    if (!suffix) {
        console.log(`Skipping apify.${s.actorSlug} (no mapping to skill output file).`);
        continue;
    }
    if (!dsId) {
        console.warn(`apify.${s.actorSlug} has no defaultDatasetId, skipping.`);
        continue;
    }

    console.log(`\nFetching apify.${s.actorSlug} dataset ${dsId} (status ${status})...`);
    const items = await fetchDataset(dsId);
    const path = `${base}_${suffix}.json`;
    writeFileSync(path, JSON.stringify(items, null, 2));
    console.log(`Saved → ${path} (${items.length} items)`);
    indexEntries.at(-1).itemCount = items.length;
}

const indexPath = `${base}_subruns.json`;
writeFileSync(indexPath, JSON.stringify(indexEntries, null, 2));
console.log(`\nSaved sub-run index → ${indexPath}`);
