import rigData from "./ren-rig.json";
import {BOOT_GEOM, BOOT_RIG, type BootKind} from "./Boot";
import {DEFAULT_SLOTS, type RigPose, solve} from "./RenRig";

// Ren's pose library. A pose sets joint angles (degrees, 0 = hanging straight down from the parent,
// positive = clockwise, so positive swings Ren's right arm (screen left) outward and his left arm inward),
// a hand per side with its wrist angle, a face, and any boots he holds or that stand on the floor.
// Every arm keeps a bend at the elbow; none is held out straight.

const PARTS = rigData.parts as unknown as Record<string, {bone: number; grip?: number[]; w: number; h: number}>;

export type HandSpec = {part: string; angle?: number; tilt?: number}; // angle: wrist bend; tilt: hand image's world tilt instead
export type Face = {eyes?: string; mouth?: string; brows?: number}; // brows: vertical brow offset (head px, negative = raised)
export type PoseDef = {
  label: string;
  angles: Partial<Record<string, number>>;
  hands: {r: HandSpec; l: HandSpec};
  face?: Face;
  held?: Partial<Record<"r" | "l", BootKind>>;
  floor?: Partial<Record<"r" | "l", BootKind>>; // boots standing beside Ren's right (screen left) / left foot
};

const relaxed = {r: {part: "hand-relaxed-r"}, l: {part: "hand-relaxed-l"}};
const ARMS_DOWN = {"upperarm-r": 6, "forearm-r": -8, "upperarm-l": -6, "forearm-l": 8};
const HOLD_R = {"upperarm-r": 12, "forearm-r": 74}; // upper arm close to the body, elbow bent so the forearm is about level
const HOLD_L = {"upperarm-l": -12, "forearm-l": -74};

export const POSES: Record<string, PoseDef> = {
  neutral: {label: "1. Neutral standing", angles: {...ARMS_DOWN}, hands: relaxed},
  wave: {
    label: "2. Waving",
    angles: {...ARMS_DOWN, "upperarm-r": 98, "forearm-r": 66, head: -2},
    hands: {r: {part: "hand-open-r", tilt: -6}, l: relaxed.l},
    face: {eyes: "happy", mouth: "smile", brows: -25},
  },
  holdOne: {
    label: "3. Holding one boot",
    angles: {...ARMS_DOWN, ...HOLD_R},
    hands: {r: {part: "hand-holdout-r", tilt: 0}, l: relaxed.l},
    held: {r: "cheap"},
  },
  holdBoth: {
    label: "4. Holding both boots",
    angles: {...HOLD_R, ...HOLD_L},
    hands: {r: {part: "hand-holdout-r", tilt: 0}, l: {part: "hand-holdout-l", tilt: 0}},
    held: {r: "cheap", l: "prem"},
  },
  pointFloor: {
    label: "5. Pointing at a boot on the floor",
    angles: {...ARMS_DOWN, "upperarm-l": -18, "forearm-l": -42, head: 4},
    hands: {r: relaxed.r, l: {part: "hand-pointout-l", angle: 28}},
    face: {brows: -40},
    floor: {r: "cheap", l: "prem"},
  },
  thumbsUp: {
    label: "6. Thumbs-up",
    angles: {...ARMS_DOWN, "upperarm-l": -10, "forearm-l": 128},
    hands: {r: relaxed.r, l: {part: "hand-thumbsup-l", tilt: 0}},
    face: {eyes: "happy", mouth: "smile"},
  },
  wince: {
    label: "7. Wince",
    angles: {"upperarm-r": 10, "forearm-r": 10, "upperarm-l": -10, "forearm-l": -10, head: -5},
    hands: {r: {part: "hand-fist-r", angle: 0}, l: {part: "hand-fist-l", angle: 0}}, // knuckles down, along the forearm
    face: {eyes: "closed", mouth: "wince", brows: 20},
  },
  celebrate: {
    label: "8. Celebrate",
    angles: {"upperarm-r": 138, "forearm-r": 28, "upperarm-l": -138, "forearm-l": -28},
    hands: {r: {part: "hand-fist-r", angle: 0}, l: {part: "hand-fist-l", angle: 0}}, // knuckles up, along the forearm
    face: {eyes: "happy", mouth: "smile", brows: -35},
  },
  // Clip-only poses (not in the gate 3 sheet)
  setDown: {
    label: "Setting both boots down (with a squat)",
    angles: {"upperarm-r": 22, "forearm-r": 14, "upperarm-l": -22, "forearm-l": -14},
    hands: {r: {part: "hand-holdout-r", tilt: 0}, l: {part: "hand-holdout-l", tilt: 0}},
    held: {r: "cheap", l: "prem"},
  },
  pointBoth: {
    label: "Pointing at both boots on the floor",
    angles: {"upperarm-r": 18, "forearm-r": 42, "upperarm-l": -18, "forearm-l": -42},
    hands: {r: {part: "hand-pointout-r", angle: -28}, l: {part: "hand-pointout-l", angle: 28}},
    face: {brows: -40},
    floor: {r: "cheap", l: "prem"},
  },
};
export const SHEET_POSES = ["neutral", "wave", "holdOne", "holdBoth", "pointFloor", "thumbsUp", "wince", "celebrate"];

