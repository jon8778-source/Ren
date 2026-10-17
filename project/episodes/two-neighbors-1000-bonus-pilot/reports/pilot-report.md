# Pilot report: Two Neighbors, Same $1,000 Bonus

`renders/pilot.mp4`: 1920x1080, 30 fps, 65.3 s. It covers the hook, "meet Max and Lena" and the start of Max's
spending (up to "The first week is great"). Built with the full pipeline. Automated results are in `qc-pilot.md`:
overall **PASS**.

| Area | Result |
|---|---|
| Voice | The same Ren voice and settings as earlier episodes (am_michael + am_eric, 0.93x). 2 chunks, -22.5 / -22.7 LUFS, pitch 133 / 131 Hz. I can't hear audio: please listen for pronunciation and pace. |
| Characters | 13 poses used (Ren, Max 30 and one year later, Lena 30 and one year later), all byte-identical to the locked sheets. |
| Numbers | Maths recalculates and all 13 story claims hold. Every spoken number matches the table; every on-screen number comes from it. Money cards are tagged "Example figures". |
| Captions | 16 captions, word for word, 0.04-0.05 s after speech starts, never more than 2 lines. |
| Visual change | 17 scenes, 57 visual changes, longest hold 4.1 s (limit 7 s). |
| Safe zone / text | Nothing in the bottom 130 px; smallest text 40 px. |
| Disclaimer | On screen at the start and end, in the "Quick note" card, and in description.txt. |

## New in this episode
- **Bonus envelope prop:** slides in, opens, and a $1,000 card rises out. It will come back in each spending scene and in the
  final shot.
- **Houses:** two houses with a fence, with Max and Lena standing in front ("Same street", "Next door for 3 years").
- **Spending card:** each purchase lands as a drawn icon card with its price, while the envelope counts down what's left
  ($1,000 to $300 to $0). Lena's scenes will use the same card (cleaner, trip, cooking class).
- **Full-video voice:** already recorded, 4:12 (the earlier estimate was about 4:20).

## What went wrong (fixed)
- The envelope flap covered the $1,000 card when it opened, and a later version pushed the envelope into the captions.
  The envelope is now layered so the card rises out of the pocket, and the label fades as the card comes up.
- The houses block was slightly too tall and its tag sat on the caption. Made shorter.
- A placeholder timing in the spending scene showed up in QC as a 2.8-hour hold. Replaced with a proper "reveal" count.
- The QC's safe-zone check covers only the bottom 130 px, so it doesn't catch a graphic running into the captions. I check
  frames by eye for that.
- Shared template change: the envelope label now fades as the card rises. "The Same $1,200 Surprise" also uses the envelope,
  so a re-render of that episode would show the same change.

## Questions before the full video
1. Listen to the voice, especially "Lena", "sixty-five inch TV" and "sneakers".
2. Do you like the houses and spending-card style? The rest of the video builds on them.
3. The full video will be about 4:15 long. You accepted the length at the script gate; just confirming it's still OK.
