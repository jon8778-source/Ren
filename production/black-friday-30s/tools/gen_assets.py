import os, sys, json, time
from huggingface_hub import InferenceClient
MODEL="black-forest-labs/FLUX.2-dev"
token=os.environ["HF_TOKEN"].strip().lstrip("<")
client=InferenceClient(provider="fal-ai", api_key=token)
STYLE=("Absolutely no writing, lettering or symbols anywhere, every sign and bag is blank. Match the art style of the input image exactly: clean dark ink outlines, flat soft colours, restrained shading, "
       "navy, cream, warm wood and soft gold accents. No text, no letters, no numbers, no logos, no people, no characters.")
ENV="Fill the entire 9:16 portrait frame edge to edge with the illustrated scene, no white borders. "
PROP="Single object centred on a solid plain white background filling the entire frame, no patterns, gradients or tints at the edges. "
JOBS={
 "E1_shop_street":("refs/porch_portrait.png", ENV+"Re-draw this as a daytime street scene with a shop front: a large shop window with completely blank plain navy banners with no writing at all, a blank red sale sign above the door, plain blank paper shopping bags with no printing or marks, clear empty pavement in the lower third. "+STYLE),
 "E2_kitchen_table":("refs/office_portrait.png", ENV+"Re-draw this as a cosy home kitchen seen from a slightly high angle: a clean empty wooden table filling the lower half of the frame with a window and soft daylight behind, a mug and a plant at the far edge, large empty space on the table for props. "+STYLE),
 "E3_porch_parcels":("refs/porch_portrait.png", ENV+"Keep this porch and front door, and add a tall messy pile of plain cardboard delivery parcels and plain blank paper shopping bags with no printing, marks or symbols stacked on the porch floor beside the door and doormat. "+STYLE),
 "E4_living_room_morning":("refs/office_portrait.png", ENV+"Re-draw this as a calm living room in soft morning light: a sofa with cushions, a coffee table, a window with warm sunrise light, a floor lamp, clear empty floor space on the left. "+STYLE),
 "P1_piggy_bank":("refs/prop_portrait.png", PROP+"Replace the folder with a single happy smiling piggy bank in navy and gold with a coin slot and a few gold coins beside it. "+STYLE),
 "P2_hourglass":("refs/prop_portrait.png", PROP+"Replace the folder with a single tall hourglass with a wooden frame and gold sand running through it. "+STYLE),
}
only=sys.argv[1:]
rep={}
for k,(ref,prompt) in JOBS.items():
    if only and k not in only: continue
    for a in range(1,4):
        try:
            img=client.image_to_image(ref,prompt=prompt,model=MODEL)
            img.save(f"images/{k}.png"); rep[k]=f"ok {img.size}"; break
        except Exception as e:
            rep[k]=f"error {type(e).__name__}: {str(e)[:250]}"; time.sleep(3)
    print(k,rep[k],flush=True)
