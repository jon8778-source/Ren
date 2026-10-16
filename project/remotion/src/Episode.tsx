import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import {Character} from "./Character";
import {FONT} from "./fonts";
import {GraphicView} from "./Graphics";
import type {Caption, Config, EpisodeProps, Scene} from "./types";

const Camera: React.FC<{scene: Scene; children: React.ReactNode}> = ({scene, children}) => {
  // Slow pan/zoom across the whole scene so stills never sit dead
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / ((scene.end - scene.start) * fps);
  const scale = scene.camera === "none" ? 1 : 1 + 0.035 * t;
  const dx = scene.camera === "drift_left" ? -18 * t : scene.camera === "drift_right" ? 18 * t : 0;
  return <AbsoluteFill style={{transform: `translateX(${dx}px) scale(${scale})`, transformOrigin: "50% 45%"}}>{children}</AbsoluteFill>;
};

const SceneView: React.FC<{scene: Scene; config: Config}> = ({scene, config}) => {
  const L = config.layout;
  const charBox = scene.layout === "character_left" ? L.character_left : L.character_right;
  const contentBox = scene.layout === "character_left" ? L.content_when_character_left : L.content_when_character_right;
  const V = L.content_virtual ?? {w: contentBox.w, h: contentBox.h};
  return (
    <Camera scene={scene}>
      {scene.character ? <Character c={scene.character} box={charBox} side={scene.layout} sceneStart={scene.start} /> : null}
      <div style={{position: "absolute", left: contentBox.x, top: contentBox.y, width: contentBox.w, height: contentBox.h}}>
        {/* Graphics are designed for the landscape content box; a vertical layout draws them there and scales down */}
        <div style={{width: V.w, height: V.h, transform: `scale(${contentBox.w / V.w})`, transformOrigin: "0 0"}}>
          <GraphicView g={scene.graphic} beats={scene.beats} box={{...contentBox, w: V.w, h: V.h}} config={config} />
        </div>
      </div>
    </Camera>
  );
};

const CaptionView: React.FC<{c: Caption; config: Config}> = ({c, config}) => {
  const frame = useCurrentFrame();
  const box = config.layout.caption;
  const opacity = interpolate(frame, [0, 4], [0, 1], {extrapolateRight: "clamp"});
  return (
    <div style={{position: "absolute", left: box.x, top: box.y, width: box.w, height: box.h, display: "flex", alignItems: "center", justifyContent: "center"}}>
      <div style={{fontSize: box.font_px, fontWeight: 600, lineHeight: 1.1, color: config.theme.ink, textAlign: "center", opacity, maxWidth: box.w}}>{c.text}</div>
    </div>
  );
};

const Disclaimer: React.FC<{config: Config}> = ({config}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: "clamp"});
  return (
    <div style={{position: "absolute", top: config.layout.disclaimer_y ?? 24, left: 0, right: 0, display: "flex", justifyContent: "center", opacity}}>
      <div style={{fontSize: config.layout.fonts.label, fontWeight: 600, color: config.theme.muted, border: `3px solid ${config.theme.line}`, borderRadius: 32, padding: "6px 28px", background: "#fff", maxWidth: config.video.width - 2 * config.layout.margin, textAlign: "center", boxSizing: "border-box"}}>
        {config.disclaimer}. People and figures are illustrative examples.
      </div>
    </div>
  );
};

export const Episode: React.FC<EpisodeProps> = (props) => {
  const {fps} = useVideoConfig();
  const f = (s: number) => Math.round(s * fps);
  return (
    <AbsoluteFill style={{backgroundColor: props.config.theme.background, fontFamily: FONT, color: props.config.theme.ink}}>
      <Audio src={staticFile(props.audio)} />
      {props.scenes.map((s) => (
        <Sequence key={s.id} from={f(s.start)} durationInFrames={Math.max(1, f(s.end) - f(s.start))} name={s.id}>
          <SceneView scene={s} config={props.config} />
        </Sequence>
      ))}
      {props.captions.map((c, i) => (
        <Sequence key={i} from={f(c.start)} durationInFrames={Math.max(1, f(c.end) - f(c.start))} name={`caption ${i + 1}`}>
          <CaptionView c={c} config={props.config} />
        </Sequence>
      ))}
      {props.overlays.map((o, i) => (
        <Sequence key={`o${i}`} from={f(o.from)} durationInFrames={Math.max(1, f(o.to) - f(o.from))} name="disclaimer">
          <Disclaimer config={props.config} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
