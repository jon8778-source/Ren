import {AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig} from "remotion";
import {Caption} from "./Caption";
import {Checklist} from "./scenes/Checklist";
import {Cta} from "./scenes/Cta";
import {Hook} from "./scenes/Hook";
import {Stack} from "./scenes/Stack";
import {theme} from "./theme";
import type {Scene, Short} from "./types";

const SceneView: React.FC<{scene: Scene; ren: Short["ren"]}> = ({scene, ren}) => {
  switch (scene.type) {
    case "hook":
      return <Hook big={scene.big} ren={ren} mood={scene.mood} />;
    case "stack":
      return <Stack amount={scene.amount} count={scene.count} label={scene.label} />;
    case "checklist":
      return <Checklist items={scene.items} ren={ren} mood={scene.mood} />;
    case "cta":
      return <Cta title={scene.title} sub={scene.sub} ren={ren} mood={scene.mood} />;
  }
};

export const RenShort: React.FC<{short: Short}> = ({short}) => {
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: theme.background, fontFamily: theme.font}}>
      {short.voiceover ? <Audio src={staticFile(short.voiceover)} /> : null}
      {short.scenes.map((scene, i) => {
        const from = Math.round(scene.start * fps);
        const duration = Math.round((scene.end - scene.start) * fps);
        return (
          <Sequence key={i} from={from} durationInFrames={duration}>
            <SceneView scene={scene} ren={short.ren} />
            <Caption text={scene.caption} durationInFrames={duration} />
          </Sequence>
        );
      })}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          width: "100%",
          textAlign: "center",
          fontSize: 30,
          color: theme.muted,
        }}
      >
        {short.disclaimer}
      </div>
    </AbsoluteFill>
  );
};
