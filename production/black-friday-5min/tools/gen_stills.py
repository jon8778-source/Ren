import os, sys, time, json
from huggingface_hub import InferenceClient
MODEL = "black-forest-labs/FLUX.2-dev"
A = "/home/claude/v3/project/prototypes/coffee-minute-v3/assets/"
REF = {"home": A + "alex-home.png", "cafe": A + "alex-cafe.png", "office": A + "office.png"}
token = os.environ["HF_TOKEN"].strip().lstrip("<")
client = InferenceClient(provider="fal-ai", api_key=token)
KEEP = ("Alex must look exactly like the reference: same face and young adult age, the same medium sage green overshirt colour (not paler), cream t-shirt, black trousers. Use the input image as the exact art style and character reference. Keep Alex identical: same face, red-brown hair, sage green overshirt, "
        "cream t-shirt and black trousers. Same warm illustrated style, sage, cream and warm wood palette, soft daylight shading. "
        "Wide 16:9 landscape scene filling the whole frame. No text, no letters, no numbers, no logos, no brands, every screen, sign and tag is blank. ")
NOALEX = ("Use the input image as the exact art style reference: same warm illustrated style, sage, cream and warm wood palette. "
          "Wide 16:9 landscape scene filling the whole frame. No people. No text, no letters, no numbers, no logos, no brands, every screen, sign and tag is blank. ")
J = {
 "H1_shop_window": ("cafe", KEEP + "New scene: Alex walks along a sunny street past a shop window with large completely blank plain cream and sage banners with absolutely no writing on them, carrying one plain paper shopping bag, glancing at the window with mild curiosity."),
 "M1_old_coat": ("home", KEEP + "New scene: Alex in a bright hallway looks at a worn, slightly faded winter coat hanging on a wall hook, one hand on his chin, thoughtful."),
 "M2_gift": ("home", KEEP + "New scene: Alex stands at a wooden table holding a small wrapped gift box with a plain ribbon, smiling warmly as he thinks of a friend."),
 "M3_charger": ("home", KEEP + "New scene: Alex sits on a chair at a wooden table in the sunny kitchen, a small smartphone leaning against a mug on the table with its charging cable pulled tight at an awkward angle, Alex frowning and holding the cable with one hand. Phone is small and realistic in size."),
 "L1_writing_list": ("office", KEEP + "New scene: Alex sits at the home office desk writing on a paper notepad with a pen, calm and focused, a mug beside him, warm daylight."),
 "L2_coat_rack": ("cafe", KEEP + "New scene: Alex in a clothing shop holds up a winter coat on a hanger with a blank price tag, checking it carefully, rack of coats behind him."),
 "P1_laptop_night": ("office", KEEP + "New scene: night time. Medium shot, Alex fills about a third of the frame, sitting at the home office desk, face lit softly by the laptop glow, small desk lamp on, dark blue window behind, leaning forward with wide eyes."),
 "P2_phone_ping": ("office", NOALEX + "New scene: night time. A smartphone with a blank glowing screen buzzing on the wooden home office desk beside a closed notebook and a desk lamp, dark blue window behind."),
 "P3_cart_items": ("home", NOALEX + "New scene: on a wooden kitchen counter, three plain unbranded products with blank labels: a compact air fryer, a pair of white wireless earbuds in an open case, and a plain mystery gift box tied with ribbon. Sage kitchen behind."),
 "P4_alex_tempted": ("office", KEEP + "New scene: night time. Close, waist-up shot of Alex at the desk, face lit by laptop glow, eyebrows raised, finger hovering near the trackpad, tempted, desk lamp glowing warm."),
 "C1_calculator": ("home", KEEP + "New scene: Alex sits on a chair at a wooden table, the whole table visible in front of him, holding a small calculator with a blank display in one hand and a pen in the other, a notepad on the table, thoughtful and slightly sceptical."),
 "C2_price_history": ("home", KEEP + "New scene: Alex sits on a chair at a wooden table in front of an open laptop, leaning slightly forward and squinting at the blank screen with curiosity, one hand on the trackpad, a mug beside the laptop. Seated normally, both feet under the table."),
 "W1_closing_laptop": ("office", KEEP + "New scene: night time. Alex gently closes the laptop lid at the home office desk with a calm relieved smile, desk lamp on, dark blue window behind. Medium shot."),
 "W2_morning_kitchen": ("home", KEEP + "New scene: morning. Alex stands in the sunny kitchen holding a mug of coffee, looking out of the window with a calm, clear-headed expression."),
 "W3_old_pan": ("home", KEEP + "New scene: morning. Alex at the kitchen hob smiling with a plain frying pan in his hand, a well-used pan, content, thinking it works fine."),
 "W4_old_earbuds": ("office", KEEP + "New scene: daytime. Alex at the desk holding up a worn old pair of wired earbuds with a tangled cable, mildly disappointed, nodding to himself."),
 "T1_sofa_bags": ("home", KEEP + "New scene: afternoon. Alex relaxes on a cream sofa in a living room, a few plain paper shopping bags neatly beside him, calm and satisfied."),
 "E1_phone_transfer": ("home", KEEP + "New scene: Alex at the sunny kitchen counter looking at his phone with a pleased smile, thumb about to tap, relaxed and confident."),
 "E2_piggy_jar": ("home", NOALEX + "New scene: on the sunny kitchen counter, a small ceramic piggy bank in cream and sage next to a glass jar of coins and a few folded notes, warm morning light."),

}
only = sys.argv[1:]
rep = {}
for k, (r, p) in J.items():
    if only and k not in only: continue
    for a in range(1, 4):
        try:
            img = client.image_to_image(REF[r], prompt=p, model=MODEL)
            img.save(f"out/{k}.png"); rep[k] = f"ok {img.size}"; break
        except Exception as e:
            rep[k] = f"error {type(e).__name__}: {str(e)[:200]}"; time.sleep(3)
    print(k, rep[k], flush=True)
