# Paste this into Claude Code (working in the jon8778-source/Ren repo, on a new isolated branch)

First unzip this package into the repo working branch at `production/black-friday-30s/` (do not commit the PNGs or video to main).

```
New Ren Short: "Black Friday test", about 30 seconds, 1080x1920. All inputs are in production/black-friday-30s/.

First: identify the active git branch and confirm the files and assets named here actually exist. Some media lives on production branches (video/free-money-v2, codex/ren-approved-v3), not necessarily main. Do not substitute assets, voice, QA or renderer silently. If something required is missing, report the blocker.
Read AGENTS.md, CLAUDE.md, project/REN_VIDEO_RULES.md and project/REN_SHORTS_RULES.md before doing anything.

Script, shot plan and asset report: production/black-friday-30s/script/ren-black-friday-30s.md. Use the narration word for word. Educational only, not financial advice; US dollars; US spelling. Do not call the workbook "free".

Steps:
1. Verify assets against production/black-friday-30s/manifest/assets_manifest.json (SHA-256). Save the asset requirements report (scene IDs, paths and hashes, approval provenance, missing items). Use the library clips named in the shot plan, Ren left and content right, mouth-closed clips only, discard clip audio, no music.
2. Environments E1-E4 and props P1-P2 (production/black-friday-30s/assets/black-friday/) are TEMPORARY and not approved. They are 768x1344: upscale once to 1080x1920 and check sharpness. Matte the white-background Ren clips and the white-background props at native resolution before compositing. Never redraw Ren. If a pose is missing, list it and ask me.
3. Draw all numbers, phone, notepad, calculator, price tags, badges, rule tags, captions and the end card in code. Run the measured text layout check (42px text, 40px captions, 30px disclaimer, safe area x=72-900, y=180-1560). Verify $100 x 0.70 = $70 in code.
4. Do not synthesize voice until I approve the script. Then use the approved British Qwen voice only, report the real narration length and flag any beat that does not fit 30 seconds.
5. Render the 15-second prototype only, with at least three distinct compositions. Run preflight and QA, then send the MP4, actual runtime, asset report, QA findings and unresolved issues. STOP and wait for my explicit approval before rendering the full Short.
Work on an isolated branch. Do not merge, upload large video files or publish.
```
