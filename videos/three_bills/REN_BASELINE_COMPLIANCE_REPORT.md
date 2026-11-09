# REN baseline compliance report: Three Bills in 30 Days, pilot (9 Nov 2026)

Branch: `video/three-bills-30-days` (new, from `video/unclaimed-401k-match-maya`; policy files copied from `origin/main`). Pilot: `/output/three_bills/ren_three_bills_pilot_57s.mp4` (local, not in git),
1920x1080, 24 fps, 56.83 s, SHA-256 7196e5d7... Status legend: PASS = measured/verified as stated; FAIL; NOT VERIFIED = not done or not independently checkable.

## 1. Preflight
| Item | Result | Evidence |
|---|---|---|
| Active branch identified; policy documents located | PASS | The working branch did not contain `REN_LONGFORM_BASELINE.md`, `REN_LONGFORM_CHECKLIST.md` or `REN_LONGFORM_REFERENCE.md`; they exist only on `origin/main` (and `codex/ren-longform-baseline`). Reported, then copied unchanged with `AGENTS.md` and `CLAUDE.md` from `origin/main` onto the new branch. No existing episode was touched (new folder `videos/three_bills/`). |
| Rules read this session | PASS (partial) | Read in full: `CLAUDE.md`, `AGENTS.md`, `REN_LONGFORM_BASELINE.md`, `REN_LONGFORM_CHECKLIST.md`, `REN_LONGFORM_REFERENCE.md`. **NOT VERIFIED: `REN_VIDEO_RULES.md` and `DECISIONS.md` were not re-read in this session** (I wrote the earlier scale/grounding section myself in a previous session; the rules were applied from that memory and from the pack). |
| Renderer, Ren clips, voice reference, QA tooling available | PASS | `project/cliplib/ren_stage.py` (+15 tests pass), `assets/ren_library/` 33 MP4s, `Audio/ren_reference.wav` (SHA 78de4bd4...), Qwen venv; episode QA written fresh (`tb_qa.py`). The repo's older `qa_timeline.py`/`validate.py`/`jitter_check.py` are tied to the 720p free_money renderer and were NOT RUN. |
| Contradictions flagged | PASS | (a) `CLAUDE.md` body still carries white-background/Kokoro rules; its new header and `AGENTS.md` say they do not govern new long-form work: followed the header. (b) Pack README points at branch `video/free-money-v2` for baseline docs; they are actually on `main`. (c) Pack SCENE_PLAN says "existing approved office"; the office plate is a corporate office, used here as a stand-in for Maya's home (see continuity). (d) Pack says plates are "approved/calibrated"; `PLATE_GEOM` was calibrated for Ren at 175 cm, and Maya's 165 cm is MY assumption. (e) `AGENTS.md` says "new branch"; the pack says Codex: followed. |

## 2. Asset provenance
| Item | Result | Evidence |
|---|---|---|
| Script v2 and voice script hashes | PASS | `tb_qa.py` 2b: SHA-256 14801320... and efa04724... match the pack's approved values. |
| Owner approval of script and Maya art | NOT VERIFIED independently | Recorded only in the pack's OWNER_DECISIONS.md ("Script approved", "Maya images approved", 9 Nov). I did not see those messages. Treated as approved because the owner supplied the pack stating it; flag if wrong. |
| Maya pose files intact | PASS | 4 PNGs match `ASSET_MANIFEST.json` hashes (tb_qa 3a). |
| Maya alpha edges | PASS (visual) | Viewed at 100% on navy and sage backgrounds (face and feet of all four poses, `/tmp` crops): no white halo, clean outline; 2-4 enclosed transparent pockets of 100-240 px (between arms and body) are intentional. |
| Maya identity vs the 401(k) episode's Maya | FAIL (discontinuity, by design of the pack) | New Maya has shoulder-length brown hair, green cardigan, navy trousers; the 401(k) Maya has dark wavy hair and a rust sweater. Same name, different design: a viewer of the channel may notice. Owner approved the new art for this episode. |
| Plates used are approved | PASS | parking lot, porch, office (library/supporting_assets, Free Money pack) and Ren's sage office. Provisional kitchen/dental plates were NOT used (style mismatch). |
| Ren clips used are approved | PASS | ren_present_palm_left, ren_shrug, ren_point_right, ren_thinking: `ren_library.json` status ok; windows checked in tb_qa 9. |
| Inventory | PASS | `ASSET_INVENTORY.md/.csv`: 23 rows, hashes, status, use. |

## 3. Genuine animation usage
| Item | Result | Evidence |
|---|---|---|
| Ren cutaways are real clips | PASS | 4 shots (S01, S06, S11, S17). tb_qa 9: inside usable windows, every frame a distinct clip frame, in-box motion, feet fixed (std < 1 px), background unchanged in every rendered frame (no pan), Ren left and graphics right. Mouth closed: NOT VERIFIED by detector; sampled frames viewed (S06 face at 100%: closed). |
| Maya motion | PASS with a limit | Maya has FOUR poses. Her "acting" is pose cross-fades (3 frames), slow camera pushes, and moving props/overlays. This is limited cut-out illustration, not actor animation, and I do not claim otherwise. S07 and S14 are one pose each with moving overlays; S13 is one pose with a chip. |
| No shot relies only on a pan over a still | PASS (metric) | tb_qa 10b: every Maya shot changes pose or carries a moving prop/overlay. This metric would accept a shot whose only motion is a chip sliding in; judge S07, S13, S14 yourself. |
| Camera movement purposeful | NOT VERIFIED | Pushes are slow (1.08-1.5x) and tied to emotion beats; whether they feel purposeful needs your eye. |

