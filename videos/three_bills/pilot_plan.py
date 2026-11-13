"""Shot plan for the ~60 s Three Bills pilot (script v2 paragraphs 0-9). Each shot names the exact script words it covers; phrases must tile the pilot narration in order.
Types: REN = genuine library clip (Ren left in his sage office, graphics right); MAYA = approved Maya pose cut-outs on an approved plate (grounded with ren_stage);
PROP = prop/graphic close-up (<= 3.5 s); the plan marks what actually moves in each shot.
"""
SHOTS = [
 # id, type, phrase, setting, what moves
 ("S01", "REN", "Three bills. Thirty days.", "sage office", "Ren (ren_present_palm_left, mirrored) presents to the right; '3 bills / 30 days' card"),
 ("S02", "MAYA", "First, Maya's car broke down.", "parking lot + car (approved plate)", "slow push-in; Maya neutral -> surprised; car-key prop spins and stops"),
 ("S03", "PROP", "Then came an urgent dental bill.", "parking lot, blurred", "invoice slides in; URGENT stamp lands"),
 ("S04", "MAYA", "And just when she thought the month couldn't get worse,", "porch (approved plate)", "Maya worried-phone -> neutral shift; slow push"),
 ("S05", "PROP", "a pipe leaked beneath her kitchen sink.", "sage office, blurred", "pipe prop drips (drop falls and splashes)"),
 ("S06", "REN", "The total? Two thousand two hundred dollars.", "sage office", "Ren (ren_shrug); finished equation card appears at once"),
 ("S07", "MAYA", "Eighteen months earlier, one unexpected bill had pushed her into debt.", "porch", "'18 months earlier' tag; Maya worried phone; credit card slides in"),
 ("S08", "MAYA", "This time, she handled all three.", "porch", "Maya relief pose (hugging phone), settle"),
 ("S09", "MAYA", "But when Maya opened her savings app afterward, she didn't feel proud.", "office plate", "Maya worried-phone; savings phone inset with the balance falling"),
 ("S10", "MAYA", "She saw how much her balance had fallen and thought, I've gone backwards.", "office plate", "thought bubble; balance phone"),
 ("S11", "REN", "Here's why she hadn't.", "sage office", "Ren (ren_point_right); 'Not backwards' chip"),
 ("S12", "PROP", "To understand that feeling, go back a year and a half.", "porch, blurred", "calendar flips to 18 months earlier"),
 ("S13", "MAYA", "Maya was doing what so many budgets require: making the rent, groceries and gas stretch until payday.", "office plate", "Maya neutral; three small chips (rent, groceries, gas) in turn"),
 ("S14", "PROP", "There wasn't much left between deposits. Her savings balance was eighty dollars.", "office, blurred", "phone inset: $80"),
 ("S15", "MAYA", "Then a six-hundred-dollar car repair landed.", "parking lot + car", "Maya surprised-envelope; '$600' repair tag"),
 ("S16", "MAYA", "She couldn't just make six hundred dollars appear. So she put the repair on a credit card,", "parking lot", "Maya worried; credit card slides in"),
 ("S17", "PROP", "postponed a dentist visit, and spent the next few months trying to catch up.", "office, blurred", "calendar page: Dentist pushed back"),
 ("S18", "REN", "The hardest part wasn't the repair itself. It was watching one surprise turn into a chain of other decisions.", "sage office", "Ren (ren_thinking); chain builds: repair, card, postponed dentist"),
]
