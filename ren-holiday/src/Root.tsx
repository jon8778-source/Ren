import React from "react";
import {Composition} from "remotion";
import {RenTest} from "./RenTest";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="RenTest" component={RenTest} durationInFrames={150} fps={30} width={1080} height={1920} />
  </>
);
