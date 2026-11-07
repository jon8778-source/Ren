# Full Short reproduction / recovery

Branch: codex/health-short-revision6. Existing v3 adapter/components are reused;
long-form production remains untouched. Current user explicitly authorized the
remaining film; the approved opening and full authorization have separate evidence.

Use the existing project Python environment (Pillow/numpy/scipy/soundfile), FFmpeg
and FFprobe. Browser QA uses installed Node Playwright and /usr/bin/chromium.

Required media outside Git (fail on missing/hash mismatch, do not regenerate):
- ../deliverables/Ren_Health_Short_v2_15s_Prototype_rev06.mp4
- ../../portrait-short-01/deliverables/Ren_Health_Plan_Portrait_1min.mp4
Their exact SHA-256s are in authorization.json and audio-preservation.json.
Approved character/office/library/reference files must also be present at the
production.json paths. New empty environment PNGs are versioned with this source.

From repository root:

```bash
python project/episodes/long1-open-enrollment/short-cinematic-v2/prepare_full.py
python project/pipeline/shorts_standards.py run \
  --manifest project/episodes/long1-open-enrollment/short-cinematic-v2/full-production/production.json \
  --stage full \
  --output project/episodes/long1-open-enrollment/short-cinematic-v2/deliverables/Ren_Health_Short_v2_Final.mp4 \
  -- python project/episodes/long1-open-enrollment/short-cinematic-v2/render_full.py
python project/episodes/long1-open-enrollment/short-cinematic-v2/full-production/validate_full.py
node project/episodes/long1-open-enrollment/short-cinematic-v2/full-production/browser_playback.cjs
```

The launcher enforces the existing real owner-approval/fingerprint record. Changed
production inputs invalidate that record; only record actual applicable owner
authorization after inspecting the change. No automatic consent or blind gate bypass.
The resume command reuses verified existing video chunks and native mattes; never
resynthesizes narration. A cache miss renders that scene from source. The first
360frames always come from the approved exact MP4. Do not regenerate them.

Outputs: final MP4 and SRT in ../deliverables/; contact sheet and complete timeline
review in deliverables/full-review/. These paths and build/ are ignored by Git.
Run full QA/playback after a genuine modification. No publication/merge step.
