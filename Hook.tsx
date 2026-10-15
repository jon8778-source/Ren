import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren} from "../Ren";
import {theme} from "../theme";
import type {Short} from "../types";

export const Hook: React.FC<{big: string; ren: Short["ren"]}> = ({big, ren}) => {
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
        <Ren ren={ren} mood="shocked" size={520} />
      </div>
    </AbsoluteFill>
  );
};
