"""Render the episode's YouTube thumbnail options (1280x720 PNG) with Remotion.

  python3 pipeline/thumbnails.py episodes/<id> [--browser-executable PATH]

Amounts come from assumptions.json. Writes renders/thumbnail-a.png, -b.png, -c.png.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import PROJECT, load_config, load_json, money  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("episode")
ap.add_argument("--browser-executable", default=None)
args = ap.parse_args()
ep = Path(args.episode).resolve()
a = load_json(ep / "assumptions.json")
chars = sorted(a["characters"].items(), key=lambda kv: kv[1]["level"])
manifest = load_json(PROJECT / "characters" / "manifest.json")["characters"]
k = lambda n: f"${n / 1000:,.1f}".rstrip("0").rstrip(".") + "K"  # 2400 -> $2.4K, 22000 -> $22K
base = {"theme": load_config()["theme"] | {"ink": "#13233F"}, "bill": money(a["bill"]),
        "low": k(chars[0][1]["income"]), "high": k(chars[-1][1]["income"]),
        "people": [{"id": c, "name": manifest.get(c, {}).get("name", c.capitalize())} for c, _ in chars]}
base["theme"] = {key: v for key, v in base["theme"].items() if v.startswith("#")}
(ep / "build").mkdir(exist_ok=True)
(ep / "renders").mkdir(exist_ok=True)
# An episode can define its own options in thumbnails.json: {"variants": "def", "text": {key: "{ref}" ...}}
spec = ep / "thumbnails.json"
variants = "abc"
if spec.exists():
    sys.path.insert(0, str(Path(__file__).parent))
    from assemble import fill  # noqa: E402
    t = load_json(spec)
    variants = t["variants"]
    base["text"] = {k: fill(v, a) for k, v in t.get("text", {}).items()}
for i, v in enumerate(variants):
    name = "abc"[i]
    props = ep / "build" / f"thumb-{name}.json"
    props.write_text(json.dumps(base | {"variant": v}))
    cmd = ["npx", "remotion", "still", "src/index.ts", "thumbnail", str(ep / "renders" / f"thumbnail-{name}.png"), f"--props={props}", "--log=error"]
    if args.browser_executable:
        cmd.append(f"--browser-executable={args.browser_executable}")
    subprocess.run(cmd, cwd=PROJECT / "remotion", check=True)
    print(f"Wrote renders/thumbnail-{name}.png")
