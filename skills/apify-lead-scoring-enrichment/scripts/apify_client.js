// Thin Apify REST-API wrapper shared by all lead-scoring-enrichment scripts.
// No SDK dependency — uses global fetch (Node 18+).

export const USER_AGENT = 'apify-awesome-skills/apify-lead-scoring-enrichment';

function getToken() {
    const token = process.env.APIFY_TOKEN;
    if (!token) {
        console.error('Error: APIFY_TOKEN is not set. Load via `node --env-file=.env ...` or export it.');
        process.exit(1);
    }
    return token;
}

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

// Start an Actor run, poll until it terminates, return {status, runData}.
export async function runActor(actorId, input, { timeoutSec = 900, pollIntervalSec = 5, sourceTag = 'run' } = {}) {
    const token = getToken();
    const slug = actorId.replace('/', '~');
    const startUrl = `https://api.apify.com/v2/acts/${slug}/runs?token=${encodeURIComponent(token)}`;

    const startResp = await fetch(startUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'User-Agent': `${USER_AGENT}/${sourceTag}`,
        },
        body: JSON.stringify(input),
    });
    if (!startResp.ok) {
        const text = await startResp.text();
        throw new Error(`Failed to start ${actorId}: ${startResp.status} ${text}`);
    }
    const { data: runStart } = await startResp.json();
    const runId = runStart.id;
    console.error(`Started ${actorId} run ${runId}`);

    const runUrl = `https://api.apify.com/v2/actor-runs/${runId}?token=${encodeURIComponent(token)}`;
    const start = Date.now();
    let lastStatus = null;
    while (true) {
        const resp = await fetch(runUrl, {
            headers: { 'User-Agent': `${USER_AGENT}/${sourceTag}_poll` },
        });
        if (!resp.ok) {
            const text = await resp.text();
            throw new Error(`Failed to poll run ${runId}: ${resp.status} ${text}`);
        }
        const { data } = await resp.json();
        if (data.status !== lastStatus) {
            console.error(`  ${actorId} → ${data.status}`);
            lastStatus = data.status;
        }
        if (['SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'].includes(data.status)) {
            return { status: data.status, runData: data };
        }
        if ((Date.now() - start) / 1000 > timeoutSec) {
            console.error(`Warning: client-side wait timed out after ${timeoutSec}s. Run may still finish on Apify.`);
            console.error(`  Check: https://console.apify.com/actors/runs/${runId}`);
            return { status: 'TIMED-OUT', runData: data };
        }
        await sleep(pollIntervalSec * 1000);
    }
}

// Fetch all items from a dataset as parsed JSON.
export async function fetchDatasetItems(datasetId, { sourceTag = 'fetch' } = {}) {
    const token = getToken();
    const url = `https://api.apify.com/v2/datasets/${datasetId}/items?token=${encodeURIComponent(token)}&format=json`;
    const resp = await fetch(url, {
        headers: { 'User-Agent': `${USER_AGENT}/${sourceTag}` },
    });
    if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`Failed to fetch dataset ${datasetId}: ${resp.status} ${text}`);
    }
    return resp.json();
}

// Run an Actor and return its default-dataset items in one call.
export async function runActorAndGetItems(actorId, input, opts = {}) {
    const { status, runData } = await runActor(actorId, input, opts);
    if (status !== 'SUCCEEDED') {
        console.error(`Warning: ${actorId} ended with status=${status}. Attempting to fetch dataset anyway.`);
    }
    if (!runData.defaultDatasetId) {
        console.error(`Warning: ${actorId} run ${runData.id} has no default dataset.`);
        return [];
    }
    return fetchDatasetItems(runData.defaultDatasetId, { sourceTag: `${opts.sourceTag || 'run'}_items` });
}

// Normalize a URL to a bare hostname (lowercase, no scheme, no www, no path).
export function toDomain(url) {
    if (!url) return '';
    let s = String(url).trim().toLowerCase();
    s = s.replace(/^https?:\/\//, '');
    s = s.replace(/^www\./, '');
    s = s.split('/')[0].split('?')[0];
    return s;
}

// Normalize a URL to a canonical https://domain form for keying sidecars.
export function toCanonicalUrl(url) {
    const d = toDomain(url);
    return d ? `https://${d}` : '';
}
