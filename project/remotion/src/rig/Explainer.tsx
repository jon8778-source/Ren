import {AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../fonts";
import {Boot, BOOT_GEOM, BOOT_RIG, type BootKind} from "./Boot";
import {clamp, key, makeBlend, type Seq} from "./motion";
import {FLOOR, flipFor, floorBoot, tiltToAngle} from "./poses";
import rigData from "./ren-rig.json";
import {RenRig, type RigPose, solve} from "./RenRig";
import TL from "./test-timeline.json";

// The boots clip in an explainer-channel style: same script, voice, lip sync and line timings as ren-rig-test,
// but the character barely travels. Ren slides in and settles; poses change with smooth eases and hold
// perfectly still; the boots and their price tags pop in; at "which pair" the boots glide down beside his
// feet (no crouch); a "?" pops in on the question. A virtual camera pushes in slowly through each line and
// cuts to a new framing between lines, with a quick close-up on the wince. 60 fps output.
const FPS = 30, OUT_PER_FRAME = 2;
const PARTS = rigData.parts as unknown as Record<string, {bone: number; grip?: number[]}>;
const C = {bg: "#F3F5F8", ink: "#13233F", line: "#E3E7EE", gold: "#F5B82E"};
const S = 0.56, X_END = 540, ROOT_Y = 1000;
const FLOOR_Y = ROOT_Y + FLOOR * S;
const s = (sec: number) => Math.round(sec * FPS);
const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];
const pop = Easing.out(Easing.back(1.7));       // graphics pop with a small bounce (props only, never Ren)

const SEQ: Seq = [
  [0, "neutral", 0],
  [s(1.43), "wave", 10],
  [s(2.95), "holdOne", 10],
  [s(6.0), "holdBoth", 10],
  [s(8.8), "neutral", 10],
  [s(9.24), "pointBoth", 10],
  [s(11.3), "thumbsUp", 10],
];
// "calm": the same clip without the pointing and thumbs-up poses. At "which pair" Ren stands with his arms
// down while the "?" pops in; for the last line he waves again.
const SEQ_CALM: Seq = [...SEQ.slice(0, 5), [s(11.3), "wave", 10]];
export type Variant = "full" | "calm";
const BLEND = {full: makeBlend(SEQ), calm: makeBlend(SEQ_CALM)};
const SLIDE = [0, 22]; // Ren slides in from the right
const WINCE = [s(8.1), s(8.8)];
const BLINKS = [2.45, 5.85, 12.75].map(s);
const GLIDE = [s(8.8), s(8.8) + 14]; // boots leave the hands and glide down beside his feet
const APPEAR = {r: SEQ[2][0] + SEQ[2][2], l: SEQ[3][0] + SEQ[3][2]}; // as the hand closes into its hold
const KIND = {r: "cheap", l: "prem"} as const;
const QUESTION = [s(9.4), s(11.3)];

// Camera shots: [first frame, scale from, scale to, focus x, focus y]; a slow push within a shot, a cut between.
// The wince close-up's focus (NaN here) is Ren's face, found from the rig at that moment.
const SHOTS: [number, number, number, number, number][] = [
  [0, 1.0, 1.04, 540, 950],
  [s(2.95), 1.1, 1.16, 470, 900],      // the $60 boot
  [s(6.0), 1.06, 1.1, 540, 900],       // both boots
  [WINCE[0], 2.0, 2.08, NaN, NaN],     // close-up on the wince
  [s(8.8), 1.0, 1.03, 540, 1050],      // wide: boots on the floor
  [s(11.3), 1.08, 1.14, 540, 880],     // thumbs-up
];
const cameraAt = (f: number) => {
  let i = 0;
  while (i + 1 < SHOTS.length && f >= SHOTS[i + 1][0]) i++;
  const end = i + 1 < SHOTS.length ? SHOTS[i + 1][0] : RIG_EXPLAINER_FRAMES;
  const [start, from, to, fx, fy] = SHOTS[i];
  // The focus point stays where it is on screen, except the face, which is brought to the middle of the frame
  const [focus, target] = Number.isNaN(fx) ? [faceFocus(), [540, 820]] : [[fx, fy], [fx, fy]];
  const scale = interpolate(f, [start, end], [from, to], clamp);
  return {scale, tx: target[0] - focus[0] * scale, ty: target[1] - focus[1] * scale};
};

