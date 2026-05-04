# Public Institutions Providing Official Company Data in Europe

*Compiled: 2026-03-19*

---

## 1. CZECH REPUBLIC (CR)

### 1.1 Business & Company Registries

#### Verejny rejstrik a Sbirka listin (Public Register and Collection of Documents)
- **Operator:** Ministerstvo spravedlnosti CR (Ministry of Justice)
- **URL:** https://or.justice.cz/
- **Data provided:** Company registration data, articles of association, ownership structures, statutory bodies, financial statements (annual reports, balance sheets, profit/loss statements) filed in the Sbirka listin (Collection of Documents)
- **Access:** Free, fully public, no registration required
- **API:** No official REST API; data accessible via ARES (see below)

#### ARES - Administrativni registr ekonomickych subjektu (Administrative Register of Economic Entities)
- **Operator:** Ministerstvo financi CR (Ministry of Finance)
- **URL:** https://ares.gov.cz/
- **Data provided:** Aggregated data from multiple source registers (Commercial Register, Trade Register, CSU Business Register, Tax Register, etc.). Company identification, addresses, legal forms, NACE codes, registration details
- **Access:** Free, fully public
- **API:** Yes - REST API at https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ with Swagger documentation at https://ares.gov.cz/swagger-ui/. Supports search by ICO (ID number) and company name. Open data published at https://data.mf.gov.cz/topics/ares
- **Notes:** The single most important aggregation point for Czech company data

#### Zivnostensky rejstrik (Trade Register)
- **Operator:** Ministerstvo prumyslu a obchodu (Ministry of Industry and Trade)
- **URL:** https://www.rzp.cz/
- **Data provided:** Trade license information, scope of business activities, business premises, validity periods
- **Access:** Free, public
- **API:** Data accessible through ARES

### 1.2 Financial & Securities Regulators

#### Ceska narodni banka - CNB (Czech National Bank)
- **URL:** https://www.cnb.cz/en/
- **Multiple data services:**

**a) Lists and Registers of Regulated Entities (JERRS)**
- **URL:** https://apl.cnb.cz/apljerrsdad/JERRS.WEB07.INTRO_PAGE?p_lang=en
- **Data provided:** All licensed/registered financial market participants - banks, insurance companies, pension funds, investment firms, payment institutions, etc.
- **Access:** Free, public web interface
- **API:** Yes - WS JERRS web service available upon application (electronically signed request to jerrsws@cnb.cz)

**b) Centralni uloziste regulovanych informaci (Central Storage of Regulated Information)**
- **URL:** https://www.cnb.cz/en/supervision-financial-market/information-published-issuers/
- **Data provided:** Regulated information from issuers of listed securities - annual reports, half-yearly reports, inside information, notifications of major holdings, manager's transactions. Czech equivalent of SEC EDGAR
- **Access:** Free, public
- **API:** Not publicly documented

**c) Financial Market Supervision Reports**
- **URL:** https://www.cnb.cz/en/supervision-financial-market/aggregate-information-financial-sector/
- **Data provided:** Aggregate statistics on banking sector, insurance, capital markets, pension funds
- **Access:** Free, public

### 1.3 Beneficial Ownership

#### Evidence skutecnych majitelu (Register of Beneficial Owners)
- **Operator:** Ministerstvo spravedlnosti CR (Ministry of Justice)
- **URL:** https://issm.justice.cz/
- **Data provided:** Ultimate beneficial owners (UBO) of companies and trusts - name, date of birth, nationality, nature and extent of beneficial interest
- **Access:** **Restricted since December 17, 2025** - public online access removed. Now available only to: registering entities, public authorities, AML-obliged persons (banks, lawyers), and persons demonstrating legitimate interest
- **API:** Not publicly available

### 1.4 Insolvency

#### Insolvencni rejstrik - ISIR (Insolvency Register)
- **Operator:** Ministerstvo spravedlnosti CR (Ministry of Justice)
- **URL:** https://isir.justice.cz/
- **Data provided:** Insolvency proceedings, bankruptcy filings, restructuring proceedings, creditor claims, court decisions
- **Access:** Free, fully public. Search by ICO (company ID) is most reliable
- **API:** ISIR provides a web service interface for automated queries

