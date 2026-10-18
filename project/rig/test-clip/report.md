# Ren rig test clip: report

`ren-rig-test.mp4`: 1080x1920, 30 fps, 15.47 s, H.264 with AAC audio. Ren's usual voice (Kokoro am_michael +
am_eric 50/50, speed 0.93). Soft background #F3F5F8, a floor shadow, burned-in captions at the top.
Rebuild: `.tools/venv/bin/python rig/test_voice.py`, then
`cd remotion && npx remotion render src/index.ts ren-rig-test ../rig/test-clip/ren-rig-test.mp4`.

I can't listen to audio: please check the voice, pronunciation and lip-sync timing by ear.

## Timing as built
| Time | Action | Line (voice start-end) |
|---|---|---|
| 0:00-0:03 | Walks in from the left (front-facing march, arm swing, knee lift, body bob), stops centre, waves with the open hand | "Hi, I'm Ren!" (1.75-2.93) |
| 0:03-0:06 | Right arm out with the holding hand and the gold $60 boot | "These boots cost sixty dollars." (3.35-5.27) |
| 0:06-0:09 | Left arm out with the navy $300 boot, then a quick wince (eyes shut, wince mouth, head tilt) | "These ones cost three hundred." (6.35-8.08) |
| 0:09-0:12 | Lowers both boots; they drop to the floor beside his feet; points with brows raised | "So which pair is actually cheaper?" (9.35-11.32) |
| 0:12-0:15 | Thumbs up, smile, happy eyes, blink | "The answer might surprise you. Follow to find out!" (11.85-14.81) |

The last line is 3 s long, so the clip runs 0.47 s over 15 s.

## What looked stiff or broken
- **Walk cycle:** the first version swung the legs side to side and they crossed over each other. That's
  unavoidable with front-facing legs. I replaced it with a front-facing march: each foot lifts in turn
  while the body glides sideways. It reads as walking but stays stiff, with a small "skating" feel because
  the feet don't plant against the floor. A real walk needs side-view (or three-quarter) legs, feet and torso.
- **Hand swaps:** clean, with no pop in position, because every hand pivots at its wrist. Two weak spots:
  the holding hand appears while the arm is still coming down from the wave (about 0.3 s of a claw
  shape at head height), and the thumbs-up fist sits a little to the side of the cuff instead of on it.
- **Boot drop:** the boots slide outward as they fall instead of dropping straight down. It's quick and
  reads as "set down", but it isn't physical.
- **Brow raise:** visible but subtle. The fringe covers the brow area, so a bigger raise disappears into
  the hair.
- **Arms out:** holding a boot, the arm is close to a straight T-pose. A little more elbow bend would look
  more natural.

## Gaps at the joints
- None at the elbows, wrists or knees in any frame I checked (walk, wave, both holds, point, thumbs up).
  The sleeve- and pants-coloured discs behind the elbows and knees cover every bend.
- At the shoulders, a raised arm shows its rounded cap over the shirt: no gap, but a visible seam.
- The knees keep the slight "mannequin" bump from the sheet, and the dark hip piece still bulges below
  the shirt hem.

## Lip sync
- Driven by the voice's loudness, frame by frame: closed when silent, then slightly open, "O" and wide as it
  gets louder. A shape is held for at least 2 frames so it doesn't flicker.
- During speech the mouth is open 81% of the frames, and closed on every silent frame. It changes shape
  about 5.6 times a second. There's no offset: the mouth track is computed from the same audio file that
  plays.
- Limits: it follows volume, not sounds, so "O" lands on loud vowels whether or not they're O sounds, and
  closed-lip sounds (m, b, p) don't always close. It will look like talking, not like exact speech.
- The wide mouth was too big at first (it read as shouting). It's now 30% smaller, and "O" 10% smaller.

## Before using this rig in a 6-minute video
1. **Side-view parts** for any walking (legs, feet, torso, head turn), or keep Ren standing and drop the walks.
2. **Hip and shoulder pieces** redrawn to match the thigh and arm widths, so the bulge and seams go away.
3. **Phoneme lip sync** (text-to-phoneme timing from the script) instead of volume, plus closed-lip mouths
   for m/b/p.
4. **A forward-pointing hand** if he needs to point at the viewer; the sheet only has sideways pointing.
5. **Brows** that sit clear of the fringe (or a fringe with a gap), so raised brows read.
6. **Pose library:** about 10 named poses (hold, present, point, shrug, thumbs up...) with eased transitions,
   so each episode scene picks poses rather than hand-keying angles. Hand swaps mid-way through the move.
7. **The standing rules:** CLAUDE.md and DECISIONS.md ban talking bob and sway, and this clip uses a walk bob
   and idle breathing at your request. Decide whether the rig is allowed to breathe in episodes before we
   use it there.
8. **Render time:** about 3 minutes for 15 s here, so about 70 minutes for 6 minutes. That's fine in the background.
