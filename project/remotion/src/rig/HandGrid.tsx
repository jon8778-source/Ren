import {AbsoluteFill} from "remotion";
import {RenRig, RigPose, solve} from "./RenRig";

// Gate 2 check: every hand on its forearm, with the forearm bent 0, 45 and 90 degrees at the elbow (inward,
// the way an elbow bends). Each hand is at its rest angle (wrist angle 0). With guides on: the forearm's
// axis extended through the hand (red) and the wrist anchor (red dot).

const HANDS = ["relaxed", "open", "point", "pointout", "thumbsup", "fist", "hold"];
const ANGLES = [0, 45, 90];
const CELL_W = 420, CELL_H = 420, LABEL_W = 220, HEADER_H = 70, SCALE = 0.62;
export const HAND_GRID_SIZE = {width: LABEL_W + CELL_W * 6, height: HEADER_H + CELL_H * HANDS.length};

const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];
const text = {position: "absolute", fontFamily: "sans-serif", color: "#13233F", fontWeight: 600, textAlign: "center"} as const;

export const HandGrid: React.FC<{guides?: boolean}> = ({guides = false}) => (
  <AbsoluteFill style={{background: "#F3F5F8"}}>
    {["r", "l"].flatMap((side, si) =>
      ANGLES.map((a, ai) => (
        <div key={`${side}${a}`} style={{...text, left: LABEL_W + (si * 3 + ai) * CELL_W, width: CELL_W, top: 14, fontSize: 30}}>
          {side === "r" ? "Ren's right" : "Ren's left"} {a}°
        </div>
      )),
    )}
    {HANDS.flatMap((h, hi) => [
      <div key={`l${h}`} style={{...text, left: 0, width: LABEL_W, top: HEADER_H + hi * CELL_H + CELL_H / 2 - 20, fontSize: 34}}>{h}</div>,
      ...["r", "l"].flatMap((side, si) =>
        ANGLES.map((a, ai) => {
          const fa = `forearm-${side}`, hand = `hand-${h}-${side}`;
          const sign = side === "r" ? -1 : 1; // inward: Ren's right forearm swings to screen right
          const pose: RigPose = {x: 0, y: 0, scale: SCALE, angles: {[fa]: sign * a}, slots: {[`hand-${side}`]: hand}};
          const {frames} = solve(pose);
          const f = frames[fa], hf = frames[hand];
          const elbow = apply(f, [0, 0]);
          const left = LABEL_W + (si * 3 + ai) * CELL_W, top = HEADER_H + hi * CELL_H;
          const ex = left + (a === 0 ? CELL_W / 2 : side === "r" ? 60 : CELL_W - 60), ey = top + 50;
          const dx = ex - elbow[0], dy = ey - elbow[1];
          const dir = [f[2], f[3]].map((v) => v / Math.hypot(f[2], f[3]));
          const wr = apply(hf, [0, 0]);
          return (
            <div key={`${h}${side}${a}`} style={{position: "absolute", left, top, width: CELL_W, height: CELL_H, overflow: "hidden", borderRight: "2px solid #dde2ea", borderBottom: "2px solid #dde2ea"}}>
              <div style={{position: "absolute", left: -left, top: -top, width: HAND_GRID_SIZE.width, height: HAND_GRID_SIZE.height}}>
                <AbsoluteFill style={{transform: `translate(${dx}px, ${dy}px)`}}>
                  <RenRig pose={pose} only={[fa, hand]} />
                </AbsoluteFill>
                {guides ? (
                  <svg style={{position: "absolute", left: 0, top: 0, zIndex: 9999}} width={HAND_GRID_SIZE.width} height={HAND_GRID_SIZE.height}>
                    <line x1={ex} y1={ey} x2={ex + dir[0] * 520} y2={ey + dir[1] * 520} stroke="#E23D3D" strokeWidth={2.5} />
                    <circle cx={wr[0] + dx} cy={wr[1] + dy} r={7} fill="#E23D3D" stroke="#fff" strokeWidth={2} />
                  </svg>
                ) : null}
              </div>
            </div>
          );
        }),
      ),
    ])}
  </AbsoluteFill>
);
