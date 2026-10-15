import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren} from "../Ren";
import {theme} from "../theme";
import type {Mood, Short} from "../types";

export const Hook: React.FC<{big: string; ren: Short["ren"]; mood?: Mood}> = ({big, ren, mood = "shocked"}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const pop = spring({frame: frame - 4, fps, config: {damping: 8, mass: 0.6}});
  return (
    <AbsoluteFill style={{alignItems: "center", paddingTop: 300}}>
      <div
        style={{
          fontSize: 250,
          fontWeight: 700,
          color: theme.cost,
          transform: `scale(${pop}) rotate(${(1 - pop) * -10}deg)`,
        }}
      >
        {big}
      </div>
      <div style={{marginTop: 60}}>
        <Ren ren={ren} mood={mood} size={700} jolts={[{at: 8}]} swaps={[{at: 80, mood: "worried"}]} />
      </div>
    </AbsoluteFill>
  );
};
