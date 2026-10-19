import {AbsoluteFill, Audio, Easing, interpolate, spring, staticFile, useCurrentFrame} from "remotion";
import {FONT} from "../fonts";
import {Boot, BOOT_COLORS} from "./Boot";
import {clamp} from "./motion";
import {FLOOR, place, POSES} from "./poses";
import {RenRig, solve} from "./RenRig";
import TL from "./test-timeline.json";

// The boots clip with Ren as a still image, like the episodes: one full-body drawing per line, held perfectly
// still, swapped with the episodes' small pop; no lip sync. The movement comes from the graphics (price cards
// that pop in and count up, a VS badge, a "?", a Follow button) and from a camera that glides between Ren and
// the cards and pushes in slowly through each line. Same script, voice and timings as the rig clips. 60 fps.
const FPS = 30, OUT_PER_FRAME = 2;
const C = {...BOOT_COLORS, bg: "#F3F5F8"};
const s = (sec: number) => Math.round(sec * FPS);

// The world (canvas px): Ren stands on the left, the two price cards are stacked on the right
const REN = {x: 330, y: 1060, scale: 0.5};
const CARD = {cheap: {x: 790, y: 640}, prem: {x: 790, y: 1200}, w: 400, h: 470};
const VS = {x: 790, y: 920};
const FEET_Y = REN.y + FLOOR * REN.scale;
const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];

// Ren's still for each line: a library pose plus a face. Changes get the episodes' pop.
type Still = {at: number; pose: string; eyes?: string; mouth?: string; head?: number};
const STILLS: Still[] = [
  {at: 0, pose: "neutral", mouth: "smile"},
  {at: s(1.6), pose: "wave", eyes: "happy", mouth: "smile"},
  {at: s(3.1), pose: "neutral", mouth: "smile"},
  {at: s(8.1), pose: "neutral", eyes: "closed", mouth: "wince", head: -5},
  {at: s(8.8), pose: "neutral", mouth: "closed", head: 3},
  {at: s(11.5), pose: "neutral", eyes: "happy", mouth: "smile"},
];

// Camera: [from frame, focus x, focus y, zoom]. The focus is put at the middle of the screen. It glides to each
// new shot over GLIDE frames, then pushes in slowly (PUSH per second) until the next one.
const SHOTS: [number, number, number, number][] = [
  [0, 540, 900, 1.0],              // wide: Ren slides in
  [s(1.45), 360, 700, 1.45],       // Ren, waving
  [s(3.0), 760, 660, 1.5],         // the $60 card
  [s(6.0), 760, 1210, 1.5],        // the $300 card
  [s(8.1), 330, 470, 2.3],         // close-up: the wince
  [s(8.8), 560, 920, 1.0],         // wide: Ren and both cards, VS
  [s(11.4), 560, 860, 1.06],       // Ren and both cards for the last line, slow push
];
const GLIDE = 18, PUSH = 0.025;
const glide = Easing.bezier(0.45, 0, 0.25, 1);
const cameraAt = (f: number) => {
  let i = 0;
  while (i + 1 < SHOTS.length && f >= SHOTS[i + 1][0]) i++;
  const [start, fx, fy, z] = SHOTS[i];
  const push = 1 + PUSH * ((f - start) / FPS);
  const fast = i === 4 ? 8 : GLIDE; // the wince is a quick move in
  if (i === 0 || f >= start + fast) return {fx, fy, z: z * push};
  const [, px, py, pz] = SHOTS[i - 1];
  const prevPush = 1 + PUSH * ((start - SHOTS[i - 1][0]) / FPS);
  const t = glide((f - start) / fast);
  return {fx: px + (fx - px) * t, fy: py + (fy - py) * t, z: pz * prevPush + (z * push - pz * prevPush) * t};
};

const pop = (f: number, at: number) => (f < at ? 0 : spring({frame: f - at, fps: FPS, config: {damping: 12, stiffness: 180}}));

const Card: React.FC<{kind: "cheap" | "prem"; f: number; at: number}> = ({kind, f, at}) => {
  const k = pop(f, at);
  if (k <= 0) return null;
  const price = kind === "cheap" ? 60 : 300;
  const shown = Math.round(price * interpolate(f, [at + 6, at + 26], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)}));
  const p = CARD[kind];
  const accent = kind === "cheap" ? C.ink : C.red;
  return (
    <div style={{position: "absolute", left: p.x - CARD.w / 2, top: p.y - CARD.h / 2, width: CARD.w, height: CARD.h, background: "#fff", borderRadius: 36, boxShadow: `0 0 0 5px ${C.line}`, transform: `scale(${k})`, transformOrigin: "50% 50%"}}>
      <div style={{position: "absolute", left: "50%", top: 40, transform: "translateX(-50%) scale(1.25)", transformOrigin: "50% 0"}}>
        <Boot kind={kind} tag={false} />
      </div>
      <div style={{position: "absolute", left: 0, right: 0, bottom: 34, textAlign: "center", fontFamily: FONT, fontWeight: 700, fontSize: 92, color: accent}}>${shown}</div>
    </div>
  );
};

