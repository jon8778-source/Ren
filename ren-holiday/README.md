# Ren holiday short (code-drawn Ren)

A standalone Remotion project. Ren is drawn entirely as SVG in `src/ren/Ren.tsx`; no images are used in
the render. `reference/ren-original.jpg` is the visual reference only.

- Colours and proportions: `src/theme.ts`
- `<Ren />` props: `expression` (neutral, happy, anxious, surprised), `mouthOpen` (0-1), `pose`
  (standing, driving, seated, holding-drink), `blink` (0-1), `sweat`, plus optional `size`, `lookX/lookY`,
  `armL/armR` overrides, `prop` (suitcase, calculator) and `tap`.

## Commands

```bash
npm install
npm run dev            # Remotion Studio preview in the browser
npm run render:test    # Step 1: out/ren-test.mp4 (5 s character test)
```

Step 2 (the 30-second short) is built after the character test is approved.
