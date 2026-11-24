# CRM hygiene: confirm contacts at their accounts

This route keeps business records current: which contacts the user already holds can still be confirmed at their account, and who holds those roles now. The user's own list is the input. Never add emails or phone numbers to it, and never ask for them.

## Steps

1. Group the contacts by account and resolve each account ([resolve-accounts.md](resolve-accounts.md)).
2. Map each account once with the contacts' roles as title phrases ([map-people.md](map-people.md)), sized to the number of contacts at that account plus a few for replacements.
3. Match contacts to rows on the profile slug (the last part of the profile URL) when the CRM has the URL. Without a URL, a match on full name at the same account is a lead to review, because names repeat.
4. Send the contacts the run did not return, and whose profile URL the user holds, to the Profile API in one batch (decision rule 6). Nobody else goes to that step.

## Outcomes, one per contact

- "Confirmed at the account": seen in the map with `verified` true, or the profile has an `experience` entry that links the account's company page.
- "Profile shows a different current employer": state what the profile shows and when it was read. Do not write "left the company"; the person may hold two roles, or the profile may be stale.
- "Not confirmed": not seen in the map, and either no profile URL or a profile that could not be read. Use this whenever evidence is missing. It says nothing about whether the person left (decision rule 5).

Add the people the map found in the same roles as "now in this role at the account", so the user can update the record instead of only flagging it.

## Output

A table per account: the contact as held in the CRM, the outcome, the evidence (row or profile read, with the run id and date), and a suggested action (keep, review, or update the role holder). Ask the user to review every "different employer" row before changing the CRM, and never bulk-overwrite records from a single run.

## Limits

- This is upkeep of business records. Its outcomes are never a basis for a decision about the person, such as hiring, tenancy, credit or insurance.
- Do not re-check the same named person on a schedule. Re-run the account map instead and treat the changes as a list to review.
