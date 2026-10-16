# Ren Video Production & Decision Log

Repo jon8778-source/Ren; work on branch ccr-a31871f7-ihoco0 (PR #2 → main). Workflow: CLAUDE.md + project/README.md. Setup: `cd project && ./setup.sh`.

## 1. Core aesthetics & style
- Ren (glasses, dark hair, navy jacket) narrates everything; characters never speak.
- Solid plain white background, edge to edge; no gradients, patterns, scenery or office.
- Font Fredoka 500/600/700 only. Colours: ink #13233F, red #E23D3D (cost), green #1E9E5A (save), gold #F5B82E/#C98A0B, muted #7A8496, line #E3E7EE. No new colours.
- Flat 2D cartoon busts; all lettering/prices/numbers drawn in code, never AI lettering.
- No shaking: no talking bob, sway or breathing. Only entrance slide + small pop on pose change. Slow pan/zoom every scene; new visual every 5-7 s.
- Voice: Kokoro-82M, am_michael 0.5 + am_eric 0.5, speed 0.93 (~165 wpm), matched to the owner's "Bank Fee" reference. No music.
- Tone: warm, upbeat storytelling (scenarios, character comparisons); original, never copied.

## 2. Structural formats
- Long video: 16:9 1920x1080, ~5-6 min (~770-940 words). Character in left/right third, cards on the other side. Captions 50px, max 2 lines, above bottom 12% (y<950), long sentences split at a pause. Text ≥40px.
- Shorts: 9:16 1080x1920, ~30 s, 2 per episode, cut from the long video's lines and voice (shorts.json → pipeline/shorts.py → config.vertical.json). Nothing in bottom 420px or under right-hand buttons.
- Thumbnails: 1280x720, 3 options. Chosen: $1,200 ep = C ("WHO COPES BETTER?" low vs high income); $2M ep = A (big number + regretful face + "AND HE NEVER WENT").
- Pattern: hook with biggest number → meet characters → per-character segment (life, event, outcome, habit) → twist + takeaways → soft CTA.
- Disclaimer "Educational only, not financial advice" on screen at start and end, and in description.
- CTA: "Check out the Money Leak Audit Workbook in the description." Never "free" in video. $2M ep: no workbook mention (owner). Descriptions keep [WORKBOOK LINK].
- Money graphics tagged "Example figures"; conceptual charts "Illustrative".

## 3. Key decisions (chronological)
1. First 9:16 Remotion short "monthly vs yearly" ($9.99→$119.88); Ren art, voice, number spoken in hook.
2. More animation added; later rejected shaking/bobbing and office/walking for long form.
3. "Ahead by 30" (HyperFrames, 9:16, 49 s, office): one-off, not the main format.
4. Long-form pipeline: assumptions.csv → calc.py (+claims.txt) → script.md (numbers as spoken, tagged) → scenes.json → Remotion → qc.py.
5. "The Same $1,200 Surprise" (5:45; Sam, Nina, Claire, Marcus, Richard). Cut from 10 to 6 min. "FREE" removed from workbook graphic.
6. "The Man Who Died With $2 Million" (4:42), owner's script word for word except: "ahead of a lot of people" → "off to a strong start"; "decades later" → "nearly two decades into retirement". EBRI line verified by owner, kept. Thumbnail A + 2 shorts (Frank "next year", Bea life fund).
7. Rejected/avoided: invented stats, unsourced "most/many people" claims, typed numbers on screen, inconsistent character art (Yara 45/70 regenerated from Yara 25), 3-line captions, content in YouTube controls area, shaking, music, coloured backgrounds.

## 4. Active rules for next videos
- "New episode: <topic>" → follow CLAUDE.md. Gates: plan/questions → script OK (before voice) → 60-s pilot → "APPROVED" → full video + QC report → thumbnail choice → 2 shorts.
- Every figure in assumptions.csv; calc.py MATHS OK; every story claim in claims.txt. Real stats need sources.json status "verified" by owner, or cut. Never invent sources.
- Locked cast in project/characters (hashes in manifest.json): Ren(8), Sam/Nina/Claire/Marcus/Richard(5), Frank/Yara/Bea at 25/45/70 (4 each).
- New art: 4-expression sheets (neutral, happy, worried, +1); make age 25 first, use as reference for older ages. Split with pipeline/split_sheet.py, check on magenta, lock in manifest.
- QC must be OVERALL PASS; fix causes, never loosen checks. Check frames from every scene and fix overlaps before sending.
- Claude can't hear audio: owner checks pronunciation and pace.
- Commit and push after each stage; keep the branch merged with main.
