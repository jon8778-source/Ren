# Maya art audit (8 Nov 2026)

Owner approved: the Maya sheets as the identity lock and source art, and the seated stool/armchair poses.
NOT approved: script (no `SCRIPT APPROVED` yet), plates, any rig output. No voice has been synthesised.

`split_sheets.py` mattes the 10 supplied sheets and cuts them into 50 single-pose transparent PNGs
(`art/poses/`, local only, gitignored). All 10 sheets split to the expected pose counts.
Source figures are about 600 px tall (seated/standing) and 300-400 px wide, so close-ups will be soft.

| ID | Status | Source poses |
|---|---|---|
| M1 settle, raise phone | feasible, hardest morph | armchair 1-3 |
| M2 phone tap | OK | props 1-2 (hand, phone) |
| M3 smile at phone | OK | armchair 2, stool 3 |
| M4 reach, lift lid | feasible | stool 3-4, laptop props |
| M5 lean in | OK | stool 5 |
| M5b over-shoulder scroll | feasible; screen faces away, so UI must be an inset | overshoulder 1-4 |
| M6 finger hover | OK | receipt_laptop 4-5 |
| M7 exhale | OK | stool 6 |
| M9 walk in, sit | feasible, stylised (4-frame cycle, 2 sit frames) | walk_sit 1-6 |
| M10 type, sip, glance | OK | stool 1-3 |
| M11 pay bill, coin in jar | OK | stool 1/5, jar |
| M12 receipt wince | OK | receipt_laptop 1-3 |
| M14 pen tick | OK | props 3 |
| M15 form into drawer | OK | drawer 1-5 |
| M13 HR desk flashback | OK, new HR character needs approval | hr_offer_folder, maya_take_folder |

Open issues: laptop-on-lap poses need a plate where that reads (or use the desk poses); the
armchair replaces the sofa in H1; the coin, separate cup and folder props are still missing.