const build = (f: number, faceF: number, variant: Variant = "full") => {
  const b = BLEND[variant](f);
  const angles: Record<string, number> = {...b.angles};
  const x = interpolate(f, SLIDE, [1400, X_END], {...clamp, easing: Easing.out(Easing.cubic)});

  // Wave: the forearm rocks from the elbow and the hand follows it
  const waveEnv = interpolate(f, [s(1.75), s(1.95), s(2.7), s(2.92)], [0, 1, 1, 0], clamp) +
    (variant === "calm" ? interpolate(f, [s(11.7), s(11.9), s(12.9), s(13.1)], [0, 1, 1, 0], clamp) : 0);
  const wave = Math.sin(((f - s(1.75)) / 12) * Math.PI * 2) * 13 * waveEnv;
  angles["forearm-r"] += wave;
  // Wince: head turns away and brows drop
  const wincing = f >= WINCE[0] && f < WINCE[1];
  angles.head = (angles.head ?? 0) + key(f, [[WINCE[0], 0], [WINCE[0] + 6, -6], [WINCE[1] - 2, -6], [WINCE[1] + 6, 0]]) + key(f, [[s(11.3), 0], [s(11.3) + 10, -3]]);
  const brows = b.brows + key(f, [[WINCE[0], 0], [WINCE[0] + 6, 22], [WINCE[1] - 2, 22], [WINCE[1] + 6, 0]]);
  const world = (side: "r" | "l") => (angles.torso ?? 0) + angles[`upperarm-${side}`] + angles[`forearm-${side}`];
  for (const side of ["r", "l"] as const) {
    const h = b.hands[side];
    angles[h.part] = tiltToAngle(h.part, world(side), h.tilt + (side === "r" ? wave * 0.5 : 0));
  }
  const lip = TL.mouth[Math.min(faceF, TL.mouth.length - 1)];
  const rest = wincing ? "wince" : f < SEQ[2][0] ? "smile" : b.rest;
  const mouth = lip === "rest" ? rest : lip;
  const blink = BLINKS.some((k) => f >= k && f < k + 4);
  const eyes = wincing ? "closed" : blink && b.eyes === "neutral" ? "closed" : b.eyes;
  const pose: RigPose = {
    x, y: ROOT_Y, scale: S, angles,
    slots: {"hand-r": b.hands.r.part, "hand-l": b.hands.l.part, mouth: `mouth-${mouth}`, "eye-r": `eye-${eyes}-r`, "eye-l": `eye-${eyes}-l`},
    offsets: {"brow-r": [0, brows], "brow-l": [0, brows]},
  };
  const sol = solve(pose);
  const grip = (side: "r" | "l") => {
    const part = b.hands[side].part;
    if (!part.includes("hold")) return null;
    const m = sol.images[part];
    const g = apply(m, PARTS[part].grip!);
    return {x: g[0], y: g[1], rot: (Math.atan2(m[1], m[0]) * 180) / Math.PI};
  };
  return {pose, grip};
};

let face: number[] | null = null;
const faceFocus = () => (face ??= apply(solve(build(WINCE[0], 0).pose).frames.head, [0, -650])); // mid-face

