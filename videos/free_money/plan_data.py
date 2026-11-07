"""Gate 1 shot plan for "I Said No to Free Money for 3 Years" (v3 rules, 1280x720, 24 fps).

  python3 videos/free_money/plan_data.py        # validates, writes shot_plan.csv and PLAN_TABLE.md

Each beat = (narration phrase, type, assets, ren pose, on-screen text (all code-built), motion).
The phrases of a scene must tile scripts/Ren_Free_Money_Script.md exactly (checked). Times are ESTIMATES
from word counts until the real narration is measured; Gate 2 recomputes them from Whisper word times.
Caps (v3): Ren 5.5 s, story still 2.5 s, graphic 3.5 s; the checker plans with a 0.1-0.3 s margin.
"""
import csv, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACE = 2.55                                   # words per second (measured on the earlier short)
CAP = {"ren": 5.5, "story": 2.5, "graphic": 3.5}
PLAN_MAX = {"ren": 5.3, "story": 2.4, "graphic": 3.4}   # planning margin for estimate error

LIB = "library/"
RS = {"R1": "ren_approved/Ren_1_neutral.jpg", "R2": "ren_approved/Ren_2_hand_on_chest_talking.jpg",
      "R3": "ren_approved/Ren_3_thinking_bust.jpg", "R4": "ren_approved/Ren_4_pointing.jpg",
      "FT": "ren_approved/Ren_extra_thinking_full_body.jpg", "FP": "ren_approved/Ren_full_body_presenting.jpg",
      "FS": "ren_approved/Ren_full_body_standing.jpg", "FW": "ren_approved/Ren_full_body_waving.jpg"}
CLIP = {"PPL": "assets/ren_library/ren_present_palm_left.mp4", "NOD": "assets/ren_library/ren_nod_yes.mp4",
        "SNO": "assets/ren_library/ren_shake_no.mp4", "THK": "assets/ren_library/ren_thinking.mp4"}
SUP = {"DEV": "supporting_assets/characters/Dev_pay_stub.png", "PRIYA": "supporting_assets/characters/Priya_hiking_style.png",
       "GARY": "supporting_assets/characters/Uncle_Gary.png", "FOLDER": "supporting_assets/props/HR_folder_page6_prop.png",
       "PORCH": "supporting_assets/backgrounds/Porch_background_16x9.png",
       "OFFICE": "supporting_assets/backgrounds/Office_background_16x9.png",
       "LOT": "supporting_assets/backgrounds/Office_parking_lot_car_16x9.png"}

