import {AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../fonts";
import {Boot, BOOT_GEOM, BOOT_RIG, type BootKind} from "./Boot";
import {ANKLE_REST, legIK, minRootY} from "./legs";
import {FLOOR, flipFor, POSES, tiltToAngle} from "./poses";
import rigData from "./ren-rig.json";
import {RenRig, type RigPose, solve} from "./RenRig";
import TL from "./test-timeline.json";

// 15-second 9:16 rig test, built from the pose library (poses.ts): walk in, wave, hold the $60 boot, hold
// both (wince at the price), squat and set them down either side, point at them, thumbs-up. Every pose change
// eases over 6-10 frames; hands swap halfway through a move. Mouths come from Rhubarb (rig/test_voice.py).
const FPS = 30;
const PARTS = rigData.parts as unknown as Record<string, {bone: number; grip?: number[]}>;
const C = {bg: "#F3F5F8", ink: "#13233F", line: "#E3E7EE"};
const S = 0.56; // canvas px per rig unit
const X_END = 540, ROOT_Y = 1000;
const FLOOR_Y = ROOT_Y + FLOOR * S;
const ease = Easing.inOut(Easing.cubic);
const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
const s = (sec: number) => Math.round(sec * FPS);
const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];

// Keyframed number channel, eased between keys
const key = (f: number, ks: [number, number][]) => {
  if (f <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (f <= ks[i][0]) return interpolate(f, [ks[i - 1][0], ks[i][0]], [ks[i - 1][1], ks[i][1]], {easing: ease});
  }
  return ks[ks.length - 1][1];
};

// ---- Pose sequence: [start frame, pose, ease frames] ----
const SEQ: [number, string, number][] = [
  [0, "neutral", 0],
  [s(1.43), "wave", 9],
  [s(2.95), "holdOne", 10],
  [s(6.0), "holdBoth", 10],
  [s(8.8), "setDown", 10],
  [s(9.24), "pointBoth", 10],
  [s(11.3), "thumbsUp", 10],
];
const WALK = s(1.4); // walk-in frames (under 1.5 s)
const SQUAT = {down: [s(8.8), s(8.8) + 10], up: [s(9.24), s(9.24) + 10], depth: 250}; // root drop in rig units
const RELEASE = s(8.8) + 11; // boots let go at the bottom of the squat
const DROP_FRAMES = 4;
const WINCE = [s(8.1), s(8.8)];
const BLINKS = [2.45, 5.85, 12.75].map(s);

type Resolved = {angles: Record<string, number>; hands: Record<"r" | "l", {part: string; tilt: number}>; brows: number; eyes: string; rest: string};
const resolve = (name: string): Resolved => {
  const d = POSES[name];
  const angles = {...(d.angles as Record<string, number>)};
  const world = (side: "r" | "l") => (angles.torso ?? 0) + (angles[`upperarm-${side}`] ?? 0) + (angles[`forearm-${side}`] ?? 0);
  const hand = (side: "r" | "l") => {
    const h = d.hands[side];
    return {part: h.part, tilt: h.tilt ?? world(side) + (h.angle ?? 0) - (PARTS[h.part].bone - 90)};
  };
  return {angles, hands: {r: hand("r"), l: hand("l")}, brows: d.face?.brows ?? 0, eyes: d.face?.eyes ?? "neutral", rest: d.face?.mouth ?? "closed"};
};
const RES = SEQ.map(([, n]) => resolve(n));

