"""Shot plan generator and checker for the Black Friday long-form (DRAFT, before script approval and before any voice).
Durations are ESTIMATES at 0.40 s/word (150 wpm, repo planning rate); real timing comes from the Qwen narration after script approval.
Checks: phrases tile the script exactly; caps (Ren 5.5 s, story still 2.5 s, graphic 3.5 s); Ren return gaps; consecutive same-kind/same-clip runs; still reuse.
  python3 tools/shot_plan.py   -> plan/SHOT_PLAN.md, plan/shot_plan.csv
Kinds: R = genuine Ren library clip on an approved plate with a code-drawn card on the right; S = story still (generated TEMPORARY Alex still S## or approved coffee-v3 plate S*);
G = code-drawn graphic / prop close-up (over a blurred approved plate). opt = optional line (FTC), only if the primary source is verified.
"""
import csv, re
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent; WPS = 0.40; CAP = {"R": 5.5, "S": 2.5, "G": 3.5}
# (kind, asset, phrase, on-screen / action)   asset: Ren clip name, still id (01..19 or ALEX-CAFE / ALEX-HOME = approved coffee-v3 plates), or 'code'
P = {1: [
 ("R", "ren_wave_hello", "Black Friday has a clever trick.", "Ren waves hello at his desk plate; start disclaimer chip"),
 ("S", "01_H1", "It can make spending", "Alex leaves the shop with two bags (still, slow push)"),
 ("G", "code", "feel like saving.", "Price tag whose 'Spending' label flips to 'Saving' (code)"),
 ("R", "ren_point_right", "Today, Alex heads into the sales with a three hundred dollar budget", "Ren points right at a '$300 budget' tag"),
 ("G", "code", "and two very different plans.", "Two-path card: Impulse Alex / Rule-following Alex"),
 ("R", "ren_present_palm_left (mirrored, inspected)", "One plan ends at three hundred and forty-one dollars.", "Ren presents the card: '$341'"),
 ("G", "code", "The other ends at two hundred and sixty-three.", "Card '$263' replaces '$341'"),
 ("G", "code", "Same shop, same sales, seventy-eight dollars apart.", "Both totals with a '$78 apart' bracket; 'Example figures'"),
 ("R", "ren_count_fingers", "Along the way, you'll get five simple rules for your own Black Friday,", "Ren counts; '5 rules' chips (mouth window to be scanned)"),
 ("G", "code", "and none of them say never buy anything.", "'Never buy anything' struck through (code)"),
 ("R", "ren_nod_yes", "Let's see what happens.", "Ren nods"),
], 2: [
 ("S", "ALEX-CAFE", "Meet Alex. Alex isn't reckless.", "Approved coffee-v3 art: Alex taps to pay (introduces Alex in approved art)"),
 ("S", "ALEX-HOME", "Alex has a holiday budget", "Approved coffee-v3 art: Alex in the kitchen"),
 ("G", "code", "of three hundred dollars,", "'$300 holiday budget' tag"),
 ("R", "ren_idle_listen", "and it has to cover a few things that genuinely need buying.", "Ren listens; 'Needs' list card appears (empty lines)"),
 ("S", "02_M1", "A winter coat.", "Alex studies the worn coat"),
 ("S", "03_M2", "A gift for a friend.", "Alex holds a gift"),
 ("S", "04_M3", "And a phone charger", "Alex untangles the cable"),
 ("R", "ren_shrug", "that only works if you hold it at just the right angle.", "Ren shrugs; charger icon card (code)"),
 ("R", "ren_nod_yes", "Waiting for Black Friday is a perfectly sensible plan.", "Ren nods; calendar card with Black Friday circled"),
 ("G", "code", "Sales can be real.", "'Sales can be real' badge"),
 ("G", "code", "The trouble usually isn't the sale.", "Price tag with a green tick"),
 ("R", "ren_thinking", "It's what the sale does to our decisions.", "Ren thinks; 'decisions' arrow card"),
], 3: [
 ("R", "ren_clipboard_tick (mouth-closed window from 5.4 s)", "Rule one: write the list before the sales start.", "Ren with 'RULE 1: Write the list' tag"),
 ("S", "05_L1", "Alex's list has three items.", "Alex writes the list"),
 ("R", "ren_point_right", "The coat is one hundred and twenty dollars,", "Ren points at a $120 coat tag"),
 ("S", "06_L2", "and it's twenty-five percent off,", "Alex holds the coat; tag $120 overlay"),
 ("R", "ren_open_arms", "so ninety. The gift is sixty dollars, twenty percent off, so forty-eight.", "Ren with tags $120 -> $90 and $60 -> $48"),
 ("G", "code", "The charger is twenty-five dollars,", "Charger tag $25"),
 ("G", "code", "twenty percent off, so twenty.", "Charger tag $25 -> $20"),
 ("R", "ren_present_palm_left (mirrored, inspected)", "Altogether that's one hundred and fifty-eight dollars, instead of two hundred and five.", "Sum card $158 vs $205"),
 ("G", "code", "A real saving of forty-seven dollars", "'$47 saved' badge"),
 ("G", "code", "on things Alex was already going to buy.", "List ticks (coat, gift, charger)"),
 ("R", "ren_idle_calm", "That's Black Friday working the way it should.", "Ren calm; green tick"),
], 4: [
 ("S", "07_P1", "Then Alex opens a shop's website.", "Alex at the laptop at night"),
 ("G", "code", "A countdown clock is ticking.", "Countdown clock 02:59:59 ticking (code)"),
 ("S", "08_P4", "A badge says only three left.", "Alex tempted; ONLY 3 LEFT badge pops (code)"),
 ("S", "10_P3", "And Alex's cart starts getting longer.", "Cart props; item counter ticks up (code)"),
 ("G", "code", "An air fryer, eighty dollars, forty percent off.", "Tag $80 -> $48"),
 ("R", "ren_shake_no", "Fancy earbuds, listed at a hundred and fifty, thirty percent off.", "Ren (return) beside tag $150 -> $105"),
 ("G", "code", "And a mystery bundle, sixty dollars, half price.", "Tag $60 -> $30"),
 ("G", "code", "The website cheerfully announces that Alex has saved", "Banner 'You saved' (code)"),
 ("G", "code", "one hundred and seven dollars.", "'$107' (32 + 45 + 30 shown as a sum)"),
 ("S", "09_P2", "Then an email pings.", "Phone buzzes on the desk"),
 ("G", "code", "Sale ends at midnight.", "Email pop-up (code)"),
 ("R", "ren_thinking", "Alex feels that little jolt of get it before it's gone.", "Ren thinks; 'get it before it's gone' card"),
 ("S", "07_P1 (callback)", "It's a very human feeling,", "Callback: Alex at the laptop"),
 ("R", "ren_point_right", "and it's the one clocks and badges tend to tap into.", "Ren points at clock + badge icons"),
 ("G", "code", "Not every timer is fake,", "OPTIONAL: 'Real or fake?' card", True),
 ("R", "ren_present_palm_left (mirrored, inspected)", "but the FTC has criticized the fake ones,", "OPTIONAL: only with a verified primary source; source chip on screen", True),
 ("R", "ren_nod_yes", "so a ticking clock isn't proof of a deal.", "OPTIONAL: continues the FTC line", True),
 ("R", "ren_open_arms", "And here's the thing. Alex hasn't saved one hundred and seven dollars.", "Ren; '$107 saved?' struck through"),
 ("R", "ren_present_palm_left (mirrored, inspected)", "Alex is about to spend one hundred and eighty-three.", "$183 sum card: 48 + 105 + 30"),
], 5: [
 ("G", "code", "Rule two: do the math.", "'RULE 2' tag on a calculator"),
 ("S", "11_C1", "A discount isn't a saving.", "Alex with calculator and notepad"),
 ("G", "code", "It's just a smaller bill.", "Bill shrinks but is still a bill"),
 ("G", "code", "Add the list to the cart", "$158 + $183 sum"),
 ("R", "ren_point_right", "and Alex is at three hundred and forty-one dollars,", "Ren points at '$341'"),
 ("G", "code", "which is forty-one dollars over budget.", "Budget bar $300 with '$41 over' in red"),
 ("R", "ren_thinking", "Rule three: check what it normally costs.", "RULE 3 tag"),
 ("R", "ren_hold_phone", "Those earbuds say they were a hundred and fifty dollars.", "Ren holds phone; was-price $150 tag"),
 ("S", "12_C2", "Alex looks at the price history,", "Alex at laptop"),
 ("R", "ren_point_right", "and they've sat at a hundred and fifteen for months.", "Price-history line chart (code) at $115"),
 ("G", "code", "At a hundred and five,", "$105 sale price on the chart"),
 ("R", "ren_shake_no", "the real saving is ten dollars, not forty-five.", "'$10, not $45' card"),
 ("G", "code", "That's still fine if Alex truly needs them,", "Green tick"),
 ("R", "ren_shrug", "but it's not the bargain the sticker shouted about.", "Ren shrugs; sticker card"),
], 6: [
 ("R", "ren_point_right", "Rule four: let it sit for twenty-four hours.", "RULE 4 tag, 24h clock"),
 ("G", "code", "Alex buys the three things on the list,", "Checkout ticks (coat, gift, charger)"),
 ("G", "code", "then leaves the other three in the cart", "Cart with air fryer, earbuds, bundle"),
 ("S", "13_W1", "and closes the laptop.", "Laptop closes; night"),
 ("S", "14_W2", "The next morning,", "Morning kitchen, mug"),
 ("G", "code", "Alex asks one question about each.", "Question card"),
 ("R", "ren_thinking", "Do I need this, or did the timer need me to buy it?", "Question card on the right"),
 ("G", "code", "The air fryer?", "Air fryer card"),
 ("S", "15_W3", "Alex already has a pan", "Old pan on the hob"),
 ("G", "code", "that works fine.", "Air fryer crossed out"),
 ("G", "code", "The mystery bundle?", "Bundle card"),
 ("G", "code", "Alex can't even remember what's in it.", "Bundle card with '?'; crossed out"),
 ("G", "code", "The earbuds?", "Earbuds card"),
 ("S", "16_W4", "The old pair really did die", "Alex with the dead wired pair"),
 ("G", "code", "last week. So those stay in.", "Earbuds tick"),
 ("G", "code", "The other two go.", "Two items removed from the cart"),
 ("R", "ren_nod_yes", "Notice that waiting doesn't mean saying no.", "Ren nods"),
 ("R", "ren_present_palm_left (mirrored, inspected)", "It just means the answer has to survive a night's sleep.", "Moon-to-sun card"),
 ("R", "ren_open_arms", "If Alex still wants the earbuds, and has room in the budget,", "Budget bar with room"),
 ("G", "code", "that's a good purchase made on purpose.", "'On purpose' badge"),
], 7: [
 ("R", "ren_present_palm_left (mirrored, inspected)", "Here's the final tally.", "Comparison card slides in"),
 ("G", "code", "Impulse Alex spends three hundred and forty-one dollars,", "Left column $341"),
 ("G", "code", "forty-one over budget.", "'$41 over' in red"),
 ("R", "ren_point_right", "Rule-following Alex spends the one hundred and fifty-eight on the list,", "Right column $158"),
 ("G", "code", "plus one hundred and five for the earbuds.", "+ $105"),
 ("G", "code", "Two hundred and sixty-three dollars.", "$263"),
 ("R", "ren_idle_calm", "That's thirty-seven under budget,", "'$37 under' in green"),
 ("G", "code", "and seventy-eight dollars less than the impulse cart.", "'$78 less' bracket = 48 + 30"),
 ("R", "ren_shrug", "Notice Alex still bought something extra. This isn't about never treating yourself.", "Ren shrugs"),
 ("S", "17_T1", "That thirty-seven dollars isn't a prize", "Alex relaxes on the sofa"),
 ("G", "code", "for being boring.", "Crossed-out 'prize' badge"),
 ("R", "ren_thinking", "It's room. Room for the next surprise bill,", "Surprise-bill envelope icon"),
 ("R", "ren_nod_yes", "or for a treat Alex plans for, rather than one the countdown picked.", "Planned treat vs countdown treat"),
], 8: [
 ("R", "ren_point_right", "Rule five: move the thirty-seven dollars you didn't spend into savings straight away,", "RULE 5 tag, $37 arrow to savings"),
 ("S", "18_E1", "before it quietly disappears.", "Alex makes a transfer on the phone"),
 ("S", "19_E2", "Quick recap. List first.", "Piggy bank on the kitchen counter"),
 ("R", "ren_count_fingers", "Do the math. Check the usual price. Wait twenty-four hours.", "Recap list builds (mouth window to be scanned)"),
 ("G", "code", "And move what's left into savings.", "Recap line 5"),
 ("R", "ren_thumbs_up (mouth-closed window from 4.9 s)", "Check out the Money Leak Audit Workbook in the description.", "End card in code; end disclaimer held 2 s+"),
 ("G", "code", "See you next time.", "End card"),
]}
def norm(s): return re.findall(r"[a-z0-9'’-]+", s.lower().replace("’", "'"))
def sections():
    t = (HERE / "script/script.md").read_text(); out = {}
    for s in re.split(r"^## ", t, flags=re.M)[1:]:
        h, body = s.split("\n", 1); n = int(h[0]); body = re.sub(r"^(Visual|Values):.*\n", "", body, flags=re.M)
        body = re.sub(r"\[OPTIONAL, NEEDS VERIFY: (.*?)\]", r"\1", body, flags=re.S); out[n] = body.strip()
    return out