## 4. Visual continuity and staging
| Item | Result | Evidence |
|---|---|---|
| Maya scale/grounding | PASS | tb_qa 10a: measured height equals `ren_stage.height_px` for 165 cm on each plate within 3%, head and feet inside the frame in every sampled frame (this caught and I fixed three shots whose head was cut off); contact shadows: viewed at 100% (S09, S15): tight shadow under both feet. |
| Ren scale/grounding | PASS | tb_qa 9; S06 feet viewed at 100%. |
| Story continuity | PARTIAL | Maya's "afterward" savings-app scene (S09, S10) and the budget scene (S13-S14) stand in the corporate office plate, not a home: no approved home plate exists (the new kitchen/dental plates are provisional). The porch stands in for her home in S04/S07/S08/S12. |
| Transitions | PASS (partial visual) | tb_qa 5: cuts only on shot boundaries, no A-B-A inserts or flashes, every cut changes the picture. Visually viewed: 6 cuts (12 frames, pre and post, at reduced size: S01/S05/S06/S10/S11/S16). NOT viewed: the other 12 cuts as frame pairs. |
| Whole pilot visually inspected | PARTIAL | Contact sheet at 1 frame/s (all 57 s, 480 px wide) viewed for the final render; 100% crops only for S06 (Ren) and S09, S15 (Maya). Mid-shot stills at 640 px were viewed for an EARLIER render of all 18 shots; not re-viewed for the final. Motion at speed and phone playback: NOT VERIFIED. |
| Not a PowerPoint look | NOT VERIFIED | 3 graphic-only shots of 19; 12 Maya shots, 4 Ren. Several cards (equation, chips, calendar) are plain; judge the feel. |

## 5. Financial accuracy
| Item | Result | Evidence |
|---|---|---|
| Arithmetic | PASS | `production/check_numbers.py` MATHS OK; tb_qa 7: 760+390+1,050 = 2,200; 2,600-2,200 = 400; 50 x 52 = 2,600. |
| Every displayed number from the checked source | PASS | `tb_ui.py` reads `production/assumptions.csv`; tb_qa 6c on 261 frames: displayed numbers 1,050 / 18 / 2,200 / 2,600 / 3 / 30 / 390 / 400 / 600 / 760 / 80 all in the source (18 and 3, 30 are day/month labels). |
| Claims and sources | NOT VERIFIED | The pack's CLAIMS_AND_SOURCES.md cites CFPB/FDIC pages; I did not open them (no network check this session). The pilot (first minute) makes no sourced statistic. |

## 6. Voice configuration
| Item | Result | Evidence |
|---|---|---|
| Qwen clone config | PASS | `gen_voice.py`: `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, English, `x_vector_only_mode=True`, `Audio/ren_reference.wav`, fixed seeds, chunks <= 45 words, resumable, no speed change/stretch/pad (tb_qa 12a); the renderer calls no TTS (12b). |
| Narration generated once | PASS | Pilot only (voice/H.wav 31.6 s, L.wav 31.3 s cut to the last sentence); no regeneration; cached chunks kept locally (voice/ is not in git). |
| Words correct | PASS (STT) | Whisper medium.en: ratios 0.93 and 0.95, differences are digits only ("$2,200" for "two thousand two hundred" etc.). |
| Accent, pace, pronunciation, joins | NOT VERIFIED | I cannot hear audio. |

## 7. Rendering QA
44 checks in `reports/hybrid_qc.md`, OVERALL PASS: contiguous frame-aligned timeline from frame 0, caps (Ren 5.5 s / graphic 3.5 s; story stills 0), no 3+ graphic run (longest 1), Ren returns longest gap 22.5 s, phrases tile the script (164 words), full decode with -xerror, 1920x1080 24 fps, 1364 frames, A/V 0.001 s apart, -18.6 LUFS / -1.0 dBTP, constant 24 fps (every packet 1/24 s), text in the safe area and >= 32 px, Maya jitter 0.051 px (limit 0.12), audio correlation 1.0000.
Pilot length is 56.8 s, not 60 s, because that is where a sentence ends (the rule: cut after a complete sentence; no padding).

## 8. Approval gates
| Gate | Status |
|---|---|
| Script v2 approval | recorded in the pack (NOT VERIFIED independently) |
| Maya art approval | recorded in the pack (NOT VERIFIED independently) |
| Pilot | **PENDING: awaiting your explicit approval** |
| Full video | NOT STARTED (blocked on pilot approval) |
| Publish / merge | NOT AUTHORIZED |

## Full-episode planning test
`SHOT_PLAN_FULL.md`: planned returns to Ren about every 20-33 s, supporting-character beats and environments per section, and the specific repetitive-card risks (the four-principles section 4:41-5:31 and the reframe 3:57-4:41) with mitigations (one scene per principle, props on Maya's porch, never 3 graphic-only shots in a row, enforced by tb_qa 1d). Honest constraint: Maya has only four poses and no home plate, so the full film will repeat poses and rely on the porch/office stand-ins unless you approve 2-3 more poses and a home plate.
