# Flight search and judgment

Read this reference for flight-only and whole-trip requests.

## Establish the evidence

Use [Google Flights Data Scraper](https://apify.com/johnvc/google-flights-data-scraper-flight-and-price-search). For a live call, inspect the current README, schema, pricing, and actual payload before interpreting it. Resolve city names to plausible airports and disclose any nearby-airport expansion rather than silently weakening the request.

Keep optional booking-option retrieval off unless requested and costed. The reviewed README limits booking-option retrieval to one-way searches; round-trip and multi-city searches return no booking options. Recheck this limitation against the current documentation before relying on it.

## Verify itinerary coverage

Do not claim that a round-trip result contains both directions merely because it is labelled round trip. Reviewed output contained an outbound itinerary plus a continuation token, leaving the concrete return itinerary unresolved.

Do not claim that a multi-city or open-jaw search produced one combined ticket merely because that search form was submitted. Confirm that the returned itinerary and quote cover every requested segment. Separate one-way searches are a recovery option, but their sum is a labelled sum of separate quotes, not a live quote for one protected or combined itinerary.

## Preserve flight price basis

Before using a returned amount in arithmetic, identify its currency, itinerary scope, traveler scope, and whether the source explicitly labels it as a party total or a per-traveler fare. Keep the exact JSON path and value, or URL and wording, as evidence.

Do not treat party-size inputs, proportional results from separate searches, amount plausibility, itinerary type, equality with price insights, or general knowledge of flight-search displays as evidence of price basis. Do not start another paid search solely to infer that basis.

When the basis is unresolved:

- report the amount as an ambiguous quote;
- for a homogeneous adult party, show the two neutral scenarios only when clearly labelled as assumptions: the quote is already the party total, or every adult has the same quoted fare;
- for a party containing children or infants, do not multiply the quote by headcount without a returned fare breakdown; leave the party total unresolved;
- do not describe either interpretation as more likely.

Use this optional internal record to keep the reasoning auditable. Do not expose it unless it helps explain an ambiguity or the user asks for it.

```yaml
flight_price_basis:
  currency:
  returned_amount:
  itinerary_scope:
  traveler_scope:
  price_basis: <explicit_party_total | explicit_per_traveler | unresolved>
  price_basis_evidence: <exact JSON path and value | URL and wording | none>
  arithmetic: <supported calculation, labelled adult-only scenarios, or unresolved>
```

## Rank and explain

Compare relevant options using the user's constraints, fare, stops, elapsed duration, layover quality, schedule risk, cabin or basic-economy restrictions, and airline preferences. Surface the cheapest and best-convenience choices separately when they differ. Use price insights only for the judgment they explicitly support; they do not establish the quote's traveler basis.
