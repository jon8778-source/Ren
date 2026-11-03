import React from "react";
import {useCurrentFrame, useVideoConfig} from "remotion";
import {renColors as C, renShape as S} from "../theme";

export type Expression = "neutral" | "happy" | "anxious" | "surprised";
export type Pose = "standing" | "driving" | "seated" | "holding-drink";
export type Pt = [number, number];
export type Arm = {elbow: Pt; wrist: Pt; open?: boolean};
export type HandProp = "none" | "suitcase" | "calculator" | "key";

export type RenProps = {
  expression?: Expression;
  mouthOpen?: number; // 0-1, usually from audio amplitude
  pose?: Pose;
  blink?: number; // 0 open, 1 closed
  sweat?: boolean;
  size?: number; // rendered height in px
  // Optional extras for scenes
  breathing?: boolean;
  lookX?: number; // pupils: -1 left .. 1 right
  lookY?: number;
  armL?: Arm; // viewer-left arm override
  armR?: Arm; // viewer-right arm override
  prop?: HandProp;
  tap?: number; // 0-1 calculator finger press
  showLegs?: boolean;
};

const W = 400;
const H = 700;
const lw = S.lineWidth;

const shoulderL: Pt = [S.headCx - S.shoulderX, S.shoulderY];
const shoulderR: Pt = [S.headCx + S.shoulderX, S.shoulderY];

const POSE_ARMS: Record<Pose, {l: Arm; r: Arm}> = {
  standing: {
    l: {elbow: [102, 405], wrist: [108, 488]},
    r: {elbow: [298, 405], wrist: [292, 488]},
  },
  driving: {
    l: {elbow: [96, 420], wrist: [128, 438]},
    r: {elbow: [304, 420], wrist: [272, 438]},
  },
  seated: {
    l: {elbow: [100, 410], wrist: [158, 470]},
    r: {elbow: [300, 410], wrist: [242, 470]},
  },
  "holding-drink": {
    l: {elbow: [100, 410], wrist: [158, 470]},
    r: {elbow: [312, 430], wrist: [262, 368]},
  },
};

// ---------- small helpers ----------
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const ArmTube: React.FC<{s: Pt; a: Arm}> = ({s, a}) => {
  const d = `M${s[0]},${s[1]} L${a.elbow[0]},${a.elbow[1]} L${a.wrist[0]},${a.wrist[1]}`;
  return (
    <g>
      <path d={d} stroke={C.outline} strokeWidth={S.armWidth + lw * 2} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <path d={d} stroke={C.shirt} strokeWidth={S.armWidth} fill="none" strokeLinecap="round" strokeLinejoin="round" />
    </g>
  );
};

const Hand: React.FC<{a: Arm; s: Pt}> = ({a, s}) => {
  const [x, y] = a.wrist;
  // point the hand along the forearm
  const ang = (Math.atan2(y - a.elbow[1], x - a.elbow[0]) * 180) / Math.PI;
  if (a.open) {
    // open palm with fingers, for waving
    return (
      <g transform={`translate(${x},${y}) rotate(${ang + 90})`}>
        {[-9, -3, 3, 9].map((fx, i) => (
          <rect key={i} x={fx - 3.6} y={-34 + Math.abs(fx) * 0.5} width={7.2} height={20} rx={3.6} fill={C.skin} stroke={C.outline} strokeWidth={lw * 0.7} />
        ))}
        <ellipse cx={-15} cy={-6} rx={5} ry={10} transform="rotate(-35 -15 -6)" fill={C.skin} stroke={C.outline} strokeWidth={lw * 0.7} />
        <ellipse cx={0} cy={-6} rx={15} ry={14} fill={C.skin} stroke={C.outline} strokeWidth={lw * 0.8} />
      </g>
    );
  }
  void s;
  return (
    <g transform={`translate(${x},${y}) rotate(${ang - 90})`}>
      <ellipse cx={0} cy={6} rx={S.handR} ry={S.handR * 1.12} fill={C.skin} stroke={C.outline} strokeWidth={lw * 0.8} />
      <path d={`M-6,10 Q0,14 6,10`} stroke={C.skinShade} strokeWidth={2.5} fill="none" strokeLinecap="round" />
    </g>
  );
};

