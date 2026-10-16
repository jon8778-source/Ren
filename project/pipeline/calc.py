"""Stage 1b: recalculate the assumptions table and flag any maths mismatch.

  python pipeline/calc.py episodes/<id>

Reads assumptions.csv, computes each character's totals (fixed costs, leaks, left over each
month, and how the surprise bill compares with savings), checks them against any "stated"
rows, checks every story claim in claims.txt against the numbers, and writes assumptions.json (used by the script check and the video) and
assumptions.md (the visible table). Exits with status 1 if anything doesn't add up.
"""
import csv
import json
import math
import sys
from types import SimpleNamespace
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
        elif r["category"] == "value":
            people[c]["_values"].append({"item": r["item"], "amount": amt})
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
            "savings_after_bill": max(0.0, savings - bill),
            "fixed_share_pct": round(100 * fixed / income),
        }
        for v in cats["_values"]:
            p[v["item"]] = v["amount"]
        if {"save_monthly", "rate", "start_age", "retire_age"} <= p.keys():
            p.update(project(p))
        if left < 0:
            problems.append(f"{c}: spends more than they earn ({money(left)} a month)")
        for key, val in stated[c].items():
            if key not in p:
                problems.append(f"{c}: stated '{key}' is not a calculated field")
            elif abs(p[key] - val) > 0.005:
                problems.append(f"{c}: stated {key} {money(val)} but the table adds up to {money(p[key])}")
        out[c] = p
    level1 = next((p for p in out.values() if p["level"] == 1), None)
    for p in out.values():
        if level1:
            p["income_multiple_vs_level1"] = math.floor(p["income"] / level1["income"])
    data = {"bill": bill, "bill_due_days": shared.get("bill_due_days"), "characters": out}
    problems += check_claims(ep, data)
    return data, problems


def project(p):
    """Invested balance by age, compounded yearly in today's dollars: save_monthly x 12 is added at the end
    of each working year; after retire_age, withdraw_monthly x 12 comes out at the end of each year."""
    bal, out = 0.0, {}
    for age in range(int(p["start_age"]), int(p.get("end_age", p["retire_age"]))):
        working = age < p["retire_age"]
        bal = bal * (1 + p["rate"]) + (p["save_monthly"] * 12 if working else -p.get("withdraw_monthly", 0) * 12)
        bal = max(bal, 0.0)
        out[f"balance_at_{age + 1}"] = round(bal, 2)
    return out


def check_claims(ep: Path, data):
    """claims.txt: one `python expression | what the script says` per line, e.g.
    `richard.leaks_total > sam.income | Richard's leaks are bigger than Sam's whole paycheck`."""
    path = ep / "claims.txt"
    if not path.exists():
        return []
    ns = {c: SimpleNamespace(**p) for c, p in data["characters"].items()}
    ns.update(bill=data["bill"], min=min, max=max, round=round)
    bad = []
    for row in path.read_text().splitlines():
        if not row.strip() or row.lstrip().startswith("#"):
            continue
        expr, _, text = row.partition("|")
        try:
            ok = eval(expr, {"__builtins__": {}}, ns)
        except Exception as e:  # a typo in claims.txt must not pass silently
            bad.append(f"claim '{text.strip()}' could not be checked: {e}")
            continue
        if not ok:
            bad.append(f"claim is false: {text.strip()} ({expr.strip()})")
    return bad


def table_md(data):
    lines = ["# Assumptions (illustrative examples, not real people)", "",
             f"Shared figure (`bill`): {money(data['bill'])}" + (f", due in {data['bill_due_days']:.0f} days." if data.get("bill_due_days") else "."), "",
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
    proj = {c: p for c, p in data["characters"].items() if "balance_at_" + str(int(p.get("retire_age", 0))) in p}
    if proj:
        lines += ["", "## Investment projection (example: compounded yearly at the given rate, today's dollars)", "",
                  "| Character | Saves / month | Rate | Withdraws / month after retiring | At 35 | At 45 | At 65 | At 85 |", "|---|---|---|---|---|---|---|---|"]
        for c, p in proj.items():
            lines.append(f"| {c} | {money(p['save_monthly'])} | {p['rate']:.0%} | {money(p.get('withdraw_monthly', 0))} | " +
                         " | ".join(money(p.get(f"balance_at_{a}", 0)) for a in (35, 45, 65, 85)) + " |")
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
