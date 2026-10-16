"""Stage 6: assembly. Resolve the scene list against the voice timings and the assumptions
table, then render with Remotion and finish the file with FFmpeg.

  python pipeline/assemble.py episodes/<id> --out renders/pilot.mp4 [--browser-executable PATH]

Writes episodes/<id>/build/props.json (everything the video needs), copies the locked
character art and the voice track into remotion/public/, renders, then uses FFmpeg to add
faststart and confirm the streams.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import PROJECT, load_config, load_json, money, resolve_ref  # noqa: E402

CUT_LEAD = 0.12  # a scene starts this long before its line, so the picture changes as the word lands
REF = re.compile(r"\{([^}|]+)(?:\|(plain))?\}")


def fill(text, assumptions):
    def sub(m):
        v = resolve_ref(m[1], assumptions)
        return f"{v:,.0f}" if m[2] == "plain" else money(v)
    return REF.sub(sub, text)


def resolve_beat(beat, scene, lines):
    """A beat is seconds after the scene starts, or "@line" / "@line+0.5" for when that line is spoken."""
    if isinstance(beat, str) and beat.startswith("@"):
        m = re.fullmatch(r"@([a-z0-9]+)([+-][0-9.]+)?", beat)
        return round(lines[m[1]]["start"] + float(m[2] or 0) - scene["start"], 3)
    return beat


def resolve_graphic(g, assumptions, manifest):
    out = {}
    for k, v in g.items():
        if k == "items" and isinstance(v, str):
            who, key = v.split(".", 1)
            out[k] = [{"item": i["item"], "amount": money(i["amount"])} for i in assumptions["characters"][who][key]]
        elif k == "series" and isinstance(v, str):
            c = assumptions["characters"][v]
            out[k] = [[int(c["start_age"]), 0]] + sorted([int(key.split("_")[-1]), round(val)] for key, val in c.items() if key.startswith("balance_at_"))
        elif k == "rows":
            out[k] = [{**resolve_graphic({x: y for x, y in r.items() if x != "character"}, assumptions, manifest),
                       "src": f"characters/{r['character']}/{r.get('pose', 'neutral')}.png"} for r in v]
        elif k == "people":
            out[k] = [{"id": p, "name": manifest[p]["name"],
                       "src": f"characters/{p}/{g.get('highlight_pose', 'neutral') if p == g.get('highlight') else 'neutral'}.png"}
                      for p in v]
        elif isinstance(v, str):
            out[k] = fill(v, assumptions)
            whole = REF.fullmatch(v)
            if whole:
                out[f"{k}_value"] = resolve_ref(whole[1], assumptions)
        elif isinstance(v, list):
            out[k] = [resolve_graphic(x, assumptions, manifest) if isinstance(x, dict) else fill(x, assumptions) if isinstance(x, str) else x for x in v]
        else:
            out[k] = v
    return out


def build_props(ep: Path, config=None):
    cfg = load_config(config)
    assumptions = load_json(ep / "assumptions.json")
    timings = load_json(ep / "audio" / "timings.json")
    scenes_in = load_json(ep / "scenes.json")
    manifest = load_json(PROJECT / "characters" / "manifest.json")["characters"]
    lines = {l["id"]: l for l in timings["lines"]}
    duration = timings["duration"]

    scenes = []
    for i, s in enumerate(scenes_in["scenes"]):
        line = lines[s["line"]]
        start = 0.0 if i == 0 else max(0.0, line["start"] + s.get("offset", 0) - CUT_LEAD)
        scenes.append({**s, "start": round(start, 3), "line_start": line["start"], "line_end": line["end"]})
    for i, s in enumerate(scenes):
        s["end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else duration

    prev_char, prev_type = None, None
    for s in scenes:
        c = s.get("character")
        if c:
            if c["pose"] not in manifest[c["id"]]["poses"]:
                raise SystemExit(f"{s['id']}: pose '{c['pose']}' is not in the locked sheet for {c['id']}")
            same = prev_char and prev_char["id"] == c["id"]
            c.update({"src": f"characters/{c['id']}/{c['pose']}.png", "enter": not same,
                      "posePop": bool(same and prev_char["pose"] != c["pose"]),
                      "speaking": [round(s["line_start"] - s["start"], 3), round(s["line_end"] - s["start"], 3)] if c["id"] == "ren" else None})
        s["graphic"] = resolve_graphic(s["graphic"], assumptions, manifest)
        s["graphic"]["enter"] = s["graphic"]["type"] != prev_type
        prev_char, prev_type = c, s["graphic"]["type"]
        s.setdefault("camera", "push")
        s["beats"] = [resolve_beat(x, s, lines) for x in s.get("beats", [])]

    captions = []
    tl = timings["lines"]
    for i, l in enumerate(tl):
        end = tl[i + 1]["start"] if i + 1 < len(tl) else min(duration, l["end"] + 1.2)
        captions.append({"text": l["text"], "start": l["start"], "end": end})

    overlays = []
    for o in scenes_in.get("overlays", []):
        if "from_end" in o:
            overlays.append({"type": o["type"], "from": round(duration - o["from_end"], 3), "to": duration})
        else:
            overlays.append({"type": o["type"], "from": o["from"], "to": o["to"]})

    return {
        "config": cfg,
        "duration": duration,
        "audio": "audio/voice.mp3",
        "scenes": scenes,
        "captions": captions,
        "overlays": overlays,
        "characters": {k: {"name": v["name"], "poses": v["poses"]} for k, v in manifest.items()},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--out", required=True, help="Output path, relative to the episode folder")
    ap.add_argument("--browser-executable", default=None)
    ap.add_argument("--config", default=None, help="Layout config, e.g. config.vertical.json for 9:16 shorts")
    args = ap.parse_args()
    ep = Path(args.episode).resolve()
    props = build_props(ep, args.config)
    (ep / "build").mkdir(exist_ok=True)
    props_path = ep / "build" / "props.json"
    props_path.write_text(json.dumps(props, indent=1) + "\n")

    public = PROJECT / "remotion" / "public"
    shutil.rmtree(public / "characters", ignore_errors=True)
    shutil.copytree(PROJECT / "characters", public / "characters")
    (public / "audio").mkdir(exist_ok=True)
    shutil.copy(ep / "audio" / "voice.mp3", public / "audio" / "voice.mp3")

    out = ep / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = out.with_name(out.stem + ".raw.mp4")
    cmd = ["npx", "remotion", "render", "src/index.ts", "episode", str(raw), f"--props={props_path}", "--log=error"]
    if args.browser_executable:
        cmd.append(f"--browser-executable={args.browser_executable}")
    subprocess.run(cmd, cwd=PROJECT / "remotion", check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-c", "copy", "-movflags", "+faststart", str(out)], check=True)
    raw.unlink()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
