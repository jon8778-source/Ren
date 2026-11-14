"""Calculates every figure in the script from data/assumptions.csv and checks it. Run: python3 tools/check_numbers.py"""
import csv, sys, pathlib
A = {r["id"]: float(r["value"]) for r in csv.DictReader(open(pathlib.Path(__file__).parent.parent / "data/assumptions.csv"))}
def sale(full, off): return full * (100 - off) / 100
coat, gift, charger = (sale(A["coat_full"], A["coat_off"]), sale(A["gift_full"], A["gift_off"]), sale(A["charger_full"], A["charger_off"]))
fry, ear, bun = (sale(A["airfryer_full"], A["airfryer_off"]), sale(A["earbuds_was"], A["earbuds_off"]), sale(A["bundle_full"], A["bundle_off"]))
list_sale = coat + gift + charger
list_full = A["coat_full"] + A["gift_full"] + A["charger_full"]
impulse = fry + ear + bun
badge_saved = (A["airfryer_full"] - fry) + (A["earbuds_was"] - ear) + (A["bundle_full"] - bun)
all_in = list_sale + impulse
rule_path = list_sale + ear
checks = {
 "coat sale 90": coat == 90, "gift sale 48": gift == 48, "charger sale 20": charger == 20,
 "list at sale 158": list_sale == 158, "list full 205": list_full == 205, "list saving 47": list_full - list_sale == 47,
 "air fryer 48": fry == 48, "earbuds 105": ear == 105, "bundle 30": bun == 30,
 "impulse items 183": impulse == 183, "badge says saved 107": badge_saved == 107,
 "impulse Alex 341": all_in == 341, "over budget 41": all_in - A["budget"] == 41,
 "rule Alex 263": rule_path == 263, "under budget 37": A["budget"] - rule_path == 37,
 "difference 78": all_in - rule_path == 78, "difference = air fryer + bundle": (all_in - rule_path) == fry + bun,
 "earbuds real saving 10 (not 45)": A["earbuds_usual"] - ear == 10 and A["earbuds_was"] - ear == 45,
}
bad = [k for k, v in checks.items() if not v]
for k, v in checks.items(): print(("OK   " if v else "FAIL ") + k)
print("MATHS OK" if not bad else "MATHS FAILED: " + ", ".join(bad)); sys.exit(1 if bad else 0)
