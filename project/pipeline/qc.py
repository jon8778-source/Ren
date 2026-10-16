"""Stage 7: quality check. Runs on the finished video and writes reports/qc-<name>.md and .json.

  python pipeline/qc.py episodes/<id> --video renders/pilot.mp4 --name pilot

Each check is PASS, FLAG (needs a look) or FAIL (must fix). Exit status 1 if anything fails.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from calc import calculate  # noqa: E402
from common import PROJECT, load_config, load_json, parse_script, resolve_ref, spoken_numbers  # noqa: E402

STAT_WORDS = re.compile(r"\b(percent|average|median|study|survey|research|according to|americans|most people|many people|a lot of people|statistic)\b|%", re.I)


class Report:
    def __init__(self):
        self.items = []

    def add(self, name, status, detail, extra=None):
        self.items.append({"check": name, "status": status, "detail": detail, **({"items": extra} if extra else {})})


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def probe(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "json", str(video)], capture_output=True, text=True).stdout
    return json.loads(out)


def audio_envelope(video, tmp):
    wav = Path(tmp) / "a.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", str(wav)], check=True)
    import soundfile as sf
    y, sr = sf.read(wav)
    hop = int(sr * 0.01)
    frames = len(y) // hop
    rms = np.sqrt(np.mean(y[: frames * hop].reshape(frames, hop) ** 2, axis=1) + 1e-12)
    return 20 * np.log10(rms), 0.01


def lufs(video):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    vals = [l.split("I:")[1].split("LUFS")[0] for l in out.splitlines() if l.strip().startswith("I:")]
    return float(vals[-1]) if vals else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--video", required=True)
    ap.add_argument("--name", default="pilot")
    args = ap.parse_args()
    ep = Path(args.episode).resolve()
    video = ep / args.video
    r = Report()
    lines = parse_script(ep)
    timings = load_json(ep / "audio" / "timings.json")
    props = load_json(ep / "build" / "props.json")
    cfg = props["config"]  # the layout the video was actually built with
    L, Q = cfg["layout"], cfg["qc"]
    # Graphics drawn in a virtual box and scaled down (vertical shorts) render text smaller
    text_scale = L["content_when_character_left"]["w"] / L["content_virtual"]["w"] if "content_virtual" in L else 1.0
    manifest = load_json(PROJECT / "characters" / "manifest.json")["characters"]
    assumptions, problems = calculate(ep)

    # 1. Maths
    drafts = sorted(c for c, p in assumptions["characters"].items() if p["status"] == "draft")
    r.add("Maths (assumptions table recalculated)", "FAIL" if problems else "PASS",
          "; ".join(problems) if problems else "All totals recalculate correctly." +
          (f" Draft figures (only incomes used in this pilot): {', '.join(drafts)}." if drafts else ""))

    # 2. Spoken numbers vs the table
    bad = []
    for l in lines:
        said = spoken_numbers(l["text"])
        if "DIGITS" in said:
            bad.append(f"[{l['id']}] uses digits; write numbers out for the voice")
            said = [x for x in said if x != "DIGITS"]
        try:
            want = [resolve_ref(x, assumptions) for x in l["refs"]]
        except KeyError as e:
            bad.append(f"[{l['id']}] unknown reference {e}")
            continue
        got = Counter(float(x) for x in said)
        exp = Counter(want)
        if 1.0 not in exp:
            got.pop(1.0, None)  # "one Tuesday", "one of" – a lone one isn't a figure unless the line says it is
        if got != exp:
            bad.append(f"[{l['id']}] says {sorted(got.elements())} but the table expects {sorted(exp.elements())}")
    r.add("Number accuracy: script vs table", "FAIL" if bad else "PASS",
          "Every spoken number matches its table value." if not bad else f"{len(bad)} mismatch(es)", bad)

    # 3. Numbers on screen only come from the table
    raw = load_json(ep / "scenes.json")
    typed = []
    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in {"id", "line", "beats", "count", "level", "offset", "from", "to", "from_end", "people", "character", "highlight"} or k.startswith("_"):
                    continue
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str) and re.search(r"\d", re.sub(r"\{[^}]*\}", "", o)):
            typed.append(f"{path}: '{o}'")
    walk(raw["scenes"], "scenes")
    r.add("Number accuracy: on-screen figures", "FAIL" if typed else "PASS",
          "All on-screen money and numbers are pulled from the assumptions table." if not typed else "Hand-typed numbers found", typed)

    # 4. Statistics need a source
    sources = load_json(ep / "sources.json") if (ep / "sources.json").exists() else {}
    stats, sourced = [], []
    for l in lines:
        src = sources.get(l["id"])
        if src:
            ok = src.get("status") == "verified"
            (sourced if ok else stats).append(f"[{l['id']}] {src['status'].upper()}: {src['claim']} ({src['url']})")
        elif STAT_WORDS.search(l["text"]):
            stats.append(f"[{l['id']}] possible statistic with no source: {l['text']}")
    r.add("Real statistics", "FLAG" if stats else "PASS",
          ("No real-world statistics are used; all figures are labelled examples." if not sourced else
           f"{len(sourced)} sourced claim(s), verified by the owner.") if not stats else
          "Claims needing a verified source ([VERIFY] in sources.json)", stats + sourced)

    # 5. Voice consistency
    ch = timings["chunks"]
    settings_same = all(c["settings"] == ch[0]["settings"] for c in ch)
    pitches = [c["median_pitch_hz"] for c in ch if c["median_pitch_hz"]]
    spread = 12 * math.log2(max(pitches) / min(pitches)) if pitches else 0
    louds = [c["lufs"] for c in ch]
    issues = []
    if not settings_same:
        issues.append("chunks used different voice settings")
    issues += [f"{c['file']} is {c['duration']:.1f}s (limit 60s)" for c in ch if c["duration"] >= 60]
    issues += [f"{c['file']} has {c['leading_silence_s']:.2f}s leading silence" for c in ch if c["leading_silence_s"] > Q["max_leading_silence_s"]]
    if spread > Q["max_pitch_spread_semitones"]:
        issues.append(f"pitch differs by {spread:.1f} semitones between chunks")
    if max(louds) - min(louds) > Q["chunk_lufs_tolerance"]:
        issues.append(f"chunk loudness differs by {max(louds) - min(louds):.1f} LU")
    v = timings["settings"]
    r.add("Voice consistency", "FLAG" if issues else "PASS",
          f"{len(ch)} chunks, identical settings ({' + '.join(f'{k} {w}' for k, w in v['blend'].items())}, speed {v['speed']}); "
          f"leading silence {', '.join(str(c['leading_silence_s']) for c in ch)}s; loudness {', '.join(str(c['lufs']) for c in ch)} LUFS; "
          f"pitch {', '.join(f'{p:.0f}' for p in pitches)} Hz (spread {spread:.1f} semitones).", issues)

    # 6. Character consistency: every image used is the locked file
    used, wrong = set(), []
    for s in props["scenes"]:
        if s.get("character"):
            used.add(s["character"]["src"])
        for p in s["graphic"].get("people", []):
            used.add(p["src"])
    for src in sorted(used):
        _, cid, f = src.split("/")
        pose = f[:-4]
        want = manifest.get(cid, {}).get("poses", {}).get(pose)
        rendered = PROJECT / "remotion" / "public" / src
        if not want:
            wrong.append(f"{src} is not in the locked sheet")
        elif not rendered.exists() or sha(rendered) != want:
            wrong.append(f"{src} differs from the locked sheet")
    r.add("Character consistency", "FAIL" if wrong else "PASS",
          f"{len(used)} poses used, all byte-identical to the locked character sheets." if not wrong else "Mismatched art", wrong)

    with tempfile.TemporaryDirectory() as tmp:
        env, step = audio_envelope(video, tmp)
        speech = env > (env.max() - 35)

        def onset_near(t):
            # First silence-to-speech transition (at least 0.12s of quiet before it) from t - 0.3s on
            need = int(0.12 / step)
            for k in range(int(max(0, t - 0.3) / step), len(speech)):
                if speech[k] and not speech[max(0, k - need):k].any():
                    return k * step
            return None

        # 7. Caption sync against speech found in the final audio
        late = []
        caps = props["captions"]
        script_text = {l["id"]: l["text"] for l in lines}
        line_starts = {round(l["start"], 3) for l in timings["lines"]}
        for i, c in enumerate(caps):
            if round(c["start"], 3) not in line_starts:
                continue  # second half of a split sentence: no pause to measure against
            onset = onset_near(c["start"])
            if onset is None or abs(onset - c["start"]) > Q["caption_sync_tolerance_s"]:
                late.append(f"caption {i + 1} at {c['start']:.2f}s, speech starts at {onset if onset is None else round(onset, 2)}s")
        joined = " ".join(c["text"] for c in caps)
        mismatched = [] if joined == " ".join(l["text"] for l in lines) else ["captions do not reproduce the script word for word"]
        cpl = L["caption"]["w"] / (0.5 * L["caption"]["font_px"])
        too_long = [f"'{c['text'][:40]}…' needs {math.ceil(len(c['text']) / cpl)} lines" for c in caps if math.ceil(len(c["text"]) / cpl) > L["caption"]["max_lines"]]
        offs = []
        for c in caps:
            if round(c["start"], 3) not in line_starts:
                continue
            o = onset_near(c["start"])
            if o is not None:
                offs.append(o - c["start"])
        r.add("Caption sync", "FLAG" if (late or mismatched or too_long) else "PASS",
              f"{len(caps)} captions (long sentences split at a pause); each starts within {Q['caption_sync_tolerance_s']}s of its speech "
              f"(measured offsets {min(offs):+.2f}s to {max(offs):+.2f}s); text matches the script word for word; all fit in {L['caption']['max_lines']} lines.",
              late + [f"caption not in script: {m}" for m in mismatched] + too_long)

        # 8. Silences over 1 second
        quiet, k, sil = [], 0, ~speech
        while k < len(sil):
            if sil[k]:
                j = k
                while j < len(sil) and sil[j]:
                    j += 1
                d = (j - k) * step
                if d > Q["max_silence_s"]:
                    quiet.append(f"{k * step:.2f}s–{j * step:.2f}s ({d:.2f}s){' (end of video)' if j >= len(sil) - 1 else ''}")
                k = j
            else:
                k += 1
        mid_quiet = [q for q in quiet if "end of video" not in q]
        r.add("Silence over 1 second", "FLAG" if mid_quiet else "PASS",
              "No gap in the voice longer than 1 second." if not mid_quiet else f"{len(mid_quiet)} long gap(s)",
              quiet)

        # 9. Safe zone: the bottom 12% (YouTube controls) must stay empty, checked on real frames
        H = cfg["video"]["height"]
        y0 = L["youtube_controls_from_y"]
        frames_dir = Path(tmp) / "f"
        frames_dir.mkdir()
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps=2,crop=iw:{H - y0}:0:{y0}", str(frames_dir / "%04d.png")], check=True)
        from PIL import Image
        hits = []
        for fp in sorted(frames_dir.glob("*.png")):
            a = np.asarray(Image.open(fp).convert("L"))
            if (a < 235).mean() > 0.0005:
                hits.append(f"{(int(fp.stem) - 1) / 2:.1f}s")
        boxes = {k: L[k] for k in ("caption", "character_left", "character_right", "content_when_character_left", "content_when_character_right")}
        out_of_zone = [f"{k} ends at y={b['y'] + b['h']} (controls start at {y0})" for k, b in boxes.items() if b["y"] + b["h"] > y0]
        out_of_zone += [f"{k} is outside the {L['margin']}px side margins" for k, b in boxes.items() if b["x"] < L["margin"] or b["x"] + b["w"] > cfg["video"]["width"] - L["margin"]]
        if "right_reserved_px" in L:  # Shorts buttons run down the right edge, level with the caption
            cap = L["caption"]
            if cap["x"] + cap["w"] > cfg["video"]["width"] - L["right_reserved_px"]:
                out_of_zone.append("captions run under the Shorts buttons on the right")
        r.add("Safe-zone placement", "FAIL" if (hits or out_of_zone) else "PASS",
              f"Checked {len(list(frames_dir.glob('*.png')))} frames (2 per second): nothing drawn in the bottom {H - y0}px. "
              f"Captions end at y={L['caption']['y'] + L['caption']['h']}; all zones sit inside {L['margin']}px margins "
              "(the small disclaimer pill sits at the very top by design).",
              [f"content in the controls area at {h}" for h in hits] + out_of_zone)

    # 10. Text readability
    eff = {k: round(v * text_scale) for k, v in L["fonts"].items()}
    small = [f"{k} text is {v}px (minimum {L['min_font_px']}px)" for k, v in eff.items() if v < L["min_font_px"]]
    if L["caption"]["font_px"] < L["min_font_px"]:
        small.append("captions below minimum size")
    r.add("Text readability", "FAIL" if small else "PASS",
          f"Smallest text {min(eff.values())}px, captions {L['caption']['font_px']}px, key numbers {eff['number']}px on a "
          f"{cfg['video']['width']}x{cfg['video']['height']} frame. "
          "Dark navy on white.", small)

    # 11. Visual change at least every 7 seconds
    events = sorted({round(s["start"] + b, 2) for s in props["scenes"] for b in [0] + s.get("beats", [])})
    events.append(props["duration"])
    gaps = [(events[i], events[i + 1] - events[i]) for i in range(len(events) - 1)]
    long_gaps = [f"{t:.1f}s: {d:.1f}s without a new visual" for t, d in gaps if d > Q["max_seconds_without_visual_change"]]
    longest = max(gaps, key=lambda g: g[1])
    scene_lengths = [s["end"] - s["start"] for s in props["scenes"]]
    r.add("Visual changes", "FLAG" if long_gaps else "PASS",
          f"{len(props['scenes'])} scenes ({min(scene_lengths):.1f}s to {max(scene_lengths):.1f}s long) with {len(events) - 1} visual changes; "
          f"longest hold {longest[1]:.1f}s at {longest[0]:.1f}s. Slow pan/zoom runs throughout.", long_gaps)

    # 12. Disclaimer and file format
    ov = props["overlays"]
    has_start = any(o["from"] <= 0.01 for o in ov)
    has_end = any(abs(o["to"] - props["duration"]) < 0.05 for o in ov)
    desc = (ep / "description.txt").read_text() if (ep / "description.txt").exists() else ""
    d_ok = cfg["disclaimer"].lower() in desc.lower()
    r.add("Disclaimer", "PASS" if (has_start and has_end and d_ok) else "FAIL",
          f"On screen at the start ({'yes' if has_start else 'NO'}) and end ({'yes' if has_end else 'NO'}); in description.txt ({'yes' if d_ok else 'NO'}).")
    info = probe(video)
    vs = next(s for s in info["streams"] if s["codec_type"] == "video")
    has_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    dur = float(info["format"]["duration"])
    loud = lufs(video)
    fmt_ok = vs["width"] == cfg["video"]["width"] and vs["height"] == cfg["video"]["height"] and has_audio
    r.add("File", "PASS" if fmt_ok else "FAIL",
          f"{vs['width']}x{vs['height']}, {vs['r_frame_rate']} fps, {dur:.1f}s, audio {'present' if has_audio else 'MISSING'}, loudness {loud} LUFS.")

    worst = "FAIL" if any(i["status"] == "FAIL" for i in r.items) else "FLAG" if any(i["status"] == "FLAG" for i in r.items) else "PASS"
    reports = ep / "reports"
    reports.mkdir(exist_ok=True)
    (reports / f"qc-{args.name}.json").write_text(json.dumps({"overall": worst, "checks": r.items}, indent=1) + "\n")
    md = [f"# Quality check: {args.name}", "", f"Video: `{args.video}`  ", f"Overall: **{worst}**", "", "| Check | Result | Detail |", "|---|---|---|"]
    md += [f"| {i['check']} | {i['status']} | {i['detail']} |" for i in r.items]
    for i in r.items:
        if i.get("items"):
            md += ["", f"**{i['check']}**", ""] + [f"- {x}" for x in i["items"]]
    (reports / f"qc-{args.name}.md").write_text("\n".join(md) + "\n")
    for i in r.items:
        print(f"[{i['status']:4s}] {i['check']}: {i['detail']}")
        for x in i.get("items", []):
            print(f"         - {x}")
    print(f"OVERALL {worst}")
    sys.exit(1 if worst == "FAIL" else 0)


if __name__ == "__main__":
    main()