const blendAt = (f: number): Resolved & {seg: number} => {
  let i = 0;
  while (i + 1 < SEQ.length && f >= SEQ[i + 1][0]) i++;
  const cur = RES[i];
  if (i === 0 || f >= SEQ[i][0] + SEQ[i][2]) return {...cur, seg: i};
  const prev = RES[i - 1];
  const t = ease((f - SEQ[i][0]) / SEQ[i][2]);
  const keys = new Set([...Object.keys(prev.angles), ...Object.keys(cur.angles)]);
  const angles: Record<string, number> = {};
  keys.forEach((k) => (angles[k] = (prev.angles[k] ?? 0) * (1 - t) + (cur.angles[k] ?? 0) * t));
  const pick = <V,>(a: V, b: V) => (t < 0.5 ? a : b); // eyes swap halfway through the move
  // Hands swap halfway, except a hand closing to hold swaps late, as it arrives at the boot
  const hand = (side: "r" | "l") => {
    const swapAt = cur.hands[side].part.includes("hold") && !prev.hands[side].part.includes("hold") ? 0.75 : 0.5;
    return {part: t < swapAt ? prev.hands[side].part : cur.hands[side].part, tilt: prev.hands[side].tilt * (1 - t) + cur.hands[side].tilt * t};
  };
  return {angles, hands: {r: hand("r"), l: hand("l")}, brows: prev.brows * (1 - t) + cur.brows * t, eyes: pick(prev.eyes, cur.eyes), rest: pick(prev.rest, cur.rest), seg: i};
};

// ---- Walk-in: six steps with planted feet; each foot lifts and swings to its next plant ----
const STEPS = 6, TS = WALK / STEPS, X0 = -110, LIFT = 80, BOB = 14;
const V = 1 / 0.85; // travel profile: steady speed, then slows to a stop over the last 30%
const travel = (u: number) => (u < 0.7 ? V * u : V * (0.7 + 0.15 - (1 - u) ** 2 / 0.6));
const bodyX = (f: number) => X0 + (X_END - X0) * travel(Math.min(1, Math.max(0, f / WALK)));
const footOff = {r: ANKLE_REST.r[0] * S, l: ANKLE_REST.l[0] * S};
const FOOT_Y = {r: ROOT_Y + ANKLE_REST.r[1] * S, l: ROOT_Y + ANKLE_REST.l[1] * S};
// Plants: [frame from, frame to, x from, x to] per step; the leading (left, screen right) foot steps first
const PLANTS = (() => {
  const last = {r: bodyX(0) + footOff.r, l: bodyX(0) + footOff.l};
  const steps: {side: "r" | "l"; f0: number; f1: number; x0: number; x1: number}[] = [];
  for (let k = 0; k < STEPS; k++) {
    const side = k % 2 === 0 ? "l" : "r";
    const f0 = k * TS, f1 = (k + 1) * TS;
    let x1 = bodyX(Math.min(WALK, f1 + TS)) + footOff[side];
    // Feet never cross: keep a planted foot at least 60% of the hip spacing from the other foot
    const minGap = 0.6 * (footOff.l - footOff.r);
    x1 = side === "r" ? Math.min(x1, last.l - minGap) : Math.max(x1, last.r + minGap);
    steps.push({side, f0, f1, x0: last[side], x1});
    last[side] = x1;
  }
  return steps;
})();
const footAt = (side: "r" | "l", f: number): number[] => {
  let x = bodyX(0) + footOff[side], y = FOOT_Y[side];
  for (const st of PLANTS.filter((p) => p.side === side)) {
    if (f >= st.f1) x = st.x1;
    else if (f > st.f0) {
      const u = (f - st.f0) / (st.f1 - st.f0);
      x = st.x0 + (st.x1 - st.x0) * ease(u);
      y -= LIFT * Math.sin(Math.PI * u);
    }
  }
  return [x, y];
};

type Built = {pose: RigPose; held: Partial<Record<"r" | "l", {kind: BootKind; x: number; y: number; rot: number}>>; blend: ReturnType<typeof blendAt>};

