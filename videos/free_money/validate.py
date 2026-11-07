"""Validate a rendered Free Money pilot (local MP4): full decode with errors fatal, format, durations,
loudness, audio continuity, shot caps and frame counts, layout results from the renderer.

  project/.tools/venv/bin/python videos/free_money/validate.py /output/free_money_S1_S2_pilot.mp4
"""
import json, subprocess, sys, re
from pathlib import Path

mp4 = Path(sys.argv[1])
rep = json.loads((mp4.parent / (mp4.stem + "_report.json")).read_text())
res = {}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


# 1. complete decode, any error is fatal
r = run(["ffmpeg", "-v", "error", "-xerror", "-i", str(mp4), "-f", "null", "-"])
res["full_decode_clean"] = r.returncode == 0 and not r.stderr.strip()
res["decode_stderr"] = r.stderr.strip()[:300]
# 2. format
pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(mp4)]).stdout)
v = next(s for s in pr["streams"] if s["codec_type"] == "video")
a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
res["video"] = f"{v['codec_name']} {v['width']}x{v['height']} {v['r_frame_rate']} {v['pix_fmt']}"
res["audio"] = f"{a['codec_name']} {a['sample_rate']} Hz ch={a['channels']}"
res["format_ok"] = (v["width"], v["height"], v["r_frame_rate"], v["codec_name"], a["codec_name"]) == (1280, 720, "24/1", "h264", "aac")
res["duration_video_s"] = float(v["duration"]); res["duration_audio_s"] = float(a["duration"])
res["av_duration_diff_s"] = round(abs(float(v["duration"]) - float(a["duration"])), 3)
nb = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(mp4)]).stdout.strip())
res["frames"] = nb
res["frames_match_duration"] = nb == round(float(v["duration"]) * 24)
# 3. loudness
p = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
res["lufs"] = float(p[p.rindex("I:") + 2:].split()[0]); res["true_peak_dbtp"] = float(p[p.rindex("Peak:") + 5:].split()[0])
# 4. audio continuity: no silence gap longer than 0.6 s inside the narration (the final hold is excluded)
sd = run(["ffmpeg", "-nostats", "-i", str(mp4), "-af", "silencedetect=n=-45dB:d=0.6", "-f", "null", "-"]).stderr
sil = [(float(s), float(e)) for s, e in zip(re.findall(r"silence_start: ([\d.]+)", sd), re.findall(r"silence_end: ([\d.]+)", sd))]
res["silences_over_0.6s_inside_narration"] = [x for x in sil if x[1] < rep["narration_s"] - 0.1]
# 5. shots: caps and frame counts
caps = {"ren": 5.5, "story": 2.5, "graphic": 3.5}
bad = []
tot = 0
for s in rep["shots"]:
    fr = round((s["end"] - s["start"]) * 24)
    tot += fr
    if fr / 24 > caps[s["type"]] + 1e-6:
        bad.append((s["i"], s["type"], fr / 24))
res["shots"] = len(rep["shots"]); res["shot_frames_sum"] = tot; res["shot_frames_equal_video_frames"] = tot == nb
res["shots_over_cap"] = bad
res["layout_problems"] = rep["layout_problems"]
res["narration_check"] = {k: {"ratio": x["ratio"], "differences": x["differences"]} for k, x in json.loads((Path(__file__).parent / "voice" / "check.json").read_text()).items() if k in ("S1", "S2")}
ok = res["full_decode_clean"] and res["format_ok"] and res["frames_match_duration"] and not res["silences_over_0.6s_inside_narration"] and not bad and not res["layout_problems"] and res["shot_frames_equal_video_frames"] and res["av_duration_diff_s"] < 0.1
res["PASS"] = bool(ok)
(mp4.parent / (mp4.stem + "_validation.json")).write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
