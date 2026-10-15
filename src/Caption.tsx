import {interpolate, useCurrentFrame} from "remotion";
import {theme} from "./theme";

export const Caption: React.FC<{text: string; durationInFrames: number}> = ({text, durationInFrames}) => {
  const frame = useCurrentFrame();
  if (!text) return null;
  const opacity = interpolate(
    frame,
    [0, 6, durationInFrames - 6, durationInFrames],
    [0, 1, 1, 0],
    {extrapolateLeft: "clamp", extrapolateRight: "clamp"},
  );
  return (
    <div
      style={{
        position: "absolute",
        bottom: 300,
        left: 80,
        right: 80,
        textAlign: "center",
        fontSize: 64,
        fontWeight: 600,
        lineHeight: 1.2,
        color: theme.ink,
        opacity,
      }}
    >
      {text}
    </div>
  );
};
