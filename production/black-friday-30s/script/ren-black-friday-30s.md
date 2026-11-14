# Ren 30-second short: Black Friday (v2, aligned to repo Shorts rules)

Rules applied: `AGENTS.md`, `CLAUDE.md`, `project/REN_SHORTS_RULES.md` (asset-first review, 1080x1920, change every 2-4s, Ren left and content right, text and numbers drawn in code, mouth-closed clips, 15-second prototype gate, stop for Jon's approval).
Format: 9:16, 1080x1920, 24fps, US dollars and US spelling. British Qwen Ren voice. No music.

## Narration (77 words, approximate timings at 0.385 s per word; measure the real voice before building)

| # | Time | Spoken line | Visual (full-bleed) | Ren clip (library) |
|---|---|---|---|---|
| 1 | 0:00-0:03 | "Black Friday isn't a sale. It's a test." | E1 shop street. Code overlay BLACK FRIDAY on the blank banner. Opening disclaimer overlay | ren_point_camera (1.12-5.88s), Ren left |
| 2 | 0:03-0:06 | "Countdowns. 'Only three left.' Built to make you rush." | E2 tabletop with phone drawn in code: countdown 02:59:59 and ONLY 3 LEFT badge, pops in | none (prop close-up) |
| 3 | 0:06-0:10 | "Rule one: make your list before the sales start." | E2 kitchen. Notepad drawn in code on the right, RULE 1 tag, items type in | ren_clipboard_tick (0.75-10s), Ren left |
| 4 | 0:10-0:12 | "Not on the list? Not a deal." | Notepad close-up, red cross over an unlisted item (code) | none |
| 5 | 0:12-0:14 | "Rule two: do the math." | E2 with calculator drawn in code, RULE 2 tag | ren_point_down_right (1.0-7.0s), Ren left |
| 6 | 0:14-0:18 | "A hundred dollars at thirty percent off still costs seventy." | Calculator close-up: 100 x 0.70 = 70, price tag $100 changes to $70 (code) | none |
| 7 | 0:18-0:20 | "It's only savings if you needed it." | E3 porch with parcel pile | ren_shrug (1.12-10s), Ren left |
| 8 | 0:20-0:23 | "Rule three: let it sit in the cart for twenty-four hours." | E2 with P2 hourglass and phone cart (code), 24h label, RULE 3 tag | none |
| 9 | 0:23-0:26 | "Still want it tomorrow? Buy it." | E4 living room, morning light | ren_nod_yes (1.12-9.0s), Ren left |
| 10 | 0:26-0:30 | "Check out the Money Leak Audit Workbook in the description." | E4 with P1 piggy bank, end card in code. Closing disclaimer held 2s+ | ren_thumbs_up (2.75-8.0s), Ren left |

Overlays: "Educational content only, not financial advice." at start and end (30px minimum, 2s+ at the end). Workbook is not called "free", per repo. Numbers are illustrative and the math check is $100 x (1 - 0.30) = $70.

If the voice runs over 30s, cut beat 7 (-6 words) or shorten beat 2 to "Countdowns. 'Only three left.'" (-5 words). I cannot listen to audio, so please check pronunciation.

## Asset requirements report (asset-first checkpoint)

| Item | Status | Source |
|---|---|---|
| Ren clips (8 above) | Reuse as-is | `assets/ren_library/*.mp4`, windows from `ren_library.json`. White-background clips need matting at native resolution before compositing on environments; inspect edges, glasses and white shoes |
| Ren stills | Not needed | `library/ren_approved/` |
| E1 shop street | New, generated | FLUX.2-dev image-to-image, style reference `Porch_background_16x9.png`. Large blank navy sign, built for code text |
| E2 kitchen table | New, generated | style reference `Office_background_16x9.png` |
| E3 porch with parcels | New, generated | style reference `Porch_background_16x9.png`. Existing porch plate extended |
| E4 living room, morning | New, generated | style reference `Office_background_16x9.png` |
| P1 piggy bank, P2 hourglass | New, generated, on white | style reference `HR_folder_page6_prop.png`. Matte out the white |
| Phone, notepad, calculator, price tag, badges, rule tags, countdown, captions, CTA | To draw in code | per rules, not generated |
| Voice | Not generated yet | Qwen British clone, after script approval |

Known issues to review: generated assets are 768x1344, below the 1080x1920 canvas, so upscale once and check sharpness on a phone-sized preview (or regenerate at higher resolution). E1 has an unusually large blank navy sign; if it looks odd in motion, ask for a regenerate. All six are temporary until Jon approves them, and none is claimed as approved art.

## Claude Code build prompt

```
New Ren Short: "Black Friday test", about 30 seconds, 1080x1920.
First: identify the active git branch and confirm the files and assets in this prompt actually exist. Some media lives on production branches (video/free-money-v2, codex/ren-approved-v3), not necessarily main. Do not substitute assets, voice, QA or renderer silently.
Read AGENTS.md, CLAUDE.md, project/REN_VIDEO_RULES.md and project/REN_SHORTS_RULES.md before doing anything.

Script and shot plan: /scripts/ren-black-friday-30s.md. Use the narration word for word. Educational only, not financial advice; US dollars; US spelling. Do not call the workbook "free".

Steps:
1. Save the asset requirements report (scene IDs, paths and SHA-256 hashes, approval provenance, missing items). Use the library clips named in the table, Ren left and content right, mouth-closed clips only, discard clip audio, no music.
2. Environments E1-E4 and props P1-P2 are in /assets/black-friday/ and are temporary until I approve them. Matte the white-background Ren clips at native resolution before compositing. Never redraw Ren. If a pose is missing, list it and ask me.
3. Draw all numbers, phone, notepad, calculator, price tags, badges, rule tags, captions and the end card in code. Run the measured text layout check (42px text, 40px captions, 30px disclaimer, safe area x=72-900, y=180-1560). Keep $100 x 0.70 = $70 verified in code.
4. Use the approved British Qwen voice only after I approve the script. Report the real narration length and flag any beat that does not fit.
5. Render the 15-second prototype only, with at least three distinct compositions. Run preflight and QA, then send the MP4, actual runtime, asset report, QA findings and unresolved issues. STOP and wait for my explicit approval before rendering the full Short.
Work on an isolated branch. Do not merge or publish.
```

## Image prompts used (FLUX.2-dev, Hugging Face image-to-image via fal-ai)

Style line: Match the art style of the input image exactly: clean dark ink outlines, flat soft colours, restrained shading, navy, cream, warm wood and soft gold accents. No text, no letters, no numbers, no logos, no people, no characters. Absolutely no writing, lettering or symbols anywhere, every sign and bag is blank.

- E1: re-draw the porch plate as a daytime street scene with a shop front, blank navy banners, a blank red sign above the door, plain blank paper shopping bags.
- E2: re-draw the office plate as a cosy home kitchen from a slightly high angle with a clean empty wooden table filling the lower half.
- E3: keep the porch and door, add a tall pile of plain cardboard parcels and blank paper bags.
- E4: re-draw the office plate as a calm living room in soft morning light with clear floor space on the left.
- P1: single happy navy-and-gold piggy bank with gold coins on plain white. P2: single wooden hourglass with gold sand on plain white.
