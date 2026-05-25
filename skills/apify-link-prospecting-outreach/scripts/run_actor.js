#!/usr/bin/env node
/**
 * Apify Actor Runner for the link-prospecting-outreach skill.
 *
 * Runs apify/link-prospecting-tool (or any compatible Actor), waits for the run
 * to finish, and downloads the default dataset. With --fetch-sub-datasets it
 * also pulls the Mentions, Author list, and the Google Search Scraper + WCC
 * sub-Actor datasets so the agent has everything it needs to populate every
 * output column.
 *
 * Usage:
 *   node --env-file=.env scripts/run_actor.js \
 *     --actor "apify/link-prospecting-tool" \
 *     --input '{"queries":"...","brand":"..."}' \
 *     --timeout 900 \
 *     --fetch-sub-datasets \
 *     --output outreach.json --format json
 */

import { parseArgs } from 'node:util';
import { writeFileSync, readFileSync, statSync } from 'node:fs';
import { dirname, basename, extname, join } from 'node:path';

// User-Agent for tracking skill usage in Apify analytics
const USER_AGENT = 'apify-awesome-skills/link-prospecting-outreach-1.0.0';

function parseCliArgs() {
    const options = {
        actor: { type: 'string', short: 'a' },
        input: { type: 'string', short: 'i' },
        output: { type: 'string', short: 'o' },
        format: { type: 'string', short: 'f', default: 'json' },
        timeout: { type: 'string', short: 't', default: '1800' },
        'poll-interval': { type: 'string', default: '5' },
        'fetch-sub-datasets': { type: 'boolean', default: false },
        help: { type: 'boolean', short: 'h' },
    };

    const { values } = parseArgs({ options, allowPositionals: false });

    if (values.help) {
        printHelp();
        process.exit(0);
    }

    if (!values.actor) {
        console.error('Error: --actor is required');
        printHelp();
        process.exit(1);
    }

    if (!values.input) {
        console.error('Error: --input is required');
        printHelp();
        process.exit(1);
    }

    return {
        actor: values.actor,
        input: values.input,
        output: values.output,
        format: values.format || 'json',
        timeout: parseInt(values.timeout, 10),
        pollInterval: parseInt(values['poll-interval'], 10),
        fetchSubDatasets: values['fetch-sub-datasets'],
    };
}

function printHelp() {
    console.log(`
Apify Actor Runner (link-prospecting-outreach skill)

Usage:
  node --env-file=.env scripts/run_actor.js \\
    --actor "apify/link-prospecting-tool" \\
    --input 'JSON' \\
    [--timeout 900] [--fetch-sub-datasets] \\
    [--output file.json] [--format json|csv|xlsx]

Options:
  --actor, -a              Actor ID (e.g., apify/link-prospecting-tool) [required]
  --input, -i              Actor input as JSON string [required]
  --output, -o             Output file path; if omitted, prints a short summary
  --format, -f             Output format: json, csv, xlsx (default: json)
  --timeout, -t            Max wait time in seconds (default: 1800). Raise to 2700+ for 5+ keyword + all-LLM-engine campaigns. If it still elapses with the Actor still running, use scripts/fetch_run_artifacts.js to poll the existing runId without restarting.
  --poll-interval          Seconds between status checks (default: 5)
  --fetch-sub-datasets     Also download: Mentions, Author list, Sub-Actor index,
                           Google Search Scraper sub-dataset, and Website Content
                           Crawler sub-dataset. Writes them next to --output with
                           suffixes _mentions, _authors, _serp, _wcc, _sub.
  --help, -h               Show this help

Examples:
  # Full run with all sub-datasets, json output
  node --env-file=.env scripts/run_actor.js \\
    --actor "apify/link-prospecting-tool" \\
    --input '{"queries":"<keyword 1>\\n<keyword 2>","brand":"<your-brand>"}' \\
    --timeout 1200 \\
    --fetch-sub-datasets \\
    --output outreach.json --format json

  # xlsx output for spreadsheet-first workflows
  node --env-file=.env scripts/run_actor.js \\
    --actor "apify/link-prospecting-tool" \\
    --input 'JSON' \\
    --fetch-sub-datasets \\
    --output outreach.xlsx --format xlsx
`);
}

