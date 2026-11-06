# Shorts standards implementation QA

Dedicated branch: `codex/shorts-production-standards`.

Changed entrypoints and new tools apply to Shorts only. Long-form renderer,
assembler, audio generation, configuration, artwork and finished MP4s are unchanged.

**18 automated regression tests passed**. Python compilation and whitespace
checks passed. The intentionally incomplete example is rejected by preflight.

Automated regression suite:

    python -m unittest discover -s project/pipeline/tests -p 'test_shorts_standards.py' -v

Coverage: approved/missing/changed/unapproved inputs; composition/full-bleed checks;
scene gaps/IDs/repeat justification; cues; measured safe bounds/font/disclaimer;
matching/stale/missing approval; refusal to launch full rendering before approval;
dependency cache invalidation; borders/black/frozen frames; A/V and timestamp faults.
Tests use temporary manifests and pixel arrays/mocked media probes, not video renders.
A separate real FFmpeg audit decoded the old health insurance Short without
rendering it. Technical results and subjective limitations are recorded separately.

The approval gate is fail-closed on missing/stale evidence and input hashes. It
cannot authenticate the truth of a transcribed user message; the operator must
record an actual explicit approval, never invent one. It is an orchestration
boundary, not a sandbox preventing arbitrary historical Python scripts being run.
Manifest declarations require review; actual text measurements require renderer
instrumentation. Border/freeze detectors are heuristics with possible false positives.
Stream synchronization is not a substitute for listening or lip-sync verification.

No new Short, prototype, character design, audio or artwork was generated. The
proposed health insurance test remains pending asset audit/approval and its own
15-second preview approval. No full video render or publication is authorized here.
