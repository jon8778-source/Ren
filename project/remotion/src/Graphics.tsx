import {Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from "remotion";
import type {Box, Config, Graphic} from "./types";

type P = {g: Graphic; beats: number[]; box: Box; config: Config};

// Spring that starts at beat i (seconds after the scene starts); 0 before it
const useBeats = (beats: number[]) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return (i: number, damping = 13) => {
    const at = beats[Math.min(i, beats.length - 1)] ?? 0;
    return frame < at * fps ? 0 : spring({frame: frame - at * fps, fps, config: {damping}});
  };
};

const Center: React.FC<{children: React.ReactNode; gap?: number}> = ({children, gap = 28}) => (
  <div style={{width: "100%", height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap}}>{children}</div>
);

// Every graphic that shows money carries this tag: the figures are illustrative
const ExampleTag: React.FC<{config: Config}> = ({config}) => (
  <div style={{alignSelf: "flex-end", fontSize: config.layout.fonts.label, fontWeight: 600, color: config.theme.muted, border: `3px solid ${config.theme.line}`, borderRadius: 999, padding: "2px 22px"}}>
    Example figures
  </div>
);

const rise = (s: number, dist = 50): React.CSSProperties => ({opacity: s, transform: `translateY(${(1 - s) * dist}px)`});

const Mailboxes: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  return (
    <Center>
      <div style={{display: "flex", gap: 34, alignItems: "flex-end"}}>
        {Array.from({length: g.count}).map((_, i) => {
          const s = b(i);
          return (
            <div key={i} style={{position: "relative", width: 180, height: 420}}>
              <div style={{position: "absolute", left: 40, top: -40, width: 100, height: 64, borderRadius: 8, background: "#fff", border: `5px solid ${T.ink}`, opacity: s > 0 ? 1 - interpolate(s, [0.7, 1], [0, 1], {extrapolateLeft: "clamp"}) : 0, transform: `translateY(${s * 150}px)`}} />
              <svg width="180" height="420" viewBox="0 0 180 420">
                <rect x="80" y="200" width="20" height="220" fill={T.muted} />
                <path d="M20 200 V110 A70 70 0 0 1 160 110 V200 Z" fill={T.save} stroke={T.ink} strokeWidth="6" />
                <rect x="55" y="112" width="70" height="12" rx="6" fill={T.ink} />
                <g transform={`rotate(${-80 * s} 165 150)`}>
                  <rect x="160" y="80" width="10" height="75" fill={T.ink} />
                  <rect x="160" y="80" width="40" height="26" fill={T.cost} />
                </g>
              </svg>
            </div>
          );
        })}
      </div>
    </Center>
  );
};

const Bill: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0);
  const stamp = b(1, 9);
  return (
    <Center>
      <ExampleTag config={config} />
      <div style={{position: "relative", width: 620, padding: "48px 56px", borderRadius: 30, border: `6px solid ${T.ink}`, background: "#fff", boxSizing: "border-box", ...rise(s, 90)}}>
        <div style={{fontSize: F.subhead, fontWeight: 700, textTransform: "uppercase", letterSpacing: 2}}>{g.title}</div>
        {[0.9, 0.75, 0.85].map((w, i) => <div key={i} style={{height: 18, width: `${w * 100}%`, borderRadius: 9, background: T.line, marginTop: 22}} />)}
        <div style={{fontSize: F.body, color: T.muted, fontWeight: 600, marginTop: 40}}>Amount due</div>
        <div style={{fontSize: F.number, fontWeight: 700, color: T.cost, lineHeight: 1}}>{g.amount}</div>
        <div style={{position: "absolute", right: -50, top: 96, fontSize: F.title, fontWeight: 700, color: T.cost, border: `7px solid ${T.cost}`, borderRadius: 18, padding: "0 22px", background: "#fff", opacity: stamp, transform: `rotate(-12deg) scale(${2 - stamp})`}}>{g.stamp}</div>
      </div>
    </Center>
  );
};

