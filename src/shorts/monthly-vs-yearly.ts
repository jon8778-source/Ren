import type {Short} from "../types";

export const monthlyVsYearly: Short = {
  id: "monthly-vs-yearly",
  durationInSeconds: 15,
  ren: {
    shocked: "ren-shocked.png",
    pointing: "ren-pointing.png",
    excited: "ren-thumbs-up.png",
    thumbsUp: "ren-thumbs-up.png",
    thinking: "ren-thinking.png",
    worried: "ren-worried.png",
    waving: "ren-waving.png",
    talking: "ren-talking.png",
    neutral: "ren-neutral.png",
  },
  voiceover: "monthly-vs-yearly.mp3", // made with scripts/voiceover.py
  disclaimer: "Example only, not financial advice",
  scenes: [
    {
      type: "hook",
      start: 0,
      end: 3.6,
      big: "$119.88",
      caption: "That's what a $9.99 subscription really costs.",
    },
    {
      type: "stack",
      start: 3.6,
      end: 8,
      amount: 9.99,
      count: 12,
      label: "$9.99 × 12 months",
      caption: "It doesn't feel like much. Until you stack it.",
    },
    {
      type: "checklist",
      start: 8,
      end: 11.4,
      items: ["Streaming", "Music", "Cloud storage", "That app you forgot"],
      caption: "Now times every subscription by 12.",
    },
    {
      type: "cta",
      start: 11.4,
      end: 15,
      title: "Free budgeting workbook",
      sub: "Link in bio",
      caption: "",
    },
  ],
};
