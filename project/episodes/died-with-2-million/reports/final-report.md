# Final report: The Man Who Died With $2 Million

`renders/full.mp4`: 1920x1080, 30 fps, 4:42. Automated results: `qc-final.md`.
Overall: **FLAG** (one item waits on the owner; everything else passes).

| Check | Result |
|---|---|
| Maths | Table recalculates; all 13 story claims hold. Frank $2,223,597 at 65, $3,978,833 at 85; Bea $889,439 / $876,859. |
| Numbers | Every spoken number matches the table; every on-screen figure comes from it. Money graphics tagged "Example figures"; the energy chart is tagged "Illustrative". |
| Real statistics | **FLAG**: the EBRI line ([r03]) is still unverified. Confirm it in sources.json (status "verified"), or I cut the sentence and its card. |
| Voice | 6 chunks under 60 s, identical settings, leading silence 0.01 s, loudness within 0.4 LU, pitch within 0.4 semitones. |
| Characters | 29 poses used, all byte-identical to the locked sheets (Frank, Yara and Bea at 25/45/70+, Ren). |
| Captions | 87 captions, word for word; long sentences split at a pause; 0.04-0.07 s after speech; all fit in 2 lines. |
| Visual change | 69 scenes, 254 visual changes, longest hold 5.2 s. |
| Silence | None over 1 s during speech. |
| Safe zone / text | Nothing in the bottom 130 px on 564 sampled frames; smallest text 40 px. |
| Disclaimer | On screen at start and end; in description.txt (with the EBRI link and the 4% assumption). |

Fixed during the build: two big numbers overlapping on "Frank retires", clipped chart labels, squashed tile text,
an over-long research subtitle, a title running into the brochure's sun, and two captions that needed three
lines and ran into the YouTube controls area.
