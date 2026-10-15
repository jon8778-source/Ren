# Ahead by 30 (HyperFrames)

49-second, 1080x1920 Ren short: "Get ahead financially by 30", five steps built around the
free Money Leak Audit Workbook. Built with [HyperFrames](https://github.com/heygen-com/hyperframes)
(HTML + GSAP compositions), unlike the Remotion shorts in `src/`.

## Timeline
| Time | Scene | Ren |
|------|-------|-----|
| 0–2.3s | Title card "Ahead by 30?" | pointing |
| 2.3–9.2s | Bank statement: leaks light up, Step 1 badge, April/May/June | pointing / talking |
| 9.2–12.9s | Forgotten charges sheet, each one circled, "$170.95 leaking" | thinking |
| 12.9–15.5s | Workbook cover | thumbs-up |
| 15.5–21s | Step 2: emergency fund bar, 1 month → 3 months | pointing / talking |
| 21–26.7s | Step 3: credit card "no" sign, "Interest works against you" | worried |
| 26.7–32.4s | Step 4: payday → savings, coins on the arrow | pointing / talking |
| 32.4–36s | $1,000 → $7,612 count-up | thinking / shocked jump |
| 36–39.8s | Compound growth chart, "Example only" | shocked / neutral |
| 39.8–43.4s | Step 5: monthly check-in, "Small fixes beat big plans" | pointing / thumbs-up |
| 43.4–49s | FREE Money Leak Audit Workbook, link in bio, disclaimer | talking / waving |

Captions show each voiceover sentence as it is spoken. Ren changes pose on each sentence,
bobs while talking, breathes and sways the whole time.

The $7,612 figure is $1,000 compounded yearly at 7% for 30 years (1000 × 1.07^30 = 7,612.26).
The bank statement, brands and charges are made up for illustration.

## Files
- `index.html`: the composition (scenes, captions, Ren, audio, GSAP timeline).
- `assets/voiceover.mp3`: one continuous track in the Ren voice (Kokoro `am_michael` + `am_eric`
  blend, 1.18×). Sentence timings are in `assets/voiceover-timings.json`; the `BEATS` list and
  caption `data-start` values in `index.html` follow them.
- `assets/sfx/`: whoosh, pop, click, sparkle and chime from the HyperFrames bundled library
  (picked with `npx hyperframes media-use resolve --type sfx`).
- `assets/ren/`, `assets/fonts/` (Fredoka), `assets/vendor/gsap.min.js`: local copies so renders
  need no network.

## Commands
```
npm install
npx hyperframes preview        # Studio: scrub, edit, retime
npx hyperframes check          # lint + layout checks
npx hyperframes render . --output ../../out/ahead-by-30.mp4 --quality delivery
```
If HyperFrames can't find Chrome, run `npx hyperframes browser ensure`, or point
`HYPERFRAMES_BROWSER_PATH` at an existing Chrome headless shell.

## Changing the script
Regenerate the voiceover sentence by sentence, then update `assets/voiceover-timings.json`, the
`BEATS` list, the caption clips, and any scene `data-start`/`data-duration` that should move.
