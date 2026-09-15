# Whole-trip orchestration

Read this reference only when the requested output combines flights with lodging, overnight bases, an event plan, or a whole-trip budget. Also read the flight and hotel references before handling their respective evidence.

## Shape the trip before pricing

1. Identify the anchor: the fixed event, appointment, destination, or immovable date. Verify time-sensitive dates, venue, access rules, and location with current authoritative sources.
2. Derive viable arrival and departure windows from that anchor and the user's constraints.
3. Compare candidate airports and transfer legs using sourced local times and travel-time evidence. State meaningful uncertainty.
4. Derive the actual lodging nights from local arrival and departure times. An arrival or departure calendar date does not automatically require a hotel night, especially for overnight travel.
5. Decide which nights belong near the airport, destination, or anchor. A long or fragile same-day transfer may justify another base; a short transfer may make one base simpler.
6. Price only viable flight and lodging shapes, following [flights.md](flights.md) and [hotels.md](hotels.md).
7. If lodging evidence suggests a constrained market, compare a nearby re-base. Re-evaluate both the lodging and every affected transfer before recommending the new shape.

## Budget without false precision

Build the sourced subtotal only from returned, compatible amounts:

- flights with verified itinerary coverage and preserved price basis;
- lodging with dates, occupancy or room assumptions, nightly or stay-total basis, and returned fee coverage.

Carry the complete `flight_price_basis` reasoning into the trip budget without inferring missing evidence. Keep rental cars, rail, local transit, fuel, tolls, parking, food, event tickets, taxes, and fees outside the sourced subtotal unless a cited source priced them for this plan. Show them separately as sourced amounts, estimates, ranges, or unknowns. Never describe the trip as fully priced while material categories remain estimated or unresolved.

## Recommend the trip shape

Explain how the anchor, local timing, transfer burden, availability, cancellation risk, and price uncertainty drive the recommendation. Provide a day-by-day outline, selected flight and lodging options, worthwhile alternatives, and a booking checklist. Do not imply that separate one-way quotes form one protected itinerary or that any option is held.
