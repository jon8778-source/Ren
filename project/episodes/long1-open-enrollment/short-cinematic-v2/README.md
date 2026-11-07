# Health insurance Short — Revision5 prototype

Latest adapter: render_revision5.py. **Only15seconds; full Short NOT approved.**
Jon explicitly rejected Revision03 for full production and requested a targeted
iteration. Earlier videos/artwork remain unchanged. No new narration or images.

## Latest deliverables

- `deliverables/Ren_Health_Short_v2_15s_Prototype_Rev05.mp4`
- `deliverables/Revision5_Narration.srt`: full narration captions, separate from
  the large story labels in the video; small caption boxes are no longer burnt in.
- `REVISION5_NOTES.md`: requested removals; original story/voice retained.
- `production.json` / `layout.json`: hashed inputs and measured final text bounds.
- `revision5-config.json`: framing and source settings.
- `technical-qa.json`, `review.json`, `QA.md`: technical results/inspection limits.

## Resume/reproduce

Use the existing project Python environment (Pillow,numpy,scipy,soundfile) and
FFmpeg/FFprobe. Restore the referenced source Short, original15s prototype for
AAC reuse, approved office/laptop artwork, fonts, animation library and reference
files at their recorded paths. No token/model download is needed for audio reuse.
From repository root:

    python project/episodes/long1-open-enrollment/short-cinematic-v2/prepare_revision5.py
    python project/pipeline/shorts_standards.py preflight --manifest project/episodes/long1-open-enrollment/short-cinematic-v2/production.json
    python project/pipeline/shorts_standards.py run --manifest project/episodes/long1-open-enrollment/short-cinematic-v2/production.json --stage prototype --output project/episodes/long1-open-enrollment/short-cinematic-v2/deliverables/Ren_Health_Short_v2_15s_Prototype_Rev05.mp4 -- python project/episodes/long1-open-enrollment/short-cinematic-v2/render_revision5.py

Scene chunks/native actor mattes are cached under build/revision4 with dependency
hashes. Both launcher and adapter enforce the360-frame prototype stage. The
existing v3 matte/compositor/font/asset methods and SceneCache are reused. This is
an episode shot adapter, not a replacement long-form production system.

## Character and narration integrity

No pointing hand is composited in Revision5. The foreground paper shapes are
also removed from Ren’s reaction. Close reaction uses ren_confused2–5s,
which changes the expression while keeping the mouth closed. Decode1280×720,
matte natively and resize once. The raised-arm negative-space pocket gets extra
background flood seeds, while the separate white shirt remains opaque. The
actual720p source limits fine detail in the close-up; no sharpening/AI upscale.

Audio is copied packet-for-packet from the original15s prototype. Its established
British Qwen1.7B Base,English,xvector-only configuration and matching reference
hashes are recorded in voice-configuration.json. No new synthesis/speed/pause
edits. Generation provenance is verified; ear-based identity/delivery assessment
must remain explicit and separate from metadata/bitstream checks.

## Historical versions

The prior render.py/prepare.py adapter and revision-01/02/03 records are retained.
Those entrypoints reproduce their historical designs; use the Revision4 commands
above for current work. Prior MP4s, source Short and long film are never overwritten.
No video/cache files go into Git. No merge or YouTube publication. STOP after
prototype delivery and await explicit approval; future major artwork needs its
own approval before full-production use.

Revision5 rerenders only0–3.5s and5.5–8.5s; the calendar, price reveal and
AAC narration are reused unchanged. Revision4 source/art/video remain preserved.
