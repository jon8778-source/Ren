# CLAUDE CODE PRODUCTION HANDOVER — REN LONG 1

**Copy this entire prompt into Claude Code. Attach/extract `ren_long1_assets.zip` and ensure `docs/REVISED_SCRIPT.md` is present.**

You are Ren's senior animation producer, story editor, video engineer, QA lead and finance fact-checker. Build a **60-second review pilot only** for a new US-focused, approximately six- to seven-minute animated personal-finance episode, then **STOP**. Do not render the full episode, cut Shorts, publish, merge, or push changes to `main` without the owner's explicit next instruction.

## Project and source-of-truth rules

- Repository: `https://github.com/jon8778-source/Ren`.
- Use a new isolated working branch (`feature/ren-long1-open-enrollment-pilot` or compatible).
- BEFORE making changes, read `AGENTS.md`, `project/REN_VIDEO_RULES.md`, `project/prototypes/coffee-minute-v3/README.md`, relevant renderer, asset manifests, validation files and `project/GITHUB_TASK_WORKFLOW.md` where publishing/checkpoint changes apply.
- The **approved coffee-minute v3 reference** and the actual checked-in repository rules outrank any contradictory generic instructions here.
- Preserve existing approved character assets, scene art, animation sources, narration and hashes. No regeneration of approved scenes.
- Check the repository before assuming paths or dependencies exist. Report missing assets/permissions clearly.
- The supplied asset pack contains **editable concept comps and math graphics derived from the user's reference images**, not replacements for the approved v3 renderer assets. Rebuild their visual treatment using approved v3 source artwork and the existing animation system.

## Episode

- Working title: **I Auto-Renewed My Health Insurance for 4 Years. Then I Did the Math.**
- Target publication: **Tuesday 10 November 2026**; don't publish automatically.
- Frame: 16:9 landscape, v3-approved style and frame rate, baseline 1280x720/24fps; higher 1920x1080 export only if source quality genuinely supports it and QA validates at output size.
- Target full-episode duration: **approximately 6–7 minutes** at natural narrator pace. The exact voice is more important than forcing a six-minute stopwatch.
- **Now produce only a fully edited, continuous 60-second pilot from the beginning of the episode**. Include live narration, office art, story cutaways, actual motion graphics, correct figures and disclaimers. This is not a slideshow or placeholder.
- Target viewers: US adults 25–45. Keep US-specific insurance terminology and figures, but **Ren's voice remains British**.
- Full revised approved-for-prototype script: `docs/REVISED_SCRIPT.md`; source notes: `docs/FACT_CHECK_AND_ASSUMPTIONS.md`. The script is a candidate for review, not prior production approval.
- Do not produce or pre-cut the two Shorts. The owner will request Shorts independently. Do keep useful timestamp/shot metadata for possible later extracts.

## Non-negotiable Ren v3 style lock

1. Preserve Ren's exact approved face, glasses, navy clothing, white shirt, proportions, linework and visual world. The approved v3 office, furniture and art remain visible.
2. Default composition: Ren left by desk, animated text/numbers right, adapted for 16:9. Add purposeful story cutaways and camera variations, never a static PowerPoint slide sequence.
3. Fredoka text styling where available, navy/sage/cream colours, mobile-readable captions, no giant white panel hiding desk/chair, no persistent Ren/Finance header, no yellow bottom progress bar or persistent footer.
4. Reuse the existing animations (`ren_present_palm_left`, `ren_nod_yes`, `ren_shake_no`, `ren_thinking`, subject to verified availability/gestural direction). No new animation batch without approval.
5. **Keep Ren's mouth closed** for the established narrator-led format. Do not improvise inaccurate mouth flaps or lip sync. No decorative body wobble. Verify whether a gesture points left or right before placing the graphic; never mirror it automatically.
6. Shot-duration caps: Ren <=5.5s, story still <=2.5s, numeric graphic <=3.5s. Narration must bridge scene cuts naturally; avoid reusing the same Ren pose in consecutive shots.
7. Decode Ren at native 1280x720 before matting/resizing. Never first downscale to 640x360. Inspect full-resolution face, glasses, hands, edges, white shirt and trainers.