// Start an actor run and return { runId, datasetId }
async function startActor(token, actorId, inputJson) {
    const apiActorId = actorId.replace('/', '~');
    const url = `https://api.apify.com/v2/acts/${apiActorId}/runs?token=${encodeURIComponent(token)}`;

    let data;
    try {
        data = JSON.parse(inputJson);
    } catch (e) {
        console.error(`Error: Invalid JSON input: ${e.message}`);
        process.exit(1);
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'User-Agent': `${USER_AGENT}/start_actor`,
        },
        body: JSON.stringify(data),
    });

    if (response.status === 404) {
        console.error(`Error: Actor '${actorId}' not found`);
        process.exit(1);
    }

    if (!response.ok) {
        const text = await response.text();
        console.error(`Error: API request failed (${response.status}): ${text}`);
        process.exit(1);
    }

    const result = await response.json();
    return {
        runId: result.data.id,
        datasetId: result.data.defaultDatasetId,
        startedAt: result.data.startedAt,
    };
}

// Get full run details (used to discover named datasets and sub-runs)
async function getRunDetails(token, runId) {
    const url = `https://api.apify.com/v2/actor-runs/${runId}?token=${encodeURIComponent(token)}`;
    const response = await fetch(url, {
        headers: { 'User-Agent': `${USER_AGENT}/run_details` },
    });
    if (!response.ok) {
        const text = await response.text();
        console.error(`Error: Failed to get run details: ${text}`);
        process.exit(1);
    }
    const result = await response.json();
    return result.data;
}

// Poll run status until complete or timeout
async function pollUntilComplete(token, runId, timeout, interval) {
    const url = `https://api.apify.com/v2/actor-runs/${runId}?token=${encodeURIComponent(token)}`;
    const startTime = Date.now();
    let lastStatus = null;

    while (true) {
        const response = await fetch(url);
        if (!response.ok) {
            const text = await response.text();
            console.error(`Error: Failed to get run status: ${text}`);
            process.exit(1);
        }

        const result = await response.json();
        const status = result.data.status;

        if (status !== lastStatus) {
            console.log(`Status: ${status}`);
            lastStatus = status;
        }

        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) {
            return { status, runData: result.data };
        }

        const elapsed = (Date.now() - startTime) / 1000;
        if (elapsed > timeout) {
            console.error(`Warning: Client-side wait timeout after ${timeout}s; run may still finish on Apify.`);
            console.error(`Check: https://console.apify.com/actors/runs/${runId}`);
            return { status: 'TIMED-OUT', runData: result.data };
        }

        await sleep(interval * 1000);
    }
}

// Fetch dataset items as parsed JSON
async function fetchDatasetItems(token, datasetId) {
    const url = `https://api.apify.com/v2/datasets/${datasetId}/items?token=${encodeURIComponent(token)}&format=json`;
    const response = await fetch(url, {
        headers: { 'User-Agent': `${USER_AGENT}/fetch_dataset` },
    });
    if (!response.ok) {
        const text = await response.text();
        console.error(`Error: Failed to download dataset ${datasetId}: ${text}`);
        return [];
    }
    return response.json();
}

// Resolve a named storage on a run (e.g., the Mentions or Author list dataset)
function resolveNamedDataset(runData, candidateNames) {
    const named = runData.namedDatasetIds || runData.namedDatasets || {};
    for (const name of candidateNames) {
        if (named[name]) return named[name];
        const lowered = Object.keys(named).find((k) => k.toLowerCase() === name.toLowerCase());
        if (lowered) return named[lowered];
    }
    return null;
}

