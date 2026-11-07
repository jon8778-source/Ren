Owner review of the 15-second prototype (7 November 2026), re-bound to the extended renderer.

The owner was sent the prototype MP4 (SHA-256 7498467423aa351c...), its contact sheet, the asset report, the launcher QA and a report listing what I
had and had not checked and the open issues (audio joins at about 5.4 s and 11.4 s not heard by me, soft pay-stub paper at 3-4.7x enlargement,
landscape plates shown 2.04x enlarged, Ren standing, no captions). The owner's reply was the single word "approved". The owner gave no further
review notes, did not list changes, and did not say what they had watched or listened to; I do not know whether the owner listened to the audio or
viewed it on a phone, and I am not recording that they did.

QA warnings: none (the launcher reported 0 errors and 0 warnings).

Re-binding (no new owner message), second time: the manifest's total length changed from 1,380 to 1,360 frames so the video ends exactly with the narration (the first full render failed the A/V endpoint check by 0.84 s; no silence may be added to the audio). The prototype was re-rendered again and is again byte-identical (same SHA-256).

First re-binding: to render the remaining beats I had to add the code for beats 7-21 to the renderer, which is a hashed dependency, so
the launcher treated the approval as stale. I re-rendered the prototype with the extended renderer; it is byte-identical to the approved file (same
SHA-256 7498467423aa351c8ef753ce53f0a746f8f232f03d8e0bf7964dc213c4c2801f) and its QA is unchanged. The v3 Shorts rules say an identical prototype needs no
new approval, so this record re-binds the owner's original "approved" to the new fingerprint. If the owner disagrees, the approval should be treated as
withdrawn and the full render discarded.
