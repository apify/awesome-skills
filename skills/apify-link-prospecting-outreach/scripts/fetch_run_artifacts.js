#!/usr/bin/env node
/**
 * Download all artifacts for an existing Apify run.
 *
 * Use when run_actor.js hit its client-side wait timeout but the Actor is
 * still running on Apify. This script polls the existing runId until terminal,
 * then mirrors run_actor.js's downloadAllArtifacts logic.
 *
 * Usage:
 *   node --env-file=.env scripts/fetch_run_artifacts.js \
 *     --run-id <runId> \
 *     --output YYYY-MM-DD_<short-name>_outreach.json \
 *     --timeout 1800
 */

import { parseArgs } from 'node:util';
import { writeFileSync } from 'node:fs';
import { dirname, basename, extname, join } from 'node:path';

const USER_AGENT = 'apify-awesome-skills/link-prospecting-outreach-1.0.0/fetch';

function parseCliArgs() {
    const options = {
        'run-id': { type: 'string' },
        output: { type: 'string', short: 'o' },
        timeout: { type: 'string', short: 't', default: '1800' },
        'poll-interval': { type: 'string', default: '15' },
    };
    const { values } = parseArgs({ options, allowPositionals: false });
    if (!values['run-id']) {
        console.error('Error: --run-id is required');
        process.exit(1);
    }
    if (!values.output) {
        console.error('Error: --output is required');
        process.exit(1);
    }
    return {
        runId: values['run-id'],
        output: values.output,
        timeout: parseInt(values.timeout, 10),
        pollInterval: parseInt(values['poll-interval'], 10),
    };
}

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

async function getRunDetails(token, runId) {
    const url = `https://api.apify.com/v2/actor-runs/${runId}?token=${encodeURIComponent(token)}`;
    const r = await fetch(url, { headers: { 'User-Agent': `${USER_AGENT}/run_details` } });
    if (!r.ok) throw new Error(`run details failed: ${await r.text()}`);
    const j = await r.json();
    return j.data;
}

async function pollUntilTerminal(token, runId, timeout, interval) {
    const start = Date.now();
    let lastStatus = null;
    while (true) {
        const data = await getRunDetails(token, runId);
        if (data.status !== lastStatus) {
            console.log(`Status: ${data.status} (runtime ${Math.round((Date.now() - start) / 1000)}s after fetch started)`);
            lastStatus = data.status;
        }
        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(data.status)) {
            return data;
        }
        if ((Date.now() - start) / 1000 > timeout) {
            console.error(`Fetch-side timeout after ${timeout}s. Run still in status: ${data.status}`);
            return data;
        }
        await sleep(interval * 1000);
    }
}

async function fetchDatasetItems(token, datasetId) {
    const url = `https://api.apify.com/v2/datasets/${datasetId}/items?token=${encodeURIComponent(token)}&format=json`;
    const r = await fetch(url, { headers: { 'User-Agent': `${USER_AGENT}/dataset` } });
    if (!r.ok) {
        console.error(`Failed to download dataset ${datasetId}: ${await r.text()}`);
        return [];
    }
    return r.json();
}

function resolveNamedDataset(runData, names) {
    const named = runData.namedDatasetIds || runData.namedDatasets || {};
    for (const n of names) {
        if (named[n]) return named[n];
        const lo = Object.keys(named).find((k) => k.toLowerCase() === n.toLowerCase());
        if (lo) return named[lo];
    }
    return null;
}

async function fetchSubActorIndex(token, runData) {
    const kv = runData.defaultKeyValueStoreId;
    if (kv) {
        const keys = ['SUB_ACTOR_RESULTS', 'sub_actor_results', 'SUB_ACTORS', 'subActors'];
        for (const k of keys) {
            const url = `https://api.apify.com/v2/key-value-stores/${kv}/records/${k}?token=${encodeURIComponent(token)}`;
            const r = await fetch(url, { headers: { 'User-Agent': `${USER_AGENT}/sub` } });
            if (r.ok) {
                try {
                    const parsed = await r.json();
                    if (Array.isArray(parsed) && parsed.length) return parsed;
                } catch { continue; }
            }
        }
    }
    // Fallback: parse parent run log for "[apify.<slug> runId:<id>]" markers
    // (Actor schema change on/before 2026-05-20 removed the KV index.)
    const logResp = await fetch(
        `https://api.apify.com/v2/actor-runs/${runData.id}/log?token=${encodeURIComponent(token)}`,
        { headers: { 'User-Agent': `${USER_AGENT}/sub_log` } },
    );
    if (!logResp.ok) return [];
    const log = await logResp.text();
    const re = /\[apify\.([a-z0-9-]+) runId:([A-Za-z0-9]+)\]/g;
    const seen = new Map();
    let m;
    while ((m = re.exec(log)) !== null) {
        const k = `${m[1]}:${m[2]}`;
        if (!seen.has(k)) seen.set(k, { actorSlug: m[1], runId: m[2] });
    }
    const out = [];
    for (const s of seen.values()) {
        try {
            const r = await fetch(
                `https://api.apify.com/v2/actor-runs/${s.runId}?token=${encodeURIComponent(token)}`,
                { headers: { 'User-Agent': `${USER_AGENT}/subrun` } },
            );
            if (!r.ok) continue;
            const data = (await r.json()).data;
            out.push({
                actorId: `apify/${s.actorSlug}`,
                runId: s.runId,
                datasetId: data.defaultDatasetId,
            });
        } catch { /* best-effort */ }
    }
    if (out.length) console.log(`Discovered ${out.length} sub-Actor run(s) via log-parsing (KV index was empty).`);
    return out;
}