### 1.5 Tax & VAT

#### Registr DPH - Register platcu DPH (VAT Payer Register)
- **Operator:** Financni sprava CR (Financial Administration)
- **URL:** https://financnisprava.gov.cz/cs/dane/dane-elektronicky/danovy-portal/registr-dph (via Moje dane portal at www.mojedane.cz)
- **Data provided:** VAT registration status, reliable/unreliable payer status ("spolehlivy platce"), registered bank accounts of VAT payers
- **Access:** Free, public
- **API:** Yes - web service (RWS) for verifying VAT payer reliability and registered bank accounts

### 1.6 Statistical Office

#### Cesky statisticky urad - CSU (Czech Statistical Office)
- **URL:** https://csu.gov.cz/
- **Business Register:** https://csu.gov.cz/business_register
- **Data provided:** Business register (RES) with data on all legal and natural persons, trusts, public authorities. Updated twice monthly. Also publishes structural business statistics, industry data
- **Access:** Free; individual lookups on web, full database downloadable as CSV via open data
- **API:** Open data catalog at https://csu.gov.cz/open-data; also published to National Catalog of Open Data (NKOD) at https://data.gov.cz/
- **Notes:** R package `czso` available for programmatic access

### 1.7 Public Procurement

#### Vestnik verejnych zakazek - VVZ (Public Procurement Bulletin)
- **Operator:** Ministerstvo pro mistni rozvoj (Ministry for Regional Development)
- **URL:** https://vvz.nipez.cz/
- **Data provided:** All public procurement notices, tender results, contract awards
- **Access:** Free, public

#### Narodni elektronicky nastroj - NEN (National Electronic Tool)
- **URL:** https://nen.nipez.cz/en/
- **Data provided:** Full electronic procurement management - tender documentation, bids, contract administration
- **Access:** Free to search; participation requires registration

### 1.8 Cybersecurity

#### NUKIB - Narodni urad pro kybernetickou a informacni bezpecnost (National Cyber and Information Security Agency)
- **URL:** https://nukib.gov.cz/
- **Data provided:** Registry of regulated entities under NIS2 (Act No. 264/2025 Sb.), critical infrastructure operators, cybersecurity incident reports. Covers 60 services across 18 sectors
- **Access:** NUKIB Portal for registration and compliance; not a public company lookup database
- **Notes:** New Cybersecurity Act effective November 1, 2025, transposing EU NIS2

### 1.9 Open Data Portal

#### Narodni katalog otevrenych dat - NKOD (National Open Data Catalog)
- **Operator:** Ministerstvo vnitra (Ministry of Interior)
- **URL:** https://data.gov.cz/english/
- **Data provided:** Aggregated open datasets from all Czech public institutions including company data, procurement, budgets
- **Access:** Free, open data

---

## 2. POLAND (PL)

### 2.1 Business & Company Registries

#### Krajowy Rejestr Sadowy - KRS (National Court Register)
- **Operator:** Ministerstwo Sprawiedliwosci (Ministry of Justice)
- **URL:** https://prs.ms.gov.pl/krs (Portal Rejestrow Sadowych)
- **Also via:** https://www.biznes.gov.pl/en/wyszukiwarka-firm
- **Data provided:** Registration data for companies (sp. z o.o., S.A., sp.k., sp.j., etc.), cooperatives, state-owned enterprises, foreign company branches. Includes: company name, registered office, share capital, management board, supervisory board, shareholders, NACE codes, registration history
- **Access:** Free, fully public online since July 1, 2021
- **API:** Not an official public REST API, but data available via commercial providers (e.g., Transparent Data)

#### Repozytorium Dokumentow Finansowych - RDF (Financial Documents Repository)
- **Operator:** Ministerstwo Sprawiedliwosci (Ministry of Justice)
- **URL:** https://ekrs.ms.gov.pl/rdf/pd/search_df (search) / https://rdf-przegladarka.ms.gov.pl/ (browser)
- **Data provided:** Financial statements (annual reports, balance sheets, P&L, cash flow statements) of all KRS-registered companies in structured XML format, auditor opinions, resolutions approving financial statements
- **Access:** Free, no login required for browsing/downloading. Search by KRS number
- **API:** No official public API; protected against automated scraping (CAPTCHA)
- **Notes:** This is the Polish equivalent of the Czech "Sbirka listin" for financial data

