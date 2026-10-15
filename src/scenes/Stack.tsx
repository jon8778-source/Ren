import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren} from "../Ren";
import {theme} from "../theme";
import type {Mood, Short} from "../types";

const STEP = 6; // frames between coins
const LAND = 10; // frames for a coin to land

export const Stack: React.FC<{amount: number; count: number; label: string; ren: Short["ren"]; mood?: Mood}> = ({
  amount,
  count,
  label,
  ren,
  mood = "worried",
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const landed = Math.max(0, Math.min(count, Math.floor((frame - LAND) / STEP) + 1));
  const total = (landed * amount).toFixed(2);
  const done = landed === count;
  const lastLand = (count - 1) * STEP + LAND;
  const finalPop = done ? spring({frame: frame - lastLand, fps, config: {damping: 9}}) : 0;

  return (
    <AbsoluteFill style={{alignItems: "center", paddingTop: 240}}>
      <div style={{fontSize: 72, fontWeight: 600, color: theme.ink}}>{label}</div>
      <div
        style={{
          fontSize: 200,
          fontWeight: 700,
          color: theme.cost,
          transform: `scale(${1 + finalPop * 0.15})`,
        }}
      >
        ${total}
      </div>
      <div style={{position: "relative", width: 360, height: 640, marginTop: 20, transform: "translateX(-120px)"}}>
        {Array.from({length: count}).map((_, i) => {
          const s = spring({frame: frame - i * STEP, fps, config: {damping: 14}});
          const drop = interpolate(s, [0, 1], [-1100, 0]);
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: 30,
                bottom: i * 44,
                width: 300,
                height: 72,
                borderRadius: "50%",
                background: theme.gold,
                border: `6px solid ${theme.goldEdge}`,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 34,
                fontWeight: 700,
                color: theme.goldEdge,
                opacity: frame < i * STEP ? 0 : 1,
                transform: `translateY(${drop}px) rotate(${(i % 2 ? 1 : -1) * 2}deg)`,
              }}
            >
              ${amount.toFixed(2)}
            </div>
          );
        })}
      </div>
      <div style={{position: "absolute", right: 0, bottom: 440}}>
        <Ren ren={ren} mood={mood} size={460} jolts={[{at: lastLand}]} swaps={[{at: lastLand, mood: "shocked"}]} />
      </div>
    </AbsoluteFill>
  );
};