const build = (f: number): Built => {
  const b = blendAt(f);
  const walking = f < WALK;
  const angles: Record<string, number> = {...b.angles};

  // Root and feet
  let x = X_END, rootY = ROOT_Y;
  let feet = {r: [X_END + footOff.r, FOOT_Y.r], l: [X_END + footOff.l, FOOT_Y.l]};
  if (walking) {
    x = bodyX(f);
    feet = {r: footAt("r", f), l: footAt("l", f)};
    const u = (f % TS) / TS;
    const fade = interpolate(f, [WALK - TS, WALK], [1, 0], clamp);
    rootY = ROOT_Y + BOB * (1 - Math.sin(Math.PI * u)) * fade;
    const swing = Math.sin((Math.PI * f) / TS) * 14 * fade; // arms swing with the steps
    angles["upperarm-r"] += swing;
    angles["upperarm-l"] += swing;
    angles["forearm-r"] += swing * 0.4;
    angles["forearm-l"] += swing * 0.4;
    angles.head = (angles.head ?? 0) - swing * 0.12;
  } else {
    const drop = key(f, [[SQUAT.down[0], 0], [SQUAT.down[1], SQUAT.depth], [SQUAT.up[0], SQUAT.depth], [SQUAT.up[1], 0]]);
    const breathe = Math.sin(((f - WALK) / FPS / 3.2) * Math.PI * 2) * 1.6;
    rootY = ROOT_Y + drop * S + breathe;
  }
  // Never over-stretch a leg: the root sinks if the feet are far apart
  rootY = Math.max(rootY, minRootY({r: [feet.r[0] / S, feet.r[1] / S], l: [feet.l[0] / S, feet.l[1] / S]}, x / S) * S);
  Object.assign(angles, legIK({r: [(feet.r[0] - x) / S, (feet.r[1] - rootY) / S], l: [(feet.l[0] - x) / S, (feet.l[1] - rootY) / S]}));

  // Wave: the forearm rocks from the elbow and the hand follows it
  const waveEnv = interpolate(f, [s(1.75), s(1.95), s(2.7), s(2.92)], [0, 1, 1, 0], clamp);
  const wave = Math.sin(((f - s(1.75)) / 12) * Math.PI * 2) * 13 * waveEnv;
  angles["forearm-r"] += wave;

  // Wince: head turns away and brows drop while the boots are held
  const wincing = f >= WINCE[0] && f < WINCE[1];
  angles.head = (angles.head ?? 0) + key(f, [[WINCE[0], 0], [WINCE[0] + 6, -6], [WINCE[1] - 2, -6], [WINCE[1] + 6, 0]]) + key(f, [[s(11.3), 0], [s(11.3) + 10, -3]]);
  const brows = b.brows + key(f, [[WINCE[0], 0], [WINCE[0] + 6, 22], [WINCE[1] - 2, 22], [WINCE[1] + 6, 0]]);

  // Hands: wrist angle from the blended world tilt
  const world = (side: "r" | "l") => (angles.torso ?? 0) + angles[`upperarm-${side}`] + angles[`forearm-${side}`];
  for (const side of ["r", "l"] as const) {
    const h = b.hands[side];
    angles[h.part] = tiltToAngle(h.part, world(side), h.tilt + (side === "r" ? wave * 0.5 : 0));
  }

  // Face
  const lip = TL.mouth[Math.min(f, TL.mouth.length - 1)];
  const rest = wincing ? "wince" : walking || f < SEQ[2][0] ? "smile" : b.rest;
  const mouth = lip === "rest" ? rest : lip;
  const blink = BLINKS.some((k) => f >= k && f < k + 4);
  const eyes = wincing ? "closed" : blink && b.eyes === "neutral" ? "closed" : b.eyes;

  const pose: RigPose = {
    x, y: rootY, scale: S, angles,
    slots: {"hand-r": b.hands.r.part, "hand-l": b.hands.l.part, mouth: `mouth-${mouth}`, "eye-r": `eye-${eyes}-r`, "eye-l": `eye-${eyes}-l`},
    offsets: {"brow-r": [0, brows], "brow-l": [0, brows]},
  };
  // Boots in hand: the hold hand's grip, upright with the hand
  const sol = solve(pose);
  const held: Built["held"] = {};
  for (const side of ["r", "l"] as const) {
    const part = b.hands[side].part;
    if (!part.includes("hold") || f >= RELEASE) continue;
    const g = apply(sol.images[part], PARTS[part].grip!);
    const m = sol.images[part];
    held[side] = {kind: side === "r" ? "cheap" : "prem", x: g[0], y: g[1], rot: (Math.atan2(m[1], m[0]) * 180) / Math.PI};
  }
  return {pose, held, blend: b};
};

