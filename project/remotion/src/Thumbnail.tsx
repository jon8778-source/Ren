import {AbsoluteFill, Img, staticFile} from "remotion";
import {FONT} from "./fonts";
import {ItemIcon} from "./Graphics";

// YouTube thumbnail, 1280x720. Three layouts; every amount is passed in from the assumptions table.
export type ThumbProps = {
  variant: "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i";
  text?: Record<string, string>;
  theme: Record<string, string>;
  bill: string;
  low: string;
  high: string;
  people: {id: string; name: string}[];
};

const char = (id: string, pose: string) => staticFile(`characters/${id}/${pose}.png`);

const Pill: React.FC<{bg: string; color: string; size: number; children: React.ReactNode; rotate?: number}> = ({bg, color, size, children, rotate = 0}) => (
  <div style={{display: "inline-block", background: bg, color, fontSize: size, fontWeight: 700, borderRadius: 24, padding: "4px 28px", transform: `rotate(${rotate}deg)`, lineHeight: 1.1}}>{children}</div>
);

// A: the bill in the middle, five faces in a row underneath
const A: React.FC<ThumbProps> = ({theme: T, bill, people}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 60, top: 40, fontSize: 92, fontWeight: 700, color: T.ink, lineHeight: 0.95}}>
      SAME BILL
      <div style={{color: T.cost}}>5 INCOMES</div>
    </div>
    <div style={{position: "absolute", right: 70, top: 46, width: 470, padding: "26px 34px", borderRadius: 30, border: `9px solid ${T.ink}`, background: "#fff", transform: "rotate(4deg)", boxSizing: "border-box"}}>
      <div style={{fontSize: 40, fontWeight: 700, color: T.ink}}>DENTAL BILL</div>
      <div style={{fontSize: 150, fontWeight: 700, color: T.cost, lineHeight: 1}}>{bill}</div>
    </div>
    <div style={{position: "absolute", left: 30, right: 30, bottom: 0, display: "flex", justifyContent: "space-between", alignItems: "flex-end"}}>
      {people.map((p, i) => (
        <Img key={p.id} src={char(p.id, i === 4 ? "shocked" : i === 1 ? "happy" : "worried")} style={{width: 236, height: 330, objectFit: "contain", objectPosition: "50% 100%"}} />
      ))}
    </div>
  </AbsoluteFill>
);

// B: the highest earner, shocked, with "and still stressed?"
const B: React.FC<ThumbProps> = ({theme: T, high, bill}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 60, top: 70, width: 720}}>
      <Pill bg={T.save} color="#fff" size={84}>{high}/mo</Pill>
      <div style={{fontSize: 118, fontWeight: 700, color: T.ink, lineHeight: 0.95, marginTop: 30}}>
        STILL
        <div style={{color: T.cost}}>STRESSED?</div>
      </div>
      <div style={{marginTop: 34}}>
        <Pill bg={T.cost} color="#fff" size={60} rotate={-3}>one {bill} bill</Pill>
      </div>
    </div>
    <Img src={char("richard", "shocked")} style={{position: "absolute", right: 30, bottom: 0, height: 660, width: 500, objectFit: "contain", objectPosition: "50% 100%"}} />
  </AbsoluteFill>
);

// C: lowest vs highest income, Ren in the middle asking who copes
const C: React.FC<ThumbProps> = ({theme: T, low, high}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 0, right: 0, top: 30, textAlign: "center", fontSize: 96, fontWeight: 700, color: T.ink}}>
      WHO COPES <span style={{color: T.cost}}>BETTER?</span>
    </div>
    <Img src={char("sam", "neutral")} style={{position: "absolute", left: 20, bottom: 0, height: 470, width: 380, objectFit: "contain", objectPosition: "50% 100%"}} />
    <Img src={char("richard", "worried")} style={{position: "absolute", right: 20, bottom: 0, height: 470, width: 380, objectFit: "contain", objectPosition: "50% 100%"}} />
    <Img src={char("ren", "thinking")} style={{position: "absolute", left: 470, bottom: 0, height: 440, width: 340, objectFit: "contain", objectPosition: "50% 100%"}} />
    <div style={{position: "absolute", left: 60, top: 190}}><Pill bg={T.gold} color={T.ink} size={64} rotate={-4}>{low}/mo</Pill></div>
    <div style={{position: "absolute", right: 60, top: 190}}><Pill bg={T.save} color="#fff" size={64} rotate={4}>{high}/mo</Pill></div>
    <div style={{position: "absolute", left: 0, right: 0, top: 205, textAlign: "center", fontSize: 72, fontWeight: 700, color: T.muted}}>vs</div>
  </AbsoluteFill>
);


