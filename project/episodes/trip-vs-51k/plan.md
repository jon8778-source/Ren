# Plan: The $3,000 Trip vs $51,000 at 70: Which Is Worth More?

## Owner decisions (Gate 1)
- D1 (a): a normal episode with the locked Ren busts (`characters/ren/`, 8 poses). No puppet rig, no walking; props
  appear beside Ren on cards, not in his hands. Ren is on screen in every scene.
- D2: Ren's usual voice (Kokoro am_michael + am_eric 50/50, speed 0.93, about 168 wpm).
- D3: shorter length accepted: 652 words, about 3:55 of voice, about 4:10 with pauses for the visuals.
- Standing rules kept: no music; Fredoka and the channel colours (config.json); the standing call to action, without
  "free"; "Example figures" on money cards; "Educational only, not financial advice" at the start and end; real-world
  claims need [VERIFY] and the owner's OK; loudness -16 LUFS; thumbnail options and two shorts afterwards.
- The brief's money note stays too: "Example only. Assumes 7% average yearly return, before inflation. Not financial
  advice." in the bottom corner whenever $3,000, $51,433 or $10,000 is on screen.
- Gates: script OK → 60-second pilot → full video + QC → thumbnail (Option 1 chosen in the brief) → two shorts.

## Numbers (assumptions.csv; `python3 pipeline/calc.py episodes/trip-vs-51k` prints MATHS OK)
- $3,000 at 28, invested at 7% a year for 42 years (to 70): 3,000 x 1.07^42 = **$51,432.77**, shown as **$51,433**
  (normal rounding). Narration: "about fifty-one thousand dollars" (within $1,000 ✔).
- Kids at 28, you live to 88: they inherit at 60 ✔. $10,000 at 30 vs at 60.

## Script changes from the owner's text (each needs the owner's OK)
1. [g02] "Lots of people plan to leave money to their kids, and that's lovely." → "If you plan to leave money to your kids,
   that's lovely." (an unsourced claim about what lots of people do).
2. [c07-c08] "Money tends to go up as we get older. Health and energy tend to go down." → "Your money can keep growing as you
   get older. Your health and energy don't always keep up." (softer than a general claim about everyone; the chart is
   labelled Illustrative).
3. [e07] "grab my free 50/30/20 workbook. The link's in the description." → "check out the Money Leak Audit Workbook in the
   description." (standing call to action, no "free").

## Claims needing your OK (sources.json, status VERIFY)
- [h05] 7% average yearly return: the example's assumption, labelled on screen as such.
- [m01] "memory dividend" and [b02] "time buckets" are ideas from Die With Zero by Bill Perkins; [r02] the book assumes you
  don't run out. Source: publisher page https://www.foyles.co.uk/book/die-with-zero/bill-perkins/9780358567097 (publisher
  copy and reviews describe both ideas). The book card on screen is a plain generic design, with no real cover art.
