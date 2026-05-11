# Pricing Deep Dive

When basic Pricing Intelligence isn't enough — complex pricing models, multiple products/SKUs, or per-use-case/per-tier comparison needed.

## When to Use

- Basic pricing scrape revealed non-trivial structure (usage-based, credit multipliers, tiered)
- User wants deeper comparison than headline price
- Multiple products/SKUs from one vendor with different pricing

## Pricing Decomposition (Nagle)

For each vendor, decompose pricing into 4 components (ref: Thomas Nagle, *The Strategy and Tactics of Pricing*):

1. **Price metric** — unit of purchase (seat, API call, record, GB, credit, transaction)
2. **Price structure** — how price varies (flat, tiered, volume, usage-based, credit × multiplier, commitment terms)
3. **Offering design** — how features are bundled (all-inclusive, modular, add-on, freemium, good/better/best)
4. **Price fences** — what separates segments (feature gates, support tiers, SLA, SSO, compliance, API access)

This decomposition reveals hidden costs and comparison dimensions.

## Normalization

Based on the decomposition:

1. **Identify common price metric** — what unit makes sense for this category?
2. **Propose comparison dimensions** — which axes matter? (per tier, per use case, per product line)
3. **⚠️ Confirm with user** — always, even in autopilot mode, unless normalization was specified by the user in the prompt. **Explain** and **confirm** the decomposition principles and proposed comparison dimensions to the user.
4. **Normalize** — convert each vendor to common unit
5. **Flag incomparables** — where and why the comparison breaks down

## Confidence

- **V (Verified)** — directly from pricing page / docs
- **C (Calculated)** — derived from documented values (base × multiplier)
- **E (Estimated)** — indirect estimate from plan names, third parties
- **? (Contact sales)** — vendor doesn't publish