// Discover sub-Actor run IDs from the parent run.
// Pre-2026-05-20 versions of apify/link-prospecting-tool wrote a SUB_ACTOR_RESULTS
// record to the default KV store with {actorId, runId, datasetId} entries. The
// current version no longer does. Strategy: try the KV record first; if missing,
// fall back to parsing the parent run log for "[apify.<slug> runId:<id>]" markers
// and resolving each sub-runId's defaultDatasetId via the API.
async function fetchSubActorIndex(token, runData) {
    const kvStoreId = runData.defaultKeyValueStoreId;
    if (kvStoreId) {
        const candidateKeys = ['SUB_ACTOR_RESULTS', 'sub_actor_results', 'SUB_ACTORS', 'subActors'];
        for (const key of candidateKeys) {
            const url = `https://api.apify.com/v2/key-value-stores/${kvStoreId}/records/${key}?token=${encodeURIComponent(token)}`;
            const response = await fetch(url, {
                headers: { 'User-Agent': `${USER_AGENT}/fetch_subactors` },
            });
            if (response.ok) {
                try {
                    const parsed = await response.json();
                    if (Array.isArray(parsed) && parsed.length) return parsed;
                } catch {
                    continue;
                }
            }
        }
    }
    // Fallback: log-parsing
    return fetchSubActorIndexFromLog(token, runData.id);
}

async function fetchSubActorIndexFromLog(token, parentRunId) {
    const url = `https://api.apify.com/v2/actor-runs/${parentRunId}/log?token=${encodeURIComponent(token)}`;
    const response = await fetch(url, {
        headers: { 'User-Agent': `${USER_AGENT}/fetch_subactors_log` },
    });
    if (!response.ok) {
        console.warn('Could not fetch parent run log for sub-Actor discovery; skipping.');
        return [];
    }
    const log = await response.text();
    const re = /\[apify\.([a-z0-9-]+) runId:([A-Za-z0-9]+)\]/g;
    const seen = new Map();
    let m;
    while ((m = re.exec(log)) !== null) {
        const key = `${m[1]}:${m[2]}`;
        if (!seen.has(key)) seen.set(key, { actorSlug: m[1], runId: m[2] });
    }
    const subs = Array.from(seen.values());
    if (!subs.length) return [];

    // Resolve defaultDatasetId for each sub-run
    const out = [];
    for (const s of subs) {
        try {
            const r = await fetch(
                `https://api.apify.com/v2/actor-runs/${s.runId}?token=${encodeURIComponent(token)}`,
                { headers: { 'User-Agent': `${USER_AGENT}/fetch_subrun` } },
            );
            if (!r.ok) continue;
            const data = (await r.json()).data;
            out.push({
                actorId: `apify/${s.actorSlug}`,
                runId: s.runId,
                datasetId: data.defaultDatasetId,
            });
        } catch {
            // best-effort
        }
    }
    console.log(`Discovered ${out.length} sub-Actor run(s) via log-parsing (KV index was empty).`);
    return out;
}

// Find a sub-Actor entry whose actor id contains a given substring.
function findSubActor(subIndex, actorSubstring) {
    if (!Array.isArray(subIndex)) return null;
    return subIndex.find((entry) => {
        const id = (entry.actorId || entry.actor || '').toLowerCase();
        return id.includes(actorSubstring.toLowerCase());
    }) || null;
}

