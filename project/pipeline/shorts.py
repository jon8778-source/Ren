"""Cut vertical shorts out of a finished long video.

  python pipeline/shorts.py episodes/<id>

Reads episodes/<id>/shorts.json. Each short lists script lines from the long video (in the
order to play them) and, optionally, scene overrides for lines whose long-video picture
doesn't work on its own. For each short this builds episodes/<id>-<short>/ with:
- audio sliced from the long video's own voice track (same take, same voice), re-spaced and
  loudness-normalized, plus timings.json,
- script.md (the chosen lines with their number tags), assumptions.csv and claims.txt copied
  from the long video, scenes.json and description.txt,
so assemble.py (with --config config.vertical.json) and qc.py run on it unchanged.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from common import load_config, load_json, parse_script  # noqa: E402
from voice import lufs, leading_silence, median_pitch_hz  # noqa: E402

GAP, LEAD, TAIL = 0.42, 0.4, 1.6


def scene_for_line(long_scenes, line_id, order):
    """The long video's scene that is on screen when this line starts."""
    best = None
    for s in long_scenes:
        if order[s["line"]] <= order[line_id]:
            best = s
    return json.loads(json.dumps(best))


def main():
    ep = Path(sys.argv[1]).resolve()
    spec = load_json(ep / "shorts.json")
    long_t = load_json(ep / "audio" / "timings.json")
    long_lines = {l["id"]: l for l in long_t["lines"]}
    script = {l["id"]: l for l in parse_script(ep)}
    raw = (ep / "script.md").read_text()
    long_scenes = load_json(ep / "scenes.json")["scenes"]
    order = {l["id"]: i for i, l in enumerate(long_t["lines"])}
    voice, sr = sf.read(ep / "audio" / "voice.wav", dtype="float32")
    cfg = load_config()["voice"]

    for name, sh in spec["shorts"].items():
        out = ep.parent / f"{ep.name}-{name}"
        (out / "audio").mkdir(parents=True, exist_ok=True)
        for f in ("assumptions.csv", "claims.txt", "sources.json"):  # sources: the owner's verified claims
            if (ep / f).exists():
                shutil.copy(ep / f, out / f)
        subprocess.run([sys.executable, str(Path(__file__).parent / "calc.py"), str(out)], check=True, capture_output=True)

        # Audio: each line's own samples from the long track, laid out with fixed gaps
        parts, timeline, t = [np.zeros(int(LEAD * sr), dtype=np.float32)], [], LEAD
        for i, lid in enumerate(sh["lines"]):
            if i:
                parts.append(np.zeros(int(GAP * sr), dtype=np.float32))
                t += GAP
            l = long_lines[lid]
            clip = voice[int((l["start"] - 0.01) * sr): int((l["end"] + 0.02) * sr)]
            parts.append(clip)
            d = len(clip) / sr
            timeline.append({**script[lid], "section": name, "start": round(t + 0.01, 3), "end": round(t + d - 0.02, 3), "chunk": 0})
            t += d
        parts.append(np.zeros(int(TAIL * sr), dtype=np.float32))
        track = np.concatenate(parts)
        sf.write(out / "audio" / "voice.wav", track, sr)
        speech = track[int(LEAD * sr): -int(TAIL * sr)]
        sf.write(out / "audio" / "chunk_00.wav", speech, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out / "audio" / "voice.wav"), "-af",
                        f"highpass=f=70,loudnorm=I={cfg['target_lufs']}:TP=-1.5:LRA=9", "-ar", "48000", "-b:a", "192k",
                        str(out / "audio" / "voice.mp3")], check=True)
        chunk = {"file": "chunk_00.wav", "start": LEAD, "duration": round(len(speech) / sr, 3),
                 "leading_silence_s": round(leading_silence(speech), 3), "lufs": lufs(out / "audio" / "chunk_00.wav"),
                 "median_pitch_hz": median_pitch_hz(out / "audio" / "chunk_00.wav"), "settings": cfg,
                 "source": f"cut from {ep.name}/audio/voice.wav"}
        (out / "audio" / "timings.json").write_text(json.dumps(
            {"settings": cfg, "duration": round(len(track) / sr, 3), "lines": timeline, "chunks": [chunk]}, indent=1) + "\n")

        # Script: the chosen lines, verbatim with their number tags
        rows = {m.group(1): m.group(0) for m in re.finditer(r"^\[([a-z0-9]+)\].*$", raw, re.M)}
        (out / "script.md").write_text(f"# {sh['title']}\n\nCut from {ep.name}. Lines in play order.\n\n## {name}\n"
                                       + "\n".join(rows[l] for l in sh["lines"]) + "\n")

        # Scenes: the long video's picture for each line, unless the short overrides it
        scenes = []
        for lid in sh["lines"]:
            s = sh.get("scenes", {}).get(lid) or scene_for_line(long_scenes, lid, order)
            s = {**s, "line": lid}
            s["beats"] = [b for b in s.get("beats", []) if not (isinstance(b, str) and b[1:].split("+")[0].split("-")[0] not in sh["lines"])] or [0.2]
            scenes.append(s)
        for i, s in enumerate(scenes, 1):
            s["id"] = f"s{i:02d}"
        (out / "scenes.json").write_text(json.dumps({"overlays": [{"type": "disclaimer", "from": 0, "to": 4}, {"type": "disclaimer", "from_end": sh.get("end_disclaimer_s", 3.5)}],
                                                     "scenes": scenes}, indent=1, ensure_ascii=False) + "\n")
        (out / "description.txt").write_text(sh["description"].strip() + "\n\n" + spec["description_footer"].strip() + "\n")
        print(f"{out.name}: {len(sh['lines'])} lines, {len(track) / sr:.1f}s")


if __name__ == "__main__":
    main()
