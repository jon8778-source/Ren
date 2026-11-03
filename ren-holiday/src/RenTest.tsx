import React from "react";
import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from "remotion";
import {Ren, blinkAt, type Arm, type Expression} from "./ren/Ren";
import {brand} from "./theme";

// 5-second character test: idle breathing, a blink, a wave,
// then neutral -> anxious (raised brows, sweat) -> happy.
const T = {
  blinks: [22, 96, 132],
  waveIn: 34,
  waveOut: 78,
  anxious: 84,
  happy: 114,
};

export const RenTest: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  // wave: raise the right arm, swing the forearm three times, lower it
  const up = interpolate(frame, [T.waveIn, T.waveIn + 8, T.waveOut - 8, T.waveOut], [0, 1, 1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  let armR: Arm | undefined;
  if (up > 0) {
    const swing = Math.sin(((frame - T.waveIn) / 12) * Math.PI * 2) * 22 * up; // degrees
    const elbow: [number, number] = [298 + 52 * up, 405 - 125 * up];
    const len = 88;
    const base = interpolate(up, [0, 1], [95, -78]); // forearm angle, deg (90 = down)
    const a = ((base + swing) * Math.PI) / 180;
    armR = {elbow, wrist: [elbow[0] + Math.cos(a) * len, elbow[1] + Math.sin(a) * len], open: up > 0.5};
  }

  const expression: Expression = frame >= T.happy ? "happy" : frame >= T.anxious ? "anxious" : "neutral";
  const swapAt = frame >= T.happy ? T.happy : frame >= T.anxious ? T.anxious : -100;
  const pop = 1 + 0.04 * Math.sin(Math.min(1, (frame - swapAt) / 8) * Math.PI) * (swapAt > 0 ? 1 : 0);

  // a short "oh no" then "yes!" mouth movement to show the mouth range
  const talk = (from: number, to: number) => (frame >= from && frame < to ? Math.abs(Math.sin(((frame - from) / 5) * Math.PI)) : 0);
  const mouthOpen = Math.max(talk(88, 104) * 0.5, talk(118, 136));

  const enter = spring({frame, fps, config: {damping: 14}});

  return (
    <AbsoluteFill style={{background: brand.background, alignItems: "center", justifyContent: "center"}}>
      <div style={{transform: `translateY(${(1 - enter) * 60}px) scale(${pop})`, opacity: enter, transformOrigin: "50% 40%"}}>
        <Ren
          size={1500}
          expression={expression}
          mouthOpen={mouthOpen}
          blink={blinkAt(frame, T.blinks)}
          sweat={expression === "anxious"}
          armR={armR}
          lookX={expression === "anxious" ? -0.6 : 0}
        />
      </div>
    </AbsoluteFill>
  );
};