// ---------- face parts ----------
const Brows: React.FC<{e: Expression}> = ({e}) => {
  const y = S.eyeY - 33;
  const g = S.eyeGap;
  const cx = S.headCx;
  // [outerY, innerY, arch]
  const shape: Record<Expression, [number, number, number]> = {
    neutral: [y + 2, y + 1, -4],
    happy: [y - 2, y - 3, -7],
    anxious: [y + 6, y - 9, 2],
    surprised: [y - 10, y - 11, -8],
  };
  const [oy, iy, arch] = shape[e];
  const brow = (side: 1 | -1) => {
    const ox = cx + side * (g + 20);
    const ix = cx + side * (g - 16);
    const mx = (ox + ix) / 2;
    return `M${ox},${oy} Q${mx},${(oy + iy) / 2 + arch} ${ix},${iy}`;
  };
  return (
    <g stroke={C.hair} strokeWidth={6} strokeLinecap="round" fill="none">
      <path d={brow(-1)} />
      <path d={brow(1)} />
    </g>
  );
};

const Eyes: React.FC<{e: Expression; blink: number; lookX: number; lookY: number}> = ({e, blink, lookX, lookY}) => {
  const ry = e === "surprised" ? 10 : e === "happy" ? 6.8 : 8.5;
  const rx = e === "surprised" ? 8 : 7;
  const open = Math.max(0, 1 - blink);
  return (
    <g>
      {[-1, 1].map((side) => {
        const cx = S.headCx + side * S.eyeGap + lookX * 4;
        const cy = S.eyeY + 2 + lookY * 3;
        if (open < 0.18) {
          // closed lid
          return <path key={side} d={`M${cx - 10},${cy + 1} Q${cx},${cy + 6} ${cx + 10},${cy + 1}`} stroke={C.eye} strokeWidth={3.6} fill="none" strokeLinecap="round" />;
        }
        return (
          <g key={side}>
            <ellipse cx={cx} cy={cy} rx={rx} ry={ry * open} fill={C.eye} />
            <circle cx={cx + 2.6} cy={cy - 3 * open} r={2.6 * Math.min(1, open * 1.3)} fill={C.lensGlint} />
          </g>
        );
      })}
    </g>
  );
};

const Glasses: React.FC = () => {
  const r = S.lensR;
  const lx = S.headCx - S.eyeGap;
  const rx = S.headCx + S.eyeGap;
  const y = S.eyeY;
  return (
    <g fill="none" stroke={C.glasses}>
      {/* temples back to the ears */}
      <path d={`M${lx - r},${y - 4} L${130},${y - 8}`} strokeWidth={4.5} />
      <path d={`M${rx + r},${y - 4} L${270},${y - 8}`} strokeWidth={4.5} />
      <circle cx={lx} cy={y} r={r} strokeWidth={5.5} fill="rgba(255,255,255,0.08)" />
      <circle cx={rx} cy={y} r={r} strokeWidth={5.5} fill="rgba(255,255,255,0.08)" />
      <path d={`M${lx + r - 1},${y - 3} Q${S.headCx},${y - 12} ${rx - r + 1},${y - 3}`} strokeWidth={4.5} />
      {/* lens glints */}
      <path d={`M${lx - 15},${y - 12} Q${lx - 11},${y - 18} ${lx - 4},${y - 20}`} stroke={C.lensGlint} strokeWidth={3} strokeLinecap="round" opacity={0.9} />
      <path d={`M${rx - 15},${y - 12} Q${rx - 11},${y - 18} ${rx - 4},${y - 20}`} stroke={C.lensGlint} strokeWidth={3} strokeLinecap="round" opacity={0.9} />
    </g>
  );
};

