import {AbsoluteFill, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren} from "../Ren";
import {theme} from "../theme";
import type {Mood, Short} from "../types";

export const Checklist: React.FC<{items: string[]; ren: Short["ren"]; mood?: Mood}> = ({items, ren, mood = "pointing"}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{paddingTop: 300, paddingLeft: 110, paddingRight: 110}}>
      {items.map((item, i) => {
        const s = spring({frame: frame - i * 12, fps, config: {damping: 13}});
        return (
          <div
            key={item}
            style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 70,
              fontWeight: 600,
              color: theme.ink,
              padding: "28px 0",
              borderBottom: `4px solid ${theme.ink}`,
              opacity: s,
              transform: `translateX(${(1 - s) * -200}px)`,
            }}
          >
            <span>{item}</span>
            <span style={{color: theme.cost}}>×12</span>
          </div>
        );
      })}
      <div style={{position: "absolute", right: 40, bottom: 440}}>
        <Ren ren={ren} mood={mood} size={460} />
      </div>
    </AbsoluteFill>
  );
};
