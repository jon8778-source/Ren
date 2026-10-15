import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren} from "../Ren";
import {theme} from "../theme";
import type {Mood, Short} from "../types";

export const Cta: React.FC<{title: string; sub: string; ren: Short["ren"]; mood?: Mood}> = ({title, sub, ren, mood = "excited"}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = spring({frame: frame - 8, fps, config: {damping: 10}});
  const nudge = Math.abs(Math.sin(frame / 5)) * 18;
  return (
    <AbsoluteFill style={{alignItems: "center", paddingTop: 260}}>
      <Ren ren={ren} mood={mood} size={760} />
      <div
        style={{
          marginTop: 50,
          fontSize: 96,
          fontWeight: 700,
          color: theme.save,
          textAlign: "center",
          padding: "0 80px",
          transform: `scale(${t})`,
        }}
      >
        {title}
      </div>
      <div
        style={{
          marginTop: 30,
          fontSize: 70,
          fontWeight: 600,
          color: theme.ink,
          transform: `translateY(${nudge}px)`,
          opacity: t,
        }}
      >
        {sub} ↓
      </div>
    </AbsoluteFill>
  );
};