const Mouth: React.FC<{e: Expression; open: number}> = ({e, open}) => {
  const cx = S.headCx + 1;
  const y = S.mouthY;
  // width, smile curve (+ = corners up), asymmetry (half-smile lifts one corner)
  const base: Record<Expression, {w: number; curve: number; tilt: number; minOpen: number}> = {
    neutral: {w: 30, curve: 7, tilt: 3, minOpen: 0},
    happy: {w: 40, curve: 12, tilt: 0, minOpen: 0.25},
    anxious: {w: 26, curve: -4, tilt: 0, minOpen: 0},
    surprised: {w: 18, curve: 0, tilt: 0, minOpen: 0.55},
  };
  const b = base[e];
  const o = Math.max(b.minOpen, Math.min(1, open));
  const x1 = cx - b.w / 2;
  const x2 = cx + b.w / 2;
  const y1 = y - b.curve * 0.4;
  const y2 = y - b.curve * 0.4 - b.tilt;
  const h = o * 26;
  if (h < 2.5) {
    if (e === "anxious") {
      return <path d={`M${x1},${y + 2} Q${cx - 7},${y - 5} ${cx},${y} Q${cx + 7},${y + 5} ${x2},${y - 1}`} stroke={C.outline} strokeWidth={3.6} fill="none" strokeLinecap="round" />;
    }
    return <path d={`M${x1},${y1} Q${cx},${y + b.curve * 0.8} ${x2},${y2}`} stroke={C.outline} strokeWidth={3.6} fill="none" strokeLinecap="round" />;
  }
  if (e === "surprised") {
    return <ellipse cx={cx} cy={y + 2} rx={8 + o * 4} ry={6 + o * 9} fill={C.mouth} stroke={C.outline} strokeWidth={3.2} />;
  }
  const top = `M${x1},${y1} Q${cx},${y + b.curve * 0.5} ${x2},${y2}`;
  const bottom = `Q${cx},${y + b.curve * 0.5 + h * 1.6} ${x1},${y1}`;
  return (
    <g>
      <defs>
        <clipPath id="ren-mouth-clip">
          <path d={`${top} ${bottom} Z`} />
        </clipPath>
      </defs>
      <path d={`${top} ${bottom} Z`} fill={C.mouth} />
      <g clipPath="url(#ren-mouth-clip)">
        <rect x={x1} y={y1 - 20} width={b.w} height={20 + (e === "happy" ? 5 : 3)} fill={C.teeth} />
        <ellipse cx={cx} cy={y + b.curve * 0.5 + h * 0.85} rx={b.w * 0.3} ry={h * 0.35} fill={C.tongue} />
      </g>
      <path d={`${top} ${bottom} Z`} fill="none" stroke={C.outline} strokeWidth={3.2} strokeLinejoin="round" />
    </g>
  );
};

const Sweat: React.FC<{frame: number}> = ({frame}) => {
  const drop = (x: number, y: number, s: number, phase: number) => {
    const t = ((frame + phase) % 40) / 40;
    const dy = t * 26;
    const op = t < 0.8 ? 1 : 1 - (t - 0.8) / 0.2;
    return (
      <g transform={`translate(${x},${y + dy}) scale(${s})`} opacity={op}>
        <path d="M0,-14 C5,-6 9,0 9,5 A9,9 0 1 1 -9,5 C-9,0 -5,-6 0,-14 Z" fill={C.sweat} stroke={C.sweatEdge} strokeWidth={2.4} />
        <ellipse cx={-3} cy={4} rx={2} ry={3} fill="#FFFFFF" />
      </g>
    );
  };
  return (
    <g>
      {drop(290, 130, 1.2, 0)}
      {drop(110, 150, 0.9, 18)}
      {drop(304, 175, 0.75, 29)}
    </g>
  );
};