#### Centralna Ewidencja i Informacja o Dzialalnosci Gospodarczej - CEIDG (Central Register of Business Activity)
- **Operator:** Ministerstwo Rozwoju i Technologii (Ministry of Development and Technology)
- **URL:** https://www.biznes.gov.pl/en/wyszukiwarka-firm
- **Data provided:** All sole proprietorships (~2.5 million entities) - name, NIP, REGON, address, scope of business, status, suspension/resumption dates
- **Access:** Free, fully public
- **API:** Yes - CEIDG provides a public API for company verification

### 2.2 Beneficial Ownership

#### Centralny Rejestr Beneficjentow Rzeczywistych - CRBR (Central Register of Beneficial Owners)
- **Operator:** Ministerstwo Finansow (Ministry of Finance)
- **URL:** https://crbr.podatki.gov.pl/
- **Data provided:** Beneficial owners of companies, foundations, associations, trusts - name, citizenship, country of residence, nature and extent of ownership/control
- **Access:** Free, public (subject to EU CJEU ruling limitations - may require legitimate interest demonstration in future)
- **API:** Yes - available via commercial providers like Transparent Data (https://transparentdata.pl/en/api-company-information-poland/ubo-poland)

### 2.3 Financial & Securities Regulators

#### Komisja Nadzoru Finansowego - KNF (Polish Financial Supervision Authority)
- **URL:** https://www.knf.gov.pl/en/
- **Entities search:** https://www.knf.gov.pl/en/ENTITIES/entities_search
- **Data provided:** Lists of regulated entities - banks, insurance companies, investment firms, payment institutions, pension funds. Warnings about unauthorized entities. Financial data on supervised sectors
- **Access:** Free, public
- **API:** Not publicly documented

#### Narodowy Bank Polski - NBP (National Bank of Poland)
- **URL:** https://nbp.pl/en/
- **Data provided:** Banking sector financial data, monetary statistics, balance of payments data, exchange rates
- **Access:** Free, public
- **API:** Yes - NBP provides APIs for exchange rates and statistical data

### 2.4 Tax & VAT

#### Biala Lista Podatnikow VAT (White List of VAT Taxpayers)
- **Operator:** Krajowa Administracja Skarbowa - KAS (National Revenue Administration)
- **URL:** https://www.podatki.gov.pl/narzedzia/white-list/
- **API documentation:** https://www.gov.pl/web/kas/api-wykazu-podatnikow-vat
- **Data provided:** VAT registration/deregistration status, registered bank accounts, NIP, REGON
- **Access:** Free, public
- **API:** Yes - official REST API with two methods:
  - "search" method: 100 queries/day, up to 30 entities per query (by NIP, REGON, or bank account + date)
  - "check" method: 5,000 queries/day for simplified verification
  - Also available as downloadable flat file (full NIP-account pair list)
- **Notes:** Updated once daily on business days

### 2.5 Insolvency & Debt

#### Krajowy Rejestr Zadluzonych - KRZ (National Register of Debtors)
- **Operator:** Ministerstwo Sprawiedliwosci (Ministry of Justice)
- **URL:** https://krz.ms.gov.pl/
- **Data provided:** Entities with pending enforcement, restructuring and bankruptcy proceedings; insolvent entities or those threatened with insolvency
- **Access:** Free, public (launched December 1, 2021)
- **API:** Not publicly documented

### 2.6 Statistical Office

#### Glowny Urzad Statystyczny - GUS (Central Statistical Office)
- **URL:** https://stat.gov.pl/en/
- **REGON database:** https://wyszukiwarkaregon.stat.gov.pl/appBIR/index.aspx
- **Data provided:** REGON register (all economic entities), structural business statistics, industry data, economic indicators. REGON number assignment for all entities
- **Access:** Free for basic lookups; bulk data may require application
- **API:** Yes - BIR (Baza Internetowa REGON) web service for REGON data queries

### 2.7 Public Procurement

#### Urzad Zamowien Publicznych - UZP (Public Procurement Office)
- **URL:** https://www.gov.pl/web/uzp-en
- **Biuletyn Zamowien Publicznych (BZP):** https://bzp.uzp.gov.pl/ (search: https://searchbzp.uzp.gov.pl/)
- **Platform e-Zamowienia:** https://ezamowienia.gov.pl/
- **Data provided:** All public procurement notices (below EU thresholds in BZP, above thresholds in TED), contract awards, annual procurement reports
- **Access:** Free, public
- **API:** e-Zamowienia platform provides some integration capabilities

### 2.8 Cybersecurity

#### CSIRT GOV / CSIRT NASK / CSIRT MON
- **URLs:**
  - CSIRT GOV: https://csirt.gov.pl/
  - CSIRT NASK: https://www.nask.pl/
- **Data provided:** Cybersecurity incident reporting and response. Not a public company data registry per se, but relevant for cybersecurity compliance status of key service operators and digital service providers
- **Access:** Incident reporting portals; not a public company lookup

### 2.9 ESG / Sustainability

Poland implements CSRD (Corporate Sustainability Reporting Directive) from January 1, 2025. ESG reports are filed as part of annual reports through the KRS/RDF system. The Warsaw Stock Exchange (GPW) also publishes ESG reporting guidelines for listed companies at https://www.gpw.pl/pub/GPW/ESG/ESG_Reporting_Guidelines.pdf.

---

## 3. EU-LEVEL INSTITUTIONS

### 3.1 Business Registers

#### Business Registers Interconnection System (BRIS)
- **Operator:** European Commission / European e-Justice Portal
- **URL:** https://e-justice.europa.eu/topics/registers-business-insolvency-land/business-registers-search-company-eu_en
- **Search portal:** https://webgate.ec.europa.eu/e-justice/searchBris.do
- **Data provided:** Basic company data (name, legal form, registered office, status, directors) from national business registers of all EU/EEA countries. Covers public and private limited liability companies and their branches
- **Access:** Free, public
- **API:** Not a public REST API; web interface only
- **Notes:** Based on Directive 2012/17/EU. Does not include financial statements

#### European Business Register (EBR)
- **Operator:** European Business Registry Association (EBRA)
- **URL:** https://ebra.be/ / https://www.eubusinessregister.org/
- **Data provided:** Company information from national business registries of member states
- **Access:** Varies by country; some free, some paid
- **Notes:** **Platform closing April 1, 2026** - being replaced by BRIS functionality

### 3.2 Beneficial Ownership

#### Beneficial Ownership Registers Interconnection System (BORIS)
- **Operator:** European Commission / European e-Justice Portal
- **URL:** https://e-justice.europa.eu/topics/registers-business-insolvency-land/beneficial-ownership-registers-interconnection-system-boris_en
- **Access portal:** https://webgate.ec.europa.eu/e-justice/38590/EN/beneficial_ownership_registers_interconnection_system_boris
- **Data provided:** Beneficial ownership data from connected national UBO registers across EU/EEA
- **Access:** Varies - following CJEU ruling and 6th AMLD, access may require demonstration of legitimate interest. Law enforcement/FIUs have full access
- **Status:** Only 17 of 30 EU/EEA countries fully connected as of 2025. Ongoing technical integration challenges

### 3.3 Securities & Financial Markets

#### European Securities and Markets Authority (ESMA) - Databases and Registers
- **URL:** https://www.esma.europa.eu/publications-and-data/databases-and-registers
- **Key databases:**

**a) Financial Instruments Reference Data System (FIRDS)**
- **Data provided:** Reference data on all financial instruments traded in EU - name, ISIN, LEI of issuer, trading venue, instrument type
- **Access:** Free, public. Human interface and machine-to-machine download
- **API:** Yes - bulk file downloads and search interface

