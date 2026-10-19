import {AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../fonts";
import {Boot, BOOT_GEOM, BOOT_RIG, type BootKind} from "./Boot";
import {frontLegs, MAX_CROUCH} from "./legs";
import {FLOOR, flipFor, POSES, tiltToAngle} from "./poses";
import rigData from "./ren-rig.json";
import {RenRig, type RigPose, solve} from "./RenRig";
import TL from "./test-timeline.json";

// 15-second 9:16 rig test, built from the pose library (poses.ts): walk in towards the camera, wave, hold the $60
// boot, hold both (wince at the price), crouch and set them down either side, point at them, thumbs-up.
// Motion-graphics style: rendered at 60 fps, every pose change a smooth ease-in-out over 10 timeline frames
// (1/3 s) with the joints overlapping by a frame or two, and holds perfectly still (no breathing, drift or
// wobble). Hands swap halfway through a move. The timeline counts 30 fps frames; the video has two per frame.
// Knee bends are drawn as foreshortening (legs.ts). Mouths come from Rhubarb (rig/test_voice.py).
const FPS = 30;
const PARTS = rigData.parts as unknown as Record<string, {bone: number; grip?: number[]}>;
const C = {bg: "#F3F5F8", ink: "#13233F", line: "#E3E7EE"};
const S = 0.56; // canvas px per rig unit
const X_END = 540, ROOT_Y = 1000;
const FLOOR_Y = ROOT_Y + FLOOR * S;
const ease = Easing.inOut(Easing.sin);
const settle = Easing.bezier(0.42, 0, 0.2, 1); // pose changes: ease in, long soft landing, no overshoot
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
  [s(1.43), "wave", 10],
  [s(2.95), "holdOne", 10],
  [s(6.0), "holdBoth", 10],
  [s(8.8), "setDown", 10],
  [s(9.24), "pointBoth", 10],
  [s(11.3), "thumbsUp", 10],
];
const WALK = s(1.4); // walk-in frames (under 1.5 s)
const CROUCH = {down: [s(8.8), s(8.8) + 10], up: [s(9.24), s(9.24) + 10]};
const RELEASE = s(8.8) + 11; // boots let go at the bottom of the crouch, standing on the floor
const DROP_FRAMES = 5;       // the hands can't reach the floor: the boots drop the last bit
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

// Overlapping action: in each move the upper arm leads, the forearm follows a frame later and the hand two
// frames later (every joint still eases over the move's own 9-10 frames)
const DELAY = (k: string) => (k.startsWith("forearm") || k === "head" ? 1 : 0);
const HAND_DELAY = 2, MAX_DELAY = 2;
type Blend = Resolved & {seg: number};
const blendAt = (f: number): Blend => {
  let i = 0;
  while (i + 1 < SEQ.length && f >= SEQ[i + 1][0]) i++;
  const cur = RES[i];
  const [start, , dur] = SEQ[i];
  if (i === 0 || f >= start + dur + MAX_DELAY) return {...cur, seg: i};
  const prev = RES[i - 1];
  const tAt = (delay: number) => settle(Math.min(1, Math.max(0, (f - start - delay) / dur)));
  const t = tAt(0);
  const keys = new Set([...Object.keys(prev.angles), ...Object.keys(cur.angles)]);
  const angles: Record<string, number> = {};
  keys.forEach((k) => {
    const tk = tAt(DELAY(k));
    angles[k] = (prev.angles[k] ?? 0) * (1 - tk) + (cur.angles[k] ?? 0) * tk;
  });
  const pick = <V,>(a: V, b: V) => (t < 0.5 ? a : b); // eyes swap halfway through the move
  // Hands swap halfway (a hand closing to hold swaps late, as it arrives at the boot). A clean swap: a
  // cross-fade showed two differently drawn hands at once
  const hand = (side: "r" | "l") => {
    const from = prev.hands[side].part, to = cur.hands[side].part;
    const th = tAt(HAND_DELAY);
    const tilt = prev.hands[side].tilt * (1 - th) + cur.hands[side].tilt * th;
    if (from === to) return {part: to, tilt};
    const swapAt = to.includes("hold") && !from.includes("hold") ? 0.75 : 0.5;
    const fs = start + HAND_DELAY + Math.round(swapAt * dur);
    return {part: f < fs ? from : to, tilt};
  };
  return {angles, hands: {r: hand("r"), l: hand("l")}, brows: prev.brows * (1 - t) + cur.brows * t, eyes: pick(prev.eyes, cur.eyes), rest: pick(prev.rest, cur.rest), seg: i};
};

// ---- Walk-in towards the camera: Ren's art faces front, so he walks out of the distance, growing ----
const STEPS = 4, TS = WALK / STEPS;
const K0 = 0.26;          // scale at the start (far away)
const HORIZON = 640;      // canvas y the floor converges to
const LIFT = 150, BOB = 14, SWAY = 14; // rig units: foot lift, rise at the passing pose, sideways weight shift
const scaleAt = (f: number) => K0 + (S - K0) * Easing.out(Easing.quad)(Math.min(1, f / WALK));
const floorAt = (k: number) => HORIZON + (FLOOR_Y - HORIZON) * (k / S);

