# Portrait Short QA

- Finished runtime: **58.875 seconds**, 1,413 frames, 1080×1920, 9:16,
  24fps H.264/yuv420p, AAC 48kHz mono, faststart MP4.
- Six excerpt files have their exact expected frame counts. Full final video
  and audio decode completed with errors fatal. All 1,413 frames checked for
  black/blank output; none found. Contact sheets reviewed at two-second intervals.
- Native presenter crop inspected for face, glasses, clothing, hands and edges;
  no scaling or new matting was applied to source character pixels.
- The 58.865333s PCM narration is exactly the concatenation of selected source
  samples; final-frame/audio difference is source codec rounding, not padding.
  No speech acceleration, silence insertion, new voice calls or music.
- Re-encoded AAC correlation to selected PCM: **0.999976**. Encoded peak:
  **−1.93dBFS**, with headroom. Cuts use source pauses around complete passages.
- 21 multi-word captions preserve selected source text/timings. They are burned
  in and also supplied as SRT. Word accuracy inherits the source; no new ASR run.
- $2,520/year and $840/year match the shared calculations. Graphics say
  premiums only and check total care costs. No guaranteed saving asserted.
- Disclaimer appears at the opening and throughout the last 3.5 seconds:
  “Educational content only, not financial advice.” (line break for readability).
- Text is outside the desk/presenter crop; right-side UI/bottom-metadata margins
  are reserved. Graphic cards remain visible across phrases for reading time.
- Original full MP4 SHA unchanged. No credentials, media or caches in Git.

Limits: no new listening session or physical Android device playback test was
available. Readability/framing was inspected from encoded samples; native source
character resolution remains 720p-derived. Graphic cards deliberately have longer
reading holds than the long-form template's 3.5-second graphics-shot guideline.
No claim is made that static graphic holds provide additional character animation.

Detailed machine results: validation.json. Exact edits: edit-manifest.json.