**b) European Rating Platform (ERP)**
- **Data provided:** Credit ratings and rating outlooks from all EU-registered credit rating agencies
- **Access:** Free, public (launched to provide free credit ratings info to the public)

**c) Short Selling Register**
- **Data provided:** Net short position notifications for sovereign issuers, list of exempted shares
- **Access:** Free, public

**d) EMIR Trade Repositories**
- **Data provided:** Lists of registered/recognized trade repositories; derivative transaction data (not directly public, but aggregate statistics published)
- **Access:** List of TRs is public; transaction data available to regulators only

**e) Registers of Investment Firms, Fund Managers, etc.**
- **Data provided:** AIFMD registers, UCITS management companies, CCP registers, CSDs, benchmark administrators
- **Access:** Free, public

#### European Banking Authority (EBA)
- **URL:** https://www.eba.europa.eu/
- **Key data resources:**

**a) EU-wide Transparency Exercise**
- **URL:** https://www.eba.europa.eu/risk-analysis-and-data/eu-wide-transparency-exercise
- **Data provided:** Bank-by-bank data for ~119 banks across 25 EU/EEA countries. Capital adequacy, risk exposures, asset quality, P&L data. Published annually
- **Access:** Free, downloadable datasets (Excel/CSV)

**b) EU-wide Stress Test Results**
- **Data provided:** Stress test results for major EU banks under adverse scenarios
- **Access:** Free, downloadable

