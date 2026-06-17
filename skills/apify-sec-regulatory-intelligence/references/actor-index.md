# Actor index — SEC & Regulatory Intelligence

All Actors below are **public** on the Apify Store under `nexgendata/`. Always confirm the live input schema with `apify actors info "nexgendata/SLUG" --input --json 2>/dev/null` before running — fields shown here are typical, not authoritative. Every Actor returns rows with a `source_url` to the official filing.

## U.S. SEC — insider & ownership
| Actor | Use it for | Key inputs (typical) |
|---|---|---|
| `sec-form-4-insider-trading-scraper` | Insider (officer/director/10%+) buys & sells, transaction-level | `dateFrom`,`dateTo` (req), `tickers[]`, `transactionTypes[]` (P=buy,S=sell), `maxFilings` |
| `sec-form4-insider-tracker` | Alt Form 4 view — CEO/CFO buy/sell focus | `tickers`, date window, `maxFilings` |
| `insider-cluster-detector` | 3+ different insiders buying the SAME stock (cluster signal) | `min_cluster_size`(3), `date_range`("last_30d"), `min_value_usd`, `exclude_sells`, `tickers[]` |
| `sec-form-144-restricted-stock-sales-tracker` | Planned insider restricted-stock sales (pre-sale notice) | date window, `tickers`, `maxFilings` |
| `sec-schedule-13dg-activist-tracker` | Activist / >5% stakes (13D/G + amendments) | `dateFrom`,`dateTo` (req), `formTypes[]` (SC 13D / 13G…), `targetTickers[]` |
| `sec-form-13f-tracker-pro` | Institutional 13F holdings (filer, positions) | `dateFrom`,`dateTo` (req), `filerCik`, `tickers[]`, `query`, `maxHoldingsPerFiling` |
| `13f-holdings-delta-tracker` | 13F position CHANGES quarter-over-quarter (adds/exits) | filer / fund, period |

## U.S. SEC — corporate events & filings
| Actor | Use it for | Key inputs |
|---|---|---|
| `sec-form-8k-material-events-scraper` | Material events (M&A, results, exec changes) by SEC item code | `dateFrom`,`dateTo` (req), `itemFilter[]` (e.g. 1.01, 2.01, 5.02), `tickers[]` |
| `sec-edgar-8k-filings` | 8-K material-events tracker (alt) | date window, tickers |
| `sec-event-router` | UNIFIED per-company SEC filings/events timeline | company/ticker, date window |
| `sec-edgar-search` | Any-filing company search (10-K, 10-Q, etc.) | `query` (req), `formTypes` ("10-K,10-Q"), date window, `maxResults` |
| `sec-edgar-filings-scraper` | Pull 10-K/10-Q & filing documents | company, form types |

## U.S. SEC — capital raises, funds, advisers
| Actor | Use it for | Key inputs |
|---|---|---|
| `sec-form-d-tracker` | Private placements / exempt offerings (Form D) | `query`, date window, `minOfferingAmount`, `industryFilter`, `maxResults` |
| `sec-form-d-scraper` | Form D private-placement filings (alt) | date window, filters |
| `sec-reg-a-plus-crowdfunding-offerings-tracker` | Reg A/A+ crowdfunding + Form D amendments | date window, filters |
| `sec-form-nport-p-mutual-fund-holdings` | Fund / ETF portfolio holdings (N-PORT-P) | fund/CIK, period |
| `sec-form-nport-mutual-fund-holdings` | Mutual-fund holdings & risk data (N-PORT) | fund/CIK, period |
| `sec-form-npx-mutual-fund-proxy-votes` | Fund proxy-vote disclosures (N-PX) | fund, period |
| `sec-form-adv-investment-adviser-tracker` | Investment-adviser registrations (Form ADV) | adviser/firm, filters |
| `sec-form-11-k-employee-stock-plan-tracker` | Employee stock-plan filings (11-K) | company, period |

## U.S. — late filings, enforcement, registration
| Actor | Use it for | Key inputs |
|---|---|---|
| `sec-form-nt-late-filing-tracker` | Companies that filed LATE (NT) — forensic early warning | `form_type`("all"), `days_back`(90), `min_market_cap`, `max_filings` |
| `sec-litigation-releases` | SEC litigation / enforcement releases | `yearStart`,`yearEnd`, `keywordFilter`, `maxReleases` |
| `finra-brokercheck-search` | Broker / firm registration & disclosure metadata | `query` (req), `searchType` ("firm"/"individual"), `maxResults` |
| `court-records-search` | Public court case records | `query`, filters |
| `ftc-enforcement-actions-scraper` | FTC enforcement actions | date / keyword |
| `epa-echo-enforcement-scraper` | EPA ECHO environmental enforcement | facility / date |

## Global regulators (NexGenData's differentiator)
| Actor | Region / regulator | Use it for |
|---|---|---|
| `finma-mas-sfc-enforcement-tracker` | CH / SG / HK | Combined FINMA + MAS + SFC enforcement actions |
| `singapore-mas-enforcement` | Singapore MAS | MAS financial-regulator actions |
| `hk-sfc-enforcement-tracker` | Hong Kong SFC | 證監會 disciplinary actions, prosecutions, fines |
| `india-sebi-filings-tracker` | India SEBI | SEBI filings & orders |
| `australia-asic-enforcement` | Australia ASIC | ASIC regulatory actions |
| `japan-edinet-insider-filings` | Japan EDINET | 大量保有報告書 / buybacks / insider filings |
| `hkex-insider-short-tracker` | Hong Kong HKEX | 董事股權變動 / short positions |
| `china-ashare-insider-trades` | China A-share | 高管增减持 insider transactions |
| `investegate-rns-aggregator` | UK LSE/AIM | RNS regulatory-announcement metadata |

## News & company context
| Actor | Use it for |
|---|---|
| `crunchbase-news-scraper` | Daily funding & M&A headlines |
| `globenewswire-press-releases-scraper` | Listed-company press releases |
| `company-data-aggregator` | LEI + SEC funding + tech profile for a company |

## RAG / LLM feeds
| Actor | Use it for |
|---|---|
| `sec-filings-rag-markdown` | SEC filings converted to clean Markdown for RAG/LLM ingestion |
| `regulatory-enforcement-rag` | Regulatory enforcement actions as Markdown for RAG |

## MCP option
| Server | Use it for |
|---|---|
| `regulatory-filings-mcp` | The whole regulatory cluster exposed as an MCP server — connect directly via the [Apify MCP connector](https://mcp.apify.com) instead of per-Actor CLI calls. |