# (phrase, type, assets, ren, text, motion)
S = {}
S["S1"] = [
 ("I was 28 when Dev", "story", "PORCH", "", "", "slow push-in on the empty porch"),
 ("held up my pay stub", "story", "PORCH+DEV+FS", "FS", "", "Dev slides in beside Ren; slight push"),
 ("and asked me one question.", "story", "DEV(crop)", "", "", "push-in on Dev holding the stub"),
 ('"Who\'s keeping the difference?"', "ren", "R4", "R4", 'quote card: "Who\'s keeping the difference?" (right of Ren, clear of face)', "R4 on the office wall, slow push-in"),
 ("I didn't know what he meant.", "ren", "R1", "R1", "", "worried fallback: slow push-in"),
 ("Then he pointed at one line,", "story", "PORCH+DEV(stub crop)", "", "", "push-in on the pay stub"),
 ("and my stomach dropped.", "graphic", "DEV(stub crop)", "", 'glowing line: "Employer match: 2%"', "line glows and pulses once"),
 ("For three years, I'd been turning down free money.", "ren", "CLIP:SNO", "SNO", "", "shake_no clip, office wall"),
 ("And the worst part?", "ren", "R3", "R3", "", "slow push-in"),
 ("I did it to impress people I barely knew.", "ren", "R2", "R2", "", "hand-on-chest still, slow drift"),
 ("Let me take you back.", "ren", "FP", "FP", "", "wide presenting still; page-flip into age 25 on the last words"),
]
S["S2"] = [
 ("Twenty-five. First real job.", "story", "OFFICE+FS", "FS", 'lower-third: "Age 25"', "wide office, Ren full body, slow push"),
 ("Forty-four thousand a year,", "graphic", "OFFICE(blurred)", "", 'card line 1: "Age 25: $44,000 salary"', "card appears in sync with the words"),
 ("and I felt like I'd made it.", "ren", "CLIP:NOD", "NOD", "", "nod_yes clip, office wall"),
 ("So I did what felt right", "ren", "R3", "R3", "", "slow push-in"),
 ("and leased a brand-new car,", "story", "LOT", "", "", "push-in on the blue car"),
 ("four hundred and eighty-nine dollars a month.", "graphic", "LOT(blurred)", "", 'card line 2: "Lease: $489/month"', "second line joins the card"),
 ("Not because I needed it.", "ren", "CLIP:SNO", "SNO", "", "shake_no clip"),
 ("Because I wanted everyone", "story", "LOT+FS", "FS", "", "Ren full body beside the car, slow push"),
 ("in that parking lot to think I was doing great.", "ren", "CLIP:THK", "THK", "", "thinking clip"),
 ("On day one, HR", "story", "OFFICE", "", 'tag: "Day one"', "empty office plate, slow push (Ren is off screen for variety)"),
 ("gave me a folder.", "story", "FOLDER", "", "", "folder slides in from the right"),
 ("Somewhere on page six", "story", "FOLDER(crop)", "", "", "slow push-in to the PAGE 6 tab"),
 ("it said the company would match every dollar", "graphic", "none", "", 'diagram: "You $1" matched by "Company $1"', "coins move across"),
 ("I put into my retirement plan,", "story", "FOLDER(crop)", "", "", "push-in to the piggy-bank panel"),
 ("up to four percent of my salary.", "graphic", "FOLDER(crop, blurred)", "", 'card line 3: "Page 6: We match 100% up to 4%"', "third line completes the card"),
 ("I never got to page six.", "ren", "R1", "R1", "", "worried fallback: slow push-in"),
 ("I picked two percent,", "graphic", "none", "", 'chip "2%" beside a faded "4%"', "chip pops in"),
 ("because two sounded responsible,", "ren", "CLIP:NOD", "NOD", "", "nod_yes clip"),
 ("and the lease sounded urgent.", "story", "LOT", "", "", "push-in on the car"),
]
S["S3"] = [
 ("Here's the thing about a match.", "ren", "R4", "R4", "", "pointing bust, slow drift"),
 ("If I put in four percent,", "graphic", "none", "", 'jar "You" fills to 4%', "jar fills"),
 ("they put in four percent,", "graphic", "none", "", 'jar "Company" fills to 4%', "second jar fills"),
 ("dollar for dollar. I put in two,", "graphic", "none", "", 'jars show "$1 = $1"; "You" resets to 2%', "jar level drops to 2%"),
 ("so they put in two.", "graphic", "none", "", '"Company" jar matches at 2%', "jar fills to 2%"),
 ("The other two percent?", "graphic", "none", "", 'ghost jar fades in: "Never paid"', "dashed ghost jar"),
 ("It wasn't saved for later.", "ren", "R3", "R3", "", "thinking bust, slow push-in"),
 ("It just never got paid.", "graphic", "none", "", 'ghost jar stays empty: "Never paid"', "jar drains and fades"),
 ("That was eight hundred and eighty dollars", "graphic", "none", "", 'counter "Age 25" | "Missed: $880"', "number counts into place"),
 ("the first year. Then I got small raises,", "graphic", "none", "", 'year counter 25 to 26', "counter ticks"),
 ("forty-six thousand, forty-eight,", "graphic", "none", "", '"$46,000", "$48,000"; "Missed: $880, $920, $960" builds', "salary line steps up; counter 26, 27"),
 ("and every year I left the same two percent,", "ren", "R1", "R1", "", "slow push-in"),
 ("and every year the ghost money", "graphic", "none", "", "ghost jars stack up", "ghost jars stack"),
 ("got bigger. Meanwhile,", "graphic", "none", "", '"3 years = about $2,760" (fixed total)', "total settles; calendar flips separately"),
 ("I made that lease payment on time,", "ren", "CLIP:NOD", "NOD", "", "nod_yes clip"),
 ("every month, with pride.", "ren", "R2", "R2", "", "hand-on-chest still"),
 ("Four hundred eighty-nine dollars to look successful,", "graphic", "none", "", '"$489/month" beside "look successful"', "two cards slide in"),
 ("while skipping about seventy-seven a month", "graphic", "none", "", '"about $77/month" ghost jar', "ghost jar glows"),
 ("that would have actually made me successful.", "ren", "FP", "FP", "", "wide presenting still, palm left"),
]
S["S4"] = [
 ("Back on that porch,", "story", "PORCH", "", "", "slow push-in"),
 ("Dev asked me three questions.", "story", "PORCH+DEV+FS", "FS", "", "Dev and Ren two-shot"),
 ('"What does this line mean?', "graphic", "PORCH(blurred)", "", 'question card 1: "What does this line mean?"', "card slides in"),
 ("What would it say", "graphic", "PORCH(blurred)", "", 'question card 2: "What would it say if you\'d read the folder?"', "card slides in"),
 ("if you'd read the folder?", "story", "FOLDER(crop)", "", "", "push-in on the folder"),
 ("And who's keeping the difference?\"", "graphic", "PORCH(blurred)", "", 'question card 3: "Who\'s keeping the difference?"', "card slides in; highlighted"),
 ("The line said two percent.", "story", "DEV(stub crop)", "", 'line: "Employer match: 2%"', "push-in on the stub"),
 ("It should have said four.", "story", "DEV(stub crop)", "", 'line changes to "Employer match: 4%"', "line swaps, glows"),
 ("And the difference?", "ren", "R4", "R4", "", "pointing bust"),
 ("The company keeps it.", "graphic", "none", "", '"Company keeps: 2%"', "ghost jar flows into the Company jar"),
 ("Not because they're evil.", "ren", "CLIP:SNO", "SNO", "", "shake_no clip"),
 ("That's just how matches work.", "ren", "R3", "R3", "", "thinking bust"),
 ("If you don't claim it,", "graphic", "none", "", '"Unclaimed" jar', "jar sits still"),
 ("it stays with them.", "graphic", "none", "", '"Stays with the company"', "jar slides to Company"),
 ("I went home, opened the app", "graphic", "none", "", "phone with a settings screen", "phone slides in"),
 ("on my phone, and changed two to four.", "graphic", "none", "", 'toggle: "2%" to "4%"', "toggle slides, number swaps"),
 ("It took ninety seconds.", "graphic", "none", "", 'badge: "90 seconds"', "badge pops"),
 ("Ninety seconds, three years late.", "ren", "R1", "R1", "", "rueful slow push-in"),
]
S["S5"] = [
 ("That night, I did the painful maths.", "ren", "R3", "R3", "", "thinking bust, slow push-in"),
 ("If that two thousand seven hundred and sixty", "graphic", "none", "", '"$2,760" number sticker', "number appears"),
 ("had been invested and grown at,", "graphic", "none", "", "coin pile starts on a 30-year timeline", "coins drop in"),
 ("say, seven percent a year,", "graphic", "none", "", 'tag: "hypothetical 7%/yr"', "tag appears"),
 ("which is a hypothetical, not a promise,", "graphic", "none", "", 'sticker: "Not a promise."', "sticker pops"),
 ("in thirty years", "graphic", "none", "", "timeline reaches year 30", "timeline runs"),
 ("it could be roughly twenty-one thousand dollars.", "graphic", "none", "", 'sticker: "$2,760 at a hypothetical 7%/yr for 30 years = about $21,000. Not a promise."', "coin pile grows; sticker settles"),
 ("That's the real cost of a lease-shaped decision.", "ren", "FP", "FP", "", "wide presenting still"),
 ("Not the payment. The opportunity.", "ren", "R4", "R4", "", "pointing bust"),
 ("But here's the twist.", "ren", "CLIP:PPL", "PPL", "", "present_palm_left clip (not mirrored)"),
 ("The day I fixed it,", "ren", "R1", "R1", "", "slow push-in"),
 ("my take-home dropped", "graphic", "none", "", "pay stub card appears", "card slides in"),
 ("by about thirty-two dollars a paycheck,", "graphic", "none", "", 'card: "Take-home change: only about $32 per paycheck (pre-tax)"', "number highlights"),
 ("because those contributions come out before income tax.", "graphic", "none", "", 'diagram: "Pre-tax contribution" arrow before "Income tax"', "arrow moves"),
 ("And I never missed it.", "ren", "R2", "R2", "", "hand-on-chest still"),
 ("I honestly couldn't tell you", "ren", "R3", "R3", "", "thinking bust"),
 ("what that thirty-two dollars used to buy me.", "graphic", "none", "", '"$32" coins fading', "coins fade out"),
 ("Probably a car wash,", "story", "LOT", "", "", "push-in on the car"),
 ("for a car", "story", "LOT", "", "", "wide on the lot"),
 ("I didn't even own.", "story", "LOT", "", "", "close on the car"),
]
S["S6"] = [
 ("Today, same car,", "story", "LOT", "", 'tag: "8 years later"', "plain plate (grade not approved), slow push"),
 ("eight years older.", "story", "LOT", "", "", "closer push on the car"),
 ("I earn around a hundred thousand a year,", "graphic", "none", "", 'card: "Today: about $100,000/yr"', "card appears"),
 ("and I always take the full match,", "ren", "R2", "R2", "", "hand-on-chest still"),
 ("plus more on top.", "graphic", "none", "", '"full match + more"', "bar extends"),
 ("My cousin Priya,", "story", "OFFICE+PRIYA", "", "", "Priya slides in"),
 ("the one who earns two hundred thousand", "graphic", "OFFICE(blurred)+PRIYA", "", 'card: "Priya: about $200,000/yr"', "card appears beside her"),
 ("and dresses like she's off", "story", "OFFICE+PRIYA", "", "", "slow push"),
 ("to hike a mountain,", "story", "PRIYA(crop)", "", "", "push-in on the backpack"),
 ("maxes hers out every year.", "graphic", "OFFICE(blurred)+PRIYA", "", '"Priya maxes out every year"', "bar fills"),
 ("Uncle Gary told me", "story", "OFFICE+GARY", "", "", "Gary slides in"),
 ('his retirement plan is "sell the boat."', "graphic", "OFFICE(blurred)+GARY", "", 'quote: "sell the boat"', "quote card"),
 ("Everyone's different. But the match works the same", "ren", "CLIP:PPL", "PPL", "", "present_palm_left clip"),
 ("for everyone who's offered one.", "ren", "R1", "R1", "", "slow push-in"),
 ("It's the first money you're owed.", "ren", "R4", "R4", "", "pointing bust"),
 ("So here's what I check now,", "ren", "FP", "FP", "", "wide presenting still"),
 ("and what I wish I'd checked at 25.", "ren", "R3", "R3", "", "thinking bust"),
 ("One, your match formula.", "graphic", "none", "", "checklist item 1: Match formula", "item draws in"),
 ("It's in the plan documents, not the vibes.", "ren", "R1", "R1", 'tick next to "Match formula" in the checklist corner', "slow push-in"),
 ("Two, your vesting schedule,", "graphic", "none", "", "checklist item 2: Vesting schedule", "item draws in"),
 ("because some companies make you stay", "graphic", "none", "", "years bar", "bar starts"),
 ("a few years before", "graphic", "none", "", "years bar", "bar fills"),
 ("the match is fully yours.", "graphic", "none", "", '"Fully yours" lock opens', "lock opens"),
 ("Three, next year's limit.", "graphic", "none", "", "checklist item 3: 2027 limit", "item draws in"),
 ("For 2027, the actuarial firm Milliman projects", "graphic", "none", "", 'card: "2027 limit: Milliman projection"', "card appears"),
 ("twenty-five thousand five hundred dollars,", "graphic", "none", "", '"$25,500"', "number appears"),
 ("up from twenty-four thousand five hundred.", "graphic", "none", "", '"up from $24,500"', "number appears"),
 ("The IRS hadn't confirmed it at the end of October,", "ren", "FT", "FT", 'tag: "IRS: not yet confirmed (end of October)"', "extra thinking full-body still, slow push"),
 ("so check the official number.", "ren", "R4", "R4", "", "pointing bust"),
 ("You don't have to max it out.", "ren", "CLIP:SNO", "SNO", "", "shake_no clip"),
 ("You just don't want to skip the free part.", "ren", "R2", "R2", "", "hand-on-chest still"),
]
S["S7"] = [
 ("If I could go back,", "ren", "R3", "R3", "", "thinking bust"),
 ("I wouldn't lecture him about coffee.", "ren", "R1", "R1", "", "slow push-in"),
 ("I'd just hand him that folder,", "story", "OFFICE+FS+FOLDER", "FS", "", "folder slides toward Ren"),
 ("open to page six.", "story", "FOLDER(crop)", "", "", "push-in on page 6"),
 ("Before you cut a single thing,", "ren", "R4", "R4", "", "pointing bust"),
 ("collect what you're already owed.", "ren", "CLIP:PPL", "PPL", "", "present_palm_left clip"),
 ("The match. The HSA money.", "graphic", "none", "", 'list: "The match", "The HSA money"', "items tick in"),
 ("The stuff in the folder.", "graphic", "FOLDER(crop, blurred)", "", 'list: "The stuff in the folder"', "item ticks in"),
 ("Twenty-five-year-old me wanted to look rich.", "story", "OFFICE+FS", "FS", 'lower-third: "Age 25"', "wide office"),
 ("Twenty-eight-year-old me just wanted to stop missing free money.", "ren", "R2", "R2", "", "hand-on-chest still"),
 ("Honestly? The second guy was richer.", "ren", "CLIP:NOD", "NOD", "", "nod_yes clip"),
 ("Next week: the month three bills hit me at once,", "ren", "FP", "FP", "", 'teaser card: "Next week: the month three bills hit me at once"'),
 ("and why, for the first time, I didn't panic.", "ren", "FW", "FW", 'small disclaimer: "Educational content only, not financial advice"', "full-body wave sign-off; hold"),
]

