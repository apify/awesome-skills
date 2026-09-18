# Actor routing table

One Actor powers both Zillow skills; the skills differ in the question they are shaped for.

| Question | Skill | Actor input shape |
|---|---|---|
| For-sale, rental, or sold listings by city or ZIP | apify-zillow-api | `locations` list, `statusType`, filters |
| Whole-metro sweep past 820 results | apify-zillow-api | `autoShard: true` with `maxUpstreamCalls` |
| Recently sold homes for comping | apify-zillow-api | `statusType: "sold"` |
| Homes with a recent price cut | apify-zillow-price-cuts | `statusType: "sale"`, `priceReduction: true` |
| A weekly price-drop feed by city | apify-zillow-price-cuts | same, on a schedule, sorted by `priceChange` |

- Actor: https://apify.com/johnvc/zillow-api?fpr=9n7kx3&fp_sid=awesomeskills
- Actor ID: `johnvc/zillow-api`
- Related family: Zoopla Property API (https://apify.com/johnvc/zoopla-property-api?fpr=9n7kx3&fp_sid=awesomeskills) and Realestate.com.au Property API (https://apify.com/johnvc/realestate-au-property-api?fpr=9n7kx3&fp_sid=awesomeskills) share the row shape for cross-market property work.