const KIND_OF = {r: "cheap", l: "prem"} as const;
type Built = {pose: RigPose; held: Partial<Record<"r" | "l", {kind: BootKind; x: number; y: number; rot: number}>>; blend: ReturnType<typeof blendAt>};

const build = (f: number, faceF: number = f): Built => {
  const b = blendAt(f);
  const walking = f < WALK;
  const angles: Record<string, number> = {...b.angles};

  // Root, scale and legs
  let x = X_END, k = S, rootY = ROOT_Y, crouch = 0;
  const lift = {r: 0, l: 0};
  if (walking) {
    k = scaleAt(f);
    const step = Math.floor(f / TS), u = (f % TS) / TS;
    const swing = step % 2 === 0 ? "l" : "r"; // the leading (left, screen right) foot steps first
    const up = Math.sin(Math.PI * u) ** 2;    // 0 at each footfall, 1 at the passing pose
    lift[swing] = LIFT * up;
    // Weight shifts over the standing foot; the body rises at the passing pose
    const toStance = swing === "l" ? -1 : 1;  // standing on the right foot (screen left) shifts left
    x = X_END + toStance * SWAY * k * Math.sin(Math.PI * u);
    angles.torso = (angles.torso ?? 0) - toStance * 1.8 * Math.sin(Math.PI * u);
    rootY = floorAt(k) - FLOOR * k - BOB * k * up;
    const arm = Math.sin((Math.PI * f) / TS) * 7; // arms swing with the steps
    angles["upperarm-r"] += arm;
    angles["upperarm-l"] += arm;
    angles["forearm-r"] += Math.abs(arm) * 0.8;
    angles["forearm-l"] -= Math.abs(arm) * 0.8;
    angles.head = (angles.head ?? 0) + toStance * 1.2 * Math.sin(Math.PI * u);
  } else {
    crouch = key(f, [[CROUCH.down[0], 0], [CROUCH.down[1], crouchDepth], [CROUCH.up[0], crouchDepth], [CROUCH.up[1], 0]]);
    rootY = ROOT_Y; // holds are perfectly still
  }
  // Crouching also bows the upper body towards the camera: the torso looks shorter, the shoulders come down
  const bow = crouchDepth > 0 ? crouch / crouchDepth : 0;
  const legs = frontLegs(lift, crouch);
  Object.assign(angles, legs.angles);
  rootY += legs.drop * k; // feet stay on the floor as the knees bend
  const stretch: RigPose["stretch"] = {...legs.stretch, torso: [1 + 0.06 * bow, 1 - 0.36 * bow]};

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
  const lip = TL.mouth[Math.min(faceF, TL.mouth.length - 1)]; // mouths keep their own (Rhubarb) timing
  const rest = wincing ? "wince" : walking || f < SEQ[2][0] ? "smile" : b.rest;
  const mouth = lip === "rest" ? rest : lip;
  const blink = BLINKS.some((k) => f >= k && f < k + 4);
  const eyes = wincing ? "closed" : blink && b.eyes === "neutral" ? "closed" : b.eyes;

  const pose: RigPose = {
    x, y: rootY, scale: k, angles, stretch,
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

// Crouch depth: the lowest the hips need to go so the held boots stand on the floor at the bottom of the
// crouch (searched once; capped at what the legs can do)
let crouchDepth = 0;
{
  const soleGap = (d: number) => {
    crouchDepth = d;
    const held = build(RELEASE - 1).held;
    return Math.min(...(["r", "l"] as const).map((side) => FLOOR_Y - (held[side]!.y + (BOOT_GEOM[KIND_OF[side]].soleY - BOOT_GEOM[KIND_OF[side]].gripY) * BOOT_RIG * S)));
  };
  let lo = 0, hi = MAX_CROUCH;
  if (soleGap(hi) > 0) lo = hi;
  else for (let i = 0; i < 20; i++) { const mid = (lo + hi) / 2; if (soleGap(mid) > 0) lo = mid; else hi = mid; }
  crouchDepth = lo;
}

// When each boot appears in its hand: as the hand arrives at waist height, at the end of the move
const APPEAR = {r: SEQ[2][0] + SEQ[2][2] - 2, l: SEQ[3][0] + SEQ[3][2] - 2};
const KIND = KIND_OF;

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
  const f = useCurrentFrame() / OUT_PER_FRAME; // timeline frame (30 fps units), fractional between them
  const b = build(f, Math.floor(f));
  const boots = bootsAt(f, b);
  const k = b.pose.scale, floorY = f < WALK ? floorAt(k) : FLOOR_Y;
  const cap = TL.captions.find((c) => f / FPS >= c.start - 0.05 && f / FPS <= c.end + 0.25);
  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
      <Audio src={staticFile("rig/test/voice.mp3")} />
      <div style={{position: "absolute", left: b.pose.x - 290 * k, top: floorY - 26 * k, width: 580 * k, height: 52 * k, borderRadius: "50%", background: C.line}} />
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

export const RIG_TEST_FRAMES = Math.ceil(TL.duration * FPS); // timeline frames
const OUT_PER_FRAME = 2;
export const RIG_TEST_FPS = FPS * OUT_PER_FRAME; // the video: 60 fps
export const RIG_TEST_OUT_FRAMES = RIG_TEST_FRAMES * OUT_PER_FRAME;
export const _build = build; // for rig checks (checkClip.ts)
export const _SEQ = SEQ;
