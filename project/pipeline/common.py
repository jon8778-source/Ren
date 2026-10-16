"""Shared helpers: paths, config, script parsing, spoken-number parsing, assumption lookups."""
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent


def load_config(path=None):
    return json.loads(Path(path or PROJECT / "config.json").read_text())


def load_json(path):
    return json.loads(Path(path).read_text())


LINE_RE = re.compile(r"^\[(?P<id>[a-z0-9]+)\]\s+(?P<text>.*?)\s*(?:\{(?P<refs>[^}]*)\})?\s*$")


def parse_script(ep: Path):
    """Return [{id, section, text, refs}] from script.md (comments and headings skipped)."""
    lines, section = [], None
    raw = re.sub(r"<!--.*?-->", "", (ep / "script.md").read_text(), flags=re.S)
    for row in raw.splitlines():
        row = row.strip()
        if row.startswith("## "):
            section = row[3:].strip()
        elif row.startswith("["):
            m = LINE_RE.match(row)
            if not m:
                raise ValueError(f"Can't parse script line: {row}")
            refs = [r.strip() for r in (m["refs"] or "").split(",") if r.strip()]
            lines.append({"id": m["id"], "section": section, "text": m["text"], "refs": refs})
    ids = [l["id"] for l in lines]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate line ids in script.md")
    return lines


UNITS = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen".split())}
TENS = {w: 10 * i for i, w in enumerate("_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()) if w != "_"}
SCALES = {"hundred": 100, "thousand": 1000, "million": 1_000_000}


def spoken_numbers(text):
    """Find numbers written as words ("two thousand four hundred", "twenty-four") and return them."""
    words = re.findall(r"[a-z]+", text.lower().replace("-", " "))
    found, total, current, active = [], 0, 0, False
    for i, w in enumerate(words):
        if w in UNITS or w in TENS:
            current += UNITS.get(w, 0) + TENS.get(w, 0)
            active = True
        elif w in SCALES and active:
            if w == "hundred":
                current *= 100
            else:
                total += current * SCALES[w]
                current = 0
        elif w == "and" and active and i + 1 < len(words) and (words[i + 1] in UNITS or words[i + 1] in TENS):
            continue
        else:
            if active:
                found.append(total + current)
            total, current, active = 0, 0, False
    if active:
        found.append(total + current)
    if re.search(r"\d", text):
        found.append("DIGITS")  # numbers must be written out for the voice
    return found


def resolve_ref(ref, assumptions):
    """sam.income -> value from assumptions.json; =24 -> 24; bill -> top-level value."""
    if ref.startswith("="):
        return float(ref[1:])
    if "." in ref:
        who, key = ref.split(".", 1)
        if ":" in key:  # nina.leak:forgotten_subscriptions -> that line item
            cat, slug = key.split(":", 1)
            items = assumptions["characters"][who][f"{cat}_items"]
            return float(next(i["amount"] for i in items if slugify(i["item"]) == slug))
        return float(assumptions["characters"][who][key])
    return float(assumptions[ref])


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def money(n):
    return f"${n:,.0f}"
