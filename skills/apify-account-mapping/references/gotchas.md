# Observed behavior behind the decision rules

Live runs on the current build of each Actor (people step build 0.0.43, 2026-10-03, unless noted). The input schemas cannot express any of this. Recheck against the current README before relying on the exact numbers.

## People step (johnvc/linkedin-company-employees-api)

- Title filter matches page text (rule 3). Run Z3qqkAOC7ZR5jxqKY, a design tool company with the single title phrase "designer", returned 26 rows, all verified. Of the 20 with a title, 14 were design roles; the rest were a director of engineering, two engineering managers, an engineer, an APM and a writer. 6 rows carried no title at all.
- A role the account sells to (rule 3). Ramp sells to finance teams. In run kc2uwGTeVzaMSnmVO (build 0.0.48, 2026-10-04), all 3 of its verified rows came from the exact phrases "CFO" and "chief financial officer", and none held an asked role: 2 titles named other roles and 1 showed no title. In run V2eIvcVZVfQiG4oZP, its 3 rows all came from "Head of Finance", and none held an asked role either. The likely cause: the company name and finance titles appear together in the headlines of people in other roles.
- Twelve searches per account on a first pass (map-people.md). At 3 people per account, both runs above searched 12 slices per company, one per title phrase first (`RUN_SUMMARY`). Run V2eIvcVZVfQiG4oZP passed 13 phrases, and the 13th, a bare "Finance", was never searched. Run kc2uwGTeVzaMSnmVO passed 6, and the Actor filled the other 6 slices with each phrase plus the account's headquarters city.
- Board seat verified as a current role (rule 4). In run sVPA6coBatNga6H6y, 100 verified rows at one large company, one row came through a current "Board Member" position. Two staff titles in the same run contain "Partner" (partner channel marketing, engineering operations).
- Placeholder profile verified (rule 4). Run N625PcxdinmsFrurv returned a "Sales Test User" profile with 0 followers and no About text, verified at the account because its profile claims the role.
- Same input, different people (rule 5). Runs KphYhTbW3gAczxMEV, hjJdj1q01dz0d1Io6 and CIvKa0u5G5iubTjoF used one company, 3 people, fresh, minutes apart. The first and third returned the same three people; the second returned two different ones.
- History mostly hidden (rule 5). In run sVPA6coBatNga6H6y, `positions` was present on 3 of 100 verified rows, and 30 of the 90 headlines were cut off with "...".
- Short first read (troubleshooting). Run KphYhTbW3gAczxMEV read 0 of 3 rows right after it finished; a re-read minutes later matched.
- Duration (workflow). Run molmIIeZLFfZw7gCo mapped 15 accounts at 3 people each, fresh, in 945 seconds. Run qIGib95litK07fGPD, the same input from cache, took 41 seconds.

## Name resolution (rule 1)

- Hard names move between runs. In runs 1x9RrboUV5Q3qItvW and 3kdjy1GcUiHY0ZXsD, the people step was given the same name list: "Notion Labs" was not found in the first and resolved in the second.
- A bare name picks the best-known company. Company API run XURKMALf0BztyjyNj (build 0.0.84, 2026-09-22) resolved "Apex" to a fund administrator headquartered in Bermuda.

## Company API rows (johnvc/linkedin-company-api)

- Empty slug on an older build (rule 1). Runs XURKMALf0BztyjyNj and gmh3lyRFBh3hOa3SP (build 0.0.84) returned `slug` null on every row while `publicUrl` was present. Run CrE5Q3C3RxgUflvoy (build 0.0.96, 2026-10-03) returned it filled, so keep `publicUrl` as the fallback.
- Website format varies (rule 2). Run CrE5Q3C3RxgUflvoy returned `website` as a bare domain for one company, with a scheme for the second, and with a scheme and www for the third.
- Affiliated pages mix employers and product pages (resolve-accounts.md, find-accounts.md). In run CrE5Q3C3RxgUflvoy, one account listed a separate company page for its AI product among `affiliatedPages`, and another listed two showcase pages.
- Size band against profile count (resolve-accounts.md). Run gmh3lyRFBh3hOa3SP returned `companySize` "501-1,000 employees" next to `employeesInLinkedin` 7,124 for the same company.
