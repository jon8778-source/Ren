# Pilot QA — 6 November 2026

Scope: continuous opening 61.041667-second review pilot, ending at the fictional
premium change from $185 to $210/month. Uses supplied revised candidate, not
uncorrected full original. Stop for explicit approval before full production.

## Checks performed

- 1280×720 landscape 16:9, 24fps, 1,465 frames, H.264/yuv420p plus AAC 48k mono.
- All 18 encoded shot frame counts and continuous coverage pass; Ren <=5.5s,
  animated graphics <=3.5s. Longer readable content persists across connected cuts.
- Complete fatal-error video decode passes; all 1,465 frames screened for black/blank.
- Reviewed all 18 encoded shot midpoints, 85 frames around all 17 transitions,
  and two 100% output frames for Ren's face, glasses, clothing and edges.
- Native 1280×720 actor decode/matte, single 0.9 composition resize. Steady left
  framing; no zoom switches/mirroring. White shirt/trainers intact in samples.
  Text is on the right in fitted translucent boxes, with no furniture overlap.
- All financial assumptions/calculations pass. Completed monetary labels are fixed
  on 453 encoded frames; arrows are drawn in code to avoid missing font glyphs.
- Three original WAVs verified against saved hashes/settings; one request per
  segment, zero retries. All processed samples retained in exact sequence.
- Narration is 61.0275s, no speed changes/time stretch/gaps/padding. Final frame
  quantisation extends video by 0.014167s. -18.1 LUFS, -1.93dBTP.
- Encoded AAC/master correlation 0.999977. All animation audio discarded; no music.
- Local forced alignment covers 182 words and maps the continuous script prefix.
  Forced alignment is not independent transcription or a spoken-word certificate.
- Exact educational disclaimer visible at opening and end.

## Voice / allowance

Actual approved British-reference Ren Qwen clone: Qwen/Qwen3-TTS-12Hz-1.7B-Base,
Space Qwen/Qwen3-TTS, /generate_voice_clone, English, use_xvector_only=True.
Unchanged approved reference/transcript hashes and settings are in manifest.json.
Three calls, zero retries, free ZeroGPU only. Measured allowance decrease:
78.148915 GPU-seconds. Request elapsed time: 87.546165 seconds. These are different
measurements. No paid/overquota use. Last snapshot 6 Nov 12:14:26 UTC: remaining
2302.693997 GPU-seconds; reported reset 7 Nov 11:23:05.372 UTC. Historical snapshot,
not a live quota guarantee. Raw original durations: 19.496875, 32.033750, 9.496875s.

## Limits / blockers

No listening, full audiovisual watch-through or physical Android playback was
available. Owner must review pronunciation, voice identity/delivery and pacing.
Closed-mouth narrator-led animation is retained; no new lip-sync rig substituted.
Primary sources for later 2027 claims were not independently accessible under the
cloud network policy. Those claims are absent from this pilot and must be checked
before remaining narration. Supporting character scenes require approved artwork
or offscreen prop staging; no new supporting portraits were created here.
The full film is deliberately ungenerated pending explicit pilot approval.
No merge, push, main/approved-art changes, GitHub MP4 upload or YouTube publication.
