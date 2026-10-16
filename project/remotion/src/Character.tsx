import {Img, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {Box, CharacterRef} from "./types";

// A character (Ren or one of the five people) standing in its zone. Slides in when it first
// appears and gives one small pop when its pose changes. Otherwise it holds still: no talking
// bob, sway or breathing, so nobody looks like they're shaking.
export const Character: React.FC<{c: CharacterRef; box: Box; side: string; sceneStart: number}> = ({c, box, side}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = c.enter ? spring({frame, fps, config: {damping: 14, stiffness: 120}}) : 1;
  const fromX = side === "character_left" ? -260 : 260;
  const pop = c.posePop ? 1 - spring({frame, fps, config: {damping: 9, stiffness: 240}}) : 0;
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
          `scale(${1 + pop * 0.04}, ${1 - pop * 0.04})`,
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
