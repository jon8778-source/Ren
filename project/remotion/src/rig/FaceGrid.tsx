import {AbsoluteFill} from "remotion";
import rigData from "./ren-rig.json";
import {NEUTRAL, RenRig, RigPose, solve} from "./RenRig";

// Gate 1 check: Ren's head with each eye set (closed mouth) and each mouth (neutral eyes).
// With guides on: red crosses at the eye and mouth anchors, and ticks marking 40% of the face width.

const FACE = (rigData as unknown as {face: {face_width: number; mouth_anchor: number[]}}).face;
const EYES = ["neutral", "closed", "happy", "wide", "surprised", "angry", "sleepy"];
const MOUTHS = ["closed", "smile", "wince", "open", "wide", "o"];
const CELL_W = 480, CELL_H = 600, LABEL_H = 64, COLS = 4, SCALE = 1.25;
const HEAD_CENTRE = [781, 1000]; // head px, middle of the face

type Cell = {label: string; slots: RigPose["slots"]};
const CELLS: Cell[] = [
  ...EYES.map((e) => ({label: `eyes: ${e}`, slots: {"eye-r": `eye-${e}-r`, "eye-l": `eye-${e}-l`}})),
  ...MOUTHS.map((m) => ({label: `mouth: ${m}`, slots: {mouth: `mouth-${m}`}})),
];
export const FACE_GRID_SIZE = {width: CELL_W * COLS, height: CELL_H * Math.ceil(CELLS.length / COLS)};

const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];

const Cross: React.FC<{at: number[]; size?: number}> = ({at, size = 14}) => (
  <svg style={{position: "absolute", left: at[0] - size, top: at[1] - size, zIndex: 9999}} width={size * 2} height={size * 2}>
    <path d={`M0 ${size}H${size * 2}M${size} 0V${size * 2}`} stroke="#E23D3D" strokeWidth={3} />
  </svg>
);

export const FaceGrid: React.FC<{guides?: boolean}> = ({guides = false}) => (
  <AbsoluteFill style={{background: "#F3F5F8"}}>
    {CELLS.map((c, i) => {
      const pose: RigPose = {x: 0, y: 0, scale: SCALE, ...NEUTRAL, slots: c.slots};
      const {images, visible} = solve(pose);
      const head = images.head;
      const hc = apply(head, HEAD_CENTRE);
      const cx = (i % COLS) * CELL_W, cy = Math.floor(i / COLS) * CELL_H;
      const dx = CELL_W / 2 - hc[0], dy = LABEL_H + (CELL_H - LABEL_H) / 2 - hc[1];
      const at = (name: string, p: number[]) => {
        const q = apply(images[name], p);
        return [q[0] + dx, q[1] + dy];
      };
      const chin = apply(head, [781, 1700])[1] + dy;
      const mouthAt = apply(head, FACE.mouth_anchor);
      const half = (FACE.face_width * 0.2) * Math.hypot(head[0], head[1]);
      const eyeCentres = visible.filter((n) => n.startsWith("eye-")).map((n) => {
        const p = (rigData.parts as Record<string, {pivot: number[]}>)[n].pivot;
        return at(n, p);
      });
      return (
        <div key={i} style={{position: "absolute", left: cx, top: cy, width: CELL_W, height: CELL_H, overflow: "hidden", borderRight: "2px solid #dde2ea", borderBottom: "2px solid #dde2ea"}}>
          <div style={{position: "absolute", left: 0, top: LABEL_H, width: CELL_W, height: chin - LABEL_H, overflow: "hidden"}}>
            <div style={{position: "absolute", left: 0, top: -LABEL_H, width: CELL_W, height: chin}}>
            <AbsoluteFill style={{transform: `translate(${dx}px, ${dy}px)`}}>
              <RenRig pose={pose} />
            </AbsoluteFill>
            {guides ? eyeCentres.map((p, j) => <Cross key={j} at={p} size={8} />) : null}
            {guides ? (
              <>
                <Cross at={[mouthAt[0] + dx, mouthAt[1] + dy]} size={8} />
                {[-1, 1].map((s) => (
                  <div key={s} style={{position: "absolute", left: mouthAt[0] + dx + s * half - 1.5, top: mouthAt[1] + dy - 40, width: 3, height: 80, background: "#E23D3D", zIndex: 9999}} />
                ))}
              </>
            ) : null}
            </div>
          </div>
          <div style={{position: "absolute", left: 0, right: 0, top: 12, textAlign: "center", fontSize: 32, fontWeight: 600, fontFamily: "sans-serif", color: "#13233F"}}>{c.label}</div>
        </div>
      );
    })}
  </AbsoluteFill>
);
