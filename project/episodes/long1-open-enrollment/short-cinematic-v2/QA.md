# Prototype QA — approval pending

**15.000 seconds**,1080×1920,9:16,24fps,H.264/yuv420p,AAC48kHz mono.
360 encoded frames, five distinct compositions:66+72+66+72+84frames.

Automated Shorts-standard QA passed with no errors or heuristic warnings:
full fatal decode, exact frame count/duration, continuous frame timestamps,
no black/blank frames, no persistent blue/uniform border bands, no A/V endpoint
mismatch, approved/hashed dependency preflight, unique scene/animation IDs,
actual measured text bounds/font sizes inside safe areas, exact final disclaimer.
No duplicated scene sequence; longest exact downsampled image hold8frames,
consistent with a brief intentional reading hold rather than a repeating loop.

Encoded audio peak **−2.00dBFS**, no clipping. Recovered narration PCM exactly
matches the specified source sample ranges. Encoded-AAC correlation0.999990.
Only0.166667s of a quiet inter-sentence pause (RMS−69.33dBFS) is removed to end
on the complete phrase “But here's the catch.” Word timings show catch ending
14.923s in the result; following speech is not cut into the prototype.
No speech acceleration, new voice/service, padding, music or source animation audio.
Qwen model/reference/settings are confirmed in voice-configuration.json; new
requests/quota consumption **zero**. The live Space was not contacted.

Price labels derive from the existing shared calculation source: Plan A$2,520,
Plan B$840 **per year in premiums**. The preview makes no net-saving claim.
The complete source Short and reference recording hashes are unchanged.

Visual inspection: all five layouts, all three start/mid/end stills per scene,
60 encoded motion samples at quarter-second intervals spanning the complete
prototype, and native-size Ren face/clothing/hand/edge and price-detail crops.
No clipped text, figures overlapping Ren, or visible white matte halo in inspected
samples. Full-screen office/desk environments fill the canvas. Purposeful cursor,
renewal-count, paper-placement, fixed-price underline and hand-to-chin movements.
Cut transitions follow the laptop/document action; no crossfade filler.

Ren appears6.25s(41.7%), slightly above the suggested25–40% target, in two different
source-clip actions. No invented seated-typing or clicking hand pose is claimed:
existing upper-body/desk staging and a real computer cursor convey the action.
There is no newly generated major artwork; future medical environment is missing
and needs approval before full-film use, as listed in ASSET_REQUIREMENTS.md.

Limitations: this is sampled visual inspection plus complete programmatic decode,
not a claim of real-time viewing/listening or physical Android testing. Spoken
word accuracy inherits the approved source timings/audio; no new ASR was run.
Art quality, naturalness, delivery and phone reading comfort remain for Jon's
prototype review. No approval has been recorded and no full Short was rendered.
