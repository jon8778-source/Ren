# Ren rig test clip: report (second version, gate 4)

`ren-rig-test.mp4`: 1080x1920, 30 fps, 15.47 s, H.264 with AAC audio. Same script and line timings as the first
version. Ren's usual voice (Kokoro am_michael + am_eric 50/50, speed 0.93). Burned-in captions at the top.
Rebuild: `rig/setup_rhubarb.sh` (once), `.tools/venv/bin/python rig/test_voice.py`, then
`cd remotion && npx remotion render src/index.ts ren-rig-test ../rig/test-clip/ren-rig-test.mp4`.
Checks: `cd remotion && npx tsx src/rig/checkClip.ts`.

I can't listen to audio: please check the voice, pronunciation and lip-sync timing by ear.

## Timing as built
Every pose change eases over 9 or 10 frames (the limit was 6-10); poses come from the gate 3 library.

| Time | Action | Line (voice start-end) |
|---|---|---|
| 0.00-1.40 s | Walks in from the left: six steps with planted feet, each foot lifts and swings with the knee bending, body bob, arm swing; settles at centre | |
| 1.43-2.95 s | Eases into the wave (9 frames), forearm rocks from the elbow, happy eyes | "Hi, I'm Ren!" (1.75-2.93) |
| 2.95-6.00 s | Eases into holding the $60 boot at waist height (10 frames); the boot appears as the hand arrives | "These boots cost sixty dollars." (3.35-5.27) |
| 6.00-8.10 s | Left arm comes up with the $300 boot (10 frames) | "These ones cost three hundred." (6.35-8.08) |
| 8.10-8.80 s | Wince: eyes shut, wince mouth, head turns away, brows drop; boots still held | |
| 8.80-9.20 s | Squats (knees out), arms lower the boots either side of him and let go at the bottom; the boots drop straight down onto the floor (4 frames) | |
| 9.24-11.30 s | Stands up while turning both hands into points at the boots on the floor (10 frames), brows raised | "So which pair is actually cheaper?" (9.35-11.32) |
| 11.30-15.47 s | Thumbs-up at chest height (10 frames), happy eyes, smile; smile held 0.66 s after the voice ends | "The answer might surprise you. Follow to find out!" (11.85-14.81) |

## What looked stiff or broken
- **Walk:** now 1.4 s with planted feet: the standing foot stays put while the other lifts and swings, so no
  more skating. Feet never cross (a minimum gap is enforced). It is still a front-facing side-step, because
  the legs are front-facing art; the lifted knee swings out sideways rather than forward.
- **Hand swaps:** each hand swaps halfway through its move, and a hand closing on a boot swaps at 75%, as
  it arrives. For about 3 frames at 3.1 s the empty hold hand is visible at shoulder height before the boot
  appears in it.
- **Set-down:** reads as setting the boots down. Ren can't bend forward (front view), so he squats with his
  knees out and the boots drop the last ~50 px straight down. The squat is a wide "plie"; a real crouch
  would need side-view legs.
- **Wince:** now happens while holding both boots (no free hands), so it is face and head only.
- **Arms:** every arm keeps an elbow bend; no straight T-poses.

## Gaps at the joints
- None at the elbows, wrists or knees in the frames I checked (walk, wave, holds, squat, point, thumbs-up). The
  sleeve and pants discs cover every bend, including the deep squat.
- Wrists: every hand sits on the cuff at any arm angle (gate 2).
- Unchanged from the first test: a raised arm shows its rounded shoulder cap over the shirt (a seam, not a
  gap), and the dark hip piece bulges below the shirt hem. Most visible in the squat.

## Props
- The boots never pass over Ren's body: on every frame, each boot's outline box stays clear of the torso,
  head, upper arm, thigh, shin and shoe boxes (closest 41 px, at 9.23 s, the $300 boot and his left shin).
- Held boots sit between the palm and the fingers. Boots on his right are mirrored so both toes point away
  from him. They stand either side of his feet, 70 rig units clear of the shoes.

## Lip sync
- Rhubarb Lip Sync 1.13 (phoneme-based, given each line's text), mapped to Ren's mouths: A (m, b, p) closed;
  B, C, G, H open (slightly open); D wide; E, F o; silence = the resting mouth (smile, closed or wince by beat).
- Every mouth is held at least 3 frames (40 holds, shortest 3). Short shapes borrow frames from a longer
  neighbour first, so most m/b/p closures survive; a few merge.
- Wide mouth only on Rhubarb's D (big open vowels): 14 frames in the whole clip.
- While speaking: open 170 frames, o 75, closed 21, wide 14, pauses 29. About 3.8 mouth changes a second.
- Ends on the smile mouth, held from the end of the voice (14.81 s) to the end of the clip (15.47 s).

## Before using this rig in a 6-minute video
1. **Side-view legs** for real walks and crouches; the front-facing side-step and plie are the limit of the
   current art.
2. **Hip and shoulder pieces** that don't bulge or show seams (still open).
3. **A forward-pointing hand** if he needs to point at the viewer.
4. **Brows** clear of the fringe, so raised brows read.
5. **Rhubarb in the pipeline:** it needs the line text; for episodes, run it per script line.
6. **Pose library:** 10 poses now (8 + set-down + point at both); episodes will want more (shrug, present,
   count on fingers...).
7. **The standing rules:** the clip keeps a walk bob and subtle idle breathing. Decide whether the animated
   rig may breathe in episodes.
8. **Render time:** a few minutes for 15 s (as before), so roughly an hour for 6 minutes, in the background.
