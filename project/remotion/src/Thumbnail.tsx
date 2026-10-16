import {AbsoluteFill, Img, staticFile} from "remotion";
import {FONT} from "./fonts";

// YouTube thumbnail, 1280x720. Three layouts; every amount is passed in from the assumptions table.
export type ThumbProps = {
  variant: "a" | "b" | "c";
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

export const Thumbnail: React.FC<ThumbProps> = (p) => {
  const V = {a: A, b: B, c: C}[p.variant];
  return (
    <AbsoluteFill style={{background: "#fff", fontFamily: FONT}}>
      <V {...p} />
    </AbsoluteFill>
  );
};
