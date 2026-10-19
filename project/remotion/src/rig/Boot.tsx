import {FONT} from "../fonts";

// The two test-clip boots, drawn flat in code (boot units: a 190 x 200 box). Cheap: thin gold boot, flat
// sole. Premium: navy, chunky sole, gold laces. Each carries its price tag above its shaft.
export type BootKind = "cheap" | "prem";

export const BOOT_COLORS = {ink: "#13233F", gold: "#F5B82E", goldEdge: "#C98A0B", red: "#E23D3D", line: "#E3E7EE", muted: "#7A8496", outline: "#1d1f26"};
const C = BOOT_COLORS;

// Shaft centre line (x), the height a hand grips it at (y), sole bottom (y) and the boot's left and right
// edges (x). Boot units, toe pointing right; a flipped boot is mirrored about its shaft centre line.
export const BOOT_GEOM: Record<BootKind, {shaftX: number; gripY: number; soleY: number; x0: number; x1: number}> = {
  cheap: {shaftX: 78, gripY: 78, soleY: 182, x0: 36, x1: 168},
  prem: {shaftX: 65, gripY: 78, soleY: 197, x0: 20, x1: 184},
};
export const BOOT_RIG = 1.7; // rig units per boot unit

export const Boot: React.FC<{kind: BootKind; tag?: boolean; flip?: boolean}> = ({kind, tag = true, flip = false}) => {
  const prem = kind === "prem";
  return (
    <div style={{position: "relative", width: 190, height: 200}}>
      <svg width="190" height="200" viewBox="0 0 190 200" style={{overflow: "visible", position: "absolute", left: 0, top: 0, transformOrigin: `${BOOT_GEOM[kind].shaftX}px 0`, transform: flip ? "scaleX(-1)" : undefined}}>
        {prem ? (
          <>
            <path d="M48 8 H112 V118 Q150 120 172 142 Q182 154 178 166 H30 V8 Z" transform="translate(-6 0)" fill={C.ink} stroke={C.outline} strokeWidth="7" strokeLinejoin="round" />
            <rect x="20" y="164" width="164" height="30" rx="10" fill={C.line} stroke={C.outline} strokeWidth="7" />
            <path d="M28 178 H176" stroke={C.muted} strokeWidth="4" strokeDasharray="8 7" />
            {[34, 58, 82, 106].map((y) => <path key={y} d={`M52 ${y} L92 ${y + 10} M92 ${y} L52 ${y + 10}`} stroke={C.gold} strokeWidth="5" strokeLinecap="round" />)}
            <path d="M30 20 H106" stroke={C.goldEdge} strokeWidth="4" strokeDasharray="6 6" />
          </>
        ) : (
          <>
            <path d="M52 16 H104 V124 Q140 128 160 148 Q168 158 164 170 H40 V16 Z" fill={C.gold} stroke={C.outline} strokeWidth="6" strokeLinejoin="round" />
            <rect x="36" y="168" width="132" height="12" rx="5" fill={C.goldEdge} stroke={C.outline} strokeWidth="5" />
            <path d="M46 60 Q76 66 100 60" fill="none" stroke={C.goldEdge} strokeWidth="4" />
          </>
        )}
      </svg>
      {tag ? (
        <div style={{position: "absolute", bottom: 212, left: BOOT_GEOM[kind].shaftX, transform: `translateX(-50%) rotate(${prem ? 6 : -6}deg)`, background: "#fff", border: `5px solid ${prem ? C.red : C.ink}`, borderRadius: 14, padding: "0 14px", fontFamily: FONT, fontWeight: 700, fontSize: 46, color: prem ? C.red : C.ink, whiteSpace: "nowrap"}}>{prem ? "$300" : "$60"}</div>
      ) : null}
    </div>
  );
};
