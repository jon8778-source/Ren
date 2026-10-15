# Ren Shorts (Remotion)

Example 14-second, 1080x1920 Ren short: "monthly vs yearly" ($9.99/mo = $119.88/yr).

## Scenes
| Time | Scene | On screen |
|------|-------|-----------|
| 0–3s | Hook | "$119.88" pops in, shocked Ren |
| 3–7.5s | Stack | 12 coins drop and stack, counter climbs to $119.88 |
| 7.5–11s | Checklist | Subscriptions slide in, each "×12" |
| 11–14s | CTA | Excited Ren, "Free budgeting workbook / Link in bio" |

All text, prices and numbers are drawn by code, so they never warp.

## First run (in Claude Code)
Open this folder in Claude Code and say:

> Install the dependencies, run the typecheck, fix anything that fails, then start Remotion Studio.

Render the finished video:
`npx remotion render monthly-vs-yearly out/monthly-vs-yearly.mp4`

## Ren art and voiceover
Ren poses live in `/public` as transparent PNGs: `ren-shocked`, `ren-pointing`, `ren-thumbs-up`,
`ren-thinking`, `ren-worried`, `ren-waving`, `ren-talking`, `ren-neutral`.
Map them to moods in a short's `ren` field (see `src/shorts/monthly-vs-yearly.ts`).
Ren is animated in every scene: squash-and-stretch entrance, breathing and sway,
jumps on key moments, and pose changes mid-scene:

| Scene | Ren |
|-------|-----|
| Hook | shocked, jumps when the number lands, then worried |
| Stack | worried, jumps to shocked when the last coin lands |
| Checklist | thinking, nods as each item slides in, then points |
| CTA | thumbs-up (`excited`), then waves goodbye |

Set a scene's opening pose with e.g. `mood: "neutral"`. Timing lives in each scene file
under `src/scenes/` (`swaps` and `jolts` on `<Ren>`, in frames from the scene start).
Moods with no image fall back to the placeholder mascot.

For a voiceover, put an MP3 in `/public` and set `voiceover: "monthly-vs-yearly.mp3"`.

## Prompt to make a new short
> Create a new short in src/shorts/ called `<id>` following the format of monthly-vs-yearly.ts.
> Topic: <topic>. 14 seconds. Hook with the biggest number in the first 3 seconds,
> soft CTA at the end. Reuse existing scene types where possible; if a new scene type
> is needed, add it to types.ts, create it in src/scenes/, and wire it into RenShort.tsx.
> Register it in src/shorts/index.ts, then render it to out/<id>.mp4.

## Prompt for a month of shorts
> Here are 16 topics: <list>. Create one file per short in src/shorts/ (14 seconds each),
> register them all, typecheck, then render each to out/<id>.mp4.