## Approved Qwen3 voice and audio lock

- Voice: approved **British male Ren** voice clone, **NOT a US voice**.
- Model: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`.
- Space: `Qwen/Qwen3-TTS`.
- Endpoint: `/generate_voice_clone`.
- Language: English; `use_xvector_only=True`.
- Reuse approved reference, audio files, segment assets and hash-tracked outputs. Do not manufacture a new voice identity.
- For new narration, use the established resumable HF/Gradio workflow; cache completed segments and resume at the last verified segment if limits interrupt. Stop cleanly on quota errors. No paid fallback, blind retried calls, speech-speed changes, time stretch or silence-padding to mask timing problems.
- Keep `HF_TOKEN` only in environment/runtime secrets. Never write tokens to Git, filenames, logs or screenshots.
- **No added background music** under current v3 rules. Discard embedded source-animation audio and preserve clean narration. Do not add incidental effects that compete with narration unless separately approved.

## Story approach and pilot coverage

The first minute should establish a **four-second versus forty-minute** contrast, quickly introduce Ren's earlier money audit, show the missed paycheck deduction, and end as the premium-increase email creates curiosity.

Suggested pilot beats, retime to the generated narration:
- 0:00–0:07: Inbox “Open enrollment closes Friday”; four-second auto-click; approved office and Ren at desk.
- 0:07–0:20: Clock becomes “40 minutes”; reveal **$1,980 potential normal-year difference**, clearly marked illustrative.
- 0:20–0:35: Car backstory and the $85 cash balance. Use icons/silhouettes rather than new off-model Ren art.
- 0:35–0:49: Audit graphic **$750 → $445 per month**, then payroll “Medical premium” line.
- 0:49–1:00: Email “Your premium contribution will increase”; **$185 → $210 per month** tease, keeping the 2027 trend statistic for later if pacing is tight.

Pilot can end mid-topic, but not mid-word, and must be a coherent edit rather than a loop or rough montage. The 60-second pilot is for visual/style/voice approval, NOT a shortened stand-in for the full episode. After review, later create the full six-to-seven-minute video from the revised script only when explicitly approved.

## Mandatory math and medical-finance QA

Use a **single shared numeric assumptions object** in the render code. Derive displayed numbers and equations from it. Static example data:

```
PPO monthly premium = 210
PPO annual premium = 210 * 12 = 2,520
PPO in-network out-of-pocket maximum = 4,000
PPO illustrative covered in-network normal-year patient share = 150
PPO worst-year premium + OOP max = 6,520
PPO normal-year premium + patient share = 2,670

HSA-eligible HDHP monthly premium = 70
HDHP annual premium = 70 * 12 = 840
HDHP in-network out-of-pocket maximum = 6,500
HDHP hypothetical covered in-network normal-year patient share = 600
Employer HSA contribution = 750
HDHP worst-year premium + OOP max = 7,340
HDHP worst-year net economic cost after HSA contribution = 6,590
HDHP normal-year cash outflow before HSA value = 840 + 600 = 1,440
HDHP normal-year net economic cost after HSA contribution = 690
Illustrative difference in normal-year net economics = 2,670 - 690 = 1,980