// ---------- head ----------
const Head: React.FC<{e: Expression; mouthOpen: number; blink: number; sweat: boolean; lookX: number; lookY: number; frame: number}> = ({e, mouthOpen, blink, sweat, lookX, lookY, frame}) => {
  const face = "M130,150 C130,82 270,82 270,150 L268,205 C264,246 232,272 200,274 C168,272 136,246 132,205 Z";
  return (
    <g>
      {/* neck */}
      <path d="M178,250 L178,300 L222,300 L222,250 Z" fill={C.skin} stroke={C.outline} strokeWidth={lw} />
      <path d="M178,262 Q200,282 222,262 L222,276 Q200,292 178,276 Z" fill={C.skinShade} />
      {/* ears */}
      <ellipse cx={128} cy={196} rx={13} ry={20} fill={C.skin} stroke={C.outline} strokeWidth={lw} />
      <ellipse cx={272} cy={196} rx={13} ry={20} fill={C.skin} stroke={C.outline} strokeWidth={lw} />
      <path d="M126,188 Q120,196 127,206" stroke={C.skinShade} strokeWidth={3} fill="none" />
      <path d="M274,188 Q280,196 273,206" stroke={C.skinShade} strokeWidth={3} fill="none" />
      {/* hair at the back of the head */}
      <path d="M124,170 C112,112 140,62 200,58 C262,62 290,112 276,170 Z" fill={C.hair} stroke={C.outline} strokeWidth={lw} />
      {/* face */}
      <path d={face} fill={C.skin} stroke={C.outline} strokeWidth={lw} />
      {/* soft shade under fringe */}
      <path d="M136,150 C160,160 240,160 264,150 L264,160 C240,170 160,170 136,160 Z" fill={C.skinShade} opacity={0.55} />
      {e === "happy" && (
        <g opacity={0.35}>
          <ellipse cx={150} cy={228} rx={14} ry={7} fill={C.blush} />
          <ellipse cx={250} cy={228} rx={14} ry={7} fill={C.blush} />
        </g>
      )}
      {/* nose */}
      <path d="M201,204 Q195,219 199,224 Q204,226 209,222" stroke={C.outline} strokeWidth={3} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      <Eyes e={e} blink={blink} lookX={lookX} lookY={lookY} />
      <Glasses />
      <Mouth e={e} open={mouthOpen} />
      {/* messy fringe with tufts */}
      <path
        d="M120,184 C104,140 110,96 138,74 C150,52 176,42 200,46 C206,36 212,31 220,28 C216,37 216,43 220,48 C250,50 272,62 282,84 C290,83 297,81 304,77 C299,90 294,98 288,104 C296,128 293,156 283,186 C279,166 273,150 263,138 C261,146 257,152 251,156 C248,144 240,132 228,124 C226,134 221,142 213,147 C210,134 202,124 190,118 C186,130 177,139 167,144 C168,134 166,126 160,120 C152,134 141,152 135,176 Z"
        fill={C.hair}
        stroke={C.outline}
        strokeWidth={lw}
        strokeLinejoin="round"
      />
      {/* hair shine strokes */}
      <g stroke={C.hairShine} strokeWidth={3.5} fill="none" strokeLinecap="round">
        <path d="M168,70 Q190,62 214,68" />
        <path d="M150,92 Q160,84 172,82" />
        <path d="M236,82 Q252,88 262,100" />
      </g>
      <Brows e={e} />
      {sweat && <Sweat frame={frame} />}
    </g>
  );
};

// ---------- body ----------
const Torso: React.FC = () => (
  <g>
    {/* shirt body */}
    <path d="M108,318 C126,300 160,292 180,290 L220,290 C240,292 274,300 292,318 C300,360 302,420 300,484 L100,484 C98,420 100,360 108,318 Z" fill={C.shirt} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
    {/* white tee showing through the open shirt */}
    <path d="M172,292 L228,292 L238,484 L162,484 Z" fill={C.tee} stroke={C.outline} strokeWidth={lw * 0.8} />
    <path d="M178,292 Q200,312 222,292" fill={C.skin} stroke={C.outline} strokeWidth={lw * 0.8} />
    <path d="M180,300 Q200,318 220,300" stroke={C.teeShade} strokeWidth={4} fill="none" />
    {/* open shirt fronts */}
    <path d="M172,292 L162,484 L148,484 L160,300 Z" fill={C.shirtShade} />
    <path d="M228,292 L238,484 L252,484 L240,300 Z" fill={C.shirtShade} />
    {/* collar */}
    <path d="M182,286 L150,302 L162,342 L176,306 Z" fill={C.shirt} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
    <path d="M218,286 L250,302 L238,342 L224,306 Z" fill={C.shirt} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
    {/* buttons on the left placket */}
    {[360, 410, 460].map((y) => (
      <circle key={y} cx={156 - (y - 360) * 0.02} cy={y} r={3.6} fill={C.button} />
    ))}
  </g>
);