// When each boot appears in its hand: as the hand arrives at waist height, at the end of the move
const APPEAR = {r: SEQ[2][0] + SEQ[2][2] - 2, l: SEQ[3][0] + SEQ[3][2] - 2};
const KIND = {r: "cheap", l: "prem"} as const;

export type BootState = {side: "r" | "l"; kind: BootKind; x: number; y: number; rot: number; scale: number; z: number};
export const bootsAt = (f: number, b: Built = build(f)): BootState[] => {
  const out: BootState[] = [];
  const atRelease = f >= RELEASE ? build(RELEASE - 1).held : null;
  for (const side of ["r", "l"] as const) {
    if (f < APPEAR[side]) continue;
    const kind = KIND[side];
    const inHand = b.held[side];
    if (inHand) {
      const pop = interpolate(f, [APPEAR[side], APPEAR[side] + 6], [0.5, 1], {...clamp, easing: Easing.out(Easing.back(2))});
      out.push({side, kind, x: inHand.x, y: inHand.y, rot: inHand.rot, scale: pop, z: 51.2});
    } else if (atRelease?.[side]) {
      // Let go at the bottom of the squat: straight down onto the floor
      const from = atRelease[side]!;
      const t = interpolate(f, [RELEASE, RELEASE + DROP_FRAMES], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
      const floorY = FLOOR_Y - (BOOT_GEOM[kind].soleY - BOOT_GEOM[kind].gripY) * BOOT_RIG * S;
      out.push({side, kind, x: from.x, y: from.y + (floorY - from.y) * t, rot: from.rot * (1 - t), scale: 1, z: 49});
    }
  }
  return out;
};

export const RigTest: React.FC = () => {
  const f = useCurrentFrame();
  const b = build(f);
  const boots = bootsAt(f, b);
  const cap = TL.captions.find((c) => f / FPS >= c.start - 0.05 && f / FPS <= c.end + 0.25);
  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
      <Audio src={staticFile("rig/test/voice.mp3")} />
      <div style={{position: "absolute", left: b.pose.x - 290 * S, top: FLOOR_Y - 26 * S, width: 580 * S, height: 52 * S, borderRadius: "50%", background: C.line}} />
      <RenRig
        pose={{
          ...b.pose,
          props: boots.map((bt) => ({
            at: [bt.x, bt.y] as [number, number], z: bt.z,
            node: (
              <div style={{position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `rotate(${bt.rot}deg) scale(${BOOT_RIG * S * bt.scale}) translate(${-BOOT_GEOM[bt.kind].shaftX}px, ${-BOOT_GEOM[bt.kind].gripY}px)`}}>
                <Boot kind={bt.kind} flip={flipFor(bt.side)} />
              </div>
            ),
          })),
        }}
      />
      {cap ? (
        <div style={{position: "absolute", left: 60, right: 60, top: 150, textAlign: "center", zIndex: 2000}}>
          <span style={{display: "inline-block", background: "#fff", borderRadius: 28, padding: "14px 34px", fontSize: 64, fontWeight: 600, color: C.ink, lineHeight: 1.2, boxShadow: `0 0 0 4px ${C.line}`}}>{cap.text}</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const RIG_TEST_FRAMES = Math.ceil(TL.duration * FPS);
export const _build = build; // for rig checks (checkClip.ts)
export const _SEQ = SEQ;
