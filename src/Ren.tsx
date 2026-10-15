import {AbsoluteFill, Img, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {Mood, Short} from "./types";
import {theme} from "./theme";

// Frame offsets are relative to the start of the scene.
export type PoseSwap = {at: number; mood: Mood};
export type Jolt = {at: number; strength?: number}; // 1 = big surprised jump + shake

type Props = {
  ren: Short["ren"];
  mood: Mood; // opening pose
  size: number;
  swaps?: PoseSwap[];
  jolts?: Jolt[];
};

const JOLT_FRAMES = 22;

export const Ren: React.FC<Props> = ({ren, mood, size, swaps = [], jolts = []}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // Current pose: the latest swap that has happened
  const passed = swaps.filter((s) => frame >= s.at).sort((a, b) => a.at - b.at);
  const lastSwap = passed[passed.length - 1];
  const current = lastSwap ? lastSwap.mood : mood;

  // Entrance: spring up from below with squash & stretch
  const enter = spring({frame, fps, config: {damping: 11, stiffness: 140}});
  const enterY = (1 - enter) * 500;
  const stretch = (1 - enter) * 0.12;

  // Pose swap pop: quick squash that springs back, hiding the image change
  const pop = lastSwap ? 1 - spring({frame: frame - lastSwap.at, fps, config: {damping: 8, stiffness: 260}}) : 0;
  const squash = pop * 0.1;

  // Reaction jolts: hop up and shake, decaying
  let joltY = 0;
  let joltX = 0;
  for (const j of jolts) {
    const t = frame - j.at;
    if (t < 0 || t > JOLT_FRAMES) continue;
    const k = j.strength ?? 1;
    if (t < 12) joltY -= Math.sin((Math.PI * t) / 12) * 70 * k;
    joltX += Math.sin(t * 2.6) * 14 * k * Math.exp(-t / 6);
  }

  // Idle life: breathing, sway from the waist; waving rocks faster, excited bounces
  const breathe = Math.sin(frame / 9) * 0.012;
  const swayDeg = current === "waving" ? Math.sin(frame / 4) * 3.5 : Math.sin(frame / 23) * 1.2;
  const bob = current === "excited" || current === "thumbsUp" ? -Math.abs(Math.sin(frame / 6)) * 18 : 0;

  const style: React.CSSProperties = {
    width: size,
    height: size,
    transformOrigin: "50% 100%",
    transform: [
      `translate(${joltX}px, ${enterY + joltY + bob}px)`,
      `rotate(${swayDeg}deg)`,
      `scale(${1 - stretch + squash}, ${1 + stretch - squash + breathe})`,
    ].join(" "),
  };

  // Stack every pose this scene uses and show only the current one, so swaps never flash while loading
  const moods = [mood, ...swaps.map((s) => s.mood)].filter((m, i, all) => all.indexOf(m) === i);
  if (moods.every((m) => ren[m])) {
    // Art is cropped at the waist, so fade the bottom edge into the background
    const fade = "linear-gradient(to bottom, black 78%, transparent 98%)";
    return (
      <div style={{...style, position: "relative"}}>
        {moods.map((m) => (
          <AbsoluteFill key={m} style={{opacity: m === current ? 1 : 0}}>
            <Img
              src={staticFile(ren[m]!)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "contain",
                objectPosition: "bottom",
                maskImage: fade,
                WebkitMaskImage: fade,
              }}
            />
          </AbsoluteFill>
        ))}
      </div>
    );
  }

  // Placeholder mascot until real Ren art is added to /public
  const happy = current === "excited" || current === "waving" || current === "thumbsUp";
  const mouth =
    current === "shocked" ? (
      <ellipse cx="100" cy="132" rx="14" ry="18" fill={theme.ink} />
    ) : current === "worried" ? (
      <path d="M75 135 Q100 118 125 135" fill="none" stroke={theme.ink} strokeWidth="6" strokeLinecap="round" />
    ) : (
      <path
        d={happy ? "M68 120 Q100 160 132 120 Z" : "M75 125 Q100 145 125 125"}
        fill={happy ? theme.ink : "none"}
        stroke={theme.ink}
        strokeWidth="6"
        strokeLinecap="round"
      />
    );
  const pupilY = current === "shocked" ? 82 : 88;

  return (
    <svg viewBox="0 0 200 200" style={style}>
      <rect x="25" y="30" width="150" height="150" rx="70" fill={theme.save} />
      <circle cx="75" cy="85" r="20" fill="#fff" />
      <circle cx="125" cy="85" r="20" fill="#fff" />
      <circle cx="78" cy={pupilY} r="9" fill={theme.ink} />
      <circle cx="122" cy={pupilY} r="9" fill={theme.ink} />
      {mouth}
      <circle cx="160" cy="45" r="22" fill={theme.gold} stroke={theme.goldEdge} strokeWidth="4" />
      <text x="160" y="53" textAnchor="middle" fontSize="24" fontWeight="700" fill={theme.goldEdge}>
        $
      </text>
    </svg>
  );
};
