export type Mood = "shocked" | "pointing" | "excited";

type Timed = {start: number; end: number; caption: string};

export type Scene =
  | (Timed & {type: "hook"; big: string})
  | (Timed & {type: "stack"; amount: number; count: number; label: string})
  | (Timed & {type: "checklist"; items: string[]})
  | (Timed & {type: "cta"; title: string; sub: string});

export type Short = {
  id: string; // letters, numbers and dashes only
  durationInSeconds: number;
  // Ren images in /public, e.g. {shocked: "ren-shocked.png"}. Missing moods use the placeholder.
  ren: Partial<Record<Mood, string>>;
  voiceover: string | null; // e.g. "monthly-vs-yearly.mp3" in /public
  disclaimer: string;
  scenes: Scene[];
};
