# Revision02 prototype QA — approval pending

15.000s,1080×1920,9:16,24fps,H.264/yuv420p,AAC48kHz mono,360frames.

Requested corrections:
- Ren400×800→540×1080: **35% larger**, position(5,400) consistently in both
  office shots. This corrects his scale relative to the desk. Original character
  proportions/appearance preserved; native1280×720 decode/matte then one resize.
- One generated1448×1086 laptop prop now supplies a detailed chassis, keyboard,
  hinge and trackpad. Code draws the readable interface on the screen. No new Ren.
- Original prototype preserved; revised export has `_Rev02` filename.

Technical production QA passes with no errors/warnings:360frames, five distinct
compositions, full fatal decode, continuous timestamps, no black/blank frames or
persistent borders, safe measured text bounds, correct disclaimer and matched
15s audio/video endpoints. Prices remain illustrative **annual premiums**:
Plan A$2,520,Plan B$840, derived from shared assumptions. No new savings claim.

**All AAC narration packets and decoded PCM are identical to Revision01.**
No new voice requests, pause edits, speech-speed changes, audio re-encoding,
music or source animation audio. Qwen voice/reference/settings unchanged.
Prior0.166667s quiet-pause edit belongs to Revision01, not this visual correction.

Only the15-second prototype video was encoded. The conservative old-chunk packet
reuse check did not prove equality, so it safely fell back to encoding five
video chunks. The two unchanged paper scenes' decoded pixels nevertheless match
Revision01 exactly. Source Short, original prototype and voice reference unchanged.

Inspection performed:60 encoded motion samples at quarter-second intervals,
all five layouts/joins and native-size Ren face/glasses/hair/white clothing/edge
and laptop crops. No sampled text/face collisions, damaged shirt or visible
white matte halo. Character enlargement exposes the detail in the existing720p
animation source; no sharpening or AI character upscale conceals source limits.

Limits: no new real-time listening or physical Android test. Delivery and
subjective artwork/motion quality remain for Jon's review. No full Short rendered.
Future medical-environment artwork still needs approval before full-film use.