Premium difference = 210 - 70 = 140/month = 1,680/year
Personal HSA contributions if redirected = 1,680
Employer HSA contribution = 750
Total HSA CONTRIBUTIONS (not end balance) = 2,430
If 600 of medical care is paid from the HSA, HSA balance (before fees/growth) = 1,830
2027 IRS HSA self-only contribution cap incl. employer = 4,500
```

- NEVER show completed formulas beside counting-up intermediate values. Draw fixed correct amounts, animate only separate supporting objects/progress.
- **Distinguish $1,440 direct cash cost from $690 net economic cost.** Employer HSA funding isn't an instant discount off the insurance bill; it's a separate asset/value that may be used for qualified costs.
- **Distinguish $2,430 contributed to the HSA from actual year-end balance.** The balance is $1,830 after a $600 HSA withdrawal, or $2,430 if those bills are paid outside the HSA and no other withdrawals/fees/growth occur.
- “Worst-year” means **covered in-network claims up to each plan's out-of-pocket limit**, not every possible cost. Premiums, uncovered services and out-of-network care are separate.
- The comparison assumes the same clinician is actually in-network, the same hypothetical $600 allowed medical services and the specified copays/cost-sharing. Do not assert all plan outcomes are universally comparable.
- Explain that **eligibility for HSA contributions requires an eligible plan and other requirements**, and federal tax advantages do not guarantee identical state tax treatment.
- Use “potential/illustrative difference” rather than asserting Ren has already received an annual $1,980 saving.

## Visual asset plan

1. Reuse the approved v3 sage office and Ren animations from GitHub as primary art.
2. Use `assets/scenes/` in the attached pack as numeric/storyboard **concept compositions** only. Recreate actual motion and typography in code with the repo's Fredoka font and design tokens.
3. Use the user's supplied `assets/character_cutouts/` only as design references if needed. They are not a substitute for the renderer's verified native 1280x720 character frames.
4. For initial pilot, construct inbox, laptop/email UI, stopwatch, car/key icon, bank balance, bill audit and medical premium paycheck line from reusable vector/text primitives. Do not burn financial numbers into uneditable generated art.
5. Full episode after approval: source-check existing Alex/Maya art; show Alex/Danny/Uncle Gary via phone messages where portraits aren't established; for Dev and Priya, use off-screen message/porch/vehicle motifs until the owner approves new character art. Any proposed new character designs must pass a distinct asset review gate before rendering.
6. Produce thumbnail concept using `assets/thumbnail_concept.png`. Do not treat it as publish-ready until reviewed.

## Research and source check

Check `docs/FACT_CHECK_AND_ASSUMPTIONS.md` and independently verify before final production or publication:
- Marsh survey projected employer benefit cost +8.2% for 2027 (NOT a projection of everyone's personal premium).
- IRS 2027 HSA self-only cap $4,500 including employer contributions.
- KFF finalized Marketplace benchmark silver premium average +13% for 2027 if the statistic remains in the final script.
- HealthCare.gov 2027 Open Enrollment dates, while explicitly distinguishing Marketplace from employer open enrollment and state differences.
- $2,670, $690, $1,980 and related comparison values are illustrative plan math, NOT Marsh/KFF/IRS data.
- Disclaimers: “Educational content only, not financial advice.” Include discreetly at opening and end.

## QA and approval gate

**Deliver only pilot and review artifacts before proceeding:**
1. `Ren_Long_01_Open_Enrollment_60s_Pilot.mp4`, actual 60 seconds as close as narration naturally permits; report exact duration.
2. Source/reference manifest for all art, code-created graphics and audio.
3. Used Qwen3 model, reference location and **nonsecret** config confirmation.
4. Render metadata: source resolutions, final fps, codec, dimensions, duration and shot list.
5. Full visual QA: inspect 100% native sharpness and gesture direction; reject blurred faces and lost white clothing.
6. Audio QA: no missing/clipped words, consistent Ren voice, no added music, no stretched audio.
7. Automated and frame-level math check: no false equations on any frame, no broken intermediary totals.
8. Run `ffmpeg` decode with errors treated as fatal; verify shot frame counts and audio continuity.
9. A concise limitations list and Git branch/commit when applicable. Keep commits off `main`.

**STOP AND REQUEST EXPLICIT APPROVAL.** Do not render the full-length video, publish, open a production merge, generate Shorts or spend further quota without the owner's approval.

## Full-video next gate (only AFTER approval)

After specific owner approval of pilot, finish the whole video with the same voice and quality criteria. Target ~6–7 minutes naturally, make any pacing adjustments transparent, add sources/description, finalize the thumbnail through a separate review, and run full-frame validation. The two Shorts remain a separate future Codex task.
