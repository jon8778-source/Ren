import {Composition} from "remotion";
import {RenShort} from "./RenShort";
import {shorts} from "./shorts";

export const FPS = 30;

export const RemotionRoot: React.FC = () => (
  <>
    {shorts.map((s) => (
      <Composition
        key={s.id}
        id={s.id}
        component={RenShort}
        durationInFrames={Math.round(s.durationInSeconds * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{short: s}}
      />
    ))}
  </>
);
