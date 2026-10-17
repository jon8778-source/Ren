# Max and Lena: character sheet prompts

Four sheets, one image each, made in this order:

1. Max at 30
2. Lena at 30
3. Max a year later (attach sheet 1 as the reference)
4. Lena a year later (attach sheet 2 as the reference)

For sheets 1 and 2, attach `project/characters/ren/neutral.png` as the style reference.

Each sheet has 4 poses in one row (1x4). `pipeline/split_sheet.py` cuts it at the white gaps between
figures, so keep the figures apart and don't let them overlap. Text labels under the figures are fine
because the splitter drops them.

## Shared style block (start every prompt with this)

> Character sheet, flat 2D cartoon in exactly the same style as the attached reference: clean bold
> dark outlines, flat colors with soft simple cel shading, friendly rounded proportions, chest-up bust,
> facing the viewer straight on, shoulders level, arms relaxed at the sides with no hands visible.
> Four poses of the SAME character side by side in one row, evenly spaced, same size and same
> head height, with wide empty white gaps between them. Solid plain white background, no shadows on the
> ground, no scenery, no props, no text except a small label under each pose. Identical face, hair,
> clothes and colors in every pose; only the facial expression changes.

## 1. Max, 30

> [style block] Character: Max, a 30-year-old man, warm light-tan skin, short dark-brown hair in a
> tidy modern quiff, clean-shaven, friendly face with brown eyes and thick straight eyebrows. Wearing a
> mustard-yellow pullover hoodie with drawstrings over a plain white T-shirt. Relaxed, likeable,
> easygoing look.
> Poses, left to right, labeled: "neutral" (calm closed-mouth smile), "happy" (big open grin, eyes
> bright), "worried" (eyebrows up and together, small frown), "regretful" (awkward sheepish half
> smile, eyes glancing sideways).

## 2. Lena, 30

> [style block] Character: Lena, a 30-year-old woman, medium-brown skin, dark curly hair tied up in
> a loose high bun with a few curls framing her face, small gold stud earrings, warm brown eyes. Wearing a
> soft sage-green knit cardigan over a cream crew-neck top. Calm, warm, approachable look.
> Poses, left to right, labeled: "neutral" (calm closed-mouth smile), "happy" (big open smile, eyes
> crinkled), "worried" (eyebrows up and together, small frown), "content" (soft relaxed smile, eyes
> gently closed, peaceful).

## 3. Max, one year later

> [style block] Use the attached Max sheet as the exact reference: same face, skin tone, eye color,
> build and art style. It is one year later, so make only these small changes: his hair is a little
> longer and messier on top, and he wears a navy zip-up jacket open over a light-grey T-shirt instead of
> the hoodie. Nothing else changes.
> Poses, left to right, labeled: "neutral" (calm closed-mouth smile), "happy" (big open grin),
> "worried" (eyebrows up and together, small frown), "shrug" (mild "meh" expression, lips pressed to one
> side, eyebrows slightly raised; shoulders slightly lifted, no hands visible).

## 4. Lena, one year later

> [style block] Use the attached Lena sheet as the exact reference: same face, skin tone, eye color,
> build and art style. It is one year later, so make only these small changes: her curly hair is now
> worn down at shoulder length, and she wears a light-blue denim jacket over a white T-shirt instead
> of the cardigan. Same gold stud earrings. Nothing else changes.
> Poses, left to right, labeled: "neutral" (calm closed-mouth smile), "happy" (big open smile, eyes
> crinkled), "worried" (eyebrows up and together, small frown), "content" (soft relaxed smile, eyes
> gently closed, peaceful).

## Before sending a sheet back, check

- All four figures have the same face, hair and clothes, at the same size.
- No figure touches another or the image edge.
- The background is plain white, with no grey floor shadow.
- There's no lettering on the clothes.
