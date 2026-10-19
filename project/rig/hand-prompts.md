# Prompts for Ren's new hand images

For an image generator. Attach two reference images with every prompt: `rig/ren/source/ren-original.jpg`
(Ren) and `rig/ren/source/ren-hands-sheet.jpg` (his current hands), so the style matches.

Generate one sheet at a time. Keep sheets whose hands match the references; regenerate any that drift in
style, skin tone or size. I cut the hands out of the white background and measure each wrist myself, so the
background must be plain white and the hands must not touch each other.

## Style block (paste at the start of every prompt)

> Cartoon hands for the character in the attached reference images, matching his existing hands exactly:
> clean flat vector-style cartoon, bold dark brown-black outline (#120803) of even weight, flat skin colour
> #E9BA9A with one soft darker shade for creases, simple rounded fingers, no fingernail detail, no sleeves, no
> jewellery, no text, no labels, no arrows. Each hand ends at the wrist with a short straight cut, and the
> wrist points straight down to the bottom of its cell, as if the forearm comes up from below. All hands are
> the same size as each other and the same size and proportions as the reference hands. Pure white
> background, no shadows, no gradients, hands well separated with lots of white space between them.

## Sheet 1: pointing, right hand (the character's right hand: thumb on the left side of the image when the back of the hand faces the viewer)

> [style block] A sheet of 5 hands in one row, all the character's RIGHT hand:
> 1. Index finger pointing straight down along the line of the forearm, other fingers curled, back of the hand facing the viewer.
> 2. The same pointing hand, but the wrist bent so the index finger points 45 degrees to the left of straight down.
> 3. Index finger pointing straight at the viewer, foreshortened: we see the fingertip and the front of the curled fingers.
> 4. A relaxed open hand with the fingers half curled and the index finger starting to straighten (halfway between relaxed and pointing).
> 5. Index finger pointing straight up, other fingers curled, palm facing the viewer.

## Sheet 2: pointing, left hand

> [style block] A sheet of 5 hands in one row, all the character's LEFT hand (the mirror of a right hand,
> thumb on the right side of the image when the back of the hand faces the viewer):
> 1. Index finger pointing straight down along the line of the forearm, other fingers curled, back of the hand facing the viewer.
> 2. The same pointing hand, but the wrist bent so the index finger points 45 degrees to the right of straight down.
> 3. Index finger pointing straight at the viewer, foreshortened: we see the fingertip and the front of the curled fingers.
> 4. A relaxed open hand with the fingers half curled and the index finger starting to straighten (halfway between relaxed and pointing).
> 5. Index finger pointing straight up, other fingers curled, palm facing the viewer.

## Sheet 3: thumbs-up, right hand

> [style block] A sheet of 4 hands in one row, all the character's RIGHT hand, wrist at the bottom:
> 1. Thumbs-up seen from the front: a fist with the curled fingers' knuckles facing the viewer, thumb pointing straight up.
> 2. Thumbs-up turned 45 degrees: the same fist rotated a quarter of the way to a side view, thumb straight up.
> 3. A closed fist with the thumb tucked against the curled fingers (the start of a thumbs-up).
> 4. The same fist with the thumb half raised, pointing up and outward at 45 degrees (halfway to a thumbs-up).

## Sheet 4: thumbs-up, left hand

> [style block] A sheet of 4 hands in one row, all the character's LEFT hand (the mirror of a right hand),
> wrist at the bottom:
> 1. Thumbs-up seen from the front: a fist with the curled fingers' knuckles facing the viewer, thumb pointing straight up.
> 2. Thumbs-up turned 45 degrees: the same fist rotated a quarter of the way to a side view, thumb straight up.
> 3. A closed fist with the thumb tucked against the curled fingers (the start of a thumbs-up).
> 4. The same fist with the thumb half raised, pointing up and outward at 45 degrees (halfway to a thumbs-up).

## Sheet 5 (optional): in-betweens, both hands

> [style block] A sheet of 4 hands in one row: the character's RIGHT hand then LEFT hand, twice:
> 1 and 2. An open hand half closed (fingers bent halfway, as between an open waving hand and a fist), palm facing the viewer.
> 3 and 4. A gripping hand seen from the front, fingers curled around an invisible vertical pole about two
> fingers thick, knuckles facing the viewer, thumb wrapped over the front.

## Checklist before sending them back
- Same outline weight, skin colour and size as the reference hands (compare them side by side).
- Right and left hands really are mirror images; thumbs on the correct side.
- Wrist at the bottom of every hand, cut straight, nothing touching the edge of the image or another hand.
- Save as PNG (JPG adds blurry edges). Name them by sheet, e.g. `sheet1-pointing-right.png`, and put them in
  `project/rig/ren/source/`.
