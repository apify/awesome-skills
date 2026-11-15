# Actor index: EU supplier, payment and counterparty checks

All seven Actors are public on the Apify Store under `lerider/`, pay per event, and return one dataset item per
checked item, in input order, with an `index`. A malformed item returns `{"index": N, "error": "..."}` and is not
charged. Prices below are from each Actor's Store README; confirm live with `apify actors info` (see gotchas.md).

| Actor | Event and price | Single input | Batch input (max) | Main output fields |
|---|---|---|---|---|
| `lerider/payee-check` (payee check) | `payee-check` $0.001 | `iban`, `payee_name`, `amount` (decimal string), `message_text`, `known_payees` | `payments` (1000) | `verdict`, `reasons`, `checks[]` (rule, ok, severity, detail), `bank`, `note` |
| `lerider/payee-check` (supplier pre-flight) | `supplier-preflight` $0.03 | `payee` {`iban` required, `name`, `vat_id`, `peppol_id`}, `invoice` {`text`, `lines`, totals, `buyer_vat_id`, `issue_date`}, `known_payees`, `pay_on` | `preflights` (200) | `verdict`, `score`, `checks` (iban, iban_change, vat, peppol, vat_math, settlement, payee_check), `unavailable`, `reasons`, `disclaimer` |
| `lerider/payee-check` (add-on) | `attested-check` $0.02 per item | `"attest": true` on either mode | same | `attestation` (RFC 3161 timestamp + OpenTimestamps proof); `{"verify": [...]}` checks one for free |
| `lerider/eu-vat-validator` | `vat-check` $0.003, only when VIES answers | `vat_id`, `expected_name` | `vat_ids` (200) | `status`, `valid`, `name`, `name_match`, `checked_at` |
| `lerider/eu-licence-check` | `licence-check` $0.02 per firm | `name`, `lei`, `reg_number`, `domain` (at least one), `country`, `claimed_licence`, `as_of` | `entities` (500) | `verdict`, `status`, `reasons`, `licences`, `warnings`, `sanctions`, `lookalike_domains`, `claimed_licence`, `coverage` |
| `lerider/eori-validator` | `eori-check` $0.002, only when EOS answers | `eori` | `eoris` (500) | `status`, `valid`, `trader`, `checked_at` |
| `lerider/eu-tin-validator` | `tin-check` $0.002, only when the EU TIN service answers | `country`, `tin` (no prefix) | `tins` (200) | `status`, `valid`, `valid_structure`, `valid_syntax` |
| `lerider/eidas-signature-check` | `signature-check` $0.03 per document read | `url` or `pdf_base64`; `signature_url` / `signature_base64` for detached XAdES; `eu_act` + `language`; `require_qualified` | `documents` (20, 25 MB each) | `verdict`, `reasons`, `signatures[]` (intact, trusted, revoked, qualified, qualified_type, qscd, signer, changed_after_signing), `trusted_lists.built_at` |
| `lerider/einvoice-validator` | `invoice-validation` $0.004 | `url`, `file_base64` or `xml`; `profile` (`auto`, `en16931`, `peppol`, `xrechnung`, `all`) | `invoices` (100) | `verdict`, `valid`, `errors[]` (official rule id), `warnings[]`, `summary`, `rules_version` |

## Verdicts per Actor

- **payee-check**. BLOCK: wrong IBAN length or check digits; a known payee name with a new IBAN; the invoice lists
  IBANs but not the one being paid; VIES says the VAT id is invalid. REVIEW: any other failed check (new payee,
  name mismatch, pressure or bank-change wording, VAT maths, Peppol not listed), or a register did not answer.
  ALLOW: every check the input switched on passed. Fewer fields in, fewer checks run.
- **eu-licence-check**. BLOCK: warning-list or EU-sanctions hit (match confidence 0.90 or more). REVIEW: withdrawn
  licence, only a similar name, a licensed name that is also on a warning list (clone risk), a domain the register
  cannot confirm (`domain_unconfirmed`), a source that could not be read, or a warning list older than 7 days.
  ALLOW: an active authorisation was found and nothing is against it.
- **eidas-signature-check**. ALLOW: every signature intact, cryptographically valid, chains to an EU trusted provider,
  not revoked, pages not changed after signing (plus qualified, with `require_qualified: true`). REVIEW: intact but
  trust not fully established. BLOCK: broken signature, revoked certificate, content changed after signing,
  byte-range tricks, unreadable PDF, or no signature at all.
- **einvoice-validator**. ALLOW: no errors against the applicable rules (warnings may remain). REVIEW: no errors but
  not a full e-invoice (Factur-X MINIMUM / BASIC WL, outdated XRechnung). BLOCK: rule or schema errors, or not an
  e-invoice.

## Coverage notes (eu-licence-check)

- Licence registers: ESMA MiFID II register (investment firms, AIFMs, UCITS managers, crowdfunding, trading venues),
  EBA payment and e-money register, ECB list of monetary financial institutions (banks, EU-27), ESMA interim MiCA
  register (CASPs, EMT/ART issuers), AMF PSAN list (FR).
- Warning lists and sanctions: ESMA MiCA non-compliant entities (EU-wide), AMF (FR), FSMA (BE), AFM (NL), EU
  consolidated financial sanctions list (legal entities only).
- Not covered: UK, CH and the rest of the world; national warning lists outside FR, BE and NL (e.g. BaFin, CONSOB,
  CNMV); IOSCO I-SCAN; insurance; purely national licences. These return `not_covered`.
- `lei`: used as a match key (exact match = confidence 1.00) and, with `resolve_lei` on, to look up the legal name at
  GLEIF so registers that list the firm without its LEI still match.
- Data is refreshed daily from the official files; `coverage[].data_as_of` shows the date per source.

## Store and MCP

- Store pages: https://apify.com/lerider/payee-check, https://apify.com/lerider/eu-vat-validator,
  https://apify.com/lerider/eu-licence-check, https://apify.com/lerider/eori-validator,
  https://apify.com/lerider/eu-tin-validator, https://apify.com/lerider/eidas-signature-check,
  https://apify.com/lerider/einvoice-validator
- Hosted MCP server, all seven as tools (token in the `Authorization: Bearer` header):
  `https://mcp.apify.com?tools=lerider/payee-check,lerider/eu-vat-validator,lerider/eu-licence-check,lerider/eori-validator,lerider/eu-tin-validator,lerider/eidas-signature-check,lerider/einvoice-validator`
- MCP docs: https://docs.apify.com/platform/integrations/mcp
