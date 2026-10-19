// Numeric checks on the rig test clips (ren-rig-test, then ren-rig-explainer), every frame:  cd remotion && npx tsx src/rig/checkClip.ts
// - boots vs Ren's body: smallest gap between a boot's outline box and the boxes of the torso, head, upper arms,
//   thighs, shins and shoes (negative = overlap)
// - feet: how far each ankle drifts from its planted spot after the walk
// - pose changes (ease lengths) and mouth holds
import rigData from "./ren-rig.json";
import {BOOT_GEOM, BOOT_RIG} from "./Boot";
import {flipFor} from "./poses";
import {solve} from "./RenRig";
import {_build, _SEQ, bootsAt, RIG_TEST_FRAMES} from "./RigTest";
import {_explainer, RIG_EXPLAINER_FRAMES} from "./Explainer";
import TL from "./test-timeline.json";

const PARTS = rigData.parts as unknown as Record<string, {w: number; h: number}>;
const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];
type Box = [number, number, number, number];
const boxOf = (pts: number[][]): Box => [Math.min(...pts.map((p) => p[0])), Math.min(...pts.map((p) => p[1])), Math.max(...pts.map((p) => p[0])), Math.max(...pts.map((p) => p[1]))];
const gap = (a: Box, b: Box) => {
  const dx = Math.max(b[0] - a[2], a[0] - b[2]), dy = Math.max(b[1] - a[3], a[1] - b[3]);
  return dx > 0 || dy > 0 ? Math.max(dx, dy) : Math.max(dx, dy); // negative when overlapping
};
// Opaque bounding box of each part image (from its alpha), so transparent margins don't count
const BODY = ["torso", "head", "upperarm-r", "upperarm-l", "thigh-r", "thigh-l", "shin-r", "shin-l", "shoe-r", "shoe-l"];

type Boots = {kind: "cheap" | "prem"; side: "r" | "l"; x: number; y: number; rot: number; scale: number}[];
// Smallest gap between any boot's outline box and any body part box (negative = overlap)
const bootGap = (pose: Parameters<typeof solve>[0], boots: Boots) => {
  const sol = solve(pose);
  const body = BODY.map((n) => {
    const m = sol.images[n];
    const {w, h} = PARTS[n];
    const inset = 0.04; // ignore the outermost 4% of each image (soft edges, margins)
    return {n, box: boxOf([[w * inset, h * inset], [w * (1 - inset), h * inset], [w * inset, h * (1 - inset)], [w * (1 - inset), h * (1 - inset)]].map((p) => apply(m, p)))};
  });
  let best = {gap: Infinity, boot: "", part: ""};
  for (const bt of boots) {
    const g = BOOT_GEOM[bt.kind];
    const k = BOOT_RIG * pose.scale * bt.scale, fl = flipFor(bt.side) ? -1 : 1, r = (bt.rot * Math.PI) / 180;
    const corner = (bx: number, by: number) => {
      const lx = (bx - g.shaftX) * fl * k, ly = (by - g.gripY) * k;
      return [bt.x + lx * Math.cos(r) - ly * Math.sin(r), bt.y + lx * Math.sin(r) + ly * Math.cos(r)];
    };
    const bb = boxOf([corner(g.x0, 10), corner(g.x1, 10), corner(g.x0, g.soleY), corner(g.x1, g.soleY)]);
    for (const p of body) {
      const d = gap(bb, p.box);
      if (d < best.gap) best = {gap: d, boot: bt.kind, part: p.n};
    }
  }
  return best;
};

let worst = {gap: Infinity, f: -1, boot: "", part: ""};
let overlapFrames = 0;
const ankleDrift: number[] = [];
for (let f = 0; f < RIG_TEST_FRAMES; f++) {
  const b = _build(f);
  const sol = solve(b.pose);
  const g = bootGap(b.pose, bootsAt(f, b));
  if (g.gap < worst.gap) worst = {...g, f};
  if (g.gap < 0) overlapFrames++;
  if (f >= 42) {
    for (const s of ["r", "l"] as const) {
      const a = apply(sol.frames[`shoe-${s}`], [0, 0]);
      const a0 = apply(_build(42).pose && solve(_build(42).pose).frames[`shoe-${s}`], [0, 0]);
      ankleDrift.push(Math.hypot(a[0] - a0[0], a[1] - a0[1]));
    }
  }
}
console.log(`ren-rig-test boots vs body: closest ${worst.gap.toFixed(1)} px (frame ${worst.f}, ${worst.boot} boot vs ${worst.part}); frames overlapping: ${overlapFrames}`);
console.log(`ankles after the walk: max drift ${Math.max(...ankleDrift).toFixed(2)} px`);
console.log(`pose changes (frames): ${_SEQ.slice(1).map(([f, n, d]) => `${n}@${f}:${d}`).join(", ")}`);
const runs: number[] = [];
let k = 1;
for (let f = 1; f <= TL.mouth.length; f++) {
  if (f < TL.mouth.length && TL.mouth[f] === TL.mouth[f - 1]) k++;
  else (runs.push(k), (k = 1));
}
console.log(`mouth holds: shortest ${Math.min(...runs)} frames, ${runs.length} holds`);

// Explainer: boots vs body every half frame (the video is 60 fps), and stillness between moves
let ex = {gap: Infinity, f: -1, boot: "", part: ""}, exOverlap = 0;
for (let f = 0; f < RIG_EXPLAINER_FRAMES; f += 0.5) {
  const b = _explainer.build(f, Math.floor(f));
  const g = bootGap(b.pose, _explainer.bootsAt(f, b));
  if (g.gap < ex.gap) ex = {...g, f};
  if (g.gap < 0) exOverlap++;
}
console.log(`ren-rig-explainer boots vs body: closest ${ex.gap.toFixed(1)} px (frame ${ex.f}, ${ex.boot} boot vs ${ex.part}); frames overlapping: ${exOverlap}`);
let moving = 0;
for (const [a, z] of [[105, 178], [194, 242], [292, 337], [352, 462]] as [number, number][])
  for (let f = a; f < z; f++) {
    const p = solve(_explainer.build(f, 0).pose), q = solve(_explainer.build(f + 1, 0).pose);
    for (const n of p.visible) if (q.images[n]) moving = Math.max(moving, ...p.images[n].map((v, i) => Math.abs(v - q.images[n][i]) * (i < 4 ? 300 : 1)));
  }
console.log(`ren-rig-explainer holds: largest frame-to-frame movement ${moving.toFixed(3)} px`);
process.exit(0); // remotion leaves browser-only timers behind
