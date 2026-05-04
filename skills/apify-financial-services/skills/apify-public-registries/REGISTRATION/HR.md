# HR — Sudski registar (Court Register) API registrace

## PPF firmy v HR
- Nova TV d.d. — OIB 75399377119, MBS 080222668

## Registrace API

1. Jdi na https://sudreg-data.gov.hr
2. Registruj se (email, organizace)
3. Po schválení dostaneš:
   - **Client ID**
   - **Client Secret**
   - **Token URL** pro OAuth2 autentizaci
4. Získej access token:
   ```bash
   curl -X POST <token-url> \
     -d "grant_type=client_credentials" \
     -d "client_id=<id>" \
     -d "client_secret=<secret>"
   ```

## Endpointy

```
Base URL: https://sudreg-data.gov.hr/api/javni/

GET /sudovi                           — seznam soudů
GET /subjekt?oib={oib}                — hledání podle OIB
GET /subjekt?mbs={mbs}                — hledání podle MBS
GET /subjekt/{id}                     — detail subjektu
GET /subjekt/{id}/uloga               — role (jednatele, prokury)
GET /subjekt/{id}/kapital             — základní kapitál
```

## Formát
- REST/JSON + XML
- OAuth2 (client_credentials flow)
- OpenAPI specifikace na portálu
- Test prostředí: https://sudreg-data-test.gov.hr
- Podpora: sudski.registar@pravosudje.hr

## Po registraci
Nastav env variables:
```bash
export HR_SUDREG_CLIENT_ID=<id>
export HR_SUDREG_CLIENT_SECRET=<secret>
export HR_SUDREG_TOKEN_URL=<url>
```
Pak spusť `fetch_all.py`.
