// Shapes of build/props.json, written by pipeline/assemble.py.
export type Box = {x: number; y: number; w: number; h: number};

export type Config = {
  video: {width: number; height: number; fps: number};
  layout: {
    caption: Box & {font_px: number; max_lines: number};
    character_left: Box;
    character_right: Box;
    content_when_character_left: Box;
    content_when_character_right: Box;
    fonts: {label: number; body: number; subhead: number; title: number; number: number; hero: number};
  };
  theme: Record<"background" | "ink" | "cost" | "save" | "gold" | "gold_edge" | "muted" | "line", string>;
  disclaimer: string;
};

export type CharacterRef = {id: string; pose: string; src: string; enter: boolean; posePop: boolean; speaking: [number, number] | null};

export type Graphic = {type: string; [key: string]: any};

export type Scene = {
  id: string;
  start: number;
  end: number;
  layout: "character_left" | "character_right";
  character: CharacterRef | null;
  graphic: Graphic;
  camera: "push" | "drift_left" | "drift_right" | "none";
  beats: number[];
};

export type Caption = {text: string; start: number; end: number};
export type Overlay = {type: "disclaimer"; from: number; to: number};

export type EpisodeProps = {
  config: Config;
  duration: number;
  audio: string;
  scenes: Scene[];
  captions: Caption[];
  overlays: Overlay[];
  characters: Record<string, {name: string; poses: Record<string, string>}>;
};