function findSubActor(idx, sub) {
    if (!Array.isArray(idx)) return null;
    return idx.find((e) => (e.actorId || e.actor || '').toLowerCase().includes(sub.toLowerCase())) || null;
}

async function main() {
    const args = parseCliArgs();
    const token = process.env.APIFY_TOKEN;
    if (!token) { console.error('APIFY_TOKEN not in .env'); process.exit(1); }

    console.log(`Polling run ${args.runId} until terminal (max ${args.timeout}s)...`);
    const runData = await pollUntilTerminal(token, args.runId, args.timeout, args.pollInterval);
    if (runData.status !== 'SUCCEEDED') {
        console.error(`Run final status: ${runData.status}`);
        // Continue anyway — partial data may still be available
    }
    console.log(`Run terminal: ${runData.status}`);

    const baseDir = dirname(args.output);
    const baseName = basename(args.output, extname(args.output));

    const primaryDatasetId = runData.defaultDatasetId;
    console.log(`\nFetching main dataset ${primaryDatasetId}...`);
    const mainData = await fetchDatasetItems(token, primaryDatasetId);
    writeFileSync(args.output, JSON.stringify(mainData, null, 2));
    console.log(`Saved main dataset → ${args.output} (${mainData.length} rows)`);

    const namedMap = {
        mentions: ['MENTIONS', 'Mentions', 'mentions'],
        authors: ['AUTHORS', 'AUTHOR_LIST', 'Authors', 'authors', 'authorList'],
        domainsWithLeads: ['DOMAINS_WITH_LEADS', 'DomainsWithLeads', 'domainsWithLeads'],
    };
    for (const [label, names] of Object.entries(namedMap)) {
        const dsId = resolveNamedDataset(runData, names);
        if (dsId) {
            const items = await fetchDatasetItems(token, dsId);
            const p = join(baseDir, `${baseName}_${label}.json`);
            writeFileSync(p, JSON.stringify(items, null, 2));
            console.log(`Saved ${label} → ${p} (${items.length} rows)`);
        } else {
            console.log(`Note: no named dataset for "${label}"`);
        }
    }

    const subIndex = await fetchSubActorIndex(token, runData);
    if (Array.isArray(subIndex) && subIndex.length) {
        const p = join(baseDir, `${baseName}_sub.json`);
        writeFileSync(p, JSON.stringify(subIndex, null, 2));
        console.log(`Saved sub-Actor index → ${p} (${subIndex.length} entries)`);

        const serp = findSubActor(subIndex, 'google-search-scraper');
        if (serp && (serp.datasetId || serp.defaultDatasetId)) {
            const items = await fetchDatasetItems(token, serp.datasetId || serp.defaultDatasetId);
            const sp = join(baseDir, `${baseName}_serp.json`);
            writeFileSync(sp, JSON.stringify(items, null, 2));
            console.log(`Saved SERP → ${sp} (${items.length} rows)`);
        }

        const wcc = findSubActor(subIndex, 'website-content-crawler');
        if (wcc && (wcc.datasetId || wcc.defaultDatasetId)) {
            const items = await fetchDatasetItems(token, wcc.datasetId || wcc.defaultDatasetId);
            const wp = join(baseDir, `${baseName}_wcc.json`);
            writeFileSync(wp, JSON.stringify(items, null, 2));
            console.log(`Saved WCC → ${wp} (${items.length} rows)`);
        }
    } else {
        console.log('Note: no sub-Actor index on the run.');
    }

    const meta = {
        runId: runData.id,
        actorId: runData.actId,
        startedAt: runData.startedAt,
        finishedAt: runData.finishedAt,
        status: runData.status,
        datasetIds: {
            default: runData.defaultDatasetId,
            keyValueStore: runData.defaultKeyValueStoreId,
        },
        consoleUrl: `https://console.apify.com/actors/runs/${runData.id}`,
    };
    const mp = join(baseDir, `${baseName}_run_metadata.json`);
    writeFileSync(mp, JSON.stringify(meta, null, 2));
    console.log(`Saved metadata → ${mp}`);
}

main().catch((e) => { console.error(`Error: ${e.message}`); process.exit(1); });