// Italy brochure prop (same drawing as the video), optional stamp
const Brochure: React.FC<{T: Record<string, string>; w: number; stamp?: string; rotate?: number}> = ({T, w, stamp, rotate = -4}) => (
  <div style={{position: "relative", width: w, height: w * 0.67, transform: `rotate(${rotate}deg)`}}>
    <svg width={w} height={w * 0.67} viewBox="0 0 640 430" style={{position: "absolute", inset: 0}}>
      <rect x="6" y="6" width="628" height="418" rx="26" fill="#fff" stroke={T.ink} strokeWidth="10" />
      <circle cx="520" cy="110" r="52" fill={T.gold} stroke={T.gold_edge} strokeWidth="6" />
      <path d="M10 300 Q160 200 320 270 T630 240 L630 420 L10 420 Z" fill={T.save} />
      <path d="M10 350 Q120 330 230 350 T450 350 T630 345 L630 420 L10 420 Z" fill={T.ink} opacity="0.8" />
      <g stroke={T.ink} strokeWidth="5"><rect x="70" y="232" width="56" height="62" fill="#fff" /><path d="M62 236 L98 206 L134 236 Z" fill={T.cost} /></g>
      <text x="230" y="120" fontSize="96" fontWeight="700" fill={T.ink} fontFamily="Fredoka">Italy</text>
    </svg>
    {stamp ? <div style={{position: "absolute", right: -w * 0.08, bottom: w * 0.06, fontSize: w * 0.13, fontWeight: 700, color: T.cost, border: `${w * 0.012}px solid ${T.cost}`, borderRadius: 16, padding: "0 18px", background: "#fff", whiteSpace: "nowrap", transform: "rotate(-12deg)"}}>{stamp}</div> : null}
  </div>
);

// D: old Frank, the money and the brochure he never used
const D: React.FC<ThumbProps> = ({theme: T, text = {}}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 50, top: 40}}>
      <Pill bg={T.save} color="#fff" size={92}>{text.money}</Pill>
      <div style={{fontSize: 104, fontWeight: 700, color: T.ink, lineHeight: 0.95, marginTop: 24}}>
        AND HE
        <div style={{color: T.cost}}>NEVER WENT</div>
      </div>
    </div>
    <div style={{position: "absolute", left: 70, bottom: 40}}><Brochure T={T} w={400} /></div>
    <Img src={staticFile("characters/frank-70/regretful.png")} style={{position: "absolute", right: 20, bottom: 0, height: 660, width: 520, objectFit: "contain", objectPosition: "50% 100%"}} />
  </AbsoluteFill>
);

// E: three old faces, who got it right?
const E: React.FC<ThumbProps> = ({theme: T}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 0, right: 0, top: 26, textAlign: "center", fontSize: 100, fontWeight: 700, color: T.ink}}>
      WHO GOT IT <span style={{color: T.save}}>RIGHT?</span>
    </div>
    <div style={{position: "absolute", left: 20, right: 20, bottom: 0, display: "flex", justifyContent: "space-around", alignItems: "flex-end"}}>
      {[["frank-70", "regretful", "SAVER", T.ink], ["yara-70", "stressed", "SPENDER", T.cost], ["bea-70", "joyful", "BALANCED", T.save]].map(([id, pose, lab, col]) => (
        <div key={id} style={{position: "relative", width: 400, height: 520}}>
          <Img src={staticFile(`characters/${id}/${pose}.png`)} style={{width: 400, height: 520, objectFit: "contain", objectPosition: "50% 100%"}} />
          <div style={{position: "absolute", left: 0, right: 0, bottom: 20, textAlign: "center"}}><Pill bg={col} color="#fff" size={52}>{lab}</Pill></div>
        </div>
      ))}
    </div>
  </AbsoluteFill>
);

// F: Frank vs Bea, money vs memories
const F_: React.FC<ThumbProps> = ({theme: T, text = {}}) => (
  <AbsoluteFill>
    <Img src={staticFile("characters/frank-70/regretful.png")} style={{position: "absolute", left: 0, bottom: 0, height: 470, width: 420, objectFit: "contain", objectPosition: "50% 100%"}} />
    <Img src={staticFile("characters/bea-70/joyful.png")} style={{position: "absolute", right: 0, bottom: 0, height: 470, width: 420, objectFit: "contain", objectPosition: "50% 100%"}} />
    <div style={{position: "absolute", left: 0, right: 0, top: 30, textAlign: "center", fontSize: 96, fontWeight: 700, color: T.ink}}>
      MONEY <span style={{color: T.muted}}>vs</span> <span style={{color: T.gold_edge}}>MEMORIES</span>
    </div>
    <div style={{position: "absolute", left: 40, top: 150}}><Pill bg={T.save} color="#fff" size={64} rotate={-4}>{text.money}</Pill></div>
    <div style={{position: "absolute", right: 60, top: 150}}><Pill bg={T.gold} color={T.ink} size={64} rotate={4}>Italy ✓</Pill></div>
    <div style={{position: "absolute", left: 470, top: 300}}><Brochure T={T} w={340} rotate={3} /></div>
  </AbsoluteFill>
);

