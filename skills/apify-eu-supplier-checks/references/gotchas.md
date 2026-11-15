# Cost guardrails and error recovery: EU supplier checks

## Confirm live prices before a batch

Prices can change. Read them from the live Actor rather than trusting a copied number:

```bash
apify actors info "lerider/payee-check" --json \
  --user-agent apify-awesome-skills/apify-eu-supplier-checks \
  2>/dev/null
```

Keep authentication in the CLI login or the `Authorization: Bearer` header, never in a URL.

## Cost model

- Pay per event, one event per item checked. A malformed item returns an `error` and is not charged.
- Charged only when the register answers: `eu-vat-validator` (VIES), `eori-validator` (EOS), `eu-tin-validator`
  (EU TIN service). `unavailable`, `invalid_format` and `not_checkable` items are free.
- Charged even when a register was down: `payee-check` supplier pre-flight and `eu-licence-check`. The verdict is
  then never ALLOW, and `unavailable` / `coverage` names the source, so a re-run later is a second charge.
- `eidas-signature-check` charges per document read, including "no signature found". A download failure or an
  unreadable file is free.
- `einvoice-validator` charges per e-invoice validated, including ones with errors. A plain PDF or other XML is free.
- `attest: true` on `payee-check` adds $0.02 per item, only when the timestamp was obtained.
- In one run, a repeated VAT id, EORI or TIN is looked up once.

Rule of thumb for confirmation: mention cost under about $5, warn over about $5, get explicit sign-off over about $20.
Always phrase it as "around $X". Example: 200 supplier pre-flights = around $6.

## Guardrails

1. Start with one item. Inspect the shape before a batch.
2. De-duplicate the input before a batch; send at most the batch limit per run (see actor-index.md).
3. `payee-check`: use the $0.001 payee-check mode for bulk IBAN screening, and the $0.03 pre-flight only for invoices
   about to be paid.
4. `eu-licence-check`: leave `refresh` at `auto` (the default). `always` refetches every source and is slower.
5. Send only what a check needs. TINs, names of sole traders and invoice texts can be personal data; the Actors keep
   nothing beyond the user's own run dataset.

## Error recovery

- `{"index": N, "error": "..."}`: fix the named field, re-run only that item.
- `unavailable` (VIES, EOS, EU TIN service, Peppol Directory): the register did not answer. Retry once later. Never
  report it as invalid, and never treat a REVIEW caused by it as ALLOW.
- `payee-check` run fails on input: you mixed `iban`/`payments` with `payee`/`preflights`. Split into two runs.
- `eidas-signature-check` with `documents`: clear the single `url` field. Same for the batch field of every Actor.
- Before retrying a run, check the original run's status. If the start response was lost, look up the existing run
  first so an uncertain response does not trigger a second paid run.

## Wording traps (what the agent must not claim)

| Result | Do not say | Say instead |
|---|---|---|
| `payee-check` ALLOW | "The supplier is safe / verified / you can pay" | "No problem found in the checks that ran: [list]. This is not your bank's Verification of Payee." |
| `eu-vat-validator` `valid` | "This company is legit" | "The VAT number is registered in VIES to [name] as of [checked_at]." |
| `eu-tin-validator` `valid` | "The TIN belongs to this person" | "The TIN has a valid format and check digit for [country]. Ownership cannot be checked." |
| `eu-licence-check` ALLOW | "The firm is safe / regulated for everything" | "An active [licence type] authorisation was found in [register]; nothing was found on the warning lists covered." |
| `eu-licence-check` no warning hit | "Not a scam" | "Not on the warning lists covered (FR, BE, NL and the EU MiCA list). Lists only hold firms an authority has noticed." |
| `eidas-signature-check` ALLOW | "The contract is legally valid / binding" | "The signature is intact, EU-trusted [and qualified]; signed content unchanged." |
| `eidas-signature-check` `qualified: true`, `qscd: false` | "This is a qualified electronic signature" | "Advanced signature with a qualified certificate; the key is not shown to be on a qualified device, so it is not a QES." |
| `payee-check` ALLOW without `known_payees` | "No sign of a bank-detail change" | "The check had no payment history, so it could not see a bank change. Call the supplier on a number you already had." |
| `einvoice-validator` ALLOW | "The invoice is genuine" | "The file passes the [rule sets] rules. That says nothing about the IBAN, VAT number or whether the invoice is real." |
