#!/usr/bin/env node
// Calls vdrmota/contact-info-scraper with its "Business leads enrichment"
// add-on enabled (maximumLeadsEnrichmentRecords + leadsEnrichmentDepartments)
// to return actual people per domain. For any lead that comes back without a
// resolved email, falls back to scalelist/bulk-email-finder-dep on the
// (firstName, lastName, domain) triple.
//
// Usage:
//   node --env-file=.env scripts/enrich_departments.js \
//     --input leads.csv \
//     --department marketing,sales \
//     --max-leads 5 \
//     [--verify-emails] \
//     --output enrichment.json
//
// --department accepts one or more of the Actor's enum values (comma-separated):
//   c_suite, product, engineering_technical, design, education, finance,
//   human_resources, information_technology, legal, marketing, medical_health,
//   operations, sales, consulting

import { parseArgs } from 'node:util';
import { readFileSync, writeFileSync } from 'node:fs';
import { parse } from 'csv-parse/sync';
import { runActorAndGetItems, toCanonicalUrl, toDomain } from './apify_client.js';

const VALID_DEPARTMENTS = new Set([
    'c_suite', 'product', 'engineering_technical', 'design', 'education',
    'finance', 'human_resources', 'information_technology', 'legal',
    'marketing', 'medical_health', 'operations', 'sales', 'consulting',
]);

const { values } = parseArgs({
    options: {
        input: { type: 'string' },
        output: { type: 'string' },
        department: { type: 'string' },
        'max-leads': { type: 'string', default: '5' },
        'verify-emails': { type: 'boolean', default: false },
    },
});

if (!values.input || !values.output || !values.department) {
    console.error('Usage: enrich_departments.js --input <leads.csv> --department <dept[,dept...]> --max-leads N [--verify-emails] --output <enrichment.json>');
    console.error(`Valid departments: ${[...VALID_DEPARTMENTS].join(', ')}`);
    process.exit(1);
}

const departments = values.department.split(',').map((s) => s.trim()).filter(Boolean);
const invalid = departments.filter((d) => !VALID_DEPARTMENTS.has(d));
if (invalid.length) {
    console.error(`Error: invalid department(s): ${invalid.join(', ')}`);
    console.error(`Valid: ${[...VALID_DEPARTMENTS].join(', ')}`);
    process.exit(1);
}

const maxLeads = parseInt(values['max-leads'], 10);
if (!Number.isFinite(maxLeads) || maxLeads < 1) {
    console.error('Error: --max-leads must be a positive integer.');
    process.exit(1);
}

const csvText = readFileSync(values.input, 'utf8');
const rows = parse(csvText, { columns: true, skip_empty_lines: true, trim: true });
if (!rows.length || !('company_url' in rows[0])) {
    console.error('Error: input CSV needs a "company_url" column.');
    process.exit(1);
}

const urls = [...new Set(rows.map((r) => toCanonicalUrl(r.company_url)).filter(Boolean))];
console.error(`Enriching ${urls.length} unique URLs — departments: ${departments.join(', ')}, max leads/domain: ${maxLeads}`);
console.error(`Estimated cost: up to ${urls.length * maxLeads} leads (charged only for leads successfully found).`);

const sidecar = Object.fromEntries(urls.map((u) => [u, { leads: [], emails: [], source: null }]));

// ---- Primary call: contact-info-scraper with Business leads enrichment on.
console.error('→ Running vdrmota/contact-info-scraper (Business leads enrichment ON)…');
const contactItems = await runActorAndGetItems(
    'vdrmota/contact-info-scraper',
    {
        startUrls: urls.map((u) => ({ url: u })),
        maxRequestsPerStartUrl: 1,
        mergeContacts: true,
        maxDepth: 0,
        maximumLeadsEnrichmentRecords: maxLeads,
        leadsEnrichmentDepartments: departments,
        verifyLeadsEnrichmentEmails: values['verify-emails'],
    },
    { sourceTag: 'departments_primary', timeoutSec: 1800 },
);
console.error(`  contact-info: ${contactItems.length} items back.`);