type BootState = {side: "r" | "l"; kind: BootKind; x: number; y: number; rot: number; scale: number; tag: number; z: number};
const bootsAt = (f: number, b = build(f, Math.floor(f)), variant: Variant = "full"): BootState[] => {
  const out: BootState[] = [];
  const atGlide = f >= GLIDE[0] ? build(GLIDE[0] - 1, 0, variant).grip : null;
  for (const side of ["r", "l"] as const) {
    if (f < APPEAR[side]) continue;
    const kind = KIND[side];
    const tag = interpolate(f, [APPEAR[side] + 6, APPEAR[side] + 14], [0, 1], {...clamp, easing: pop});
    if (f < GLIDE[0]) {
      const g = b.grip(side);
      if (!g) continue;
      const sc = interpolate(f, [APPEAR[side], APPEAR[side] + 9], [0, 1], {...clamp, easing: pop});
      out.push({side, kind, ...g, scale: sc, tag, z: 51.2});
      continue;
    }
    // Glide from the hand down to the floor beside his foot, with a slight lift as it leaves the hand
    const from = atGlide!(side)!;
    const fb = floorBoot(side, kind);
    const to = {x: X_END + fb.x * S, y: FLOOR_Y - (BOOT_GEOM[kind].soleY - BOOT_GEOM[kind].gripY) * BOOT_RIG * S};
    const t = interpolate(f, GLIDE, [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
    out.push({side, kind, x: from.x + (to.x - from.x) * t, y: from.y + (to.y - from.y) * t - 50 * Math.sin(Math.PI * t), rot: from.rot * (1 - t), scale: 1, tag, z: 49});
  }
  return out;
};

const Question: React.FC<{f: number; head: number[]}> = ({f, head}) => {
  const k = interpolate(f, [QUESTION[0], QUESTION[0] + 9], [0, 1], {...clamp, easing: pop}) * interpolate(f, [QUESTION[1] - 6, QUESTION[1]], [1, 0], {...clamp, easing: Easing.in(Easing.quad)});
  if (k <= 0) return null;
  return (
    <div style={{position: "absolute", left: head[0] + 110, top: head[1] - 60, width: 130, height: 130, borderRadius: 65, background: C.gold, border: `6px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT, fontWeight: 700, fontSize: 92, color: C.ink, transform: `scale(${k}) rotate(${8 * (1 - k)}deg)`, zIndex: 900}}>?</div>
  );
};

export const Explainer: React.FC<{variant?: Variant}> = ({variant = "full"}) => {
  const f = useCurrentFrame() / OUT_PER_FRAME;
  const b = build(f, Math.floor(f), variant);
  const boots = bootsAt(f, b, variant);
  const cam = cameraAt(f);
  const head = apply(solve(b.pose).frames.head, [0, -1500]); // top of the head (head px above the chin)
  const cap = TL.captions.find((c) => f / FPS >= c.start - 0.05 && f / FPS <= c.end + 0.25);
  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
      <Audio src={staticFile("rig/test/voice.mp3")} />
      <AbsoluteFill style={{transformOrigin: "0 0", transform: `translate(${cam.tx}px, ${cam.ty}px) scale(${cam.scale})`}}>
        <div style={{position: "absolute", left: b.pose.x - 290 * S, top: FLOOR_Y - 26 * S, width: 580 * S, height: 52 * S, borderRadius: "50%", background: C.line}} />
        <RenRig
          pose={{
            ...b.pose,
            props: boots.map((bt) => ({
              at: [bt.x, bt.y] as [number, number], z: bt.z,
              node: (
                <div style={{position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `rotate(${bt.rot}deg) scale(${BOOT_RIG * S * bt.scale}) translate(${-BOOT_GEOM[bt.kind].shaftX}px, ${-BOOT_GEOM[bt.kind].gripY}px)`}}>
                  <Boot kind={bt.kind} flip={flipFor(bt.side)} tagScale={bt.tag} />
                </div>
              ),
            })),
          }}
        />
        <Question f={f} head={head} />
      </AbsoluteFill>
      {cap ? (
        <div style={{position: "absolute", left: 60, right: 60, top: 150, textAlign: "center", zIndex: 2000}}>
          <span style={{display: "inline-block", background: "#fff", borderRadius: 28, padding: "14px 34px", fontSize: 64, fontWeight: 600, color: C.ink, lineHeight: 1.2, boxShadow: `0 0 0 4px ${C.line}`}}>{cap.text}</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const RIG_EXPLAINER_FRAMES = Math.ceil(TL.duration * FPS); // timeline frames
export const RIG_EXPLAINER_FPS = FPS * OUT_PER_FRAME;
export const RIG_EXPLAINER_OUT_FRAMES = RIG_EXPLAINER_FRAMES * OUT_PER_FRAME;
export const _explainer = {build, bootsAt}; // for rig checks
