import {AbsoluteFill, Img, staticFile} from "remotion";
import rigData from "./ren-rig.json";

// Ren as a cut-out puppet. Every part is placed by forward kinematics from rig.json (built by
// rig/make_rig.py): frame = parentFrame * T(attach) * R(angle) * S(scale ratio); image = frame * R(-bone+90) * T(-pivot).
// Angles are degrees, 0 = the bone hanging straight down from its parent, positive = clockwise.

type Part = {src: string; w: number; h: number; pivot: number[]; parent: string | null; attach: number[] | null; scale: number; bone: number; z: number; slot?: string; width?: number; grip?: number[]; front?: number[][]};
const PARTS = rigData.parts as unknown as Record<string, Part>;
const COLORS = rigData.colors;

export type RigPose = {
  x: number;            // root (hip centre) position on the canvas
  y: number;
  scale: number;        // canvas px per rig unit
  angles?: Partial<Record<string, number>>;
  slots?: Partial<Record<string, string>>; // slot -> part name, e.g. {"mouth": "mouth-o"}
  offsets?: Partial<Record<string, [number, number]>>; // extra translation in the parent's image px (brow raise)
  z?: Partial<Record<string, number>>;     // layer overrides, e.g. bring an arm in front of the torso
  // Drawn in a part's frame, or on the canvas when part is omitted. A hold hand's fingers ("front" in rig.json)
  // are drawn a second time at the hand's layer + 0.4, so a prop at the hand's layer + 0.2 sits between them.
  props?: {part?: string; at: [number, number]; node: React.ReactNode; z: number}[];
};

export const DEFAULT_SLOTS: Record<string, string> = {
  "eye-r": "eye-neutral-r", "eye-l": "eye-neutral-l", "brow-r": "brow-r", "brow-l": "brow-l",
  mouth: "mouth-closed", "hand-r": "hand-relaxed-r", "hand-l": "hand-relaxed-l",
};

type M = [number, number, number, number, number, number]; // a b c d e f (CSS matrix)
const mul = (m: M, n: M): M => [m[0] * n[0] + m[2] * n[1], m[1] * n[0] + m[3] * n[1], m[0] * n[2] + m[2] * n[3], m[1] * n[2] + m[3] * n[3], m[0] * n[4] + m[2] * n[5] + m[4], m[1] * n[4] + m[3] * n[5] + m[5]];
const T = (x: number, y: number): M => [1, 0, 0, 1, x, y];
const R = (deg: number): M => {
  const r = (deg * Math.PI) / 180;
  return [Math.cos(r), Math.sin(r), -Math.sin(r), Math.cos(r), 0, 0];
};
const S = (s: number): M => [s, 0, 0, s, 0, 0];
const apply = (m: M, p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];

export const solve = (pose: RigPose) => {
  const slots = {...DEFAULT_SLOTS, ...pose.slots};
  const frames: Record<string, M> = {};
  const images: Record<string, M> = {};
  const frameOf = (name: string): M => {
    if (frames[name]) return frames[name];
    const p = PARTS[name];
    const a = pose.angles?.[name] ?? 0;
    let f: M;
    if (!p.parent) {
      f = mul(mul(T(pose.x, pose.y), S(pose.scale * p.scale)), R(a));
    } else {
      const par = PARTS[p.parent];
      const pf = frameOf(p.parent);
      const off = pose.offsets?.[name] ?? [0, 0];
      // attach point in the parent's frame: undo the parent's bone rotation and pivot
      const local = apply(mul(R(-(par.bone - 90)), T(-par.pivot[0], -par.pivot[1])), [p.attach![0] + off[0], p.attach![1] + off[1]]);
      f = mul(mul(mul(pf, T(local[0], local[1])), R(a)), S(p.scale / par.scale));
    }
    frames[name] = f;
    images[name] = mul(mul(f, R(-(p.bone - 90))), T(-p.pivot[0], -p.pivot[1]));
    return f;
  };
  const visible = Object.keys(PARTS).filter((n) => !PARTS[n].slot || slots[PARTS[n].slot!] === n);
  visible.forEach(frameOf);
  return {visible, frames, images, slots};
};

const css = (m: M) => `matrix(${m.map((v) => v.toFixed(5)).join(",")})`;

