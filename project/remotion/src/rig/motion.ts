import {Easing, interpolate} from "remotion";
import rigData from "./ren-rig.json";
import {POSES} from "./poses";

// Shared motion helpers for the rig clips: eased keyframe channels and blending between library poses.
const PARTS = rigData.parts as unknown as Record<string, {bone: number}>;

export const ease = Easing.inOut(Easing.sin);
export const settle = Easing.bezier(0.42, 0, 0.2, 1); // pose changes: ease in, long soft landing, no overshoot
export const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;

// Keyframed number channel, eased between keys
export const key = (f: number, ks: [number, number][], easing = ease) => {
  if (f <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (f <= ks[i][0]) return interpolate(f, [ks[i - 1][0], ks[i][0]], [ks[i - 1][1], ks[i][1]], {easing});
  }
  return ks[ks.length - 1][1];
};

export type Resolved = {angles: Record<string, number>; hands: Record<"r" | "l", {part: string; tilt: number}>; brows: number; eyes: string; rest: string};
// A library pose with every hand's wrist expressed as a world tilt, so poses can be blended
export const resolve = (name: string): Resolved => {
  const d = POSES[name];
  const angles = {...(d.angles as Record<string, number>)};
  const world = (side: "r" | "l") => (angles.torso ?? 0) + (angles[`upperarm-${side}`] ?? 0) + (angles[`forearm-${side}`] ?? 0);
  const hand = (side: "r" | "l") => {
    const h = d.hands[side];
    return {part: h.part, tilt: h.tilt ?? world(side) + (h.angle ?? 0) - (PARTS[h.part].bone - 90)};
  };
  return {angles, hands: {r: hand("r"), l: hand("l")}, brows: d.face?.brows ?? 0, eyes: d.face?.eyes ?? "neutral", rest: d.face?.mouth ?? "closed"};
};

// Overlapping action: in each move the upper arm leads, the forearm follows a frame later and the hand two
// frames later (every joint still eases over the move's own frames)
const DELAY = (k: string) => (k.startsWith("forearm") || k === "head" ? 1 : 0);
const HAND_DELAY = 2, MAX_DELAY = 2;
export type Seq = [number, string, number][]; // [start frame, pose, ease frames]
export type Blend = Resolved & {seg: number};

export const makeBlend = (seq: Seq) => {
  const res = seq.map(([, n]) => resolve(n));
  return (f: number): Blend => {
    let i = 0;
    while (i + 1 < seq.length && f >= seq[i + 1][0]) i++;
    const cur = res[i];
    const [start, , dur] = seq[i];
    if (i === 0 || f >= start + dur + MAX_DELAY) return {...cur, seg: i};
    const prev = res[i - 1];
    const tAt = (delay: number) => settle(Math.min(1, Math.max(0, (f - start - delay) / dur)));
    const t = tAt(0);
    const keys = new Set([...Object.keys(prev.angles), ...Object.keys(cur.angles)]);
    const angles: Record<string, number> = {};
    keys.forEach((k) => {
      const tk = tAt(DELAY(k));
      angles[k] = (prev.angles[k] ?? 0) * (1 - tk) + (cur.angles[k] ?? 0) * tk;
    });
    const pick = <V,>(a: V, b: V) => (t < 0.5 ? a : b); // eyes swap halfway through the move
    // Hands swap a third of the way in, so a gesture forms early in the move; a hand closing to hold swaps late,
    // as it arrives at the boot. A clean swap: a cross-fade showed two differently drawn hands at once
    const hand = (side: "r" | "l") => {
      const from = prev.hands[side].part, to = cur.hands[side].part;
      const th = tAt(HAND_DELAY);
      const tilt = prev.hands[side].tilt * (1 - th) + cur.hands[side].tilt * th;
      if (from === to) return {part: to, tilt};
      const swapAt = to.includes("hold") && !from.includes("hold") ? 0.75 : 0.35;
      const fs = start + HAND_DELAY + Math.round(swapAt * dur);
      return {part: f < fs ? from : to, tilt};
    };
    return {angles, hands: {r: hand("r"), l: hand("l")}, brows: prev.brows * (1 - t) + cur.brows * t, eyes: pick(prev.eyes, cur.eyes), rest: pick(prev.rest, cur.rest), seg: i};
  };
};