def scene_text():
    parts = re.split(r"\*\*\[(S\d+): [^\]]*\]\*\*", (ROOT / "scripts" / "Ren_Free_Money_Script.md").read_text())
    return {parts[i]: " ".join(parts[i + 1].split()) for i in range(1, len(parts), 2)}

def main():
    T = scene_text(); problems = []; rows = []; n = 0; clock = 0.0; last = None
    for sid in S:
        if " ".join(b[0] for b in S[sid]) != T[sid]:
            problems.append(f"{sid}: phrases do not tile the script exactly")
        for ph, typ, assets, ren, text, motion in S[sid]:
            n += 1; w = len(ph.split()); d = w / PACE
            if d > PLAN_MAX[typ]: problems.append(f"{sid} #{n} {typ} est {d:.1f}s > plan max {PLAN_MAX[typ]}: {ph}")
            if ren and ren == last: problems.append(f"{sid} #{n} repeats Ren pose {ren} in consecutive shots")
            last = ren or None if typ != "graphic" and not ren else ren
            if not ren and typ == "graphic": last = None
            if not ren and typ == "story": last = None
            rows.append(dict(shot=f"{n:03d}", scene=sid, est_start=round(clock, 1), est_end=round(clock + d, 1), est_dur=round(d, 1),
                             narration=ph, type=typ, assets=assets, ren_pose=ren, onscreen_text=text, motion=motion))
            clock += d
    with open(HERE / "shot_plan.csv", "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    from collections import Counter
    c = Counter(r["type"] for r in rows); pose = Counter(r["ren_pose"] for r in rows if r["ren_pose"])
    print(f"{len(rows)} shots, est {clock/60:.1f} min | types {dict(c)} | poses {dict(pose)}")
    for p in problems: print("PROBLEM:", p)
    with open(HERE / "PLAN_TABLE.md", "w") as f:
        f.write("| # | Scene | Est. time (s) | Narration | Type | Asset | Ren pose | On-screen text (code-built) | Motion |\n|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| {r['shot']} | {r['scene']} | {r['est_start']:.0f}-{r['est_end']:.0f} | {r['narration'].replace('|','/')} | {r['type']} | {r['assets']} | {r['ren_pose'] or ''} | {r['onscreen_text'].replace('|','/')} | {r['motion']} |\n")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
