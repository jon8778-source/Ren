# Production source / financial accuracy notes

Current production text is narration.txt/script.md. Original supplied and revised
candidate files in ../docs/ are preserved as historical inputs, not the final voice
source. Jon approved three replacements on 6 November 2026 (“Yes ok with that”).
See wording-approval.json for exact text and original 17 WAV hashes.

Removed from current narration/graphics: the unverified 2027 employer-cost 8.2%
forecast, the $4,500 HSA limit and the January 15 Marketplace deadline. Current
copy directs viewers to their actual employer plans, current IRS rules and the
current HealthCare.gov/state Marketplace dates. No unchecked date/limit/forecast
is represented as checked. No KFF premium statistic or unattributed expert quote.

Reference URLs for viewers/future checks (not fetched or independently certified
under the current restricted cloud network policy):
- IRS Publication 969: https://www.irs.gov/publications/p969 — HSA eligibility,
  federal tax treatment and qualified medical distributions; employer funding
  counts toward annual contribution limits. State treatment can differ.
- HealthCare.gov: https://www.healthcare.gov/quick-guide/dates-and-deadlines/ —
  current federal enrollment/effective-date guidance; check state exchanges too.
- https://www.healthcare.gov/glossary/out-of-pocket-maximum-limit/ — covered
  in-network limits; premiums and other exclusions are separate.

Ren, Dev, Priya, the group chat and plan costs are fictional. These are not plan
quotes, benefit guarantees or actual claim records. Shared ../assumptions.json
and calculations.py derive every plan/HSA amount; calculation-results.json passes.

PPO:210×12=2520; covered in-network bad-year2520+4000=6520. HDHP:70×12=840;
bad-year840+6500=7340, then750 employer HSA value gives6590; net gap70.
Normal PPO2520+150=2670. HDHP direct cash840+600=1440; after750 HSA value,
net economics690, illustrative gap1980. HSA employer value is not a cash rebate.
Premium difference140/month=1680/year; plus750 employer=2430 CONTRIBUTED before
spending/fees/growth. After600 HSA withdrawal1830 remains; if paid from other cash,
2430 can remain in the HSA absent other activity. No investment return assumed.
