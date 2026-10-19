# Prompts for Ren's full-body pose images

For an image generator. These replace the rig-built stills in the static version (`ren-still-explainer`):
each pose is one complete drawing, so the joints are drawn properly instead of assembled from parts.

## How to generate
1. **Attach references to every prompt:** `project/characters/ren/neutral.png` and
   `project/characters/ren/waving.png` (Ren's approved look), plus `project/rig/ren/source/ren-body-sheet.jpg`
   (his trousers and shoes).
2. **Make pose 1 first.** When it looks right, attach it as a reference for every other pose ("same
   character, same size and position as the attached full-body image"). This keeps the size, proportions and
   ground line consistent across all images.
3. **One pose per image.** Regenerate any that drift in face, clothes, colours or size.
4. **Save as PNG** and put them in `project/rig/ren/source/fullbody/`, named as below.

## Style block (paste at the start of every prompt)

> The character in the attached reference images, drawn as a full-body figure, head to toe, matching his
> existing look exactly: clean flat vector-style cartoon, bold dark near-black outline of even weight, soft
> cel shading. A young man with messy black hair and round black glasses; an open navy-blue button shirt-jacket
> over a plain white T-shirt; dark charcoal slim trousers; navy canvas sneakers with white soles. Same face,
> same proportions, same colours as the references.
> Front-facing, standing, both feet flat on the ground, the figure centred and filling about 85% of the image
> height, with the soles of his shoes on the same horizontal line near the bottom of the image in every
> picture. Portrait image, 3:4. Pure white background, no ground shadow, no props unless described, no text,
> no labels, no border.

## The poses

1. **`ren-full-neutral.png`** — Standing relaxed, arms down at his sides with a slight bend at the elbows,
   hands relaxed, a friendly closed-mouth smile.
2. **`ren-full-waving.png`** — Waving hello: his right arm raised beside his head (on the left of the
   image), elbow bent, open palm facing the viewer, fingers up; big open smile; other arm relaxed at his side.
3. **`ren-full-presenting.png`** — Presenting something beside him: his left arm (on the right of the image)
   held out to the side at waist height, elbow slightly bent, palm open and facing up as if showing the viewer
   something; open-mouth friendly expression, as if talking; other arm relaxed.
4. **`ren-full-pointing.png`** — Pointing at something to the side: his left arm (on the right of the image)
   reaching out diagonally upward to the side, index finger extended and pointing outward, other fingers
   curled; mouth slightly open, as if explaining; other arm relaxed.
5. **`ren-full-thinking.png`** — Thinking: one hand on his chin, the other arm folded across his waist
   supporting the elbow; eyes glancing up to one side; closed-mouth small smile.
6. **`ren-full-worried.png`** — Wincing at a high price: shoulders slightly raised, both hands clenched near
   his chest, eyes squeezed shut, teeth clenched in a grimace.
7. **`ren-full-shocked.png`** — Shocked: eyes wide, mouth open in an O, both hands raised beside his face,
   palms out.
8. **`ren-full-shrug.png`** — Shrugging: both elbows bent at his sides, forearms out, palms open and facing
   up, eyebrows raised, small uncertain smile.
9. **`ren-full-thumbs-up.png`** — Happy thumbs-up: his right arm (on the left of the image) bent with the
   fist at chest height, thumb up; big smile with closed happy eyes; other arm relaxed.
10. **`ren-full-holding-card.png`** — Holding a sign in front of his chest with both hands, elbows bent: the
    sign is a plain flat bright green rectangle (#00FF00), no outline, no shading, wider than it is tall; his
    fingers wrap over its top and sides. Nothing else in the image is green. (I replace the green with any
    graphic, e.g. a price card.)

## Checklist before sending them back
- Same face, hair, glasses, clothes and colours as the references; looks like the same character in all ten.
- Full body, head to toe, nothing cropped; the shoe soles on the same line and the figure the same size in
  every image (lay them side by side to check).
- Pure white background, no shadow, no text.
- Hands with five fingers and natural joints; arms clearly connected at the shoulders.
- PNG files, named as above.

These are new character art, so when they're approved for episodes they go through the usual route:
cut out with `pipeline/cutout.py`, checked on a coloured background, and added to `characters/manifest.json`.
