# Open Enrollment Short 01 — revision 2, Qwen Ren voice

Owner said the stock voice and scene timing felt rushed and the white background
was too basic. This replaces that prototype's presentation; the v1 files remain
preserved. **Prototype only. Stop for explicit owner approval before a final
production render or publication.** Same feature branch codex/open-enrollment-short-01.

## Voice identity and pace

The earlier draft used stock US Kokoro am_michael to follow the initial US voice
direction. This revision returns to the established **British-reference Ren
clone**, not a stock voice:

- Qwen/Qwen3-TTS-12Hz-1.7B-Base, Qwen/Qwen3-TTS Space.
- /generate_voice_clone; English; use_xvector_only=True; model_size=1.7B.
- The existing Audio/ren_reference.wav and matching transcript remain unchanged;
  exact hashes/settings/fingerprints saved before generation in manifest.json.
- One generation request, no retry or paid fallback. Original WAV saved immediately
  and hash-checked. Native original 10.856875 seconds; duration/silence/corruption
  safeguards passed. Saved completed voice is reused with no new quota/API request.
- Free ZeroGPU allowance decrease **19.157088 GPU-seconds**. Request elapsed
  **22.823741 seconds** includes queue/upload/transfer; it is not GPU usage.

The permitted script adaptation is shorter; original full script stays in the
parent folder. All three question concepts, four seconds, forty minutes, almost
two thousand dollars and Tuesday remain. Spoken "Actual use?" corresponds to
on-screen "What did I use?". No words are removed from the accepted Qwen output.

**Finished runtime is 18.00 seconds**, the authorized maximum, used for clearer
reading after the owner's feedback. Four phases hold 4s / 5.5s / 4.5s / 4s.
Speech is not accelerated, slowed or stretched. It is split only at three quiet
phrase boundaries; every normalized source sample is retained, in order.
Explicit editorial reading pauses of **1.47s, 1.39s and 1.64s** separate the four
beats while UI/character animation and music continue. They are disclosed pacing
edits requested by the owner, not blank filler or a way to disguise failed audio.
Existing generic no-padding/rapid-cut rules are superseded here by the latest
specific request for reading time; no extra blank duration is appended.

The 0.4s opening and last ~2.24s music/animated end hold are in timing.json.
All three cards settle by 4.9s and remain to 9.5s. Values persist through the
4.5s comparison; the illustrative difference continues on the end card.

## Engaging motion and backgrounds

A full-colour navy/sage environment replaces the cream canvas. Opening reuses
the same native seated office art with a slight camera drift and clear space
for the animated email, pointer click and stopwatch. The question cutaway uses
the actual native Ren thinking clip and code-drawn shield/usage/branch cards.
The comparison builds proportional bars while numbers stay correct and fixed.
The end card uses the actual native nod clip plus an assembling calendar.
No endless zooms, decorative body wobble, automatic mirroring or generic characters.

Existing source is decoded/matted at 1280×720, cropped and resized once. The
refined external matte preserves opaque white shirt/trainers and avoids a white
fringe. Ren and furniture proportions are unchanged in the seated art. Code text
never covers his face or hands. End financial badge stays clear of his feet.
Navy/sage/cream and Fredoka retain the v3 brand; no yellow footer/channel heading.

The earlier reference-based seated pose remains a draft asset for review, not
newly approved artwork. No new image-generation request was needed for revision2.
Closed-mouth narrator format remains; no approved seated lip-sync rig exists.
The actual thinking/nod gestures provide subtle expressions/motion.

## Financial and delivery constraints

Shared assumptions remain in ../assumptions.json: $2,670 − $690 = **$1,980**.
Bars are explicitly illustrative comparisons; labels remain completed during
animation. No verified quote, guaranteed saving, investment forecast or claim
that a lower premium is automatically better. Friday is a fictional email example.
Tuesday end card remains 10 November 2026, not a scheduling/publication action.

Exact disclaimer **Educational content only, not financial advice.** is visible
through the last 4 seconds, 37px cream on navy, above typical bottom UI controls.
Original procedural music is regenerated at 84 BPM, kept beneath the voice;
original mouse click/card pops align to this cut. No source animation audio or
third-party recording is used. See QA.md and validation.json for measured checks.

## Reproduce / resume

Install FFmpeg/ffprobe and requirements.txt in Python 3.12. From repository root:

```sh
python project/episodes/open-enrollment-short-01/revision-02/voice.py
python project/episodes/open-enrollment-short-01/revision-02/prepare.py
python project/episodes/open-enrollment-short-01/revision-02/render.py --stills
python project/episodes/open-enrollment-short-01/revision-02/render.py
python project/episodes/open-enrollment-short-01/revision-02/validate.py
```

On this cloud machine, voice.py uses /workspace/ren-voice-test-venv/bin/python;
prepare/render/validate use /workspace/Ren/project/.tools/venv/bin/python.
Completed voice replay path was tested: no generation/quota request. A missing
voice requires configured HF_TOKEN, ready free ZeroGPU quota, and the existing
unchanged reference. Never print tokens. Failed/uncertain/stale requests stop.
No blind retry or stock/paid fallback. Speech over the limit would block delivery.

Original Qwen WAV and checkpoint are tracked. Derived media/cache/MP4s stay out
of Git. No push, merge, main change, GitHub video upload or YouTube publication.
Temporary delivery hosting is separate; full listening/physical Android review
remains with the owner before approval. Never claim those checks from decoding.
