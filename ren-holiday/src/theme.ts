// All of Ren's colours and proportions live here. Tweak freely.
// Coordinates are in Ren's own SVG space: a 400 x 700 box, head at the top,
// feet at the bottom. The <Ren size={...}/> prop scales the whole thing.

export const renColors = {
  outline: "#1B2238", // thin dark navy line art
  skin: "#EBC29C", // tan
  skinShade: "#D9A880",
  blush: "#E8907A",
  hair: "#15171C",
  hairShine: "#3A3F4B",
  glasses: "#1E1F24",
  lensGlint: "#FFFFFF",
  eye: "#1B1B1F",
  mouth: "#7A2E2E",
  tongue: "#D86A6A",
  teeth: "#FFFFFF",
  shirt: "#2F3A57", // navy button-up
  shirtShade: "#252E47",
  button: "#1B2238",
  tee: "#F4F6F8", // plain white tee
  teeShade: "#DDE2E8",
  pants: "#4B5266",
  pantsShade: "#3E4456",
  shoes: "#2A2B30",
  sweat: "#8FD3F4",
  sweatEdge: "#3D8FC0",
  // props
  suitcase: "#E2763A",
  suitcaseEdge: "#B4552A",
  wheel: "#2B2E36",
  calculator: "#C9D2DC",
  calcScreen: "#9EC7A3",
  glass: "#CFEFFF",
  juice: "#F6A93B",
};

export const renShape = {
  lineWidth: 4.5, // outline thickness
  headCx: 200,
  headCy: 175,
  eyeY: 186,
  eyeGap: 36, // distance from centre to each eye
  lensR: 27,
  mouthY: 244,
  shoulderY: 322,
  shoulderX: 82, // distance from centre to each shoulder joint
  armWidth: 38, // sleeve thickness
  handR: 15,
  hipY: 476,
  breathPx: 2.2, // how far the head rises when breathing
  breathSeconds: 3.4,
};

export const brand = {
  background: "#FFFFFF",
  ink: "#13233F",
  cost: "#E23D3D",
  save: "#1E9E5A",
  gold: "#F5B82E",
  sky: "#BFE3F7",
};
