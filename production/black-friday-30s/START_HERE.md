# Ren Black Friday 30s: production package

Contents
- CLAUDE_CODE_PROMPT.md: the prompt to paste into Claude Code
- script/ren-black-friday-30s.md: narration, 10-beat shot plan, clip mapping, asset requirements report
- assets/black-friday/: 4 environments (E1-E4) and 2 props (P1-P2), generated with FLUX.2-dev in the approved Ren style; TEMPORARY, not approved
- manifest/assets_manifest.json: SHA-256 hashes, sizes and approval status
- tools/gen_assets.py: how the assets were generated (needs a Hugging Face token in the HF_TOKEN environment variable; no token is stored here)

Not included, by design: Ren clips and stills (use the repo library), voice audio (generated only after script approval), phone/notepad/calculator/text graphics (drawn in code).
Stop point: Claude Code must stop after the 15-second prototype for your approval.