export const RenRig: React.FC<{pose: RigPose; joints?: boolean; debug?: boolean; only?: string[]}> = ({pose, joints = true, debug = false, only}) => {
  const solved = solve(pose);
  const {frames, images} = solved;
  const visible = only ? solved.visible.filter((n) => only.includes(n)) : solved.visible;
  const layer = (n: string) => pose.z?.[n] ?? PARTS[n].z;
  // Joint caps: a sleeve/pants-coloured disc behind each elbow and knee, so a bend never opens a gap
  const caps = joints
    ? (["forearm-r", "forearm-l", "shin-r", "shin-l"] as const).filter((n) => visible.includes(n)).map((n) => {
        const leg = n.startsWith("shin");
        const p = PARTS[n];
        const r = leg ? 52 : ((PARTS[n].width ?? 100) / 2) * 0.92;
        return {key: `cap-${n}`, m: frames[n], r, color: leg ? COLORS.pants : COLORS.sleeve, z: layer(n) - 0.5, p};
      })
    : [];
  return (
    <AbsoluteFill>
      {caps.map((c) => (
        <svg key={c.key} width={c.r * 2} height={c.r * 2} style={{position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `${css(c.m)} translate(${-c.r}px, ${-c.r}px)`, zIndex: Math.round(c.z * 10), overflow: "visible"}}>
          <circle cx={c.r} cy={c.r} r={c.r} fill={c.color} />
        </svg>
      ))}
      {visible.map((n) => (
        <Img key={n} src={staticFile(PARTS[n].src)} style={{position: "absolute", left: 0, top: 0, width: PARTS[n].w, height: PARTS[n].h, transformOrigin: "0 0", transform: css(images[n]), zIndex: Math.round(layer(n) * 10)}} />
      ))}
      {visible.filter((n) => PARTS[n].front).map((n) => (
        <Img key={`${n}-front`} src={staticFile(PARTS[n].src)} style={{position: "absolute", left: 0, top: 0, width: PARTS[n].w, height: PARTS[n].h, transformOrigin: "0 0", transform: css(images[n]), zIndex: Math.round((layer(n) + 0.4) * 10), clipPath: `polygon(${PARTS[n].front!.map(([x, y]) => `${x}px ${y}px`).join(", ")})`}} />
      ))}
      {debug
        ? visible.filter((n) => PARTS[n].parent && !/^(eye|brow|mouth|nose|glasses)/.test(n)).map((n) => {
            const [x, y] = apply(frames[n], [0, 0]);
            return <div key={`dot-${n}`} style={{position: "absolute", left: x - 9, top: y - 9, width: 18, height: 18, borderRadius: 9, background: "#E23D3D", border: "3px solid #fff", zIndex: 9999}} />;
          })
        : null}
      {(pose.props ?? []).map((pr, i) => (
        <div key={`prop${i}`} style={{position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `${pr.part ? css(frames[pr.part]) + " " : ""}translate(${pr.at[0]}px, ${pr.at[1]}px)`, zIndex: Math.round(pr.z * 10)}}>{pr.node}</div>
      ))}
    </AbsoluteFill>
  );
};

// Neutral standing pose: arms hanging close to the body, wrists turned in a little so the fingers point
// straight down towards the thighs, legs straight
export const NEUTRAL: Omit<RigPose, "x" | "y" | "scale"> = {
  angles: {"upperarm-r": 6, "upperarm-l": -6, "forearm-r": -3, "forearm-l": 3, "hand-relaxed-r": -5, "hand-relaxed-l": 5},
};

export const RigStill: React.FC<{background?: string; scale?: number; debug?: boolean}> = ({background = "#F3F5F8", scale = 0.72, debug = false}) => (
  <AbsoluteFill style={{background}}>
    <RenRig pose={{x: 540, y: 1060, scale, ...NEUTRAL}} debug={debug} />
  </AbsoluteFill>
);

// Hand-swap check: four copies, each with a raised arm and a different sheet hand
const HAND_TESTS: {label: string; pose: Omit<RigPose, "x" | "y" | "scale">}[] = [
  {label: "open (wave)", pose: {angles: {...NEUTRAL.angles, "upperarm-r": 150, "forearm-r": -20, "hand-open-r": 10}, slots: {"hand-r": "hand-open-r", mouth: "mouth-smile"}}},
  {label: "hold", pose: {angles: {...NEUTRAL.angles, "upperarm-r": 70, "forearm-r": 30, "hand-hold-r": 0}, slots: {"hand-r": "hand-hold-r"}}},
  {label: "point", pose: {angles: {...NEUTRAL.angles, "upperarm-l": -60, "forearm-l": -30, "hand-point-l": 0}, slots: {"hand-l": "hand-point-l", "eye-r": "eye-surprised-r", "eye-l": "eye-surprised-l"}}},
  {label: "thumbs up", pose: {angles: {...NEUTRAL.angles, "upperarm-l": -35, "forearm-l": -130, "hand-thumbsup-l": -15}, slots: {"hand-l": "hand-thumbsup-l", "eye-r": "eye-happy-r", "eye-l": "eye-happy-l", mouth: "mouth-smile"}}},
];
export const HandTest: React.FC = () => (
  <AbsoluteFill style={{background: "#F3F5F8"}}>
    {HAND_TESTS.map((t, i) => (
      <AbsoluteFill key={i}>
        <RenRig pose={{x: 135 + (i % 2) * 540 + 135, y: 560 + Math.floor(i / 2) * 900, scale: 0.36, ...t.pose}} />
        <div style={{position: "absolute", left: (i % 2) * 540, width: 540, top: 120 + Math.floor(i / 2) * 900, textAlign: "center", fontSize: 40, fontFamily: "sans-serif", color: "#13233F"}}>{t.label}</div>
      </AbsoluteFill>
    ))}
  </AbsoluteFill>
);
