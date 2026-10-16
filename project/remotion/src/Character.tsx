import {Img, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {Box, CharacterRef} from "./types";

// A character (Ren or one of the five people) standing in its zone. Slides in when it first
// appears, pops when its pose changes, breathes, and bobs while Ren is speaking.
export const Character: React.FC<{c: CharacterRef; box: Box; side: string; sceneStart: number}> = ({c, box, side}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const enter = c.enter ? spring({frame, fps, config: {damping: 14, stiffness: 120}}) : 1;
  const fromX = side === "character_left" ? -260 : 260;
  const pop = c.posePop ? 1 - spring({frame, fps, config: {damping: 9, stiffness: 240}}) : 0;
  const breathe = Math.sin(t * 2.1) * 0.01;
  const speaking = c.speaking && t >= c.speaking[0] && t <= c.speaking[1];
  const bob = speaking ? -Math.abs(Math.sin(t * 9)) * 7 : 0;
  const sway = Math.sin(t * 1.3) * 0.8;
  return (
    <div
      style={{
        position: "absolute",
        left: box.x,
        top: box.y,
        width: box.w,
        height: box.h,
        opacity: enter,
        transformOrigin: "50% 100%",
        transform: [
          `translateX(${(1 - enter) * fromX}px)`,
          `translateY(${bob}px)`,
          `rotate(${sway}deg)`,
          `scale(${1 + pop * 0.06}, ${1 - pop * 0.06 + breathe})`,
        ].join(" "),
      }}
    >
      <Img
        src={staticFile(c.src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "contain",
          objectPosition: "50% 100%",
          maskImage: "linear-gradient(to bottom, black 86%, transparent 100%)",
          WebkitMaskImage: "linear-gradient(to bottom, black 86%, transparent 100%)",
        }}
      />
    </div>
  );
};
