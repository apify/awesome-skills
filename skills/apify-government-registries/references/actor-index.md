# Actor index: government registries

All Actors are by the skill author (`regdata`), pay per event, and run on an Apify token alone. Fetch the input schema before calling any of them:

```bash
apify actors info "<ACTOR_ID>" --input \
  --user-agent apify-awesome-skills/apify-government-registries \
  2>/dev/null
```

## Cross-border

| User need | Actor ID | Returns |
|-----------|----------|---------|
| Sanctions + adverse media | `regdata/adverse-media-screener` | OFAC, UN, EU, UK list matches and classified negative-news hits |

## Poland

| User need | Actor ID | Returns |
|-----------|----------|---------|
| One-call KYB verdict | `regdata/poland-kyb-check` | Identity, beneficial owners, insolvency for company and owners |
| Beneficial owners | `regdata/crbr-beneficial-owners-scraper` | CRBR UBO entries, discrepancy reports |
| Insolvency / debtors | `regdata/krz-debtor-scraper` | KRZ bankruptcy, restructuring, enforcement proceedings |
| Court gazette notices | `regdata/msig-scraper` | MSiG bankruptcy, liquidation and registration notices |
| Board members, shareholders | `regdata/krs-fullnames-scraper` | KRS officers and shareholders with full names |
| Financial statements | `regdata/poland-krs-financial-scraper` | Balance sheet and P&L from filed statements |
| Business identity | `regdata/polish-regon-scraper` | REGON identity, PKD codes, status |
| Licensed financial firms | `regdata/knf-registry-scraper` | KNF payment, e-money and lending registers |
| Politically exposed persons | `regdata/poland-parliamentary-pep-scraper` | Sejm members across terms |
| Land registry | `regdata/ekw-ksiegi-wieczyste-scraper` | Property owners, mortgages, easements |
| Waste-management registration | `regdata/bdo-waste-registry-scraper` | BDO register entries |
| Competition authority decisions | `regdata/uokik-decisions-scraper` | UOKiK decisions and fines |
| Tax-office auctions | `regdata/poland-elicytacje-auction-scraper` | eLicytacje auction listings |

## Germany and Austria

| User need | Actor ID | Returns |
|-----------|----------|---------|
| German company profile | `regdata/germany-handelsregister-scraper` | Officers, capital, register number, EUID |
| German insolvency | `regdata/germany-insolvency-scraper` | Insolvency announcements |
| Austrian insolvency and court notices | `regdata/austria-ediktsdatei-scraper` | Ediktsdatei publications |
| Austrian business directory | `regdata/wko-business-directory-scraper` | WKO members with contact details |

## Southern and Western Europe

| User need | Actor ID | Returns |
|-----------|----------|---------|
| Spanish corporate acts | `regdata/borme-corporate-acts-scraper` | BORME incorporations, appointments, dissolutions |
| Spanish company directory | `regdata/spain-company-directory-scraper` | NIF, officers, CNAE, legal form |
| Spanish insolvency | `regdata/spain-concursal-scraper` | Registro Publico Concursal parties and roles |
| Italian company profile | `regdata/italy-registro-imprese-scraper` | Company data, officers, PEC |
| Italian certified email | `regdata/italy-pec-lookup` | PEC address and SDI code by VAT number |
| French company profile | `regdata/societe-com-scraper` | SIREN, directors, financials |
| Belgian company profile | `regdata/belgium-kbo-company-scraper` | KBO/BCE company, directors, NACEBEL |
| Portuguese corporate acts | `regdata/portugal-corporate-acts-scraper` | Published acts: incorporations, changes, dissolutions |
| Irish company profile | `regdata/ireland-cro-company-scraper` | CRO identity, status, address |
| Cypriot company profile | `regdata/cyprus-drcor-company-scraper` | Identity, directors, secretary, registered office |

## Central Europe and Nordics

| User need | Actor ID | Returns |
|-----------|----------|---------|
| Czech insolvency | `regdata/czech-isir-insolvency-scraper` | ISIR debtor, case, court |
| Czech public auctions | `regdata/czech-drazby-auction-scraper` | Auction listings |
| Slovak beneficial owners | `regdata/slovakia-rpvs-ubo-scraper` | RPVS UBO entries with PEP flag |
| Danish annual accounts | `regdata/denmark-annual-accounts` | CVR financial statements |
| Norwegian annual accounts | `regdata/norway-annual-accounts` | Bronnoysund financial statements |
| Estonian annual accounts | `regdata/estonia-annual-accounts` | e-Business Register financials |

## Americas, Africa, Middle East

| User need | Actor ID | Returns |
|-----------|----------|---------|
| California business entity | `regdata/california-sos-business-scraper` | Entity, agent, status |
| California UCC liens | `regdata/california-ucc-lien-scraper` | Debtors and secured parties |
| Illinois business entity | `regdata/illinois-sos-business-search` | LLCs, corporations, agents |
| US county recorded documents | `regdata/us-county-recorded-documents` | Lis pendens, liens, deeds (TX, OH, MI) |
| Colombian company | `regdata/colombia-rues-company-scraper` | RUES identity, chamber, status |
| Nigerian company | `regdata/nigeria-cac-company-scraper` | CAC identity, classification, status |
| Abu Dhabi Global Market company | `regdata/uae-adgm-public-register-scraper` | ADGM register entries |
