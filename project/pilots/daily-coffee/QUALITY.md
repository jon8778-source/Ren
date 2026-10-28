# Coffee pilot — quality report

Complete pilot rendered **for review**, not owner-approved for publication.

- Video: 4:55.19 container duration; 1280×720, 24 fps, H.264/yuv420p and AAC, MP4 faststart.
- Complete narration master: 4:55.153; 48 kHz mono, 24-bit PCM WAV. MP3 convenience copy supplied.
- Master loudness: -16.09 LUFS; true peak -1.50 dBTP.
- Encoded video audio: −16.10 LUFS; −1.34 dBTP. Audio/video timing agrees within one frame.
- Fifteen original WAVs are retained unchanged. Only 1.94 seconds of excessive edge silence were removed from derived narration. Internal pauses retained; no speech-speed changes, duration padding, music or source-clip audio.
- 895-word original script; all four illustrative calculations checked, including $4 × 365 = $1,460. No statistics or investment-return assumptions. Figures visibly labelled illustrative.
- 84 visual shots, with animated Ren, brief Max/Lena cutaways and moving graphics. Every shot midpoint was inspected, plus calculation end frames and the closing CTA. No visible crop/overlap found in those frames. Full-motion owner review remains required.
- Bundled office and narrative stills are template placeholders, not the approved office/Alex artwork. Source clip windows were checked against actual media. The inconsistent ren_explain_hands window was excluded.
- Same Qwen 1.7B Base / English / use_xvector_only=True configuration and reference hashes throughout. No acoustic boundary flags. This does not establish spoken-word accuracy, British accent or speaker identity: **all segments still need listening review** because no local ASR model is installed. No listening approvals were fabricated.
- 22 tests passed. Completed originals are hash-checked on resume. Script, settings, reference hashes, statuses and per-request observations remain in manifest.json. Credentials, models and temporary render caches are excluded from GitHub.

## Usage

Observed quota decrease for pilot paragraph requests: **422.552965 GPU-seconds**. Instrumented generation-attempt elapsed time: **506.983 seconds**, including queue/transfer/checkpoint overhead, excluding offline quota waiting and CPU video rendering. These are different measurements. The reused opening diagnostic previously cost 7.367073 quota GPU-seconds; it was not regenerated.

No over-quota usage was reported. Public ZeroGPU account allowance was used; no paid hardware, paid endpoint, credit top-up or alternative voice service was requested. The final account allowance base was 2,400 GPU-seconds (earlier sessions reported 300).

## Before publishing

Listen through all words and segment boundaries to confirm the Ren voice and pronunciation; inspect full-motion playback. Replace placeholder artwork if required and fill the workbook URL in the description. Nothing has been merged into main or published to a video platform.

## Files

- [MP4 video](deliverables/ren-coffee-pilot.mp4)
- [Complete narration WAV](deliverables/narration.wav)
- [Narration MP3](deliverables/narration.mp3)
- [Original script](script.md)
- [Detailed measurements and hashes](quality-report.json)
