# Pilot revision 2: summary, QA report and before/after

**File (local only, not in git):** `/output/free_money_S1_S2_pilot_rev02.mp4`. The original `/output/free_money_S1_S2_pilot.mp4` is kept.
**Status: STOP. Waiting for your written approval.** Scenes 3 onwards are not rendered, and no further assets were created. This is a revision of the Gate 2 pilot, so Gate 2 is still open: "pilot approved" has not been given.

## 0. Conflicts in the brief, and what I did
1. **Shot caps against "fewer arbitrary cuts".** The v3 rules cap a Ren shot at 5.5 s, a story still at 2.5 s and a graphic at 3.5 s. I kept every cap and put the action inside the shots (camera moves, pose changes, moving objects). The pilot's 30 shots became 22.
2. **1080p.** The library clips are native 1280×720 and the v3 rules forbid enlarging them, so rev02 stays at 1280×720.
3. **"Ren on the left at his desk" as the approved composition.** I could not find it written in `AGENTS.md` or the v3 rules. I used it as your instruction (Ren left, graphics right). The one exception is the "Let me take you back" shot, where he presents palm-left to the left, because the v3 rule against pointing away from content wins.
4. **No seated pose exists.** I placed the approved bust behind the plate's own desk and laptop, redrawn over his lower body.
5. **Narration for the remaining scenes.** A background job was generating S3-S7 narration. Your "no additional assets" rule applies, so I stopped it. Three unused chunks from before the stop (S3_03, S4_01, S4_02) are not in the video.

## 1. Revision summary
**What changed:** the same narration (the audio track is bit-identical to the pilot, MD5 `f927e4f3…`), the same figures and the same story. All visuals were rebuilt as actions and scenes, from the same approved art.
**By scene (S1 + S2):**
- **Porch:** Ren and Dev now share one two-shot, Ren left and Dev right, with a continuous push toward Dev and the pay stub. The stub shot tilts down onto the stub, the glowing "Employer match: 2%" line pulses, then darkens and sinks on "my stomach dropped".
- **Ren narrating:** the presenter composition has Ren on the left and graphics on the right. Ren changes pose on narration beats (R1 to R3 on "I didn't know what he meant", R3 to R2 on "I did it to impress people", R3 to R2 on the discovery of the 4% match).
- **Office, age 25:** Ren sits behind the real desk and laptop, with the desk redrawn over him. The laptop lights up on "forty-four thousand" and the age/salary card appears on the right wall.
- **Car lease:** Ren raises the phone (library clip `ren_hold_phone`, the real raise action). The lease screen lights up inside the phone. The cut to the phone screen is a match cut showing "$489 per month" large, and it returns at the end with a "Payment due" banner.
- **Employer match:** the page-6 folder arrives on the desk, the camera pushes into the page, and "We match 100%" is drawn on the page's own yellow row. A 401(k) screen shows coin stacks accumulating, You and Company, with the "=" equal on every frame. The final card builds up the three lines in sync.
- **Parking lot:** a slow push on Ren and the car, so the $489 trade-off is also shown against what he wanted to be seen driving.
**Animation technique:** real library action (phone raise), pose changes at narration beats, foreground-object movement (folder, banner, coins) and motivated camera pushes. No articulated rig exists, so there are no limb or face animations. No distorted limbs, floating hands or changed proportions.
**Transitions:** every cut now does a job. Porch two-shot to Dev close-up is a continuous push (Dev's question). The stub close-up gives information (the 2% line), and the cut back to Ren is the reaction. The page peel marks the move into the flashback (time change) and is the only effect used. Phone-in-hand to phone screen is a match cut. The lot is a change of location, the desk to the folder close-up is a match, and the 2% chip against the faded 4% explains the choice. There are no fades, bouncing text or zoom presets.

## 2. QA report
| Area | What I checked | Result |
|---|---|---|
| Character consistency | all 44 first and middle frames of the full render, plus 100% crops of the bust, desk and full-body faces, the porch, and the phone hand | Ren matches the design lock in every frame (hair, cowlick, round glasses, navy shirt over white tee). Dev and the other art unchanged. Hands and face edges clean. |
| Animation quality | per-shot motion measurement and the frames | no shot is static any more: 0 static frames (the pilot had 17%). The three screen graphics were near-static, so I added slow pushes. Pose swaps are hard cuts, not tweens, which is deliberate for flat art. |
| Narration sync | cut times are the first word of each phrase from the Whisper word timings; the stub, laptop, folder and chip events are tied to word times | in sync by construction. I could not hear it, so the ear check is yours. |
| Financial accuracy | every figure against the script | $44,000, $489/month, "match 100% up to 4%", 2%, 4% all match the narration. The coin stacks are drawn from the same count on every frame. The "Payment due" banner is a dramatisation, not a new claim. No new financial claims. |
| Visual readability | text size at 1280×720, overlaps, safe area | all card text is 40 px or larger. My layout check found no text over faces or Ren, and nothing off-frame. I moved cards and chips off the bookshelf. |
| Audio | decode, loudness, gaps | -16.2 LUFS, true peak -1.6 dBTP, no clipped narration, no gap except the 0.63 s sentence-end pause. Bit-identical to the pilot. |
| Rendering defects | full decode with errors fatal, frame counts | clean. 1,238 frames, 24 fps, 51.58 s. No black frames in the frames I checked. |
**Defects found and fixed during the review:** cards and chips overlapping the bookshelf; "/month" running off the phone; the three-line card text too small after shrinking to fit; the "We match 100%" strip not on the yellow row; the disclaimer tag sitting on Ren's foot; and a "=" briefly shown between unequal coin stacks.

## 3. Before and after
| | Pilot | Revision 2 |
|---|---|---|
| Shots | 30 | 22 |
| Average shot / longest | 1.7 s / 3.0 s | 2.3 s / 4.3 s |
| Static frames (nothing moving) | 17% | 0% |
| Hard cuts | 48 | 32 |
| Characters doing something | stills with a push | seated at the desk, holding a phone, reacting by pose, folder arriving |
| Money on screen | cards on a blurred background | $489 on a phone, 401(k) screen, strip on the folder page, coin stacks |
| Composition | Ren right, cards left | Ren left, graphics right |
| Transitions | mostly cuts and a squeeze/peel | cuts with a job; page peel only for the time change |
| Narration | | identical audio |
The measured motion energy is lower (2.73 to 2.31). That is because the pilot's number came from the cut jumps. Rev02's motion comes from camera and action.

## 4. Remaining limitations
- **No articulated animation.** The mouth stays closed, with no talking motion. The seated shot shows only head and shoulders, because the laptop hides the rest.
- **Single poses for Dev, Priya and Gary,** so Dev is moved by camera only. The folder slides flat onto the desk with no hand. The phone close-up has no hand either.
- **The folder on the desk is small.** The full-size folder is the next shot.
- **Present-day Ren and the flashback share the office plate,** separated only by the "Age 25" tag and the peel.
- **Resolution** stays at 1280×720. The plates are 1672 px wide, so camera pushes stay under 1.3× to avoid softening.
- **Voice items still open:** please listen to "lease" (heard as "least") and the accent.
- **Validation** is my own validator; the repo has no reference MP4 to compare against.