async function downloadAllArtifacts(token, runId, primaryDatasetId, outputPath, format, fetchSub) {
    const baseDir = outputPath ? dirname(outputPath) : '.';
    const baseName = outputPath
        ? basename(outputPath, extname(outputPath))
        : `run_${runId}`;

    // Main dataset
    const mainData = await fetchDatasetItems(token, primaryDatasetId);
    if (outputPath) {
        await writeOutput(outputPath, format, mainData);
        console.log(`Saved main dataset to: ${outputPath}`);
        reportSummary(outputPath, format, mainData.length);
    } else {
        displayQuickAnswer(mainData, primaryDatasetId);
    }

    if (!fetchSub) return { mainData, sidecarPaths: {} };

    // Get full run details to find the named datasets and the sub-Actor index
    const runData = await getRunDetails(token, runId);
    const sidecarPaths = {};

    // Named datasets on the parent run
    const namedMap = {
        mentions: ['MENTIONS', 'Mentions', 'mentions'],
        authors: ['AUTHORS', 'AUTHOR_LIST', 'Authors', 'authors', 'authorList'],
        domainsWithLeads: ['DOMAINS_WITH_LEADS', 'DomainsWithLeads', 'domainsWithLeads'],
    };
    for (const [label, names] of Object.entries(namedMap)) {
        const dsId = resolveNamedDataset(runData, names);
        if (dsId) {
            const items = await fetchDatasetItems(token, dsId);
            const path = join(baseDir, `${baseName}_${label}.json`);
            writeFileSync(path, JSON.stringify(items, null, 2));
            console.log(`Saved ${label} dataset to: ${path} (${items.length} rows)`);
            sidecarPaths[label] = path;
        } else {
            console.log(`Note: no named dataset found for "${label}" on the parent run.`);
        }
    }

    // Sub-Actor results index
    const subIndex = await fetchSubActorIndex(token, runData);
    if (Array.isArray(subIndex) && subIndex.length) {
        const indexPath = join(baseDir, `${baseName}_sub.json`);
        writeFileSync(indexPath, JSON.stringify(subIndex, null, 2));
        sidecarPaths.subIndex = indexPath;
        console.log(`Saved sub-Actor index to: ${indexPath} (${subIndex.length} entries)`);

        const serpEntry = findSubActor(subIndex, 'google-search-scraper');
        if (serpEntry && (serpEntry.datasetId || serpEntry.defaultDatasetId)) {
            const items = await fetchDatasetItems(token, serpEntry.datasetId || serpEntry.defaultDatasetId);
            const path = join(baseDir, `${baseName}_serp.json`);
            writeFileSync(path, JSON.stringify(items, null, 2));
            console.log(`Saved Google Search Scraper sub-dataset to: ${path} (${items.length} rows)`);
            sidecarPaths.serp = path;
        } else {
            console.log('Note: no Google Search Scraper sub-Actor entry found in the index.');
        }

        const wccEntry = findSubActor(subIndex, 'website-content-crawler');
        if (wccEntry && (wccEntry.datasetId || wccEntry.defaultDatasetId)) {
            const items = await fetchDatasetItems(token, wccEntry.datasetId || wccEntry.defaultDatasetId);
            const path = join(baseDir, `${baseName}_wcc.json`);
            writeFileSync(path, JSON.stringify(items, null, 2));
            console.log(`Saved Website Content Crawler sub-dataset to: ${path} (${items.length} rows)`);
            sidecarPaths.wcc = path;
        } else {
            console.log('Note: no Website Content Crawler sub-Actor entry found in the index.');
        }
    } else {
        console.log('Note: no sub-Actor index found on the parent run. SERP positions and WCC body text will not be available unless fetched manually from the Apify console.');
    }

    return { mainData, sidecarPaths, runData };
}

async function writeOutput(outputPath, format, data) {
    if (format === 'json') {
        writeFileSync(outputPath, JSON.stringify(data, null, 2));
        return;
    }
    if (format === 'csv') {
        writeFileSync(outputPath, toCsv(data));
        return;
    }
    if (format === 'xlsx') {
        const XLSX = await loadXlsx();
        if (!XLSX) {
            console.error('Error: xlsx format requested but the "xlsx" package is not installed. Run `npm install` inside scripts/.');
            process.exit(1);
        }
        const ws = XLSX.utils.json_to_sheet(data);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, 'Outreach');
        XLSX.writeFile(wb, outputPath);
        return;
    }
    console.error(`Error: unknown --format "${format}". Use json, csv, or xlsx.`);
    process.exit(1);
}

async function loadXlsx() {
    try {
        return (await import('xlsx')).default;
    } catch {
        return null;
    }
}

function toCsv(data) {
    if (!data.length) return '';
    const fieldnames = Object.keys(data[0]);
    const csvLines = [fieldnames.join(',')];
    for (const row of data) {
        const values = fieldnames.map((key) => {
            let value = row[key];
            if (typeof value === 'string' && value.length > 200) {
                value = value.slice(0, 200) + '...';
            } else if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
                value = JSON.stringify(value) || '';
            }
            if (value === null || value === undefined) return '';
            const strValue = String(value);
            if (strValue.includes(',') || strValue.includes('"') || strValue.includes('\n')) {
                return `"${strValue.replace(/"/g, '""')}"`;
            }
            return strValue;
        });
        csvLines.push(values.join(','));
    }
    return csvLines.join('\n');
}