#### European Insurance and Occupational Pensions Authority (EIOPA)
- **URL:** https://www.eiopa.europa.eu/
- **Data provided:** Insurance sector statistics, pension fund data, Solvency II reporting data, risk dashboards
- **Access:** Aggregate data free; entity-level data varies

#### ECB Banking Supervision (SSM - Single Supervisory Mechanism)
- **URL:** https://www.bankingsupervision.europa.eu/
- **Data provided:**
  - List of all supervised entities (significant and less significant institutions) in eurozone
  - Supervisory banking statistics
  - SREP aggregate results
- **Access:** Free, public
- **API:** ECB Data Portal at https://data.ecb.europa.eu/ provides API access to statistical data

### 3.4 European Single Access Point (ESAP)

#### ESAP
- **Operator:** ESMA (on behalf of the European Commission)
- **URL:** https://www.esma.europa.eu/esmas-activities/data/european-single-access-point-esap
- **Data provided:** Will provide single access to: financial information, sustainability/ESG reports, regulatory disclosures from EU companies
- **Access:** Will be free, multilingual, machine-readable
- **Timeline:**
  - July 2026: Start collecting information from Collection Bodies
  - July 2027: Information accessible to the public
  - January 2028: Phase 2 information collection
  - January 2029: Phase 2bis
- **Notes:** This will become the most important pan-European company data portal for both financial and ESG data. Designed to replace fragmented national systems

### 3.5 Legal Entity Identification

#### Global Legal Entity Identifier Foundation (GLEIF)
- **URL:** https://www.gleif.org/
- **LEI Search:** https://search.gleif.org/
- **Data provided:** Legal Entity Identifiers (LEI) - 20-digit codes for unique identification of legal entities in financial transactions. Includes: entity name, registered address, headquarters address, legal form, registration authority, ownership relationships (direct & ultimate parent)
- **Access:** Free, fully public
- **API:** Yes - comprehensive REST API at https://www.gleif.org/en/lei-data/gleif-api. Supports filters, full-text search, fuzzy matching. Production since 2020. Also provides bulk download files (CSV, XML)
- **Notes:** Maps to OpenCorporates IDs (bi-weekly updated CSV). Over 2.7 million LEIs globally

### 3.6 Public Procurement

#### Tenders Electronic Daily (TED)
- **Operator:** Publications Office of the European Union
- **URL:** https://ted.europa.eu/en/
- **Developer docs:** https://docs.ted.europa.eu/api/latest/index.html
- **Data provided:** ~800,000 public procurement notices per year from all EU/EEA countries, worth over EUR 815 billion. Contract notices, contract awards, prior information notices
- **Access:** Free, public
- **API:** Yes - TED API for retrieving, submitting, validating, and visualizing notices. Bulk XML downloads available (daily and monthly packages). CSV subset also available
- **Formats:** XML (full), CSV (subset), PDF/HTML rendering

