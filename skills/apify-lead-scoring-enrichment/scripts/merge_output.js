#!/usr/bin/env node
// Pure-Node merge: joins scoring.json + enrichment.json (+ optional scored.json
// from the agent) onto the input CSV keyed by canonical https://domain and
// writes leads.enriched.csv.
//
// Usage:
//   node scripts/merge_output.js \
//     --leads leads.csv \
//     --scoring scoring.json \
//     --enrichment enrichment.json \
//     [--scores scored.json] \
//     --output leads.enriched.csv

import { parseArgs } from 'node:util';
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { stringify } from 'csv-stringify/sync';
import { toCanonicalUrl } from './apify_client.js';

const { values } = parseArgs({
    options: {
        leads: { type: 'string' },
        scoring: { type: 'string' },
        enrichment: { type: 'string' },
        scores: { type: 'string' },
        output: { type: 'string' },
    },
});

if (!values.leads || !values.output) {
    console.error('Usage: merge_output.js --leads <leads.csv> [--scoring scoring.json] [--enrichment enrichment.json] [--scores scored.json] --output <leads.enriched.csv>');
    process.exit(1);
}

const rows = parse(readFileSync(values.leads, 'utf8'), { columns: true, skip_empty_lines: true, trim: true });

function loadJson(path) {
    if (!path) return {};
    if (!existsSync(path)) {
        console.error(`Warning: ${path} not found — skipping.`);
        return {};
    }
    return JSON.parse(readFileSync(path, 'utf8'));
}

const scoring = loadJson(values.scoring);
const enrichment = loadJson(values.enrichment);
const scores = loadJson(values.scores);

function techSummary(t) {
    if (!t) return '';
    // BuiltWith outputs vary; try common shapes.
    const groups = t.techs || t.technologies || t.techStack || t.Results?.[0]?.Result?.Paths?.[0]?.Technologies || [];
    if (Array.isArray(groups) && groups.length) {
        return groups.slice(0, 8).map((g) => g.name || g.Name || g).filter(Boolean).join(', ');
    }
    return '';
}

function contentSummary(c) {
    if (!c) return '';
    const text = c.markdown || c.text || c.pageContent || '';
    return text ? text.replace(/\s+/g, ' ').slice(0, 240) : '';
}

function metaField(m, ...keys) {
    if (!m) return '';
    for (const k of keys) {
        if (m[k]) return m[k];
    }
    return '';
}

const enrichedRows = rows.map((row) => {
    const canon = toCanonicalUrl(row.company_url);
    const sc = scoring[canon] || {};
    const en = enrichment[canon] || {};
    const scored = scores[canon] || {};

    return {
        ...row,
        tech_summary: techSummary(sc.tech),
        content_summary: contentSummary(sc.content),
        company_size: metaField(sc.metadata, 'companySize', 'size', 'employees'),
        industry: metaField(sc.metadata, 'industry', 'category'),
        tech_score: scored.tech_score ?? '',
        content_score: scored.content_score ?? '',
        metadata_score: scored.metadata_score ?? '',
        score: scored.score ?? '',
        qualified: typeof scored.qualified === 'boolean' ? String(scored.qualified) : '',
        outreach_hook: scored.outreach_hook ?? '',
        leads: Array.isArray(en.leads) && en.leads.length ? JSON.stringify(en.leads) : '',
        lead_names: Array.isArray(en.leads) ? en.leads.map((l) => l.fullName).filter(Boolean).join(';') : '',
        lead_titles: Array.isArray(en.leads) ? en.leads.map((l) => l.title).filter(Boolean).join(';') : '',
        emails: Array.isArray(en.emails) ? en.emails.join(';') : '',
        authors: Array.isArray(en.authors) ? en.authors.map((a) => a.name).join(';') : '',
    };
});

const columns = Object.keys(enrichedRows[0] || {});
writeFileSync(values.output, stringify(enrichedRows, { header: true, columns }));
console.error(`Wrote ${values.output} — ${enrichedRows.length} rows, ${columns.length} columns.`);
