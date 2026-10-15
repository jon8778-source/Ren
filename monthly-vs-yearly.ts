import type {Short} from "../types";

export const monthlyVsYearly: Short = {
  id: "monthly-vs-yearly",
  durationInSeconds: 14,
  ren: {}, // add e.g. {shocked: "ren-shocked.png", excited: "ren-excited.png"}
  voiceover: null, // add e.g. "monthly-vs-yearly.mp3"
  disclaimer: "Example only, not financial advice",
  scenes: [
    {
      type: "hook",
      start: 0,
      end: 3,
      big: "$119.88",
      caption: "That's what a $9.99 subscription really costs.",
    },
    {
      type: "stack",
      start: 3,
      end: 7.5,
      amount: 9.99,
      count: 12,
      label: "$9.99 × 12 months",
      caption: "It doesn't feel like much. Until you stack it.",
    },
    {
      type: "checklist",
      start: 7.5,
      end: 11,
      items: ["Streaming", "Music", "Cloud storage", "That app you forgot"],
      caption: "Now times every subscription by 12.",
    },
    {
      type: "cta",
      start: 11,
      end: 14,
      title: "Free budgeting workbook",
      sub: "Link in bio",
      caption: "",
    },
  ],
};
