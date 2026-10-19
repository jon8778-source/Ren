import {Composition} from "remotion";
import {Episode} from "./Episode";
import {Thumbnail, type ThumbProps} from "./Thumbnail";
import type {EpisodeProps} from "./types";
import {HandTest, RigStill} from "./rig/RenRig";
import {FACE_GRID_SIZE, FaceGrid} from "./rig/FaceGrid";
import {HAND_GRID_SIZE, HandGrid} from "./rig/HandGrid";
import {POSE_SHEET_SIZE, PoseSheet, PoseStill} from "./rig/PoseStill";
import {RIG_TEST_FPS, RIG_TEST_OUT_FRAMES, RigTest} from "./rig/RigTest";
import {Explainer, RIG_EXPLAINER_FPS, RIG_EXPLAINER_OUT_FRAMES} from "./rig/Explainer";

// Props come from build/props.json: npx remotion render src/index.ts episode out.mp4 --props=<file>
export const Root: React.FC = () => (
  <>
  <Composition id="ren-rig-still" component={RigStill} width={1080} height={1920} fps={30} durationInFrames={1} defaultProps={{}} />
  <Composition id="ren-face-grid" component={FaceGrid} {...FACE_GRID_SIZE} fps={30} durationInFrames={1} defaultProps={{guides: false}} />
  <Composition id="ren-hand-grid" component={HandGrid} {...HAND_GRID_SIZE} fps={30} durationInFrames={1} defaultProps={{guides: false}} />
  <Composition id="ren-pose" component={PoseStill} width={1080} height={1920} fps={30} durationInFrames={1} defaultProps={{name: "neutral"}} />
  <Composition id="ren-pose-sheet" component={PoseSheet} {...POSE_SHEET_SIZE} fps={30} durationInFrames={1} defaultProps={{}} />
  <Composition id="ren-rig-hands" component={HandTest} width={1080} height={1920} fps={30} durationInFrames={1} defaultProps={{}} />
  <Composition id="ren-rig-explainer" component={Explainer} width={1080} height={1920} fps={RIG_EXPLAINER_FPS} durationInFrames={RIG_EXPLAINER_OUT_FRAMES} defaultProps={{}} />
  <Composition id="ren-rig-test" component={RigTest} width={1080} height={1920} fps={RIG_TEST_FPS} durationInFrames={RIG_TEST_OUT_FRAMES} defaultProps={{}} />
  <Composition id="thumbnail" component={Thumbnail} width={1280} height={720} fps={30} durationInFrames={1} defaultProps={{} as ThumbProps} />
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
  </>
);
