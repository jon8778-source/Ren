import {Img, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {Mood, Short} from "./types";
import {theme} from "./theme";

type Props = {ren: Short["ren"]; mood: Mood; size: number};

export const Ren: React.FC<Props> = ({ren, mood, size}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame, fps, config: {damping: 12}});
  const bob = Math.sin(frame / 6) * (mood === "excited" ? 16 : 5);
  const style: React.CSSProperties = {
    width: size,
    height: size,
    transform: `translateY(${(1 - enter) * 400 + bob}px) scale(${0.6 + 0.4 * enter})`,
  };

  const file = ren[mood];
  if (file) {
    return <Img src={staticFile(file)} style={{...style, objectFit: "contain"}} />;
  }

  // Placeholder mascot until real Ren art is added to /public
  const mouth =
    mood === "shocked" ? (
      <ellipse cx="100" cy="132" rx="14" ry="18" fill={theme.ink} />
    ) : (
      <path
        d={mood === "excited" ? "M68 120 Q100 160 132 120 Z" : "M75 125 Q100 145 125 125"}
        fill={mood === "excited" ? theme.ink : "none"}
        stroke={theme.ink}
        strokeWidth="6"
        strokeLinecap="round"
      />
    );
  const pupilY = mood === "shocked" ? 82 : 88;

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
