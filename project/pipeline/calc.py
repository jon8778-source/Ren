"""Stage 1b: recalculate the assumptions table and flag any maths mismatch.

  python pipeline/calc.py episodes/<id>

Reads assumptions.csv, computes each character's totals (fixed costs, leaks, left over each
month, and how the surprise bill compares with savings), checks them against any "stated"
rows, and writes assumptions.json (used by the script check and the video) and
assumptions.md (the visible table). Exits with status 1 if anything doesn't add up.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def money(n):
    return f"${n:,.0f}"


def calculate(ep: Path):
    rows = list(csv.DictReader(open(ep / "assumptions.csv", newline="")))
    shared, people, stated = {}, defaultdict(lambda: defaultdict(list)), defaultdict(dict)
    meta = {}
    for r in rows:
        amt = float(r["amount"])
        if r["character"] == "all":
            shared[r["category"]] = amt
            continue
        c = r["character"]
        meta.setdefault(c, {"level": int(r["level"]), "status": set()})["status"].add(r["status"])
        if r["category"] == "stated":
            stated[c][r["item"]] = amt
        else:
            people[c][r["category"]].append({"item": r["item"], "amount": amt})

    bill = shared["bill"]
    out, problems = {}, []
    for c, cats in people.items():
        if len(cats["income"]) != 1:
            problems.append(f"{c}: needs exactly one income row")
            continue
        income = cats["income"][0]["amount"]
        fixed = sum(i["amount"] for i in cats["fixed"])
        leaks = sum(i["amount"] for i in cats["leak"])
        savings = sum(i["amount"] for i in cats["savings"])
        left = income - fixed - leaks
        p = {
            "level": meta[c]["level"],
            "status": "draft" if "draft" in meta[c]["status"] else "final",
            "income": income,
            "fixed_items": cats["fixed"],
            "fixed_total": fixed,
            "leak_items": cats["leak"],
            "leaks_total": leaks,
            "left_over": left,
            "savings": savings,
            "bill_covered_by_savings": min(bill, savings),
            "bill_shortfall": max(0.0, bill - savings),
        }
        if left < 0:
            problems.append(f"{c}: spends more than they earn ({money(left)} a month)")
        for key, val in stated[c].items():
            if key not in p:
                problems.append(f"{c}: stated '{key}' is not a calculated field")
            elif abs(p[key] - val) > 0.005:
                problems.append(f"{c}: stated {key} {money(val)} but the table adds up to {money(p[key])}")
        out[c] = p
    return {"bill": bill, "bill_due_days": shared.get("bill_due_days"), "characters": out}, problems


def table_md(data):
    lines = ["# Assumptions (illustrative examples, not real people)", "",
             f"Surprise bill: {money(data['bill'])}, due in {data['bill_due_days']:.0f} days.", "",
             "| Level | Character | Status | Take-home / month | Fixed costs | Leaks | Left over | Savings | Bill shortfall |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c, p in sorted(data["characters"].items(), key=lambda kv: kv[1]["level"]):
        lines.append(f"| {p['level']} | {c} | {p['status']} | {money(p['income'])} | {money(p['fixed_total'])} | "
                     f"{money(p['leaks_total'])} | {money(p['left_over'])} | {money(p['savings'])} | {money(p['bill_shortfall'])} |")
    for c, p in sorted(data["characters"].items(), key=lambda kv: kv[1]["level"]):
        lines += ["", f"## Level {p['level']}: {c} ({p['status']})", "", "| Item | Monthly |", "|---|---|"]
        lines += [f"| {i['item']} | {money(i['amount'])} |" for i in p["fixed_items"]]
        lines += [f"| **Fixed costs total** | **{money(p['fixed_total'])}** |"]
        lines += [f"| Leak: {i['item']} | {money(i['amount'])} |" for i in p["leak_items"]]
        lines += [f"| **Leaks total** | **{money(p['leaks_total'])}** |",
                  f"| **Left over** ({money(p['income'])} − {money(p['fixed_total'])} − {money(p['leaks_total'])}) | **{money(p['left_over'])}** |"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ep = Path(sys.argv[1])
    data, problems = calculate(ep)
    data["problems"] = problems
    (ep / "assumptions.json").write_text(json.dumps(data, indent=1) + "\n")
    (ep / "assumptions.md").write_text(table_md(data))
    for c, p in sorted(data["characters"].items(), key=lambda kv: kv[1]["level"]):
        print(f"L{p['level']} {c:8s} income {money(p['income']):>8s}  fixed {money(p['fixed_total']):>8s}  leaks {money(p['leaks_total']):>7s}"
              f"  left {money(p['left_over']):>7s}  savings {money(p['savings']):>7s}  [{p['status']}]")
    print("MATHS OK" if not problems else "MATHS MISMATCH:\n  " + "\n  ".join(problems))
    sys.exit(1 if problems else 0)
