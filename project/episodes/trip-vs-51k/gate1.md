# Gate 1: "The $3,000 Trip vs $51,000 at 70: Which Is Worth More?"

Status: Gate 1 (asset inventory, missing items, storyboard, voiceover timing). Nothing is built or rendered.

## 0. Decisions needed before anything is built
The brief overrides several of the owner's standing rules (CLAUDE.md, DECISIONS.md) and the decision of
2026-10-18 to shelve the puppet rig. Each item needs an answer.

| # | Brief says | Standing rule / current state | Options |
|---|---|---|---|
| D1 | Use "the existing Ren puppet rig, pose library and face set"; Ren walks between props | The rig was rejected ("many errors") and moved to branch `lab/animated-ren`, never to be merged. **No pose library exists**: only hand-set joint angles from the 15 s test. Rules ban walking, bob and sway in episodes. | (a) Make this video with the locked Ren busts in the normal pipeline: no walking, no held props (props sit beside him). (b) Make it on the lab branch with the rig, accepting its known problems (front-facing march, hip bulge, no forward point...), as a second, bigger rig test. (c) First fix the rig on the lab branch (new part sheets, pose library), then make this video. |
| D2 | Voice "clear, warm, friendly male", about 140 words a minute | Ren's locked voice: Kokoro am_michael + am_eric 50/50, speed 0.93, about 168 words a minute | (a) Ren's voice as is. (b) Ren's voice slowed to about 0.80 (changes how he sounds; you'd need to listen). (c) A different voice (breaks "one voice"). |
| D3 | Script fills 6:00 | The script is **653 words**: about **4:40 at 140 wpm**, **3:53 at Ren's pace**. Every section is shorter than its time window (table in section 3). | (a) Accept about 4:40 (or 3:53). (b) Add about 190 words (you write them, or I draft them for your OK). (c) Stretch with long pauses (not recommended: dead air, and QC fails silences over 1 s). |
| D4 | Background music, 18 dB under the voice | No music (standing rule). No music file attached. | Keep no music, or send a licensed track and confirm the rule change for this video. |
| D5 | Poppins font; navy #1F2A44, green #2E9E5B, coral #E8574A, gold #F2B33D | Fredoka only; navy #13233F, green #1E9E5A, red #E23D3D, gold #F5B82E | Use the brief's font and colours for this video only, or keep the channel's. |
| D6 | CTA: "free 50/30/20 workbook", card "Free budgeting workbook · link in bio" | Never say "free" in the video; standing CTA "Check out the Money Leak Audit Workbook in the description" (you approved that swap last episode). The card says "bio", the script says "description". | Keep the standing CTA, or confirm a 50/30/20 workbook exists and drop "free". |
| D7 | Real book: Die With Zero by Bill Perkins ("memory dividend", "time buckets", "only works if you won't run out") | Real-world claims need `[VERIFY]` plus a source, verified by you, or get cut. | You confirm these attributions (and the book cover card stays a generic design), or I reword them to "an idea some planners use". |
| D8 | "Lots of people plan to leave money to their kids" / "Money tends to go up as we get older. Health and energy tend to go down." | Unsourced "many people" claims get cut (QC flags them). | Reword: "If you plan to leave money to your kids..." and "For most of us, money..." → "Money can grow as you get older, while energy..." (I'd draft; your OK). |
| D9 | "$51,432" | 3,000 x 1.07^42 = **51,432.77**. Normal rounding gives **$51,433**; $51,432 drops the cents. | Show $51,433 (rounded), or keep $51,432 and treat it as "rounded down". The narration says "about fifty-one thousand", which is correct either way. |
| D10 | Disclaimer only when $3,000 / $51,432 / $10,000 are on screen | "Educational only, not financial advice" at the start and the end of every video | Use both: the brief's note on money screens, plus the standing start/end disclaimer. |
| D11 | Normalise to -14 LUFS | The pipeline uses -16 LUFS | Fine to use -14 for this video (YouTube's own target); say if not. |

Maths checks (code): 3,000 x 1.07^42 = 51,432.77 ✔ (28 to 70 is 42 years ✔). Kids born when you're 28 and you live to 88: they inherit at 60 ✔.

## 1. Asset inventory (what exists now)
**Ren, locked busts** (`project/characters/ren/`, used in every episode): neutral, talking, pointing, thinking, shocked,
worried, waving, thumbs-up. Chest-up, no separate hands, so no held props and no walking.

**Ren, puppet rig** (branch `lab/animated-ren`, rejected test):
- Body: torso, head, upper arms, forearms, thighs, shins, shoes (left and right), glasses, nose.
- Hands (left and right): relaxed, open palm, holding (C-shape), point (sideways), outward point, thumbs up, fist.
- Eyes: neutral, closed, happy (^^), wide, surprised, angry, sleepy.
- Brows: neutral, wide, surprised, sleepy.
- Mouths: closed, slightly open, wide, O, smile, wince.
- Renderer: forward kinematics, slot swaps, joint caps. Test animation: front-facing march, wave, hold, point,
  thumbs up, wince, blink, breathing, volume-based lip sync.

**Episode graphics** (Remotion, channel style): statement, lineup, question, list, step, stamp card, envelope,
spend card, icon cards, joy chart (money vs feeling lines), energy chart (money up, energy down, from the $2M
episode), growth chart, compare bars, result cards, CTA card, week of treats, side-by-side, houses.

**Your attached images** (from the shorts asset pack; the zip itself wasn't attached): backpack, sandcastle and skis icons,
EXPIRES stamp; the portrait cards ($3,000 / $51,432 / "You can't buy back 28" / "Save on purpose. Spend on purpose." /
"Try this tonight" / decade boxes / "Fund these first" / workbook pill / disclaimer pill). The icons can be reused as
given; the cards will be rebuilt as landscape overlays, as you asked.

## 2. Missing items
**Poses (rig), if D1 is (b) or (c).** I won't invent these; please supply them:
1. Eyes looking left and right (for "looks between them"). Only straight-ahead eyes exist.
2. Shrug (raised shoulders, open palms up). There are no shoulder parts and no palms-up hand.
3. A side-view or three-quarter body set (legs, feet, torso) for a real walk. The front-facing march skates.
4. A forward-pointing hand (at the viewer or into the scene). Only sideways pointing exists.
5. A two-hand hold for the sheet of paper (a pinch or thumb-over hand). The C-shape hold only grips round things.
6. Rhubarb mouth shapes that don't exist: F (pucker, "oo/w"), G (f/v, teeth on lip), H (l, tongue up), and
   closed-lip A (m/b/p; the current closed mouth is a smile line). Mapping without them: A, X → closed;
   B → slightly open; C, H → O or slightly open; D → wide; E, F → O; G → slightly open.

**Poses (busts), if D1 is (a):** a shrug and a "holding something" pose aren't in the 8 locked busts. Without them,
props appear beside Ren on cards, and "looks between them" becomes Ren thinking.

**Props to draw in code** (flat style, the channel's line weight): plane ticket, beach postcard, stack of cash, rocking
chair, hourglass, sheet of paper with 5 boxes, gift box, house key, piggy bank, camping tent, generic book card
("Die With Zero", plain cover), sparkle, cooking-class icon (chef hat, from the last episode), savings jar, "Enough"
target line, checklist ticks, beach and dinner-table icons, kids and friends as photo-frame silhouettes.

**Tooling:** Rhubarb Lip Sync (downloadable here; checked). Music track (D4).

## 3. Voiceover timing map (estimated until the voice is recorded)
| Section | Window | Words | At 140 wpm | At Ren's pace (~168 wpm) | Short by (140 wpm) |
|---|---|---|---|---|---|
| Hook | 0:00-0:30 | 64 | 27 s | 23 s | 3 s |
| Memory dividend | 0:30-1:20 | 91 | 39 s | 33 s | 11 s |
| The catch | 1:20-2:20 | 100 | 43 s | 36 s | 17 s |
| Time buckets | 2:20-3:25 | 92 | 39 s | 33 s | 26 s |
| Give while it matters | 3:25-4:20 | 98 | 42 s | 35 s | 13 s |
| Guardrails | 4:20-5:20 | 117 | 50 s | 42 s | 10 s |
| Close | 5:20-6:00 | 91 | 39 s | 33 s | 1 s |
| **Total** | 6:00 | **653** | **4:40** | **3:53** | **1:20** |

Once the voice is recorded, every line gets an exact start and end (timings.json), and the storyboard beats below
are tied to those words rather than to clock times.

## 4. Storyboard (beats tied to the words; times at 140 wpm)
| Scene | Time | Ren | Visuals and overlays |
|---|---|---|---|
| 1. Hook | 0:00-0:27 | Centre between the halves; looks left on "take the trip", right on "invest it"; shrug on "not quite" | Split screen. Left: plane ticket, "$3,000 trip at 28". Right: cash stack, "$51,432 at 70", counting up from 3,000 on "becomes about fifty-one thousand". Money disclaimer bottom corner. Slow push-in on "something that money can't buy back". |
| 2. Memory dividend | 0:27-1:06 | Beside the book card, then gestures along the timeline | Generic "Die With Zero - Bill Perkins" card. Overlay "The memory dividend". Beach postcard at age 28 on a 40-year timeline; sparkles pop out at "tell the story", "a song", "remember when"; a counter of sparkles grows with "the dividend lasts forty years". |
| 3. The catch | 1:06-1:49 | Points at the chart; winces as the lines cross | $51,432 card returns with a rocking chair and hourglass. Three small "can buy" icons (cruise, bills, gift). Chart: "Money" rises, "Energy & health" falls with age (marked Illustrative). Overlay "Some experiences expire". Kids and friends photo frames fade on "moved away", "grown up". |
| 4. Time buckets | 1:49-2:28 | Holds the sheet of paper, then steps aside | Five landscape boxes (30s-70s). Cooking class in every box; backpack, skis, sandcastle in the early boxes, then faded with EXPIRES in the 60s and 70s. Overlay "Fund these first". |
| 5. Give while it matters | 2:28-3:10 | Points at each end of the timeline | Timeline 28 to 88. $10,000 arrives at 30 (house key) vs at 60 (gift box). Overlay "Same money. Different impact." Money disclaimer. |
| 6. Guardrails | 3:10-4:00 | Counts on his hand, thumbs up at "permission" | Checklist ticks: Emergency fund / No high-interest debt / Retirement on track. Savings chart with an "Enough" target line. "Life fund" jar filling each month (piggy bank as the jar). Cheap memories: tent, beach, dinner table. |
| 7. Close | 4:00-4:40 | Back in the centre; smile, held 0.5 s after the last word | The hook split screen returns; the trip side glows on "the trip might be the better investment". Overlay "Save on purpose. Spend on purpose." CTA card (wording per D6). "Educational only, not financial advice." |

Thumbnail (Gate 3): Option 1, Ren with a plane ticket and a cash stack, "$3,000?" and "$51,000?" in big text.
With the busts, the ticket and cash sit beside Ren; with the rig, he holds them.
