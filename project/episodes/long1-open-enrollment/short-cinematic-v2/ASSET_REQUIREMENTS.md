# Health insurance Short v2 — asset-first report

## Prototype assets: available, no major new artwork needed

- Approved v3 office: `../../../prototypes/coffee-minute-v3/assets/office.png`.
  Exact approved original,1672×941. Reframed full-bleed, no blue surround.
- Ren: `../../../../assets/ren_library/ren_nod_yes.mp4` and
  `ren_thinking.mp4`. Actual 1280×720,10.005s sources inspected at
  0.5/1.5/2.5/3.5s. Nod is a restrained acknowledgement; thinking raises a hand
  to his chin. Closed narrator-led mouth, no mirrored gesture or clip loop.
  Two distinct clips/intervals, not repeating one stock presenter cycle.
- Native-resolution matte: reuse `../render.py:matte`, including enclosed-white
  preservation and edge-colour repair. Decode native before crop/final resize.
- Existing Fredoka, shared assumptions/calculations and source word timings.
- Original Short MP4 found at
  `../portrait-short-01/deliverables/Ren_Health_Plan_Portrait_1min.mp4`.
  This is the requested original under its local capitalisation/name. Its SHA is
  locked in voice-configuration.json; it is preserved without modification.
- British Qwen narration recovered from that Short. Existing clone configuration,
  reference WAV/transcript and prior successful generation manifest are present;
  both reference hashes match. No new synthesis is needed for visual revision.

## New reusable code props (authorized by this request)

Laptop/email, keep-current-plan button, cursor/click, four renewal confirmations,
wood desktop, insurance papers, paper shadows, comparison/detail mark.
Draw labels/numbers in code, using $2,520 and $840 annual **premiums**, derived
from the existing shared assumptions. These are physical screen/paper objects
in the story, not generic floating infographics. No new character design.

## Missing poses / deliberate staging

There is no separately verified seated typing/clicking animation among the
inspected approved clips. Use the approved upper-body cutout behind the foreground
laptop/desk, with the computer cursor performing the click. Do not invent arm or
hand articulation. A restrained nod and later hand-to-chin reaction are real
approved clip actions, not newly generated lip sync or a seated-body redesign.

## Later full-film requirements — not used/rendered in this prototype

1. **Medical environment:** a matching empty clinic/pharmacy room for the
   coverage/cost section. First assess existing approved artwork; otherwise brief:
   “Full-bleed 9:16 clinic consultation environment in Ren v3 flat illustrated
   style, cream/sage furniture, restrained navy outlines, no people or embedded
   labels; clear foreground surface for a code-drawn bill.” References required:
   approved office original for palette/linework plus approved medical prop sheet
   `../full/assets/medical-props.png`. New major environment must be presented to
   Jon and explicitly approved before use. No asset generated or substituted here.
2. If actual medical-plan documents require a deductible amount, the verified
   assumptions currently do **not** state one. Show a labelled deductible field
   without a fabricated value; existing verified OOP limits are $4,000/$6,500.
3. Any new major scene or pose must be listed and approved. This prototype does
   not approve uncreated artwork. Current renderer deliberately supports only
   its 360-frame prototype; the full Short is gated and not rendered.

## Revision 02 — requested by Jon

Jon reported Ren was too small and explicitly requested generating a physical
laptop prop for the clip. One laptop illustration was generated from the approved
office style reference. Original: assets/laptop-generated.png (1448×1086 RGBA).
No Ren artwork/reference was regenerated. This prop is authorized for the revised
review prototype; final visual approval remains pending. The renderer composites
an opaque, code-labelled display over the generated blank screen, retaining the
illustrated chassis, real key layout, hinge and trackpad. No baked-in AI text.

Ren's composition size changes400×800→540×1080 (35% larger), at(5,400) in both
office shots. Native1280×720 decode/matte is retained, followed by one1.5× resize
of the character crop. No artificial sharpening or AI character upscale. Actual
face/edge detail and desk-relative scale will be inspected at100% and phone size.
Previous prototype is preserved; Revision02 is a separate MP4. Original narration AAC packets are copied unchanged. The two paper scenes
retain their designs/timings; their video is re-encoded when the conservative
source-packet cache check cannot prove reuse, rather than reusing uncertain data.