function displayQuickAnswer(data, datasetId) {
    const total = data.length;
    if (total === 0) {
        console.log('\nNo leads returned. See reference/troubleshooting.md → "0 leads returned".');
        return;
    }
    console.log(`\n${'='.repeat(60)}`);
    console.log(`TOP 5 LEADS (of ${total} total)`);
    console.log('='.repeat(60));
    for (let i = 0; i < Math.min(5, data.length); i++) {
        const item = data[i];
        console.log(`\n--- Lead ${i + 1} ---`);
        for (const [key, value] of Object.entries(item)) {
            let displayValue = value;
            if (typeof value === 'string' && value.length > 100) {
                displayValue = value.slice(0, 100) + '...';
            } else if (Array.isArray(value) || (typeof value === 'object' && value !== null)) {
                const jsonStr = JSON.stringify(value);
                displayValue = jsonStr.length > 100 ? jsonStr.slice(0, 100) + '...' : jsonStr;
            }
            console.log(`  ${key}: ${displayValue}`);
        }
    }
    console.log(`\n${'='.repeat(60)}`);
    if (total > 5) console.log(`Showing 5 of ${total} leads.`);
    console.log(`Full data: https://console.apify.com/storage/datasets/${datasetId}`);
    console.log('='.repeat(60));
}

function reportSummary(outputPath, format, fallbackCount) {
    try {
        const stats = statSync(outputPath);
        const size = stats.size;
        let count = fallbackCount;
        if (typeof count !== 'number') {
            const content = readFileSync(outputPath, 'utf-8');
            if (format === 'json') {
                const data = JSON.parse(content);
                count = Array.isArray(data) ? data.length : 1;
            } else if (format === 'csv') {
                const lines = content.split('\n').filter((line) => line.trim());
                count = Math.max(0, lines.length - 1);
            } else {
                count = 'unknown';
            }
        }
        console.log(`Records: ${count}`);
        console.log(`Size: ${size.toLocaleString()} bytes`);
    } catch {
        // ignore summary failures
    }
}

// Write the run_metadata.json sidecar
function writeRunMetadata(outputPath, runData, inputs) {
    if (!outputPath) return;
    const baseDir = dirname(outputPath);
    const baseName = basename(outputPath, extname(outputPath));
    const metadataPath = join(baseDir, `${baseName}_run_metadata.json`);
    const metadata = {
        runId: runData.id,
        actorId: runData.actId,
        startedAt: runData.startedAt,
        finishedAt: runData.finishedAt,
        status: runData.status,
        inputs,
        datasetIds: {
            default: runData.defaultDatasetId,
            keyValueStore: runData.defaultKeyValueStoreId,
        },
        consoleUrl: `https://console.apify.com/actors/runs/${runData.id}`,
    };
    writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    console.log(`Saved run metadata to: ${metadataPath}`);
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
    const args = parseCliArgs();

    const token = process.env.APIFY_TOKEN;
    if (!token) {
        console.error('Error: APIFY_TOKEN not found in .env file');
        console.error('');
        console.error('Add your token to .env file:');
        console.error('  APIFY_TOKEN=your_token_here');
        console.error('');
        console.error('Get your token: https://console.apify.com/account/integrations');
        process.exit(1);
    }

    console.log(`Starting actor: ${args.actor}`);
    const { runId, datasetId } = await startActor(token, args.actor, args.input);
    console.log(`Run ID: ${runId}`);
    console.log(`Dataset ID: ${datasetId}`);

    const { status, runData } = await pollUntilComplete(token, runId, args.timeout, args.pollInterval);

    if (status !== 'SUCCEEDED') {
        console.error(`Error: Actor run ${status}`);
        console.error(`Details: https://console.apify.com/actors/runs/${runId}`);
        if (status === 'TIMED-OUT') {
            console.error('Tip: see reference/troubleshooting.md → "Actor run TIMED-OUT".');
        }
        process.exit(1);
    }

    let inputsParsed = {};
    try {
        inputsParsed = JSON.parse(args.input);
    } catch {
        // best-effort, metadata will skip
    }

    await downloadAllArtifacts(token, runId, datasetId, args.output, args.format, args.fetchSubDatasets);

    if (args.output) {
        writeRunMetadata(args.output, runData, inputsParsed);
    }
}

main().catch((err) => {
    console.error(`Error: ${err.message}`);
    process.exit(1);
});