export const StillExplainer: React.FC = () => {
  const f = useCurrentFrame() / OUT_PER_FRAME;
  const cam = cameraAt(f);
  // Ren: slides in from the left, then holds; one small pop on each change of still
  const enter = spring({frame: f, fps: FPS, config: {damping: 14, stiffness: 120}});
  let si = 0;
  while (si + 1 < STILLS.length && f >= STILLS[si + 1].at) si++;
  const st = STILLS[si];
  const pp = si > 0 ? 1 - pop(f, st.at) : 0;
  const def = POSES[st.pose];
  const placed = place({...def, face: {...def.face, eyes: st.eyes, mouth: st.mouth}}, REN.x, REN.y, REN.scale, {angles: {head: st.head ?? 0}});
  const head = apply(solve(placed.pose).frames.head, [0, -1500]); // top of the head
  const vs = pop(f, s(9.0));
  const q = pop(f, s(9.4)) * interpolate(f, [s(11.2), s(11.4)], [1, 0], clamp);
  const follow = pop(f, s(13.0));
  const cap = TL.captions.find((c) => f / FPS >= c.start - 0.05 && f / FPS <= c.end + 0.25);
  return (
    <AbsoluteFill style={{background: C.bg, fontFamily: FONT}}>
      <Audio src={staticFile("rig/test/voice.mp3")} />
      <AbsoluteFill style={{transformOrigin: "0 0", transform: `translate(${540 - cam.fx * cam.z}px, ${960 - cam.fy * cam.z}px) scale(${cam.z})`}}>
        <div style={{position: "absolute", left: REN.x - 150, top: FEET_Y - 14, width: 300, height: 28, borderRadius: "50%", background: C.line, opacity: enter}} />
        <AbsoluteFill style={{opacity: enter, transform: `translateX(${(1 - enter) * -420}px)`}}>
          <AbsoluteFill style={{transformOrigin: `${REN.x}px ${FEET_Y}px`, transform: `scale(${1 + pp * 0.04}, ${1 - pp * 0.04})`}}>
            <RenRig pose={placed.pose} />
          </AbsoluteFill>
        </AbsoluteFill>
        <Card kind="cheap" f={f} at={s(3.15)} />
        <Card kind="prem" f={f} at={s(6.15)} />
        {vs > 0 ? (
          <div style={{position: "absolute", left: VS.x - 70, top: VS.y - 70, width: 140, height: 140, borderRadius: 70, background: C.ink, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT, fontWeight: 700, fontSize: 64, transform: `scale(${vs})`, zIndex: 900}}>VS</div>
        ) : null}
        {q > 0 ? (
          <div style={{position: "absolute", left: head[0] + 110, top: head[1] - 60, width: 130, height: 130, borderRadius: 65, background: C.gold, border: `6px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT, fontWeight: 700, fontSize: 92, color: C.ink, transform: `scale(${q})`, zIndex: 900}}>?</div>
        ) : null}
      </AbsoluteFill>
      {follow > 0 ? (
        <div style={{position: "absolute", left: 0, right: 0, bottom: 60, textAlign: "center", zIndex: 2000}}>
          <span style={{display: "inline-block", background: C.red, color: "#fff", borderRadius: 50, padding: "18px 54px", fontSize: 60, fontWeight: 700, transform: `scale(${follow})`}}>Follow for part 2</span>
        </div>
      ) : null}
      {cap ? (
        <div style={{position: "absolute", left: 60, right: 60, top: 150, textAlign: "center", zIndex: 2000}}>
          <span style={{display: "inline-block", background: "#fff", borderRadius: 28, padding: "14px 34px", fontSize: 64, fontWeight: 600, color: C.ink, lineHeight: 1.2, boxShadow: `0 0 0 4px ${C.line}`}}>{cap.text}</span>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const STILL_EXPLAINER_FPS = FPS * OUT_PER_FRAME;
export const STILL_EXPLAINER_OUT_FRAMES = Math.ceil(TL.duration * FPS) * OUT_PER_FRAME;
