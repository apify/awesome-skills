# Actor index — APAC Company & Financial Data

All Actors below are **public** on the Apify Store under `nexgendata/`. Always confirm the live input schema with `apify actors info "nexgendata/SLUG" --input --json 2>/dev/null` before running — fields shown here are typical, not authoritative. Field names vary by country. Every Actor returns rows with a `source_url` to the official exchange, registry, or regulator.

## Company registries & corporate lookup
| Actor | Use it for | Key inputs (typical) |
|---|---|---|
| `singapore-acra-company-lookup` | Singapore ACRA / BizFile+ company lookup — UEN, status, directors | `queries[]` or `query` (company name/UEN); aliases `companies[]`/`names[]`/`name` |
| `japan-houjin-bangou-corporate-registry` | Japan corporate registry (法人番号 / NTA) — number, name, address | `corporate_number`, `company_name_filter` (商号), `prefecture_filter`, `category_filter`, `max_records`; optional `nta_api_key` |
| `ogd-india-companies-registry` | India MCA companies master data (via OGD) — CIN, ROC, status | `company_name_contains`, `roc`, `state`, `max_results`; optional `api_key` |

## Listed-company disclosures & announcements
| Actor | Region / source | Key inputs |
|---|---|---|
| `japan-tdnet-timely-disclosures` | Japan TDnet — 適時開示 timely disclosures (TSE) | `date_from`,`date_to` (YYYY-MM-DD), `company_filter`, `ticker_filter` (4-digit code), `disclosure_type`, `max_disclosures` |
| `taiwan-mops-company-announcements` | Taiwan MOPS — 公開資訊觀測站 重大訊息 | `date_from`,`date_to` (TPE), `company_filter` (中文/EN), `ticker_filter` (4-digit), `disclosure_type`, `max_disclosures` |
| `hkex-news-announcements` | Hong Kong HKEXnews — 披露易 listed-company announcements | `tickers[]`, `categoryFilter`, `lookbackDays`, `maxResults` |
| `sgx-company-announcements` | Singapore SGX — company disclosure feed | `tickers[]`, `category`, `lookbackDays`, `maxResults` |
| `india-sebi-filings-tracker` | India SEBI — filings & orders | `filing_types[]`, `company_filter[]`, `days_back`, `start_date`/`end_date`, `sector_filter`, `status_filter`, `max_filings` |

## Insider / large-shareholder filings
| Actor | Region / source | Key inputs |
|---|---|---|
| `japan-edinet-insider-filings` | Japan EDINET — 大量保有報告書 (large-holder) / 自社株買い (buyback) | `apiKey` (EDINET key, **required**), `date_from`,`date_to`, `doc_type`, `filer_name`, `issuer_ticker` (4-digit), `enrich_xbrl`, `max_filings` |
| `hkex-insider-short-tracker` | Hong Kong HKEX — 董事股權變動 (director dealings) / 沽空持倉 (short positions) | `stockCode`, `disclosureType`, `startDate`,`endDate`, `minSharesChanged`, `limit` |
| `china-ashare-insider-trades` | China A-share — 高管增减持 insider transactions | `stockCodes[]`, `dateRange` (preset) or `startDate`/`endDate`, `transactionType`, `maxRecords` |

