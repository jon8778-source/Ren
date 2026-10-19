import {AbsoluteFill} from "remotion";
import {FONT} from "../fonts";
import {Boot, BOOT_GEOM} from "./Boot";
import {RenRig} from "./RenRig";
import {FLOOR, place, POSES, type Placed} from "./poses";

// Gate 3 check: each pose in the library as a 1080x1920 still (ren-pose, props {name}), and all eight on
// one contact sheet (ren-pose-sheet).
const BG = "#F3F5F8", INK = "#13233F", SHADOW = "#E3E7EE";

export const PlacedRen: React.FC<{placed: Placed; shadow?: boolean}> = ({placed, shadow = true}) => {
  const {pose, boots} = placed;
  return (
    <AbsoluteFill>
      {shadow ? <div style={{position: "absolute", left: pose.x - 290 * pose.scale, top: pose.y + FLOOR * pose.scale - 26 * pose.scale, width: 580 * pose.scale, height: 52 * pose.scale, borderRadius: "50%", background: SHADOW}} /> : null}
      <RenRig
        pose={{
          ...pose,
          props: boots.map((b) => ({
            at: [b.x, b.y] as [number, number], z: b.z,
            node: (
              <div style={{position: "absolute", left: 0, top: 0, transformOrigin: "0 0", transform: `rotate(${b.rot}deg) scale(${b.k}) translate(${-BOOT_GEOM[b.kind].shaftX}px, ${-BOOT_GEOM[b.kind].gripY}px)`}}>
                <Boot kind={b.kind} />
              </div>
            ),
          })),
        }}
      />
    </AbsoluteFill>
  );
};

const SCALE = 0.56, ROOT_Y = 1000;
export const PoseStill: React.FC<{name: string}> = ({name}) => (
  <AbsoluteFill style={{background: BG}}>
    <PlacedRen placed={place(POSES[name], 540, ROOT_Y, SCALE)} />
    <div style={{position: "absolute", left: 0, right: 0, top: 110, textAlign: "center", fontFamily: FONT, fontWeight: 600, fontSize: 64, color: INK}}>{POSES[name].label}</div>
  </AbsoluteFill>
);

const COLS = 4, CW = 1080 / 2, CH = 1920 / 2;
export const POSE_SHEET_SIZE = {width: CW * COLS, height: CH * 2};
export const PoseSheet: React.FC = () => (
  <AbsoluteFill style={{background: BG}}>
    {Object.keys(POSES).map((n, i) => (
      <div key={n} style={{position: "absolute", left: (i % COLS) * CW, top: Math.floor(i / COLS) * CH, width: CW, height: CH, overflow: "hidden", borderRight: "2px solid #dde2ea", borderBottom: "2px solid #dde2ea"}}>
        <div style={{position: "absolute", left: 0, top: 0, width: 1080, height: 1920, transform: "scale(0.5)", transformOrigin: "0 0"}}>
          <PoseStill name={n} />
        </div>
      </div>
    ))}
  </AbsoluteFill>
);
