# Revision 6 — asset requirements and targeted storyboard

Jon explicitly approved the two generated artwork assets by replying “Approve”.
The exact PNG hashes and approval scope are recorded in artwork-approval.json.
This approves artwork for the 15-second prototype, not the MP4/full Short.

## Reused inputs

- Approved v3 office original, right upper-wall crop for the close camera; no floor behind Ren’s face.
- Existing generated laptop, wood environment, Fredoka typography and document
  drawing components from the existing v3 Short adapter.
- Exact Revision 5 AAC audio, script and narration cues. Qwen British male,
  Qwen/Qwen3-TTS-12Hz-1.7B-Base, English, use_xvector_only=True, existing reference.
- Shared premium assumptions/calculation module: Plan A $2,520/year, Plan B
  $840/year. Both illustrative annual premiums, not guaranteed total savings.

## Newly approved inputs

1. Chest-up concerned Ren: native 941×1672 transparent PNG. Resize once to 900px
   wide, no sharpening/AI upscaling. Closed lips, hands outside frame. Target
   face width about 35% of final portrait canvas; verify actual encoded frame.
2. Right-hand trackpad insert: native 1568×1003 transparent PNG. Back of right
   hand visible, wrist/cuff lower-right, index toward screen. Scale once to
   620px wide; no mirror/rotation. Short depression represents one click.

No missing artwork, new characters, voices or dependencies are proposed.
Approval provenance and all actual dependency hashes are in production.json.
Original artwork and all earlier renderers/production manifests stay unchanged.

## Shot plan (24 fps)

| Time | Composition and action |
| --- | --- |
| 0–2 | Button already fills laptop close-up. Palm-down hand clicks at 0.625s. Brief pull-back exposes trackpad; confirmation changes on screen. |
| 2–5 | Physical annual calendar: four successive confirmed years, ending on Year 4. |
| 5–9 | Genuine chest-up Ren, concerned reaction with clear eyes. Locked 4s hold for interpretation; no fake lip/body motion or foreground papers. |
| 9–11.5 | Plan A paper settles into desk geography. Correct $2,520/year fixed, underline directs attention. Plan B figure still concealed. |
| 11.5–15 | Fold opens to $840/year in sage. Hold both figures; “Premiums only” and care-cost inspection signal the catch. |

This intentionally retains a single approved reaction expression as authorized;
it does not pretend to be a newly generated acting animation. Mouth remains closed.
Exact disclaimer appears briefly at opening and for final two seconds, no banner.
All interface/financial text is code-drawn and measured at final resolution.

## Reproduction and gate

From repository root, with the existing project Python environment:

```bash
python project/episodes/long1-open-enrollment/short-cinematic-v2/prepare_revision6.py
python project/pipeline/shorts_standards.py run \
  --manifest project/episodes/long1-open-enrollment/short-cinematic-v2/revision-06/production.json \
  --stage prototype \
  --output project/episodes/long1-open-enrollment/short-cinematic-v2/deliverables/Ren_Health_Short_v2_15s_Prototype_rev06.mp4 \
  -- python project/episodes/long1-open-enrollment/short-cinematic-v2/render_revision6.py
```

Only 360 frames are implemented. STOP after delivering Revision 6 and await
explicit prototype approval. No full Short, long-form changes or voice requests.
Video, screenshots and caches stay outside Git.
