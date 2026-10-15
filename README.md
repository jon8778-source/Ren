# Ren Shorts (Remotion)

Example 17.5-second, 1080x1920 Ren short: "monthly vs yearly" ($9.99/mo = $119.88/yr).

## Scenes
| Time | Scene | On screen |
|------|-------|-----------|
| 0–6s | Hook | "$119.88" pops in, shocked Ren |
| 6–10.4s | Stack | 12 coins drop and stack, counter climbs to $119.88 |
| 10.4–13.8s | Checklist | Subscriptions slide in, each "×12" |
| 13.8–17.5s | CTA | Excited Ren, "Free budgeting workbook / Link in bio" |

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

## Voiceover
`public/monthly-vs-yearly.mp3` was generated locally with the open-source
[Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) TTS model (Apache-2.0),
as a 50/50 blend of voices `am_michael` and `am_eric` at 1.18× speed, matched to the reference
Ren voice (median pitch ~135 Hz, wide expressive pitch range, quick pace).
To voice a new short:

1. One-time setup:
   ```
   pip install kokoro-onnx soundfile          # ffmpeg must be on PATH
   npm pack kokoro-q8-shards@1.0.0 kokoro-js@1.2.1
   tar xzf kokoro-q8-shards-1.0.0.tgz && cat package/kokoro-q8.part{0..5}.bin > kokoro-q8.onnx
   tar xzf kokoro-js-1.2.1.tgz               # voices are in package/voices/
   ```
   (Or download `onnx/model_quantized.onnx` from onnx-community/Kokoro-82M-v1.0-ONNX on Hugging Face;
   sha256 `fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478`.)
2. Run one `"START|text"` per scene, using each scene's start time:
   ```
   python scripts/voiceover.py --model kokoro-q8.onnx --voices package/voices \
     --duration 17.5 --out public/<id>.mp3 "0|First line" "6|Second line" ...
   ```
   It prints where each line lands; keep each line inside its scene (lengthen the scene if not).
3. Set `voiceover: "<id>.mp3"` in the short's file.

That blend is the default. Other American male voices: `am_michael`, `am_puck` (brighter), `am_fenrir`
(fuller), `am_adam`, `am_eric`, `am_liam`; pass one (`--voice am_puck`) or a blend
(`--voice am_michael:0.5,am_fenrir:0.5`). Write numbers the way they should be said ("nine ninety-nine", "twelve").

## Prompt to make a new short
> Create a new short in src/shorts/ called `<id>` following the format of monthly-vs-yearly.ts.
> Topic: <topic>. 14 seconds. Hook with the biggest number in the first 3 seconds,
> soft CTA at the end. Reuse existing scene types where possible; if a new scene type
> is needed, add it to types.ts, create it in src/scenes/, and wire it into RenShort.tsx.
> Register it in src/shorts/index.ts, then render it to out/<id>.mp4.

## Prompt for a month of shorts
> Here are 16 topics: <list>. Create one file per short in src/shorts/ (14 seconds each),
> register them all, typecheck, then render each to out/<id>.mp4.
