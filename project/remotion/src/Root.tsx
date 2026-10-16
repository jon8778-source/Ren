import {Composition} from "remotion";
import {Episode} from "./Episode";
import type {EpisodeProps} from "./types";

// Props come from build/props.json: npx remotion render src/index.ts episode out.mp4 --props=<file>
export const Root: React.FC = () => (
  <Composition
    id="episode"
    component={Episode}
    width={1920}
    height={1080}
    fps={30}
    durationInFrames={30}
    defaultProps={{} as EpisodeProps}
    calculateMetadata={({props}) => ({
      durationInFrames: Math.ceil(props.duration * props.config.video.fps),
      fps: props.config.video.fps,
      width: props.config.video.width,
      height: props.config.video.height,
    })}
  />
);