const LegsStanding: React.FC = () => (
  <g>
    <path d="M112,478 L196,478 L192,662 L126,662 Z" fill={C.pants} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
    <path d="M204,478 L288,478 L274,662 L208,662 Z" fill={C.pants} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
    <path d="M196,486 L200,620 L204,486" fill={C.pantsShade} />
    <path d="M120,660 L198,660 C200,690 196,696 186,696 L114,696 C104,696 106,668 120,660 Z" fill={C.shoes} stroke={C.outline} strokeWidth={lw} />
    <path d="M202,660 L280,660 C294,668 296,696 286,696 L214,696 C204,696 200,690 202,660 Z" fill={C.shoes} stroke={C.outline} strokeWidth={lw} />
  </g>
);

const LegsSeated: React.FC = () => (
  <g>
    {/* thighs coming toward camera */}
    <path d="M104,476 L296,476 C306,500 304,540 290,556 L110,556 C96,540 94,500 104,476 Z" fill={C.pants} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
    <path d="M200,486 L200,552" stroke={C.pantsShade} strokeWidth={5} />
    {/* shins */}
    <path d="M118,552 L188,552 L184,660 L126,660 Z" fill={C.pantsShade} stroke={C.outline} strokeWidth={lw} />
    <path d="M212,552 L282,552 L274,660 L216,660 Z" fill={C.pantsShade} stroke={C.outline} strokeWidth={lw} />
    <path d="M118,656 L192,656 C196,686 190,694 180,694 L114,694 C104,694 104,664 118,656 Z" fill={C.shoes} stroke={C.outline} strokeWidth={lw} />
    <path d="M208,656 L282,656 C296,664 296,694 286,694 L220,694 C210,694 204,686 208,656 Z" fill={C.shoes} stroke={C.outline} strokeWidth={lw} />
  </g>
);

// ---------- props ----------
const Suitcase: React.FC<{hand: Pt}> = ({hand}) => {
  const [x, y] = hand;
  return (
    <g>
      <path d={`M${x - 16},${y + 14} L${x - 16},${y - 4} Q${x},${y - 14} ${x + 16},${y - 4} L${x + 16},${y + 14}`} stroke={C.outline} strokeWidth={7} fill="none" strokeLinecap="round" />
      <rect x={x - 62} y={y + 12} width={124} height={150} rx={16} fill={C.suitcase} stroke={C.outline} strokeWidth={lw} />
      <path d={`M${x - 30},${y + 22} L${x - 30},${y + 152} M${x + 30},${y + 22} L${x + 30},${y + 152}`} stroke={C.suitcaseEdge} strokeWidth={6} />
    </g>
  );
};

const Calculator: React.FC<{tap: number}> = ({tap}) => (
  <g transform="translate(200,430) rotate(-6)">
    <rect x={-48} y={-40} width={96} height={124} rx={10} fill={C.calculator} stroke={C.outline} strokeWidth={lw} />
    <rect x={-36} y={-30} width={72} height={26} rx={4} fill={C.calcScreen} stroke={C.outline} strokeWidth={2.5} />
    {[0, 1, 2].map((r) =>
      [0, 1, 2].map((c) => (
        <rect key={`${r}${c}`} x={-36 + c * 26} y={4 + r * 22} width={20} height={16} rx={3} fill={r === 1 && c === 1 && tap > 0.5 ? "#8E9AA8" : "#FFFFFF"} stroke={C.outline} strokeWidth={2} />
      )),
    )}
  </g>
);

