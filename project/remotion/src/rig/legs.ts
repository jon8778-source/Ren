import rigData from "./ren-rig.json";
import {solve} from "./RenRig";

// Two-bone leg IK: given where each ankle should be (rig units from the root, with the torso upright), returns
// thigh, shin and shoe angles that put it there. Knees bend outward (front view), shoes stay level.
const PARTS = rigData.parts as unknown as Record<string, {w: number; h: number}>;
const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];
const rest = solve({x: 0, y: 0, scale: 1});
const at = (n: string) => apply(rest.frames[n], [0, 0]);
const deg = (v: number[]) => (Math.atan2(v[1], v[0]) * 180) / Math.PI;
const sub = (a: number[], b: number[]) => [a[0] - b[0], a[1] - b[1]];

const LEG = (["r", "l"] as const).map((s) => {
  const hip = at(`thigh-${s}`), knee = at(`shin-${s}`), ankle = at(`shoe-${s}`);
  const l1 = Math.hypot(...sub(knee, hip)), l2 = Math.hypot(...sub(ankle, knee)), d0 = Math.hypot(...sub(ankle, hip));
  // The rest knee's signed angle off the hip->ankle line, and the unsigned triangle angle at rest
  const s0 = deg(sub(knee, hip)) - deg(sub(ankle, hip));
  const A0 = (Math.acos(Math.min(1, (l1 * l1 + d0 * d0 - l2 * l2) / (2 * l1 * d0))) * 180) / Math.PI;
  return {s, hip, knee, ankle, l1, l2, a1: deg(sub(knee, hip)), a2: deg(sub(ankle, knee)), s0, A0};
});
export const ANKLE_REST = {r: LEG[0].ankle, l: LEG[1].ankle};
export const HIP = {r: LEG[0].hip, l: LEG[1].hip};
export const LEG_LEN = {r: LEG[0].l1 + LEG[0].l2, l: LEG[1].l1 + LEG[1].l2};
// The shoe's sole sits this far below the ankle pivot (rig units)
const soleOf = (s: "r" | "l") => apply(rest.images[`shoe-${s}`], [PARTS[`shoe-${s}`].w / 2, PARTS[`shoe-${s}`].h - 6])[1] - LEG[s === "r" ? 0 : 1].ankle[1];
export const SOLE = {r: soleOf("r"), l: soleOf("l")};

export const legIK = (target: {r: number[]; l: number[]}): Record<string, number> => {
  const out: Record<string, number> = {};
  for (const L of LEG) {
    const t = target[L.s];
    const d = sub(t, L.hip);
    const dist = Math.min(Math.hypot(...d), (L.l1 + L.l2) * 0.9995);
    // Angle at the hip between the hip->ankle line and the thigh (law of cosines)
    const cosA = (L.l1 * L.l1 + dist * dist - L.l2 * L.l2) / (2 * L.l1 * dist);
    const A = (Math.acos(Math.max(-1, Math.min(1, cosA))) * 180) / Math.PI;
    const base = deg(d);
    // At rest the knee sits where the art has it; extra bend pushes it outward (Ren's right leg, screen left,
    // bends to screen left: clockwise from the hip->ankle line, positive in screen coordinates)
    const outward = L.s === "r" ? 1 : -1;
    const thighDir = base + L.s0 + outward * (A - L.A0);
    const rad = (thighDir * Math.PI) / 180;
    const knee = [L.hip[0] + Math.cos(rad) * L.l1, L.hip[1] + Math.sin(rad) * L.l1];
    const shinDir = deg(sub([L.hip[0] + d[0] * (dist / Math.hypot(...d)), L.hip[1] + d[1] * (dist / Math.hypot(...d))], knee));
    const thigh = thighDir - L.a1;
    const shin = shinDir - L.a2 - thigh;
    out[`thigh-${L.s}`] = thigh;
    out[`shin-${L.s}`] = shin;
    out[`shoe-${L.s}`] = -(thigh + shin);
  }
  return out;
};

// Lowest the root may sit above both ankles so neither leg over-stretches (largest allowed root y offset is
// returned as a minimum: root y must be >= this for the given ankle targets in world rig units)
export const minRootY = (ankleWorld: {r: number[]; l: number[]}, rootX: number) =>
  Math.max(...(["r", "l"] as const).map((s) => {
    const dx = ankleWorld[s][0] - (rootX + HIP[s][0]);
    const reach = LEG_LEN[s] * 0.985;
    return ankleWorld[s][1] - HIP[s][1] - Math.sqrt(Math.max(0, reach * reach - dx * dx));
  }));