## Stock screeners (Asian exchanges)
| Actor | Exchange / index | Key inputs |
|---|---|---|
| `kospi-stock-screener` | Korea KOSPI / KOSDAQ | `market`, `limit`, `sector`, `min_market_cap_billion_krw`, `enrich_sector` |
| `tse-japan-stock-screener` | Japan TSE / 日経225 | `index`, `limit`, `min_market_cap_jpy_billion`, `sector`, `enrich_fundamentals` |
| `twse-stock-screener` | Taiwan TWSE | `limit`, `min_trade_value_twd`, `min_volume`, `max_pe_ratio`, `min_dividend_yield`, `sector`, `include_etfs` |
| `sgx-singapore-stock-screener` | Singapore SGX / STI | `market`, `limit`, `min_market_cap_sgd`, `sector`, `enrich_fundamentals` |
| `nse-india-stock-screener` | India NSE (+ index screener) | `limit`, `exchange`, `min_market_cap_crore`, `sector` |
| `bse-india-stock-screener` | India BSE (Bombay) equities | company / cap / sector filters (confirm via `--input`) |
| `eastmoney-china-stock-screener` | China A-shares (Eastmoney 东方财富) | `market`, `sort_by`, `sort_order`, `max_results` |
| `chinese-adrs-stock-screener` | China ADRs on NYSE/NASDAQ | cap / sector filters (confirm via `--input`) |
| `star-market-china-stock-screener` | Shanghai STAR Market 上海科创板 | cap / sector filters |
| `chinext-china-stock-screener` | Shenzhen ChiNext 深圳创业板 | cap / sector filters |
| `bse-beijing-stock-screener` | Beijing Stock Exchange 北京证券交易所 | cap / sector filters |
| `hkex-hang-seng-stock-screener` | Hong Kong HKEX / Hang Seng 恒生指數 | cap / sector filters |
| `hose-vietnam-stock-screener` | Vietnam HOSE / VN30 | cap / sector filters |
| `idx-indonesia-stock-screener` | Indonesia IDX / LQ45 | cap / sector filters |
| `set-thailand-stock-screener` | Thailand SET / SET50 | cap / sector filters |
| `pse-philippines-stock-screener` | Philippines PSE / PSEi | cap / sector filters |
| `bursa-malaysia-stock-screener` | Malaysia Bursa / KLCI | cap / sector filters |

## IPO calendars & pipelines
| Actor | Region | Key inputs |
|---|---|---|
| `apac-ipo-calendar-sweep` | Pan-APAC IPO sweep (all major Asian markets) | `country`, `status`, `lookbackDays`, `lookaheadDays`, `sector`, `minProceedsUsdMillion`, `limit` |
| `hkex-ipo-calendar` | Hong Kong HKEX (主板 / GEM) | `mode`, `lookbackDays`, `lookaheadDays`, `listingBoard`, `sector`, `minProceedsHkdMillion`, `limit` |
| `korea-ipo-pipeline-tracker` | Korea 코스피/코스닥 IPO pipeline | `opendart_api_key` (**required**), `stage_filter`, `market_filter`, `min_offering_size_KRW`, `date_from`/`date_to`, `max_records` |

## Regulator enforcement (Asia)
| Actor | Region / regulator | Key inputs |
|---|---|---|
| `singapore-mas-enforcement` | Singapore MAS — financial-regulator actions | `action_type`, `date_from`,`date_to`, `firm_filter`, `individual_filter`, `max_results` |
| `hk-sfc-enforcement-tracker` | Hong Kong SFC — 證監會 紀律處分 / 檢控 / 罰款 | `action_type`, `party_type`, `decision_date_from`,`decision_date_to`, `keyword`, `limit` |
| `finma-mas-sfc-enforcement-tracker` | CH / SG / HK combined (FINMA + MAS + SFC) | `regulator`, `action_type`, `days_back`, `min_fine_amount` (USD), `max_actions` |

## Markets context & flows
| Actor | Use it for | Key inputs |
|---|---|---|
| `china-etf-flow-tracker` | China ETF fund flows (Eastmoney 东方财富 ETF资金流向) | confirm via `--input` |
| `analyst-price-targets` | Analyst consensus / upgrades / downgrades (incl. APAC tickers) | confirm via `--input` |
| `pr-newswire-asia-press-releases-scraper` | PR Newswire Asia — corporate press releases | confirm via `--input` |
| `india-rbi-monetary-policy-statements` | India RBI MPC monetary-policy statements | confirm via `--input` |

> Note: several APAC registry / exchange / regulator Actors are still in the public-flip queue (e.g. Korea DART/KIND/KRX, Taiwan MOEA/FSC, Japan FSA/JPX, India MCA detailed-filings, China CNIPA, Singapore MAS-FI-directory, PSE Edge). They are **omitted here on purpose** — this index routes only to Actors that are currently `isPublic:true`. As flips proceed, add the new public slugs here.
