# Health-plan portrait Short

58.875-second 1080×1920, 24fps H.264/AAC derivative of the revised full MP4.
Six complete narration excerpts keep the original British Qwen Ren voice and
speaking speed. No new voice requests, music, footage audio, silence padding,
new character art, YouTube publication or GitHub media upload.

## Reproduce

Run from this directory using the existing project Python environment with
Pillow, numpy and soundfile; FFmpeg/FFprobe must be on PATH:

    mkdir -p build deliverables
    python render.py
    python validate.py

`edit-manifest.json` records the source SHA, exact frame/sample selections,
word timings and resulting timeline. Update its absolute source path after
moving the project; the source SHA must still match. Source MP4 and temporary
build/media files are deliberately excluded from Git. `script.md` lists the
spoken excerpts. `captions.json` and exported SRT retain source word timing.

## Layout and reuse

Actual Ren/office frames are decoded from the full MP4 at native resolution.
The leftmost 610×680 crop is pasted without enlargement at (35,475); no new
matte, character recreation or sharpening. Presenter stays left, fitted white
black-bordered graphics stay right. Other shots use mobile-sized v3 cards.
Fredoka and existing full-film medical props are reused. Navy/sage/cream design.
Prices derive from the parent shared calculation source: $2,520/year and
$840/year are premiums, not guaranteed total costs or savings. The narrative
explicitly explains circumstances where the PPO could be better.

The six encoded excerpts are audio/edit groups, not six scene-length limits.
Source presenter cuts remain inside these groups; graphic layouts stay stable
while emphasis changes rather than rapidly replacing text. No artificial
shot-count claim is made for the longer readable graphic holds in this Short.

## Limitations

Programmatic audio continuity/PCM checks and visual frame inspection do not
constitute listening, human word verification, or physical Android playback.
Native character detail cannot exceed that in the finished 720p source.
