# European Companies Guide — Portfolio Focus

Shared reference for handling European companies across all analysis skills.

## SEC Filing Availability

- Many European companies don't file with SEC (no CIK)
- ADR-listed European companies (e.g. AUTL) DO have SEC filings
- For non-SEC filers, look for annual reports on company investor relations pages
- For EU-listed companies, use Yahoo Finance and FMP as primary data sources

## Reporting Frequency

- Quarterly reporting may be limited — semi-annual reporting is common for EU firms
- When quarterly data is unavailable, use semi-annual figures and interpolate cautiously
- Check company IR page for reporting calendar

## Currency Handling

- Use EUR as base currency unless company reports in local currency
- Apply current FX rates from Yahoo Finance or Alpha Vantage
- Note currency of each data point in output tables
- Key portfolio currencies: CZK, PLN, SEK, HUF, BGN, TRY, GBP, USD

## Data Source Priority (for non-SEC filers)

1. Company investor relations (annual/semi-annual reports)
2. Yahoo Finance (prices, basic financials)
3. Financial Modeling Prep (ratios, estimates)
4. Finnhub (real-time quotes, basic financials)
5. Alpha Vantage (FX rates, technical indicators)