const Lineup: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const h = b(0);
  return (
    <Center gap={10}>
      {g.tag ? <ExampleTag config={config} /> : null}
      <div style={{display: "flex", gap: 12, alignItems: "flex-end"}}>
        {g.people.map((p: {id: string; name: string; src: string}, i: number) => {
          const s = g.enter ? b(i) : 1;
          const isHi = g.highlight === p.id;
          const dim = g.highlight ? (isHi ? 1 : 1 - 0.7 * h) : 1;
          const grow = isHi ? 1 + 0.12 * h : 1;
          return (
            <div key={p.id} style={{width: 206, display: "flex", flexDirection: "column", alignItems: "center", opacity: s * dim, transform: `translateY(${(1 - s) * 60}px) scale(${grow})`, transformOrigin: "50% 100%"}}>
              <Img src={staticFile(p.src)} style={{width: 206, height: 330, objectFit: "contain", objectPosition: "50% 100%"}} />
              <div style={{fontSize: F.body, fontWeight: 600, marginTop: 8}}>{p.name}</div>
            </div>
          );
        })}
      </div>
      <div style={{height: 100, display: "flex", alignItems: "center"}}>
        {g.tag ? (
          <div style={{fontSize: F.subhead, fontWeight: 700, color: "#fff", background: T.save, borderRadius: 999, padding: "8px 38px", ...rise(h, 30)}}>{g.tag}</div>
        ) : null}
      </div>
    </Center>
  );
};

