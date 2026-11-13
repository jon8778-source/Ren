# Scene and animation direction: THREE BILLS

**Target:** 16:9 1280×720 or higher, 24 fps hybrid Ren animation, target ~6:00 (actual duration dictated by natural Qwen delivery). This is a **beat map**, not a frame-accurate shot list; convert to contiguous, frame-aligned shots once audio is approved. Distinguish actual character animation from moving a still.

| Time guide | Story focus | Visual staging and action | Assets / overlays | Ren return |
|---|---|---|---|---|
| 0:00–0:35 | Three surprises; Maya's immediate feelings | Genuine Ren MP4 in calibrated office, animated car key spinning to halt, Maya reacting to blank bill, sink drip, animated dates 3/16/27, Ren close-up and Maya staring at phone | approved Ren MP4; `car_key.png`, `blank_invoice.png`, `leaking_pipe.png`, `maya_03_worried_phone.png`, existing office; numbers drawn in code | 0:00, 0:16, 0:27 |
| 0:35–1:16 | Flashback: old $80 buffer/$600 repair | Maya walks to car only if approved walking motion exists; otherwise cut from character shot to car exterior, invoice close-up and phone. Ren narrates consequence in office | existing repo parking plate; approved Maya cutouts; phone and invoice props; overlay `$80`, `$600` code-generated | 0:35, 0:56 |
| 1:16–1:57 | Automatic $50 for 52 weeks | Calendar pages turning around account transfer, not a static 52-box presentation; Maya physically puts phone down and walks out of frame only if genuine motion exists. Cut to weekend outing via existing approved scene if available | prop `blank_phone.png`, `savings_envelope.png`; animated overlays `$50/week`, `52 weeks`, `$2,600` | 1:17, 1:42 |
| 1:57–2:37 | Day 3, car repair | Source parking plate with grounded Maya; car-key close-up; Ren explains balance change; short overlay of $760 | existing car plate; Maya surprisedd, car key, phone; code overlay $2,600 − $760 = $1,840 | 1:58, 2:22 |
| 2:37–3:14 | Day 16, dentist | Establishing dental waiting room; Maya checking phone on existing calibrated neutral background, cut to invoice; optional rear-camera move through the clinic, no mouth animation | `dental_waiting_plate_16x9.png` (provisional), Maya worried, `blank_invoice.png`, code overlay `$390`, `$1,450` | 2:39, 3:03 |
| 3:14–3:57 | Day 27, kitchen leak | Establish leak by close-up on exposed pipe; Maya reacts with envelope; Ren returns; actual separate overlay balance calculation. Keep new kitchen plate unpopulated until geometrically calibrated | `kitchen_sink_plate_16x9.png` (provisional), pipe prop, Maya surprised, code overlay `$1,050`, `$2,200`, `$400` | 3:18, 3:40 |
| 3:57–4:41 | Reframe: used fund, not failed | Short story flashbacks of three problems resolved; juxtapose a repaired car, medical receipt, fixed pipe using action and movement; Ren close-up delivers point | existing scenes/props, Maya relief, animated fund bar with **correct fixed total** | 4:00, 4:27 |
| 4:41–5:31 | Four practical principles | Demonstrate each principle with Maya using a phone, separating envelopes, and selecting an accessible savings account; avoid a PowerPoint stretch of four rectangles | approved Maya neutral + worried + relief, envelope, phone, illustrated environment; code icons/text only | 4:43, 5:08 |
| 5:31–~6:02 | Payoff and question | Maya outside at sunset/porch, breathing more easily; animated Ren close, meaningful ending. No invented sequel or guarantee | approved porch plate with perspective check, Maya relief, Ren actual animation, end-card disclaimer | 5:31, 5:48 |

## First-minute pilot visual checklist

- 00:00–00:05 real Ren animation, no static Ken Burns masquerading as motion.
- ~00:05–00:15: car, invoice and kitchen shots interleaved with actual Ren movement. No story still longer than 2.5s.
- ~00:15–00:25: sum of `$2,200`, calculated and rendered in code. No faux counting total beside a partly drawn equation.
- ~00:25–00:35: Maya looks at bank phone; the screen is blank in PNG and must be drawn in code. Cut back to animated Ren.
- ~00:35–01:00: flashback $80 buffer, $600 bill and opportunity-cost anxiety. Keep Ren in actual 5.5s-or-shorter animation shots, source clip audio muted.
- Use **v2** episode narration from `SCRIPT.md`, not v1 or placeholder story shorthand. Trim/split beats only after natural approved Qwen audio timing and script approval.

## Shot and camera constraints (mandatory)

- `REN_LONGFORM_BASELINE.md`, `REN_VIDEO_RULES.md`, `REN_LONGFORM_CHECKLIST.md` (8 Nov 2026) take precedence over historical white-only/Kokoro instructions.
- Ren MP4 animation shot ≤5.5s; story **still** ≤2.5s; standalone graphics ≤3.5s. For longer narrative beats use multiple distinct actions and different shot types.
- Ren returns in roughly 30–45s unless it would interrupt meaningful action.
- Office presenter default: Ren left, visuals/figures right. Do not cover furniture with large panels or use permanent footer.
- No speaking animation for Maya. All spoken lines are voiced by Ren, with approved Qwen clone only.
- Standing figures scaled with calibrated perspective in `project/cliplib/ren_stage.py`, feet above frame bottom with tight algorithmic contact shadows. Do not pretend a standing character is seated behind laptop/desk.
- No body wobble or pixel-snapped shaking; use float-placement (`paste_smooth` / `place_smooth`). Align shadows to character motion.
- New kitchen and dental plates are original **provisional** flat illustrations. They are clean establishers only until perspective has been calibrated or owner explicitly approves a corresponding shot construction. Do not treat them as approved film frames.
- Per-shot and complete film QA: 24fps frame-aligned contiguous timeline, `[start,end)` cuts, inspect every shot midpoint and transition, actual full decode fatal on error, 100% face/feet/shadow edge checks, run existing `validate.py`, `jitter_check.py`, `qa_timeline.py`.

## Script v2 continuity additions

- Flashback: show the $600 car repair resulting in credit-card debt and a postponed dentist visit, but do not invent extra fees or interest amounts.
- Fund build: show card payoff **before** 52 weekly contributions. Contributions pause at the $2,600 target; do not depict deposits continuing into the three-bill month.
- Day 27: include Maya opening the banking app that evening and thinking she had gone backwards; emotional callback to the hook, before Ren reframes the outcome.
- The four Maya pose PNGs are **owner approved**. Their motion still must be honest cutout/limited illustration; do not call it full-body actor animation.