const Drink: React.FC<{hand: Pt}> = ({hand}) => {
  const [x, y] = hand;
  return (
    <g transform={`translate(${x - 6},${y - 46})`}>
      <path d="M-22,-26 L22,-26 L16,44 L-16,44 Z" fill={C.glass} stroke={C.outline} strokeWidth={lw} strokeLinejoin="round" />
      <path d="M-19,-6 L19,-6 L16,40 L-16,40 Z" fill={C.juice} />
      <circle cx={10} cy={-30} r={11} fill="#F7D84A" stroke={C.outline} strokeWidth={3} />
      <path d="M6,-50 L-2,-4" stroke="#E2493E" strokeWidth={6} strokeLinecap="round" />
    </g>
  );
};

const SteeringWheel: React.FC = () => (
  <g>
    <circle cx={200} cy={448} r={92} fill="none" stroke={C.outline} strokeWidth={30} />
    <circle cx={200} cy={448} r={92} fill="none" stroke={C.wheel} strokeWidth={22} />
    <path d="M118,452 L282,452" stroke={C.wheel} strokeWidth={18} />
    <circle cx={200} cy={455} r={26} fill={C.wheel} stroke={C.outline} strokeWidth={lw} />
  </g>
);

// ---------- the character ----------
export const Ren: React.FC<RenProps> = ({
  expression = "neutral",
  mouthOpen = 0,
  pose = "standing",
  blink = 0,
  sweat = false,
  size = 1200,
  breathing = true,
  lookX = 0,
  lookY = 0,
  armL,
  armR,
  prop = "none",
  tap = 0,
  showLegs = true,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const phase = breathing ? Math.sin((frame / fps / S.breathSeconds) * Math.PI * 2) : 0;
  const breath = (phase + 1) / 2; // 0..1

  let l = armL ?? POSE_ARMS[pose].l;
  let r = armR ?? POSE_ARMS[pose].r;
  if (prop === "calculator" && !armL && !armR) {
    l = {elbow: [104, 440], wrist: [168, 470]};
    r = {elbow: [304, 408], wrist: [lerp(232, 222, tap), lerp(422, 448, tap)]};
  }
  // the hands rise slightly with each breath
  const by = -breath * S.breathPx;
  const lift = (a: Arm): Arm => ({...a, elbow: [a.elbow[0], a.elbow[1] + by * 0.6], wrist: [a.wrist[0], a.wrist[1] + by * 0.4]});
  l = lift(l);
  r = lift(r);

  const seated = pose !== "standing";

  return (
    <svg width={(size * W) / H} height={size} viewBox={`0 0 ${W} ${H}`} style={{overflow: "visible"}}>
      {showLegs && (seated ? <LegsSeated /> : <LegsStanding />)}
      <g transform={`translate(200,${S.shoulderY}) scale(${1 + breath * 0.012},${1 + breath * 0.008}) translate(-200,${-S.shoulderY})`}>
        <Torso />
      </g>
      <g transform={`translate(0,${-breath * S.breathPx})`}>
        <Head e={expression} mouthOpen={mouthOpen} blink={blink} sweat={sweat} lookX={lookX} lookY={lookY} frame={frame} />
      </g>
      {pose === "driving" && <SteeringWheel />}
      {prop === "calculator" && <Calculator tap={tap} />}
      <ArmTube s={shoulderL} a={l} />
      <ArmTube s={shoulderR} a={r} />
      {prop === "suitcase" && <Suitcase hand={l.wrist} />}
      <Hand a={l} s={shoulderL} />
      <Hand a={r} s={shoulderR} />
      {pose === "holding-drink" && <Drink hand={r.wrist} />}
    </svg>
  );
};

// Natural blink curve: closes and opens over ~6 frames around each listed frame.
export const blinkAt = (frame: number, at: number[], len = 6): number => {
  for (const f of at) {
    const d = frame - f;
    if (d >= 0 && d < len) {
      const t = d / (len - 1);
      return 1 - Math.abs(t * 2 - 1);
    }
  }
  return 0;
};
