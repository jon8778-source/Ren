# Ren videos

## Current animation prototype route (27 October 2026)

For new animated prototypes, use `project/cliplib/README.md` and `render_hybrid.py`: animated Ren
in an office, brief story cutaways and moving infographics, with the Qwen cloned voice. This is the
owner-requested update to the prototype style and supersedes the white-only/static-bust/Kokoro
rules below **for this route**. The office and story art in the example are placeholders until the
approved office/Alex assets are supplied. Do not describe them as the exact approved artwork.
The legacy episode workflow below still applies to existing episodes.


Animated personal-finance videos narrated by Ren, the mascot. Owner: the channel creator, who reviews
at fixed gates. Two systems live here:

- `project/`: **the main pipeline**. A 16:9 long video (about 6 minutes) plus vertical shorts and
  thumbnails per episode. Use this for new episodes. Read `project/README.md` for every command.
- `project/DECISIONS.md`: condensed decision log (read first).
- `src/` (Remotion) and `videos/` (HyperFrames): older one-off 9:16 shorts. Leave them alone unless asked.

## "New episode: <topic>" means this workflow

When the owner asks for a new episode (a 6-minute video and 2 shorts), run these stages in
`project/episodes/<id>/` (`<id>` is a short slug of the topic). **Stop at each gate and wait for the
owner's reply before continuing.**

1. **Setup** (once per session): `cd project && ./setup.sh`. In the Claude Code cloud container, pass
   `--browser-executable /opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell` to
   assemble.py and thumbnails.py.
2. **Plan and numbers:** `assumptions.csv` (income, fixed costs, leaks, savings per character, plus any
   `value` rows the story needs) and `claims.txt` (every factual story claim as a checkable expression).
   Run `python3 pipeline/calc.py episodes/<id>`: it must print MATHS OK.
3. **Script:** `script.md`, about 900 words for 6 minutes, with numbers written as spoken and each line
   tagged with the table values it says. **GATE: send the script and wait for "OK".**
4. **Scenes:** `scenes.json`. Reuse the templates in `remotion/src/Graphics.tsx` and add new ones if needed.
   Put numbers on screen only as `{refs}`; change the visual at least every 7 seconds.
5. **Voice:** `.tools/venv/bin/python pipeline/voice.py episodes/<id> --model .tools/kokoro-q8.onnx --voices .tools/voices`
6. **Render:** `python3 pipeline/assemble.py episodes/<id> --out renders/full.mp4 ...` (about 9 minutes; run it
   in the background). Look at frames from every scene and fix overlaps before the QC.
7. **QC:** `.tools/venv/bin/python pipeline/qc.py episodes/<id> --video renders/full.mp4 --name final`.
   It must say OVERALL PASS. Fix causes, never loosen checks. Send the video and `reports/qc-final.md`.
8. **Thumbnails:** `python3 pipeline/thumbnails.py episodes/<id> ...`, giving three options.
   **GATE: the owner picks one.**
9. **Shorts:** write `shorts.json`, with two self-contained ~30-second stories made of the long video's
   lines, plus scene overrides where a line's picture needs context. Run `pipeline/shorts.py`, then assemble
   with `--config config.vertical.json`, then QC each short. Send both.
10. Commit and push after each stage, on the session's working branch.

## Owner's standing decisions
- Ren narrates everything. One voice: Kokoro `am_michael` + `am_eric` 50/50 (settings in `config.json`).
  No music.
- Solid plain white background. No other colours or fonts beyond `config.json` (Fredoka, navy/green/red/gold).
- Characters must not shake: no talking bob or sway. Only the entrance slide and a small pop on pose changes.
- Cast with locked art in `project/characters/` (hashes in `manifest.json`): Ren (guide), Sam (L1), Nina (L2),
  Claire (L3), Marcus (L4), Richard (L5). New characters: cut out with `pipeline/cutout.py`, check the
  cutouts on a coloured background, then add them to the manifest.
- US dollars, US-style costs. Every figure is an illustrative example, labelled "Example figures" on screen.
- Never invent statistics or sources. A real statistic needs `[VERIFY]` plus a source link, or it gets cut.
  The QC flags claims like "most people".
- "Educational only, not financial advice" on screen at the start and end, and in the description.
- Call to action: "Check out the Money Leak Audit Workbook in the description." Don't call the workbook
  "free" in the video. Descriptions carry a `[WORKBOOK LINK]` placeholder for the owner.
- Long video about 6 minutes. Shorts 9:16, about 30 seconds, two per episode. The owner liked thumbnail
  layout "C": who copes better, lowest vs highest income.
- If unsure, ask rather than guess. Say plainly that you can't listen to the audio, and ask the owner to
  check pronunciation.