// Output item is one row per start URL (mergeContacts=true). Leads live under
// `leadsEnrichment` / `leads` / `businessLeads` depending on Actor version.
function extractLeads(item) {
    return item.leadsEnrichment
        || item.leads
        || item.businessLeads
        || item.employees
        || [];
}

for (const item of contactItems) {
    const canon = toCanonicalUrl(item.url || item.startUrl || item.domain);
    if (!canon || !(canon in sidecar)) continue;

    const rawLeads = extractLeads(item);
    for (const lead of rawLeads) {
        const email = lead.email || lead.workEmail || lead.emailAddress || null;
        const first = lead.firstName || lead.first_name || (lead.name || '').split(/\s+/)[0] || '';
        const last = lead.lastName || lead.last_name || (lead.name || '').split(/\s+/).slice(1).join(' ') || '';
        const person = {
            firstName: first,
            lastName: last,
            fullName: lead.name || `${first} ${last}`.trim(),
            title: lead.title || lead.jobTitle || lead.role || '',
            department: lead.department || departments[0] || '',
            email,
            emailVerification: lead.emailVerification || null,
            linkedin: lead.linkedin || lead.linkedInUrl || lead.linkedIn || null,
            phone: lead.phone || null,
            source: 'contact-info-scraper',
        };
        sidecar[canon].leads.push(person);
        if (email) sidecar[canon].emails.push(email);
    }
    if (rawLeads.length && !sidecar[canon].source) sidecar[canon].source = 'contact-info-scraper';
}

// Dedup emails per URL.
for (const canon of Object.keys(sidecar)) {
    sidecar[canon].emails = [...new Set(sidecar[canon].emails)];
}

// ---- Fallback: leads with a first+last name but no email → bulk-email-finder-dep.
const noEmailLeads = [];
for (const [canon, entry] of Object.entries(sidecar)) {
    for (const lead of entry.leads) {
        if (!lead.email && lead.firstName && lead.lastName) {
            noEmailLeads.push({ canon, lead, domain: toDomain(canon) });
        }
    }
}

if (noEmailLeads.length) {
    console.error(`→ Fallback: ${noEmailLeads.length} leads have no email → scalelist/bulk-email-finder-dep…`);
    let finderItems = [];
    try {
        finderItems = await runActorAndGetItems(
            'scalelist/bulk-email-finder-dep',
            {
                leads: noEmailLeads.map(({ lead, domain }) => ({
                    first_name: lead.firstName,
                    last_name: lead.lastName,
                    company_domain: domain,
                })),
            },
            { sourceTag: 'departments_fallback', timeoutSec: 900 },
        );
    } catch (e) {
        console.error(`  bulk-email-finder-dep failed: ${e.message}. Continuing without fallback data.`);
    }
    console.error(`  email-finder: ${finderItems.length} items back.`);

    for (const item of finderItems) {
        const email = item.email || item.emailAddress;
        if (!email) continue;
        const domain = (item.company_domain || item.domain || '').toLowerCase();
        const first = (item.first_name || item.firstName || '').toLowerCase();
        const last = (item.last_name || item.lastName || '').toLowerCase();
        const match = noEmailLeads.find(({ lead, domain: d }) =>
            d === domain
            && lead.firstName.toLowerCase() === first
            && lead.lastName.toLowerCase() === last);
        if (!match) continue;
        match.lead.email = email;
        match.lead.source = 'bulk-email-finder-dep';
        sidecar[match.canon].emails.push(email);
    }

    for (const canon of Object.keys(sidecar)) {
        sidecar[canon].emails = [...new Set(sidecar[canon].emails)];
    }
}

writeFileSync(values.output, JSON.stringify(sidecar, null, 2));
const withPeople = Object.values(sidecar).filter((v) => v.leads.length).length;
const withEmails = Object.values(sidecar).filter((v) => v.emails.length).length;
console.error(`Wrote ${values.output}. ${withPeople}/${urls.length} URLs have ≥1 lead; ${withEmails}/${urls.length} have ≥1 email.`);
