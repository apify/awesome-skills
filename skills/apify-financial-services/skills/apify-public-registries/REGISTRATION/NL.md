# NL — KvK (Kamer van Koophandel) API registrace

## PPF firmy v NL
- PPF Group N.V. — KvK 33264887
- Home Credit N.V. — KvK 34126597
- e& PPF Telecom Group B.V. — KvK 59009187
- CME Media Enterprises B.V. — KvK 33246826
- PPF NIPOS B.V. — KvK 90143299
- PPF Comco B.V. — KvK 85404632
- PPF Real Estate Holding B.V. — KvK 34276162

## Registrace API

1. Jdi na https://developers.kvk.nl
2. Klikni "Aanmelden" (registrovat)
3. Vyplň formulář (jméno, email, organizace, use case)
4. Po schválení dostaneš **API key**
5. Key se posílá v headeru: `apikey: <tvůj-klíč>`

## Endpointy

```
Base URL: https://api.kvk.nl/api/v1/

GET /zoeken?handelsnaam={name}        — hledání podle jména
GET /zoeken?kvkNummer={kvk}           — hledání podle KvK čísla
GET /basisprofielen/{kvkNummer}       — základní profil firmy
GET /vestigingsprofielen/{vestigingsnummer} — profil pobočky
```

## Formát
- REST/JSON
- OpenAPI/Swagger dokumentace na portálu
- Rate limit: dle subscription tier

## Po registraci
Přidej API key do env variable `KVK_API_KEY` a spusť `fetch_all.py`.