const Question: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const q = b(1, 8);
  return (
    <Center gap={36}>
      <div style={{width: 260, height: 260, borderRadius: "50%", background: T.gold, color: T.ink, fontSize: 190, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${q}) rotate(${(1 - q) * -30}deg)`}}>?</div>
      <div style={{fontSize: F.title, fontWeight: 700, textAlign: "center", lineHeight: 1.05, ...rise(b(0))}}>
        {g.title}
        <div style={{color: T.gold_edge}}>{g.subtitle}</div>
      </div>
    </Center>
  );
};

const Statement: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const u = b(2);
  return (
    <Center gap={22}>
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.muted, ...rise(b(0))}}>{g.lead}</div>
      <div style={{fontSize: F.title, fontWeight: 700, textAlign: "center", lineHeight: 1.05, ...rise(b(1))}}>{g.title}</div>
      <div style={{position: "relative", fontSize: F.title, fontWeight: 700, color: T.save, ...rise(u)}}>
        {g.subtitle}
        <div style={{position: "absolute", left: 0, bottom: -10, height: 12, width: "100%", borderRadius: 6, background: T.gold, transformOrigin: "0 50%", transform: `scaleX(${u})`}} />
      </div>
    </Center>
  );
};

const Spotlight: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const frame = useCurrentFrame();
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0);
  const sweep = Math.sin(frame / 14) * 60;
  return (
    <Center gap={30}>
      <div style={{position: "relative", width: 520, height: 300, ...rise(s)}}>
        <div style={{position: "absolute", inset: 0, borderRadius: 28, border: `6px solid ${T.ink}`, padding: "36px 40px", boxSizing: "border-box", display: "flex", flexDirection: "column", gap: 26}}>
          {[0.85, 0.6, 0.75, 0.5].map((w, i) => <div key={i} style={{height: 22, width: `${w * 100}%`, borderRadius: 11, background: i === 2 ? T.cost : T.line}} />)}
        </div>
        <svg width="240" height="240" viewBox="0 0 240 240" style={{position: "absolute", left: 200 + sweep, top: 60}}>
          <circle cx="95" cy="95" r="70" fill="rgba(245,184,46,0.25)" stroke={T.ink} strokeWidth="14" />
          <path d="M146 146 L215 215" stroke={T.ink} strokeWidth="22" strokeLinecap="round" />
        </svg>
      </div>
      <div style={{fontSize: F.title, fontWeight: 700, ...rise(s)}}>{g.title}</div>
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.save, ...rise(b(1))}}>{g.subtitle}</div>
    </Center>
  );
};

const LevelTitle: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s0 = b(0, 9);
  return (
    <Center gap={18}>
      <div style={{fontSize: F.subhead, fontWeight: 700, background: T.gold, color: T.ink, borderRadius: 999, padding: "6px 40px", transform: `scale(${s0})`}}>LEVEL {g.level}</div>
      <div style={{fontSize: F.hero, fontWeight: 700, lineHeight: 1, ...rise(b(1))}}>{g.name}</div>
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.muted, ...rise(b(1))}}>{g.subtitle}</div>
    </Center>
  );
};

const Profile: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const T = config.theme;
  const F = config.layout.fonts;
  const n = g.facts.length;
  const at = (beats[n] ?? 0) * fps;
  const count = interpolate(frame, [at, at + 0.8 * fps], [0, g.amount_value], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <Center>
      <ExampleTag config={config} />
      <div style={{width: 760, padding: "44px 56px", borderRadius: 34, border: `6px solid ${T.ink}`, boxSizing: "border-box", display: "flex", flexDirection: "column", gap: 18}}>
        {g.facts.map((f: string, i: number) => (
          <div key={i} style={{fontSize: F.subhead, fontWeight: 600, ...rise(b(i), 30)}}>{f}</div>
        ))}
        <div style={{height: 4, background: T.line, margin: "10px 0"}} />
        <div style={{...rise(b(n), 30)}}>
          <div style={{fontSize: F.body, fontWeight: 600, color: T.muted}}>{g.label}</div>
          <div style={{display: "flex", alignItems: "baseline", gap: 20}}>
            <span style={{fontSize: F.number, fontWeight: 700, color: T.save, lineHeight: 1}}>${Math.round(count).toLocaleString("en-US")}</span>
            <span style={{fontSize: F.body, fontWeight: 600, color: T.muted}}>{g.per}</span>
          </div>
        </div>
      </div>
    </Center>
  );
};

const Budget: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const tone = g.tone === "cost" ? T.cost : T.ink;
  const items: {item: string; amount: string}[] = g.items;
  const totalS = b(items.length, 9);
  return (
    <Center>
      <ExampleTag config={config} />
      <div style={{width: 860, padding: "28px 52px", borderRadius: 34, border: `6px solid ${tone}`, boxSizing: "border-box"}}>
        <div style={{fontSize: F.subhead, fontWeight: 700, color: tone, marginBottom: 10}}>{g.title}</div>
        {items.map((it, i) => {
          const s = b(i);
          return (
            <div key={i} style={{display: "flex", justifyContent: "space-between", fontSize: F.body, fontWeight: 600, padding: "8px 0", borderBottom: `3px solid ${T.line}`, opacity: s, transform: `translateX(${(1 - s) * -60}px)`}}>
              <span>{it.item}</span>
              <span style={{color: g.tone === "cost" ? T.cost : T.ink}}>{it.amount}</span>
            </div>
          );
        })}
        <div style={{display: "flex", justifyContent: "space-between", fontSize: F.subhead, fontWeight: 700, color: tone, paddingTop: 16, opacity: totalS, transform: `scale(${0.9 + 0.1 * totalS})`, transformOrigin: "100% 50%"}}>
          <span>{g.total_label}</span>
          <span>{g.total}</span>
        </div>
      </div>
    </Center>
  );
};

const Result: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const color = (t: string) => (t === "save" ? T.save : t === "gold" ? T.gold_edge : t === "cost" ? T.cost : T.ink);
  return (
    <Center gap={40}>
      <ExampleTag config={config} />
      <div style={{display: "flex", gap: 36}}>
        {g.stats.map((s: {label: string; value: string; tone: string}, i: number) => {
          const v = b(i, 10);
          return (
            <div key={i} style={{width: 470, padding: "36px 0", borderRadius: 34, border: `6px solid ${color(s.tone)}`, textAlign: "center", opacity: v, transform: `scale(${0.7 + 0.3 * v})`}}>
              <div style={{fontSize: F.body, fontWeight: 600, color: T.muted}}>{s.label}</div>
              <div style={{fontSize: F.number, fontWeight: 700, color: color(s.tone), lineHeight: 1.05}}>{s.value}</div>
            </div>
          );
        })}
      </div>
      <div style={{fontSize: F.body, fontWeight: 600, color: T.muted, ...rise(b(g.stats.length), 20)}}>{g.equation}</div>
    </Center>
  );
};

const Envelope: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 12);
  const open = b(1, 12);
  return (
    <Center gap={30}>
      <div style={{fontSize: F.subhead, fontWeight: 700, background: T.ink, color: "#fff", borderRadius: 999, padding: "6px 36px", opacity: s}}>{g.label}</div>
      <div style={{position: "relative", width: 560, height: 360, transform: `translateX(${(1 - s) * 700}px) rotate(${(1 - s) * 18}deg)`}}>
        <div style={{position: "absolute", left: 50, right: 50, top: 40 - open * 130, height: 260, borderRadius: 14, background: "#fff", border: `5px solid ${T.ink}`, display: "flex", alignItems: "flex-start", justifyContent: "center", paddingTop: 20, boxSizing: "border-box", fontSize: F.title, fontWeight: 700, color: T.cost}}>$</div>
        <svg width="560" height="360" viewBox="0 0 560 360" style={{position: "absolute", inset: 0, overflow: "visible"}}>
          <rect x="5" y="5" width="550" height="350" rx="24" fill="#fdf7ea" stroke={T.ink} strokeWidth="8" />
          <path d="M10 350 L280 170 L550 350" fill="none" stroke={T.ink} strokeWidth="6" />
          <path d="M8 10 L280 200 L552 10" fill={T.gold} stroke={T.ink} strokeWidth="8" strokeLinejoin="round" transform={`translate(0 ${10 - open * 10}) scale(1 ${1 - 2 * open}) translate(0 ${-10 + open * 10})`} style={{transformOrigin: "280px 10px"}} />
        </svg>
      </div>
    </Center>
  );
};

const BillVsSavings: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const W = 900;
  const billW = W * b(0);
  const saveW = W * (g.savings_value / g.bill_value) * b(2);
  const bar = (w: number, color: string, label: string): React.ReactNode => (
    <div style={{position: "relative", height: 96, width: W, borderRadius: 24, background: T.line}}>
      <div style={{position: "absolute", left: 0, top: 0, bottom: 0, width: Math.max(w, 0), borderRadius: 24, background: color}} />
      <div style={{position: "absolute", left: Math.max(w, 0) + 18, top: 0, bottom: 0, display: "flex", alignItems: "center", fontSize: F.subhead, fontWeight: 700, color, whiteSpace: "nowrap"}}>{w > 10 && w < W - 200 ? label : ""}</div>
      <div style={{position: "absolute", right: 24, top: 0, bottom: 0, display: "flex", alignItems: "center", fontSize: F.subhead, fontWeight: 700, color: "#fff"}}>{w >= W - 200 ? label : ""}</div>
    </div>
  );
  return (
    <Center gap={18}>
      <ExampleTag config={config} />
      <div style={{width: W, fontSize: F.body, fontWeight: 600}}>Surprise bill <span style={{color: T.muted}}>· {g.due}</span></div>
      <div style={{opacity: b(0)}}>{bar(billW, T.cost, g.bill)}</div>
      <div style={{width: W, fontSize: F.body, fontWeight: 600, marginTop: 24, opacity: b(1)}}>{g.savings_label}</div>
      <div style={{opacity: b(1)}}>{bar(saveW, T.save, g.savings)}</div>
      <div style={{marginTop: 30, fontSize: F.title, fontWeight: 700, color: T.cost, ...rise(b(3, 9), 30)}}>Short by {g.shortfall}</div>
    </Center>
  );
};

const VIEWS: Record<string, React.FC<P>> = {
  mailboxes: Mailboxes,
  bill: Bill,
  lineup: Lineup,
  question: Question,
  statement: Statement,
  spotlight: Spotlight,
  level_title: LevelTitle,
  profile: Profile,
  budget: Budget,
  result: Result,
  envelope: Envelope,
  bill_vs_savings: BillVsSavings,
};

export const GraphicView: React.FC<P> = (p) => {
  const View = VIEWS[p.g.type];
  if (!View) throw new Error(`Unknown graphic type: ${p.g.type}`);
  return <View {...p} />;
};
