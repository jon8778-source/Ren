import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren} from "../Ren";
import {theme} from "../theme";
import type {Short} from "../types";

export const Cta: React.FC<{title: string; sub: string; ren: Short["ren"]}> = ({title, sub, ren}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = spring({frame: frame - 8, fps, config: {damping: 10}});
  const nudge = Math.abs(Math.sin(frame / 5)) * 18;
  return (
    <AbsoluteFill style={{alignItems: "center", paddingTop: 260}}>
      <Ren ren={ren} mood="excited" size={600} />
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
