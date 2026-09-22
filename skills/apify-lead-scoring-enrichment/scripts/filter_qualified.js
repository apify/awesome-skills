#!/usr/bin/env node
// Filter leads.csv to only the rows the agent marked qualified in scored.json.
// Pure Node — no Actor calls. The agent must have written `qualified: true`
// (or `qualified: false`) on each row of scored.json before running this.
//
// Usage:
//   node scripts/filter_qualified.js \
//     --leads leads.csv \
//     --scores scored.json \
//     --output qualified_leads.csv

import { parseArgs } from 'node:util';
import { readFileSync, writeFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import { toCanonicalUrl } from './apify_client.js';

const { values } = parseArgs({
    options: {
        leads: { type: 'string' },
        scores: { type: 'string' },
        output: { type: 'string' },
    },
});

if (!values.leads || !values.scores || !values.output) {
    console.error('Usage: filter_qualified.js --leads <leads.csv> --scores <scored.json> --output <qualified_leads.csv>');
    process.exit(1);
}

const rows = parse(readFileSync(values.leads, 'utf8'), { columns: true, skip_empty_lines: true, trim: true });
const scored = JSON.parse(readFileSync(values.scores, 'utf8'));

const qualified = rows.filter((row) => {
    const canon = toCanonicalUrl(row.company_url);
    const entry = scored[canon];
    return entry && entry.qualified === true;
});

if (!rows.length) {
    console.error('Error: leads.csv is empty.');
    process.exit(1);
}
if (!qualified.length) {
    console.error('Warning: 0 leads qualified. Enrichment would be a no-op — lower your threshold or fix your rules.');
}

const columns = Object.keys(rows[0]);
writeFileSync(values.output, stringify(qualified, { header: true, columns }));
console.error(`Wrote ${values.output} — ${qualified.length}/${rows.length} leads qualified (${((qualified.length / rows.length) * 100).toFixed(0)}%).`);
