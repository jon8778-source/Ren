# Ren Short 01 — Open Enrollment (prototype only)

Title: **I Clicked "Keep My Plan" in 4 Seconds**.
Intended publication: Monday, 9 November 2026. Full-story teaser: Tuesday,
10 November 2026. Neither video is published or scheduled by this task.

Dedicated local branch: `codex/open-enrollment-short-01`, based on approved
v3 commit `c6bb363baf13666cce15ece777fde39190ffe8a7`.

**STOP AT PROTOTYPE APPROVAL.** The complete draft is 15.00 seconds, 1080×1920,
24 fps, H.264/AAC. No final production render is generated. Explicit owner
approval of this MP4 is required before final production or publication.

## Scripts and voice

`script-original.txt` preserves the full supplied source. `script-adapted.txt`
is the concise production adaptation permitted by the request. It retains the
four-second choice, all three questions, forty minutes, almost two thousand
dollars, and Tuesday teaser. English numerals are spoken as words. Native local
US narration is 11.626667 seconds, begins at 0.25s and ends at 11.876667s. The
original lo-fi bed and animated end-card reading hold complete the 15s draft.
No speech-rate or time-stretch correction is used: Kokoro speed=1.0.

Selected voice: **Kokoro-82M q8, `am_michael`, `en-us`**, local CPU. This is an
intentional US male voice change from the channel's earlier British Qwen clone,
explicitly requested for this Short. Historical v3 British/no-music instructions
are superseded by this task's specific US voice and music direction. No paid
service, HF generation request or quota consumption. The saved original WAV,
text/settings/model/vector hashes and result are preserved in `audio/`.
The full original script measured 17.130667 seconds at the same native rate;
the permitted concise adaptation keeps the prototype at the 15-second target.
See audio/script-duration-check.json.

The existing local Kokoro weights/vector are Apache-licensed according to their
packaged model README; cached model/package dependencies stay out of Git.

The local rough independent ASR screen recognizes the overall message but differs
on several question words. It is not a pronunciation/word certificate; listen to
the prototype. Forced alignment against the script times the UI focus and ending.
No listening/full audiovisual playback is claimed by programmatic checks.

## Assets and appearance

See `audit.json`, `asset-manifest.json`, `asset-brief.txt` and `assets/ui/`.
Reused: actual approved v3 office, palette, Fredoka, source renderer/matte
functions, native 1280×720 nod animation. Four actual gesture frames and source
duration were inspected. No half-resolution actor decoding, sharpening,
mirroring, generic stock characters or source animation audio.

Missing seated pose: one reference-based seated office illustration was made
from the exact approved Ren source frame and office. It is new draft artwork
for approval, not an already approved library asset. His navy overshirt/white
shirt are retained from the source of truth instead of redesigning a sweater.
Opening art is a native-resolution portrait crop, with information in a separate
clear area to the right. No text covers his face, hands, chair or desktop.

The seated opening is a still reference-based pose; existing standing nod
animation supplies subtle movement on the end card. There is no approved seated
lip-sync rig. Ren stays closed-mouth, with no random talking animation. Further
character animation/lip sync is an identified limitation rather than claimed work.
Code-drawn click, stopwatch hand, staggered cards and changing question focus
carry purposeful movement. Cards persist long enough for reading.

Eight reusable SVG assets cover email/button, stopwatch, all three cards,
comparison, Tuesday card and disclaimer. `assets.py` and `render.py` produce
all numbers/text from shared assumptions, never from generated image text.
`2670 - 690 = 1980` is always completed correctly; no incorrect count-up.
The costs are labelled illustrative, not plan quotations or guaranteed savings.
A lower cost is not stated to guarantee a better-fit plan. Friday is a fictional
email example, not a universal enrollment deadline.

Music/effects: original deterministic sample-free 90 BPM lo-fi plucks/percussion,
mouse click and three restrained card pops. Source and provenance in `sound.py`
and `audio/music-rights.json`; no external recordings/melody/licensed track.

## Reproduce and resume

Install FFmpeg/ffprobe (libx264/AAC), Python 3.12, and pinned requirements.
Restore approved v3 artwork with its existing unpacker; exact reference assets
remain preserved. From repository root:

```sh
python project/prototypes/coffee-minute-v3/unpack_artwork.py
python -m pip install -r project/episodes/open-enrollment-short-01/requirements.txt
python project/episodes/open-enrollment-short-01/voice.py
python project/episodes/open-enrollment-short-01/sound.py
python project/episodes/open-enrollment-short-01/assets.py
python project/episodes/open-enrollment-short-01/render.py --stills
python project/episodes/open-enrollment-short-01/render.py
python project/episodes/open-enrollment-short-01/validate.py
```

`voice.py` reuses the complete saved original before accessing any model. If
starting without the original, provide configured `REN_KOKORO_MODEL` (q8 ONNX)
and `REN_KOKORO_VOICE` (am_michael.bin) paths, or the repository's existing
`project/.tools/` layout. No credentials are required for local synthesis.
Stale narration/hash mismatch blocks overwrite. Never regenerate the seated
art or a completed original WAV simply because work is interrupted.

On this cloud machine the working interpreter is
`/workspace/Ren/project/.tools/venv/bin/python`.

## Review and approval

`QA.md` and `validation.json` state performed checks and limitations. Full fatal
decoding, 360-frame black/blank screening, expected scene coverage, encoded audio
correlation, loudness/headroom, fixed arithmetic/disclaimer regions pass.
30 encoded samples plus native layout evidence were inspected. This is not a
physical Android playback test or a listening pass. Those remain review steps.

Final-card exact text: **Educational content only, not financial advice.**
It stays visible from 10.3s to 15.0s, 38px high-contrast type, clear of bottom UI.

Only local source checkpoint(s) are committed. No merge, source push, GitHub MP4
upload or automatic YouTube publication. MP4s, generated audio stems, caches and
credentials stay out of Git. The original narration WAV is retained for recovery.
Temporary delivery hosting is separate from GitHub and may expire.