// Bonus envelope prop (same drawing as the video), with an optional amount card sticking out
const BonusEnvelope: React.FC<{T: Record<string, string>; w: number; amount?: string; rotate?: number}> = ({T, w, amount, rotate = -5}) => (
  <div style={{position: "relative", width: w, height: w * 0.9, transform: `rotate(${rotate}deg)`}}>
    <svg width={w} height={w * 0.9} viewBox="0 0 560 504" style={{position: "absolute", inset: 0}}>
      <rect x="5" y="149" width="550" height="350" rx="24" fill="#fdf7ea" stroke={T.ink} strokeWidth="10" />
      <path d="M8 154 L280 10 L552 154" fill={T.gold} stroke={T.ink} strokeWidth="10" strokeLinejoin="round" />
      <rect x="50" y="40" width="460" height="260" rx="14" fill="#fff" stroke={T.ink} strokeWidth="8" />
      <path d="M5 294 L280 394 L555 294 V475 Q555 499 531 499 H29 Q5 499 5 475 Z" fill="#fdf7ea" stroke={T.ink} strokeWidth="10" strokeLinejoin="round" />
    </svg>
    {amount ? <div style={{position: "absolute", left: 0, right: 0, top: w * 0.13, textAlign: "center", fontSize: w * 0.2, fontWeight: 700, color: T.save}}>{amount}</div> : null}
  </div>
);

// G: Max vs Lena a year later, the same envelope between them (layout C style)
const G: React.FC<ThumbProps> = ({theme: T, text = {}}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 0, right: 0, top: 26, textAlign: "center", fontSize: 100, fontWeight: 700, color: T.ink}}>
      WHO'S <span style={{color: T.save}}>HAPPIER?</span>
    </div>
    <Img src={staticFile("characters/max-31/shrug.png")} style={{position: "absolute", left: 10, bottom: 0, height: 500, width: 400, objectFit: "contain", objectPosition: "50% 100%"}} />
    <Img src={staticFile("characters/lena-31/happy.png")} style={{position: "absolute", right: 10, bottom: 0, height: 500, width: 400, objectFit: "contain", objectPosition: "50% 100%"}} />
    <div style={{position: "absolute", left: 460, top: 200}}><BonusEnvelope T={T} w={360} amount={text.money} /></div>
    <div style={{position: "absolute", left: 0, right: 0, bottom: 40, textAlign: "center"}}><Pill bg={T.ink} color="#fff" size={52}>SAME BONUS</Pill></div>
  </AbsoluteFill>
);

// H: the big number and Lena, happy a year later
const H: React.FC<ThumbProps> = ({theme: T, text = {}}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 50, top: 50}}>
      <Pill bg={T.save} color="#fff" size={110}>{text.money}</Pill>
      <div style={{fontSize: 100, fontWeight: 700, color: T.ink, lineHeight: 0.95, marginTop: 26}}>
        ONLY ONE
        <div style={{color: T.save}}>WAS HAPPIER</div>
      </div>
      <div style={{marginTop: 26}}><Pill bg={T.gold} color={T.ink} size={56} rotate={-3}>a year later</Pill></div>
    </div>
    <Img src={staticFile("characters/lena-31/happy.png")} style={{position: "absolute", right: 10, bottom: 0, height: 660, width: 520, objectFit: "contain", objectPosition: "50% 100%"}} />
  </AbsoluteFill>
);

// I: things vs time, each person with what they bought
const I: React.FC<ThumbProps> = ({theme: T, text = {}}) => (
  <AbsoluteFill>
    <div style={{position: "absolute", left: 0, right: 0, top: 26, textAlign: "center", fontSize: 100, fontWeight: 700, color: T.ink}}>
      <span style={{color: T.cost}}>THINGS</span> <span style={{color: T.muted}}>vs</span> <span style={{color: T.save}}>TIME</span>
    </div>
    <Img src={staticFile("characters/max-31/shrug.png")} style={{position: "absolute", left: 0, bottom: 0, height: 480, width: 400, objectFit: "contain", objectPosition: "50% 100%"}} />
    <Img src={staticFile("characters/lena-31/happy.png")} style={{position: "absolute", right: 0, bottom: 0, height: 480, width: 400, objectFit: "contain", objectPosition: "50% 100%"}} />
    <div style={{position: "absolute", left: 400, top: 270, transform: "scale(1.3) rotate(-6deg)", transformOrigin: "0 0"}}><ItemIcon icon="tv" T={T as any} /></div>
    <div style={{position: "absolute", left: 640, top: 290, transform: "scale(1.3) rotate(6deg)", transformOrigin: "0 0"}}><ItemIcon icon="trip" T={T as any} /></div>
    <div style={{position: "absolute", left: 0, right: 0, top: 160, textAlign: "center"}}><Pill bg={T.gold} color={T.ink} size={52}>Same {text.money}. One year later.</Pill></div>
  </AbsoluteFill>
);

export const Thumbnail: React.FC<ThumbProps> = (p) => {
  const V = {a: A, b: B, c: C, d: D, e: E, f: F_, g: G, h: H, i: I}[p.variant];
  return (
    <AbsoluteFill style={{background: "#fff", fontFamily: FONT}}>
      <V {...p} />
    </AbsoluteFill>
  );
};