const apply = (m: number[], p: number[]) => [m[0] * p[0] + m[2] * p[1] + m[4], m[1] * p[0] + m[3] * p[1] + m[5]];

// The wrist angle that gives a hand image a chosen world tilt, given the arm angles above it
export const tiltToAngle = (hand: string, parentWorld: number, tilt: number) => PARTS[hand].bone - 90 + tilt - parentWorld;

// Floor: the bottom of the shoes in the neutral pose, in rig units below the root (hip centre)
const neutralSolve = solve({x: 0, y: 0, scale: 1, angles: POSES.neutral.angles});
export const FLOOR = Math.max(...["shoe-r", "shoe-l"].map((n) => apply(neutralSolve.images[n], [PARTS[n].w / 2, PARTS[n].h - 6])[1]));
const SHOE_X = {
  r: Math.min(...[0, PARTS["shoe-r"].h].map((y) => apply(neutralSolve.images["shoe-r"], [0, y])[0])),
  l: Math.max(...[0, PARTS["shoe-l"].h].map((y) => apply(neutralSolve.images["shoe-l"], [PARTS["shoe-l"].w, y])[0])),
};
const FLOOR_GAP = 70; // rig units between a shoe and a floor boot

// Boots on Ren's right (screen left) are flipped, so every toe points away from him.
export const flipFor = (side: "r" | "l") => side === "r";

// Where a floor boot's shaft centre stands (rig units from the root), with its outline FLOOR_GAP clear of the shoe
export const floorBoot = (side: "r" | "l", kind: BootKind) => {
  const g = BOOT_GEOM[kind];
  const x = side === "r" ? SHOE_X.r - FLOOR_GAP - (g.shaftX - g.x0) * BOOT_RIG : SHOE_X.l + FLOOR_GAP + (g.shaftX - g.x0) * BOOT_RIG;
  return {x, top: FLOOR - g.soleY * BOOT_RIG};
};

export type Placed = {pose: RigPose; boots: {kind: BootKind; x: number; y: number; rot: number; k: number; z: number; flip: boolean}[]};

// A pose definition placed on the canvas: root at (x, y), `scale` canvas px per rig unit.
// Optional overrides let a timeline blend angles and swap faces without redefining the pose.
export const place = (def: PoseDef, x: number, y: number, scale: number, extra?: Partial<RigPose>): Placed => {
  const angles: Record<string, number> = {...(def.angles as Record<string, number>), ...(extra?.angles as Record<string, number>)};
  const world = (side: "r" | "l") => (angles.torso ?? 0) + (angles[`upperarm-${side}`] ?? 0) + (angles[`forearm-${side}`] ?? 0);
  for (const side of ["r", "l"] as const) {
    const h = def.hands[side];
    angles[h.part] = h.tilt !== undefined ? tiltToAngle(h.part, world(side), h.tilt) : (h.angle ?? 0);
  }
  const face = def.face ?? {};
  const eyes = face.eyes ?? "neutral";
  const brow = face.brows ?? 0;
  const pose: RigPose = {
    x, y, scale,
    angles,
    slots: {...DEFAULT_SLOTS, "hand-r": def.hands.r.part, "hand-l": def.hands.l.part, mouth: `mouth-${face.mouth ?? "closed"}`, "eye-r": `eye-${eyes}-r`, "eye-l": `eye-${eyes}-l`, ...extra?.slots},
    offsets: {"brow-r": [0, brow], "brow-l": [0, brow], ...extra?.offsets},
    z: extra?.z,
  };
  const sol = solve(pose);
  const boots: Placed["boots"] = [];
  for (const side of ["r", "l"] as const) {
    const kind = def.held?.[side];
    if (kind) {
      const hand = def.hands[side].part;
      const g = apply(sol.images[hand], PARTS[hand].grip!);
      const hm = sol.images[hand];
      const tilt = (Math.atan2(hm[1], hm[0]) * 180) / Math.PI; // the hand image's world rotation
      boots.push({kind, x: g[0], y: g[1], rot: tilt, k: scale * BOOT_RIG, z: (pose.z?.[hand] ?? 51) + 0.2, flip: flipFor(side)});
    }
    const fk = def.floor?.[side];
    if (fk) {
      const fb = floorBoot(side, fk);
      const g = BOOT_GEOM[fk];
      boots.push({kind: fk, x: x + fb.x * scale, y: y + (fb.top + g.gripY * BOOT_RIG) * scale, rot: 0, k: scale * BOOT_RIG, z: 49, flip: flipFor(side)});
    }
  }
  return {pose, boots};
};