### 3.7 Statistics

#### Eurostat
- **URL:** https://ec.europa.eu/eurostat/
- **Database:** https://ec.europa.eu/eurostat/data/database
- **Structural Business Statistics:** https://ec.europa.eu/eurostat/web/structural-business-statistics/database
- **Data provided:** Aggregate business statistics by country, sector, size class. Covers: number of enterprises, turnover, value added, employment, investment. Also: trade statistics, R&D expenditure, ICT usage
- **Access:** Free for aggregate/published data. Microdata (firm-level) available only to recognized research entities upon application (8-10 week process)
- **API:** Yes - SDMX 3.0 REST API. Supports JSON-stat, SDMX-CSV, SDMX-ML, TSV formats. Full documentation at https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/

### 3.8 Open Data & Aggregators

#### EU Open Data Portal
- **URL:** https://data.europa.eu/
- **Data provided:** Aggregates open datasets from EU institutions and member states, including company-related datasets
- **Access:** Free

#### OpenCorporates
- **URL:** https://opencorporates.com/
- **Data provided:** Largest open database of companies globally - aggregates data from official registries worldwide. Basic company data: name, jurisdiction, status, registration date, officers
- **Access:** Basic search free; bulk access and API are paid (commercial license)
- **API:** Yes - REST API (paid). Linked to GLEIF LEI data

#### OpenSanctions
- **URL:** https://www.opensanctions.org/
- **Data provided:** Sanctions lists, PEP databases, company data from various registries (including CZ and PL business registers)
- **Access:** Free for non-commercial use

---

## SUMMARY TABLE

| Institution | Country | Data Type | Free? | API? |
|---|---|---|---|---|
| **Justice.cz (Verejny rejstrik)** | CZ | Company registration, financial statements | Yes | Via ARES |
| **ARES** | CZ | Aggregated company data | Yes | Yes (REST) |
| **CNB - JERRS** | CZ | Regulated financial entities | Yes | Yes (WS) |
| **CNB - Central Storage** | CZ | Issuer reports (annual, half-yearly) | Yes | No |
| **ISIR** | CZ | Insolvency proceedings | Yes | Yes (WS) |
| **Evidence skutecnych majitelu** | CZ | Beneficial ownership | Restricted | No |
| **Registr DPH** | CZ | VAT payer status | Yes | Yes (RWS) |
| **CSU Business Register** | CZ | Business statistics | Yes | Open data |
| **VVZ/NEN** | CZ | Public procurement | Yes | Partial |
| **KRS** | PL | Company registration | Yes | No (official) |
| **RDF** | PL | Financial statements | Yes | No |
| **CEIDG** | PL | Sole proprietorships | Yes | Yes |
| **CRBR** | PL | Beneficial ownership | Yes* | Via 3rd party |
| **KNF** | PL | Regulated financial entities | Yes | No |
| **Biala Lista VAT** | PL | VAT taxpayer data | Yes | Yes (REST) |
| **KRZ** | PL | Insolvency/debt | Yes | No |
| **GUS/REGON** | PL | Business statistics | Yes | Yes (BIR WS) |
| **BZP/e-Zamowienia** | PL | Public procurement | Yes | Partial |
| **BRIS** | EU | Basic company data cross-border | Yes | No |
| **BORIS** | EU | Beneficial ownership cross-border | Restricted | No |
| **ESMA (FIRDS, ERP, etc.)** | EU | Securities, ratings, instruments | Yes | Yes |
| **EBA Transparency** | EU | Bank-by-bank financial data | Yes | Downloads |
| **ECB SSM** | EU | Supervised bank lists | Yes | Yes |
| **ESAP** | EU | Financial + ESG data (from 2027) | Yes | TBD |
| **GLEIF** | Global | Legal Entity Identifiers | Yes | Yes (REST) |
| **TED** | EU | Public procurement | Yes | Yes (REST) |
| **Eurostat** | EU | Business statistics (aggregate) | Yes | Yes (SDMX) |

*\* May be subject to legitimate interest requirements following EU CJEU ruling*