def main():
    S = sections(); rows = []; problems = []; t0 = 0.0; k = 0
    for n in sorted(P):
        ph = " ".join(x[2] for x in P[n]); a, b = norm(ph), norm(S[n])
        if a != b:
            import difflib; d = [x for x in difflib.ndiff(b, a) if x[0] in "+-"][:12]; problems.append(f"section {n}: phrases do not tile the script ({len(a)} vs {len(b)} words): {d}")
        for x in P[n]:
            kind, asset, phrase, act = x[:4]; opt = len(x) > 4; k += 1; w = len(norm(phrase)); d = w * WPS; rows.append(dict(n=k, section=n, t=round(t0, 1), words=w, est_s=round(d, 1), kind=kind, asset=asset, phrase=phrase, action=act, optional=opt))
            t0 += d
            if d > CAP[kind] + 1e-9: problems.append(f"shot {k} ({kind}) est {d:.1f}s > cap {CAP[kind]}s: {phrase[:50]}")
    # Ren returns (gaps between the start of consecutive Ren shots, excluding optional)
    ren = [r for r in rows if r["kind"] == "R" and not r["optional"]]; gaps = [round(b["t"] - a["t"], 1) for a, b in zip(ren, ren[1:])]
    still_ids = [r["asset"].split()[0] for r in rows if r["kind"] == "S"]; reuse = sorted({s for s in still_ids if still_ids.count(s) > 1})
    runs = []; cur = 1
    for a, b in zip(rows, rows[1:]):
        if a["kind"] == b["kind"] == "G": cur += 1
        else:
            if cur >= 3: runs.append(cur)
            cur = 1
    total = sum(r["est_s"] for r in rows if not r["optional"]); kinds = {kd: round(sum(r["est_s"] for r in rows if r["kind"] == kd and not r["optional"]), 1) for kd in "RSG"}
    with open(HERE / "plan/shot_plan.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    L = ["# Black Friday long-form: shot plan (DRAFT, for the script gate; estimates only)", "",
         f"{len(rows)} shots ({sum(1 for r in rows if r['optional'])} optional FTC shots). Estimated length {total:.0f} s ({total / 60:.2f} min) at 0.40 s/word without the optional line; the real length comes from the Qwen narration after approval. Ren {kinds['R']:.0f} s, story stills {kinds['S']:.0f} s, graphics {kinds['G']:.0f} s.", "",
         f"Longest estimated Ren gap (start to start of consecutive Ren shots): {max(gaps):.0f} s; gaps over 45 s: {[g for g in gaps if g > 45]}. Same-kind graphic runs of 3+: {len(runs)}. Stills reused as deliberate callbacks: {reuse}.", "",
         "| # | Sec | Est start | Words | Est s | Kind | Asset | Narration | On screen / action |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows: L.append(f"| {r['n']} | {r['section']} | {int(r['t'] // 60)}:{int(r['t'] % 60):02d} | {r['words']} | {r['est_s']} | {r['kind']}{' (opt)' if r['optional'] else ''} | {r['asset']} | {r['phrase']} | {r['action']} |")
    (HERE / "plan/SHOT_PLAN.md").write_text("\n".join(L) + "\n")
    print(len(rows), "shots;", round(total), "s est; kinds", kinds, "; Ren gaps", gaps, "; reuse", reuse, "; G runs>=3:", len(runs))
    for p in problems: print("PROBLEM:", p)
main()
