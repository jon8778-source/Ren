import {AbsoluteFill, Audio, Easing, interpolate, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../fonts";
import rigData from "./ren-rig.json";
import {NEUTRAL, RenRig, type RigPose, solve} from "./RenRig";
import TL from "./test-timeline.json";

// 15-second 9:16 rig test: walk in and wave, cheap boot, premium boot (wince), point, thumbs up.
const FPS = 30;
const PARTS = rigData.parts as unknown as Record<string, {bone: number; grip?: number[]}>;
const T = {
  bg: "#F3F5F8", ink: "#13233F", gold: "#F5B82E", goldEdge: "#C98A0B", red: "#E23D3D", line: "#E3E7EE", muted: "#7A8496", outline: "#1d1f26",
};
const SCALE = 0.56;
const ROOT_Y = 1000;
const FLOOR_Y = ROOT_Y + 808 * SCALE; // bottom of the shoes in the neutral pose
const ease = Easing.inOut(Easing.cubic);
const s = (sec: number) => sec * FPS;

// Keyframed channel: [[frame, value], ...], eased in and out between keys, held outside them
const key = (f: number, ks: [number, number][]) => {
  if (f <= ks[0][0]) return ks[0][1];
  for (let i = 1; i < ks.length; i++) {
    if (f <= ks[i][0]) return interpolate(f, [ks[i - 1][0], ks[i][0]], [ks[i - 1][1], ks[i][1]], {easing: ease});
  }
  return ks[ks.length - 1][1];
};
// Step channel: the value whose start frame is the latest one <= f
const step = <V,>(f: number, ks: [number, V][]): V => ks.reduce((v, k) => (f >= k[0] ? k[1] : v), ks[0][1]);

// The hand angle (relative to its forearm) that keeps a hand image upright at a chosen world tilt
const upright = (hand: string, parentWorld: number, tilt = 0) => PARTS[hand].bone - 90 + tilt - parentWorld;

const WALK_END = s(1.8);
const X0 = -260, X1 = 540;
const STRIDE = 400; // canvas px per walk cycle (two steps)

const BEATS = {
  waveUp: [s(1.7), s(2.2)], waveEnd: s(3.0),
  cheapUp: [s(3.05), s(3.5)],
  premUp: [s(6.05), s(6.5)], wince: [s(8.1), s(8.8)],
  lower: [s(9.05), s(9.6)], drop: s(9.62), land: s(10.0),
  point: [s(10.0), s(10.45)], pointEnd: s(11.9),
  thumbs: [s(11.95), s(12.45)],
};

type Built = {pose: RigPose; boots: {cheap: number[] | null; prem: number[] | null}; blink: boolean};

const build = (f: number): Built => {
  const t = f / FPS;
  // Walk in: eased travel; leg phase follows distance so the feet travel with the body
  const travel = interpolate(f, [0, WALK_END], [0, 1], {extrapolateRight: "clamp", easing: Easing.out(Easing.quad)});
  const x = X0 + (X1 - X0) * travel;
  const phase = ((x - X0) / STRIDE) * Math.PI * 2;
  const amp = interpolate(f, [WALK_END - s(0.35), WALK_END], [1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const walking = f < WALK_END;
  const sw = Math.sin(phase) * amp;
  const lift = (v: number) => Math.max(0, v); // a knee bends only while its leg swings forward
  const bob = walking ? -Math.abs(Math.cos(phase)) * 9 * amp : 0;
  const breathe = walking ? 0 : Math.sin(((t - 1.8) / 3.2) * Math.PI * 2) * 2.2;

  // Arms: [upper, fore] per side, eased between poses
  const ur = key(f, [[0, 6], [BEATS.waveUp[0], 6], [BEATS.waveUp[1], 150], [BEATS.waveEnd, 150], [BEATS.cheapUp[1], 72], [BEATS.lower[0], 72], [BEATS.lower[1], 14], [BEATS.thumbs[0], 14], [BEATS.thumbs[1], 6]]);
  const fr = key(f, [[0, -3], [BEATS.waveUp[0], -3], [BEATS.waveUp[1], -22], [BEATS.waveEnd, -22], [BEATS.cheapUp[1], 22], [BEATS.lower[0], 22], [BEATS.lower[1], 4], [BEATS.thumbs[1], -3]]);
  const ul = key(f, [[0, -6], [BEATS.premUp[0], -6], [BEATS.premUp[1], -72], [BEATS.lower[0], -72], [BEATS.lower[1], -14], [BEATS.point[0], -14], [BEATS.point[1], -62], [BEATS.pointEnd, -62], [BEATS.thumbs[1], -32]]);
  const fl = key(f, [[0, 3], [BEATS.premUp[0], 3], [BEATS.premUp[1], -22], [BEATS.lower[0], -22], [BEATS.lower[1], -4], [BEATS.point[0], -4], [BEATS.point[1], -30], [BEATS.pointEnd, -30], [BEATS.thumbs[1], -150]]);
  const armSwing = sw * 13; // arms swing opposite the legs
  const urA = ur + (walking ? -armSwing : 0) + (walking ? 0 : breathe * 0.25);
  const ulA = ul + (walking ? -armSwing : 0) - (walking ? 0 : breathe * 0.25);
  const wave = f > BEATS.waveUp[1] && f < BEATS.waveEnd ? Math.sin(((f - BEATS.waveUp[1]) / 11) * Math.PI * 2) * 13 * Math.min(1, (BEATS.waveEnd - f) / 6) : 0;
  const frA = fr + wave;

  // Hands: swap at the start of each move, angle chosen so the hand image stays upright
  const handR = step(f, [[0, "hand-relaxed-r"], [BEATS.waveUp[0] + 4, "hand-open-r"], [BEATS.waveEnd + 4, "hand-hold-r"], [BEATS.drop, "hand-relaxed-r"]]);
  const handL = step(f, [[0, "hand-relaxed-l"], [BEATS.premUp[0] + 4, "hand-hold-l"], [BEATS.drop, "hand-relaxed-l"], [BEATS.point[0] + 3, "hand-pointout-l"], [BEATS.thumbs[0] + 6, "hand-thumbsup-l"]]);
  const torsoA = walking ? sw * 1.2 : 0;
  const worldR = torsoA + urA + frA, worldL = torsoA + ulA + fl;
  const handAngle = (h: string, world: number) =>
    h.includes("relaxed") ? 0 : h.includes("open") ? upright(h, world, wave * 0.6) : h.includes("pointout") ? upright(h, world, -12) : h.includes("thumbs") ? upright(h, world, 6) : upright(h, world, 0);

  // Face
  const speakingMouth = TL.mouth[Math.min(f, TL.mouth.length - 1)];
  const smile = f >= s(12.0);
  const wincing = f >= BEATS.wince[0] && f < BEATS.wince[1];
  const rest = smile || f < s(1.6) ? "mouth-smile" : "mouth-closed";
  const mouth = wincing && speakingMouth === "closed" ? "mouth-wince" : speakingMouth === "closed" ? rest : `mouth-${speakingMouth}`;
  const blinks = [2.45, 5.85, 9.15, 12.7, 14.95].map(s);
  const blink = blinks.some((b) => f >= b && f < b + 4) && !wincing;
  const eyes = wincing ? "closed" : blink ? "closed" : f >= BEATS.thumbs[1] && f < s(14.9) ? "happy" : "neutral";
  const browRaise = key(f, [[0, 0], [s(9.3), 0], [s(9.6), -55], [s(11.5), -55], [s(11.9), 0]]) + (wincing ? 30 : 0);
  const headA = (walking ? -sw * 1.5 : 0) + key(f, [[0, 0], [s(6.4), 0], [s(6.8), -3], [BEATS.wince[0], -3], [BEATS.wince[0] + 4, 5], [BEATS.wince[1], 5], [BEATS.wince[1] + 8, 0], [s(9.4), 0], [s(9.9), 4], [s(11.6), 4], [s(12.2), -3]]);

  const pose: RigPose = {
    x, y: ROOT_Y + bob + breathe, scale: SCALE,
    angles: {
      ...NEUTRAL.angles, torso: torsoA, head: headA,
      "upperarm-r": urA, "forearm-r": frA, "upperarm-l": ulA, "forearm-l": fl,
      [handR]: handAngle(handR, worldR), [handL]: handAngle(handL, worldL),
      // Front-facing march: each foot lifts in turn (the leg slides up under the hips, knee bends a little)
      "thigh-r": lift(sw) * 5 - sw * 3, "thigh-l": -lift(-sw) * 5 - sw * 3,
      "shin-r": -lift(sw) * 14, "shin-l": lift(-sw) * 14,
      "shoe-r": lift(sw) * 8, "shoe-l": -lift(-sw) * 8,
    },
    slots: {
      "hand-r": handR, "hand-l": handL, mouth,
      "eye-r": `eye-${eyes}-r`, "eye-l": `eye-${eyes}-l`,
    },
    offsets: {"brow-r": [0, browRaise], "brow-l": [0, browRaise], "thigh-r": [0, -lift(sw) * 115], "thigh-l": [0, -lift(-sw) * 115]},
  };
  const sol = solve(pose);
  const grip = (h: string) => {
    const m = sol.images[h];
    const g = PARTS[h].grip!;
    return [m[0] * g[0] + m[2] * g[1] + m[4], m[1] * g[0] + m[3] * g[1] + m[5]];
  };
  return {
    pose,
    boots: {cheap: handR === "hand-hold-r" ? grip(handR) : null, prem: handL === "hand-hold-l" ? grip(handL) : null},
    blink,
  };
};

// Boots, drawn flat in code. Cheap: thin gold boot, flat sole. Premium: navy, chunky sole, gold laces.
const Boot: React.FC<{kind: "cheap" | "prem"; label: string}> = ({kind, label}) => {
  const prem = kind === "prem";
  return (
    <div style={{position: "relative", width: 190, height: 250}}>
      <svg width="190" height="200" viewBox="0 0 190 200" style={{overflow: "visible"}}>
        {prem ? (
          <>
            <path d="M48 8 H112 V118 Q150 120 172 142 Q182 154 178 166 H30 V8 Z" transform="translate(-6 0)" fill={T.ink} stroke={T.outline} strokeWidth="7" strokeLinejoin="round" />
            <rect x="20" y="164" width="164" height="30" rx="10" fill={T.line} stroke={T.outline} strokeWidth="7" />
            <path d="M28 178 H176" stroke={T.muted} strokeWidth="4" strokeDasharray="8 7" />
            {[34, 58, 82, 106].map((y) => <path key={y} d={`M52 ${y} L92 ${y + 10} M92 ${y} L52 ${y + 10}`} stroke={T.gold} strokeWidth="5" strokeLinecap="round" />)}
            <path d="M30 20 H106" stroke={T.goldEdge} strokeWidth="4" strokeDasharray="6 6" />
          </>
        ) : (
          <>
            <path d="M52 16 H104 V124 Q140 128 160 148 Q168 158 164 170 H40 V16 Z" fill={T.gold} stroke={T.outline} strokeWidth="6" strokeLinejoin="round" />
            <rect x="36" y="168" width="132" height="12" rx="5" fill={T.goldEdge} stroke={T.outline} strokeWidth="5" />
            <path d="M46 60 Q76 66 100 60" fill="none" stroke={T.goldEdge} strokeWidth="4" />
          </>
        )}
      </svg>
      <div style={{position: "absolute", left: prem ? 96 : -70, top: prem ? 4 : 10, transform: `rotate(${prem ? 8 : -8}deg)`, background: "#fff", border: `5px solid ${prem ? T.red : T.ink}`, borderRadius: 14, padding: "0 14px", fontFamily: FONT, fontWeight: 700, fontSize: 50, color: prem ? T.red : T.ink, whiteSpace: "nowrap"}}>{label}</div>
    </div>
  );
};

export const RigTest: React.FC = () => {
  const f = useCurrentFrame();
  const b = build(f);
  // Boots: pop into the hand when it starts holding, then fall to the floor when released and stay there
  const atDrop = build(BEATS.drop - 1).boots;
  const fall = interpolate(f, [BEATS.drop, BEATS.land], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.in(Easing.quad)});
  const bounce = f > BEATS.land ? Math.max(0, Math.sin(((f - BEATS.land) / 8) * Math.PI)) * 14 * Math.max(0, 1 - (f - BEATS.land) / 16) : 0;
  const BOOT_K = SCALE * 2.1;
  const BOOT = {w: 190 * BOOT_K, h: 200 * BOOT_K}; // drawn size on the canvas
  const bootAt = (kind: "cheap" | "prem") => {
    const inHand = b.boots[kind];
    const start = kind === "cheap" ? BEATS.cheapUp[0] + 8 : BEATS.premUp[0] + 8;
    if (f < start) return null;
    const pop = interpolate(f, [start, start + 8], [0.4, 1], {extrapolateRight: "clamp", easing: Easing.out(Easing.back(2))});
    if (inHand && f < BEATS.drop) return {x: inHand[0], y: inHand[1], rot: 0, scale: pop};
    const from = atDrop[kind]!;
    const floorX = kind === "cheap" ? X1 - 330 : X1 + 330;
    return {x: from[0] + (floorX - from[0]) * fall, y: from[1] + (FLOOR_Y - BOOT.h * 0.87 - from[1]) * fall - bounce, rot: (kind === "cheap" ? -1 : 1) * 10 * Math.sin(fall * Math.PI), scale: 1};
  };
  const cap = TL.captions.find((c) => f / FPS >= c.start - 0.05 && f / FPS <= c.end + 0.25);
  return (
    <AbsoluteFill style={{background: T.bg, fontFamily: FONT}}>
      <Audio src={staticFile("rig/test/voice.mp3")} />
      <div style={{position: "absolute", left: b.pose.x - 260, top: FLOOR_Y - 26, width: 520, height: 52, borderRadius: "50%", background: T.line}} />
      <RenRig pose={b.pose} />
      {(["cheap", "prem"] as const).map((k) => {
        const p = bootAt(k);
        if (!p) return null;
        return (
          <div key={k} style={{position: "absolute", left: p.x - BOOT.w * 0.4, top: p.y - BOOT.h * 0.1, width: 190, height: 250, transformOrigin: "40% 10%", transform: `scale(${BOOT_K * p.scale}) rotate(${p.rot}deg)`, zIndex: 505}}>
            <Boot kind={k} label={k === "cheap" ? "$60" : "$300"} />
          </div>
        );
      })}
      {cap ? (
        <div style={{position: "absolute", left: 60, right: 60, top: 150, textAlign: "center", zIndex: 2000}}>
          <span style={{display: "inline-block", background: "#fff", borderRadius: 28, padding: "14px 34px", fontSize: 64, fontWeight: 600, color: T.ink, lineHeight: 1.2, boxShadow: `0 0 0 4px ${T.line}`}}>{cap.text}</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const RIG_TEST_FRAMES = Math.ceil(TL.duration * FPS);
