# Health Insurance Short — cinematic v2 prototype

Branch `codex/health-short-cinematic-v2`. **Prototype only; approval pending.**
The original Short and long-form movie remain unchanged. This directory neither
synthesises remaining narration nor renders the complete Short.

## Deliverables

- `deliverables/Ren_Health_Short_v2_15s_Prototype_Rev02.mp4`: 1080×1920,24fps,H.264/AAC.
- `ASSET_REQUIREMENTS.md`: reusable assets, staging limits, future missing artwork.
- `STORYBOARD.md`: five prototype compositions and planned continuation.
- `voice-configuration.json`: exact approved Qwen settings/reference/audio identity.
- `production.json`: hashed inputs, shot timings, captions and purpose of movement.
- `layout.json`: measured actual text bounds including every animated-frame extrema.
- `deliverables/*.qa.json/.md`: automated production-standard checks.
- `review.json` / `QA.md`: source/audio integrity and inspection scope/limitations.

## Reproduce / resume

Use the existing project Python environment (Pillow,numpy,scipy,soundfile) plus
FFmpeg/FFprobe. Restore the exact original Short, approved v3 artwork and Ren
library at their recorded paths. No model download/token is needed to reuse audio.
From repository root:

    python project/episodes/long1-open-enrollment/short-cinematic-v2/prepare.py
    python project/pipeline/shorts_standards.py preflight --manifest project/episodes/long1-open-enrollment/short-cinematic-v2/production.json
    python project/pipeline/shorts_standards.py run --manifest project/episodes/long1-open-enrollment/short-cinematic-v2/production.json --stage prototype --output project/episodes/long1-open-enrollment/short-cinematic-v2/deliverables/Ren_Health_Short_v2_15s_Prototype_Rev02.mp4 -- python project/episodes/long1-open-enrollment/short-cinematic-v2/render.py

The launcher enforces the 15-second stage. The renderer separately refuses a full
render. Source-hashed native actor caches and validated video-only scene chunks
allow interruption recovery. No blind retries or audio generation calls exist.
When code/inputs intentionally change before approval, run prepare.py to record
new hashes. After approval, prepare.py refuses to overwrite the locked inputs.

## Existing implementation reuse

Uses `../render.py`'s established native-resolution white-preserving matte and
approved v3 Fredoka. Two actual Ren source intervals are decoded at1280×720,
then cropped and resized once to540×1080 (1.5× linear, no sharpening/upscaling AI).
Ren is35% larger than Revision01 and positioned at(5,400) consistently in both
office shots. A newly generated1448×1086 laptop prop supplies the chassis,
hinge, keyboard and trackpad; code supplies crisp display text.
Source character face, glasses, clothes and body proportions are unchanged.
Office original fills the entire portrait frame; desk macro scenes are code-drawn
prop environments, without a blue surround or framed landscape video.

Revision02 copies the original15-second prototype AAC stream packet-for-packet.
The original prototype and both unchanged paper scenes are preserved.
For initial audio provenance, British Qwen narration was decoded from the existing MP4. Exact source
samples0–13.84s plus14.006667–15.166667s make15s. Only0.166667s of measured quiet
inter-sentence pause is removed; no words, speech-speed changes or silence padding.
No new Qwen request or GPU quota consumption. Reference audio is not modified.

After delivery STOP for explicit Jon approval. Future major medical artwork
also requires approval before use. Media/caches remain excluded from Git.

The generated laptop original is retained in assets/laptop-generated.png. It was
explicitly requested by Jon for this revised prototype; final design approval is
pending, as for the entire preview. No new character design was generated.
