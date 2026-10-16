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
        <div style={{position: "absolute", right: -50, top: 96, fontSize: F.title, fontWeight: 700, color: T.cost, border: `7px solid ${T.cost}`, borderRadius: 18, padding: "0 22px", background: "#fff", whiteSpace: "nowrap", opacity: stamp, transform: `rotate(-12deg) scale(${2 - stamp})`}}>{g.stamp}</div>
      </div>
    </Center>
  );
};

const Lineup: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const h = b(0);
  const few = g.people.length <= 3;
  const pw = few ? 300 : 206;
  const ph = few ? 450 : 330;
  return (
    <Center gap={10}>
      <div style={{display: "flex", gap: 12, alignItems: "flex-end"}}>
        {g.people.map((p: {id: string; name: string; src: string}, i: number) => {
          const s = g.enter && !g.labels ? b(i) : 1;
          const isHi = g.highlight === p.id;
          const dim = g.highlight ? (isHi ? 1 : 1 - 0.7 * h) : 1;
          const grow = isHi ? 1 + 0.12 * h : 1;
          return (
            <div key={p.id} style={{width: pw, display: "flex", flexDirection: "column", alignItems: "center", opacity: s * dim, transform: `translateY(${(1 - s) * 60}px) scale(${grow})`, transformOrigin: "50% 100%"}}>
              <Img src={staticFile(p.src)} style={{width: pw, height: ph, objectFit: "contain", objectPosition: "50% 100%"}} />
              <div style={{fontSize: F.body, fontWeight: 600, marginTop: 8}}>{p.name}</div>
              {g.labels && g.labels[i] ? (
                <div style={{fontSize: F.label, fontWeight: 700, color: T.ink, background: T.line, borderRadius: 16, padding: "4px 12px", marginTop: 6, textAlign: "center", ...rise(b(i), 20)}}>{g.labels[i]}</div>
              ) : null}
            </div>
          );
        })}
      </div>
      <div style={{height: 100, display: "flex", alignItems: "center"}}>
        {g.tag ? (
          <div style={{fontSize: F.subhead, fontWeight: 700, color: "#fff", background: T.save, borderRadius: 999, padding: "8px 38px", ...rise(h, 30)}}>{g.tag}</div>
        ) : null}
      </div>
      {g.tag && g.tag.includes("$") ? <ExampleTag config={config} /> : null}
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
  const money = [g.lead, g.title, g.subtitle].some((t) => typeof t === "string" && t.includes("$"));
  return (
    <Center gap={22}>
      {money ? <ExampleTag config={config} /> : null}
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.muted, ...rise(b(0))}}>{g.lead}</div>
      <div style={{fontSize: F.title, fontWeight: 700, textAlign: "center", lineHeight: 1.05, ...rise(b(1))}}>{g.title}</div>
      <div style={{position: "relative", fontSize: F.title, fontWeight: 700, color: T.save, ...rise(u)}}>
        {g.subtitle}
        <div style={{position: "absolute", left: 0, bottom: -10, height: 12, width: "100%", borderRadius: 6, background: T.gold, transformOrigin: "0 50%", transform: `scaleX(${u})`}} />
      </div>
      {g.note ? <div style={{marginTop: 26, fontSize: F.label, fontWeight: 600, color: T.muted, textAlign: "center", maxWidth: 1000, ...rise(b(3), 20)}}>{g.note}</div> : null}
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
  const compact = g.compact || items.length > 4;
  const totalS = b(items.length, 9);
  return (
    <Center>
      <ExampleTag config={config} />
      <div style={{width: 860, padding: "28px 52px", borderRadius: 34, border: `6px solid ${tone}`, boxSizing: "border-box"}}>
        <div style={{fontSize: F.subhead, fontWeight: 700, color: tone, marginBottom: 10}}>{g.title}</div>
        {items.map((it, i) => {
          const s = b(i);
          return (
            <div key={i} style={{display: "flex", justifyContent: "space-between", fontSize: compact ? F.label : F.body, fontWeight: 600, padding: compact ? "3px 0" : "8px 0", borderBottom: `3px solid ${T.line}`, opacity: s, transform: `translateX(${(1 - s) * -60}px)`}}>
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
  const top = Math.max(g.bill_value, g.savings_value);
  const billW = W * (g.bill_value / top) * b(0);
  const saveW = W * (g.savings_value / top) * b(2);
  const bar = (w: number, color: string, label: string): React.ReactNode => (
    <div style={{position: "relative", height: 96, width: W, borderRadius: 24, background: T.line}}>
      <div style={{position: "absolute", left: 0, top: 0, bottom: 0, width: Math.max(w, 0), borderRadius: 24, background: color}} />
      <div style={{position: "absolute", left: Math.max(w, 0) + 18, top: 0, bottom: 0, display: "flex", alignItems: "center", fontSize: F.subhead, fontWeight: 700, color, whiteSpace: "nowrap"}}>{w > 10 && w < W - 220 ? label : ""}</div>
      <div style={{position: "absolute", left: 0, width: Math.max(w, 0), top: 0, bottom: 0, display: "flex", alignItems: "center", justifyContent: "flex-end", paddingRight: 24, boxSizing: "border-box", fontSize: F.subhead, fontWeight: 700, color: "#fff"}}>{w >= W - 220 ? label : ""}</div>
    </div>
  );
  return (
    <Center gap={18}>
      <ExampleTag config={config} />
      <div style={{width: W, fontSize: F.body, fontWeight: 600}}>Surprise bill <span style={{color: T.muted}}>· {g.due}</span></div>
      <div style={{opacity: b(0)}}>{bar(billW, T.cost, g.bill)}</div>
      <div style={{width: W, fontSize: F.body, fontWeight: 600, marginTop: 24, opacity: b(1)}}>{g.savings_label}</div>
      <div style={{opacity: b(1)}}>{bar(saveW, T.save, g.savings)}</div>
      <div style={{marginTop: 30, fontSize: F.title, fontWeight: 700, color: g.verdict_tone === "save" ? T.save : T.cost, ...rise(b(3, 9), 30)}}>{g.verdict}</div>
    </Center>
  );
};


const tone = (T: Config["theme"], t?: string) => (t === "save" ? T.save : t === "gold" ? T.gold_edge : t === "cost" ? T.cost : T.ink);

// Numbered list (rules, takeaways). Numbers come from the order, never typed in the text.
const List: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  return (
    <Center gap={26}>
      <div style={{fontSize: F.title, fontWeight: 700, alignSelf: "flex-start", ...rise(b(0))}}>{g.title}</div>
      {g.items.map((it: string, i: number) => {
        const s = b(i + 1);
        return (
          <div key={i} style={{alignSelf: "stretch", display: "flex", alignItems: "center", gap: 28, fontSize: F.subhead, fontWeight: 600, opacity: s, transform: `translateX(${(1 - s) * -70}px)`}}>
            {g.numbered === false ? (
              <div style={{width: 26, height: 26, borderRadius: 13, background: T.gold, flex: "none", marginLeft: 22}} />
            ) : (
              <div style={{width: 84, height: 84, borderRadius: 42, background: T.gold, color: T.ink, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center", flex: "none"}}>{i + 1}</div>
            )}
            <span>{it}</span>
          </div>
        );
      })}
      {g.footer ? <div style={{fontSize: F.subhead, fontWeight: 700, color: tone(T, g.footer_tone), ...rise(b(g.items.length + 1))}}>{g.footer}</div> : null}
    </Center>
  );
};

// Three tiles with arrows: comes in -> goes out -> what's left
const Tiles: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  return (
    <Center>
      <div style={{display: "flex", alignItems: "center", gap: 18}}>
        {g.tiles.map((t: {label: string; tone: string}, i: number) => {
          const s = b(i, 10);
          return (
            <div key={i} style={{display: "flex", alignItems: "center", gap: 18}}>
              {i ? <svg width="56" height="40" viewBox="0 0 56 40" style={{opacity: s}}><path d="M4 20 H46 M32 6 L48 20 L32 34" fill="none" stroke={T.ink} strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" /></svg> : null}
              <div style={{width: 300, height: 300, borderRadius: 40, border: `7px solid ${tone(T, t.tone)}`, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontSize: F.subhead, fontWeight: 700, color: tone(T, t.tone), padding: 20, boxSizing: "border-box", transform: `scale(${0.6 + 0.4 * s})`, opacity: s}}>{t.label}</div>
            </div>
          );
        })}
      </div>
    </Center>
  );
};

// Payment plan: a "now" block from savings, then one block per month
const PaymentPlan: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const T = config.theme;
  const F = config.layout.fonts;
  const n = Math.round(g.months_value);
  const start = (beats[1] ?? 0) * fps;
  const per = ((beats[2] ?? 3) * fps - start) / n;
  return (
    <Center gap={30}>
      <ExampleTag config={config} />
      <div style={{display: "flex", alignItems: "flex-end", gap: 22}}>
        <div style={{textAlign: "center", ...rise(b(0))}}>
          <div style={{width: 190, height: 190, borderRadius: 26, background: T.gold, color: T.ink, display: "flex", alignItems: "center", justifyContent: "center", fontSize: F.subhead, fontWeight: 700}}>{g.now}</div>
          <div style={{fontSize: F.label, fontWeight: 600, color: T.muted, marginTop: 10}}>{g.now_label}</div>
        </div>
        <div>
          <div style={{display: "grid", gridTemplateColumns: "repeat(5, 120px)", gap: 14}}>
            {Array.from({length: n}).map((_, i) => {
              const s = frame < start + i * per ? 0 : spring({frame: frame - start - i * per, fps, config: {damping: 12}});
              return (
                <div key={i} style={{height: 88, borderRadius: 18, background: T.save, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: F.label, fontWeight: 700, opacity: s, transform: `scale(${0.5 + 0.5 * s})`}}>{g.monthly}</div>
              );
            })}
          </div>
          <div style={{fontSize: F.label, fontWeight: 600, color: T.muted, marginTop: 10, textAlign: "center", opacity: b(1)}}>{g.months_label}</div>
        </div>
      </div>
      <div style={{fontSize: F.subhead, fontWeight: 700, ...rise(b(2))}}>{g.total_label}</div>
    </Center>
  );
};

// Bar groups: each group compares a few labelled amounts on its own scale
const CompareGroups: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const W = 560;
  let k = 0;
  return (
    <Center gap={34}>
      <ExampleTag config={config} />
      {g.groups.map((grp: {title: string; bars: {label: string; value: string; value_value: number; tone: string}[]}, gi: number) => {
        const top = Math.max(...grp.bars.map((x) => x.value_value));
        return (
          <div key={gi} style={{display: "flex", flexDirection: "column", gap: 14}}>
            <div style={{fontSize: F.body, fontWeight: 700, color: T.muted, opacity: b(k)}}>{grp.title}</div>
            {grp.bars.map((bar, bi) => {
              const s = b(k++);
              return (
                <div key={bi} style={{display: "flex", alignItems: "center", gap: 20}}>
                  <div style={{width: 230, fontSize: F.body, fontWeight: 600, textAlign: "right"}}>{bar.label}</div>
                  <div style={{width: Math.max(18, W * (bar.value_value / top) * s), height: 70, borderRadius: 18, background: tone(T, bar.tone)}} />
                  <div style={{fontSize: F.subhead, fontWeight: 700, color: tone(T, bar.tone), opacity: s}}>{bar.value}</div>
                </div>
              );
            })}
          </div>
        );
      })}
      {g.footer ? <div style={{fontSize: F.subhead, fontWeight: 700, color: tone(T, g.footer_tone), ...rise(b(k), 30)}}>{g.footer}</div> : null}
    </Center>
  );
};

// Pay and spending rising together (lifestyle creep), no numbers
const Rising: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 20);
  const steps = [0.35, 0.55, 0.75, 1];
  return (
    <Center gap={24}>
      <div style={{display: "flex", alignItems: "flex-end", gap: 70, height: 440}}>
        {[{label: g.left, color: T.save}, {label: g.right, color: T.cost}].map((col, ci) => (
          <div key={ci} style={{display: "flex", flexDirection: "column", alignItems: "center", gap: 14}}>
            <div style={{display: "flex", alignItems: "flex-end", gap: 12, height: 380}}>
              {steps.map((h, i) => (
                <div key={i} style={{width: 64, height: 380 * h * Math.min(1, Math.max(0, s * 4 - i)), borderRadius: 14, background: col.color, opacity: 0.45 + 0.15 * i}} />
              ))}
            </div>
            <div style={{fontSize: F.subhead, fontWeight: 700, color: col.color}}>{col.label}</div>
          </div>
        ))}
      </div>
      <div style={{fontSize: F.subhead, fontWeight: 700, ...rise(b(1))}}>{g.caption}</div>
    </Center>
  );
};

// Credit card with a balance that grows with interest
const CardDebt: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const frame = useCurrentFrame();
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 12);
  const up = b(1);
  return (
    <Center gap={34}>
      <ExampleTag config={config} />
      <div style={{position: "relative", width: 560, height: 350, borderRadius: 36, background: T.ink, transform: `rotate(${(1 - s) * -14}deg) scale(${0.7 + 0.3 * s})`, opacity: s}}>
        <div style={{position: "absolute", left: 50, top: 90, width: 100, height: 74, borderRadius: 14, background: T.gold}} />
        <div style={{position: "absolute", left: 50, bottom: 50, color: "#fff", fontSize: F.body, fontWeight: 600, letterSpacing: 4}}>•••• •••• ••••</div>
        <div style={{position: "absolute", right: -60, top: -50, fontSize: F.title, fontWeight: 700, color: "#fff", background: T.cost, borderRadius: 24, padding: "4px 26px"}}>+{g.amount}</div>
      </div>
      <div style={{display: "flex", alignItems: "center", gap: 18, fontSize: F.subhead, fontWeight: 700, color: T.cost, opacity: up}}>
        <svg width="64" height="64" viewBox="0 0 64 64" style={{transform: `translateY(${-Math.abs(Math.sin(frame / 10)) * 8}px)`}}>
          <path d="M32 56 V10 M12 28 L32 8 L52 28" fill="none" stroke={T.cost} strokeWidth="9" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {g.caption}
      </div>
    </Center>
  );
};

// One dollar split into fixed costs and the rest
const ShareBar: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const W = 940;
  const s = b(0, 18);
  const pct = g.share_value / 100;
  return (
    <Center gap={30}>
      <ExampleTag config={config} />
      <div style={{fontSize: F.number, fontWeight: 700, color: T.cost, lineHeight: 1, ...rise(b(1))}}>{g.headline}</div>
      <div style={{position: "relative", width: W, height: 130, borderRadius: 30, background: T.line, overflow: "hidden"}}>
        <div style={{position: "absolute", left: 0, top: 0, bottom: 0, width: W * pct * s, background: T.cost, display: "flex", alignItems: "center", paddingLeft: 30, boxSizing: "border-box", color: "#fff", fontSize: F.subhead, fontWeight: 700, whiteSpace: "nowrap"}}>{g.left_label}</div>
      </div>
      <div style={{width: W, marginTop: -16, textAlign: "right", fontSize: F.label, fontWeight: 700, color: T.save, opacity: b(2)}}>↑ {g.right_label}</div>
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.muted, ...rise(b(2))}}>{g.caption}</div>
    </Center>
  );
};

// The habit that made the difference
const Habit: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 10);
  return (
    <Center gap={26}>
      <div style={{fontSize: F.subhead, fontWeight: 700, color: T.muted, ...rise(s)}}>{g.name}'s habit</div>
      <div style={{display: "flex", alignItems: "center", gap: 34, padding: "40px 54px", borderRadius: 40, border: `7px solid ${T.save}`, transform: `scale(${0.7 + 0.3 * s})`, opacity: s}}>
        <svg width="120" height="120" viewBox="0 0 120 120"><circle cx="60" cy="60" r="56" fill={T.save} /><path d="M32 62 L52 82 L90 40" fill="none" stroke="#fff" strokeWidth="13" strokeLinecap="round" strokeLinejoin="round" /></svg>
        <div style={{fontSize: F.title, fontWeight: 700, lineHeight: 1.05, maxWidth: 620}}>{g.habit}</div>
      </div>
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.save, ...rise(b(1))}}>{g.detail}</div>
    </Center>
  );
};

// Call to action: the workbook, "in the description"
const Cta: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const frame = useCurrentFrame();
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 12);
  return (
    <Center gap={22}>
      <div style={{width: 380, height: 450, borderRadius: "16px 32px 32px 16px", background: T.save, color: "#fff", padding: "46px 40px", boxSizing: "border-box", display: "flex", flexDirection: "column", gap: 20, boxShadow: "-16px 0 0 #157a45 inset", transform: `rotate(${-4 + (1 - s) * -10}deg) translateY(${(1 - s) * 120}px)`, opacity: s}}>
        <div style={{fontSize: 60, fontWeight: 700, lineHeight: 1.02}}>{g.title}</div>
        <div style={{marginTop: "auto", display: "flex", flexDirection: "column", gap: 14}}>
          {g.lines.map((l: string, i: number) => <div key={i} style={{display: "flex", alignItems: "center", gap: 14, fontSize: F.label, fontWeight: 600}}><div style={{width: 30, height: 30, borderRadius: 7, background: "rgba(255,255,255,0.9)"}} />{l}</div>)}
        </div>
      </div>
      <div style={{display: "flex", alignItems: "center", gap: 18, fontSize: F.title, fontWeight: 700, ...rise(b(1))}}>
        {g.where}
        <svg width="60" height="70" viewBox="0 0 60 70" style={{transform: `translateY(${Math.abs(Math.sin(frame / 9)) * 12}px)`}}><path d="M30 6 V58 M8 38 L30 62 L52 38" fill="none" stroke={T.ink} strokeWidth="9" strokeLinecap="round" strokeLinejoin="round" /></svg>
      </div>
      {g.note ? <div style={{fontSize: F.subhead, fontWeight: 600, color: T.save, ...rise(b(2))}}>{g.note}</div> : null}
    </Center>
  );
};


// Recurring prop: the Italy travel brochure (sun, hills, sea, coastline houses), all drawn in code
const Brochure: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 12);
  const tag = b(1);
  const stamp = b(2, 9);
  return (
    <Center gap={30}>
      <div style={{position: "relative", width: 640, height: 430, transform: `rotate(${-3 + (1 - s) * 10}deg) translateY(${(1 - s) * 120}px)`, opacity: s}}>
        <svg width="640" height="430" viewBox="0 0 640 430" style={{position: "absolute", inset: 0}}>
          <rect x="6" y="6" width="628" height="418" rx="26" fill="#fff" stroke={T.ink} strokeWidth="8" />
          <line x1="216" y1="10" x2="216" y2="420" stroke={T.line} strokeWidth="5" />
          <line x1="424" y1="10" x2="424" y2="420" stroke={T.line} strokeWidth="5" />
          <circle cx="520" cy="110" r="52" fill={T.gold} stroke={T.gold_edge} strokeWidth="6" />
          <path d="M10 300 Q160 200 320 270 T630 240 L630 420 L10 420 Z" fill={T.save} />
          <path d="M10 350 Q120 330 230 350 T450 350 T630 345 L630 420 L10 420 Z" fill={T.ink} opacity="0.8" />
          <g stroke={T.ink} strokeWidth="5">
            <rect x="70" y="232" width="56" height="62" fill="#fff" />
            <path d="M62 236 L98 206 L134 236 Z" fill={T.cost} />
            <rect x="140" y="248" width="46" height="50" fill="#fff" />
            <path d="M134 252 L163 226 L192 252 Z" fill={T.cost} />
          </g>
        </svg>
        <div style={{position: "absolute", left: 250, top: 40, fontSize: F.title, fontWeight: 700, color: T.ink}}>{g.title}</div>
        {g.stamp ? (
          <div style={{position: "absolute", right: -30, bottom: 40, fontSize: F.title, fontWeight: 700, color: T.cost, border: `7px solid ${T.cost}`, borderRadius: 18, padding: "0 22px", background: "#fff", whiteSpace: "nowrap", opacity: stamp, transform: `rotate(-10deg) scale(${2 - stamp})`}}>{g.stamp}</div>
        ) : null}
      </div>
      <div style={{height: 70}}>
        {g.tag ? <div style={{fontSize: F.subhead, fontWeight: 700, color: "#fff", background: T.ink, borderRadius: 999, padding: "6px 36px", ...rise(tag, 30)}}>{g.tag}</div> : null}
      </div>
    </Center>
  );
};


// "Next year" moments: a drawn icon card (ticket or mountain) with an optional stamp
const StampCard: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 12);
  const tag = b(1);
  const stamp = b(2, 9);
  const icon = g.icon === "mountain" ? (
    <svg width="360" height="240" viewBox="0 0 360 240"><path d="M10 230 L130 60 L190 140 L240 90 L350 230 Z" fill={T.save} stroke={T.ink} strokeWidth="8" strokeLinejoin="round" /><path d="M110 88 L130 60 L152 92 L138 84 L124 96 Z" fill="#fff" stroke={T.ink} strokeWidth="5" strokeLinejoin="round" /><circle cx="300" cy="60" r="34" fill={T.gold} stroke={T.gold_edge} strokeWidth="6" /></svg>
  ) : (
    <svg width="360" height="240" viewBox="0 0 360 240"><path d="M20 40 H340 V95 A25 25 0 0 0 340 145 V200 H20 V145 A25 25 0 0 0 20 95 Z" fill={T.gold} stroke={T.ink} strokeWidth="8" strokeLinejoin="round" /><line x1="250" y1="48" x2="250" y2="192" stroke={T.ink} strokeWidth="5" strokeDasharray="12 10" /><path d="M110 150 V80 L170 70 V140" fill="none" stroke={T.ink} strokeWidth="9" strokeLinecap="round" /><circle cx="98" cy="150" r="16" fill={T.ink} /><circle cx="158" cy="140" r="16" fill={T.ink} /></svg>
  );
  return (
    <Center gap={26}>
      <div style={{position: "relative", padding: "30px 60px", borderRadius: 34, border: `6px solid ${T.ink}`, background: "#fff", textAlign: "center", transform: `scale(${0.7 + 0.3 * s}) rotate(${(1 - s) * -8}deg)`, opacity: s}}>
        {icon}
        <div style={{fontSize: F.title, fontWeight: 700, marginTop: 6}}>{g.title}</div>
        {g.stamp ? <div style={{position: "absolute", right: -70, top: 40, fontSize: F.title, fontWeight: 700, color: T.cost, border: `7px solid ${T.cost}`, borderRadius: 18, padding: "0 22px", background: "#fff", whiteSpace: "nowrap", opacity: stamp, transform: `rotate(-12deg) scale(${2 - stamp})`}}>{g.stamp}</div> : null}
      </div>
      <div style={{height: 70}}>{g.tag ? <div style={{fontSize: F.subhead, fontWeight: 700, color: "#fff", background: T.ink, borderRadius: 999, padding: "6px 36px", ...rise(tag, 30)}}>{g.tag}</div> : null}</div>
    </Center>
  );
};

// Shared chart frame: ages along the bottom, a polyline drawn in over its beat
const useLine = (pts: [number, number][], progress: number) => {
  let len = 0;
  for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return {d: "M" + pts.map((p) => p.join(" ")).join(" L"), len, offset: len * (1 - progress)};
};

// Frank's money rising while his health and energy fall (illustrative, no numbers)
const EnergyChart: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const W = 900, H = 520, L = 40, B = 60;
  const ages: number[] = g.series.map((p: [number, number]) => p[0]);
  const a0 = ages[0], a1 = ages[ages.length - 1];
  const top = Math.max(...g.series.map((p: [number, number]) => p[1]));
  const x = (age: number) => L + ((age - a0) / (a1 - a0)) * (W - L - 20);
  const y = (v: number) => H - B - v * (H - B - 40);
  const money = useLine(g.series.map((p: [number, number]) => [x(p[0]), y(p[1] / top)] as [number, number]), b(1, 30));
  const energy = useLine(ages.map((a) => [x(a), y(0.95 - 0.8 * Math.pow((a - a0) / (a1 - a0), 1.6))] as [number, number]), b(2, 30));
  return (
    <Center gap={10}>
      <div style={{alignSelf: "flex-end", fontSize: F.label, fontWeight: 600, color: T.muted, border: `3px solid ${T.line}`, borderRadius: 999, padding: "2px 22px"}}>Illustrative</div>
      <svg width={W} height={H} style={{opacity: b(0)}}>
        <line x1={L} y1={H - B} x2={W - 10} y2={H - B} stroke={T.line} strokeWidth="5" />
        {[a0, Math.round((a0 + a1) / 2), a1].map((a) => (
          <text key={a} x={x(a)} y={H - 14} textAnchor="middle" fontSize={F.label} fontWeight={600} fill={T.muted} fontFamily="Fredoka">Age {a}</text>
        ))}
        <path d={money.d} fill="none" stroke={T.save} strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={money.len} strokeDashoffset={money.offset} />
        <path d={energy.d} fill="none" stroke={T.cost} strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={energy.len} strokeDashoffset={energy.offset} />
        <text x={W - 20} y={70} textAnchor="end" fontSize={F.subhead} fontWeight={700} fill={T.save} fontFamily="Fredoka" opacity={b(1)}>{g.money_label}</text>
        <text x={W - 20} y={H - B - 30} textAnchor="end" fontSize={F.subhead} fontWeight={700} fill={T.cost} fontFamily="Fredoka" opacity={b(2)}>{g.energy_label}</text>
      </svg>
    </Center>
  );
};

// Invested balance by age (from the projection), with one marked age
const GrowthChart: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const W = 900, H = 470, L = 40, B = 60;
  const pts: [number, number][] = g.series.filter((p: [number, number]) => p[0] <= g.until_value);
  const a0 = g.series[0][0], a1 = g.until_value;
  const top = Math.max(...pts.map((p) => p[1]));
  const x = (age: number) => L + ((age - a0) / (a1 - a0)) * (W - L - 40);
  const y = (v: number) => H - B - (v / top) * (H - B - 40);
  const line = useLine(pts.map((p) => [x(p[0]), y(p[1])] as [number, number]), b(0, 30));
  const m = b(1, 10);
  return (
    <Center gap={16}>
      <ExampleTag config={config} />
      <svg width={W} height={H}>
        <line x1={L} y1={H - B} x2={W - 10} y2={H - B} stroke={T.line} strokeWidth="5" />
        {[a0, a1].map((a) => <text key={a} x={x(a)} y={H - 14} textAnchor="middle" fontSize={F.label} fontWeight={600} fill={T.muted} fontFamily="Fredoka">Age {a}</text>)}
        <path d={line.d} fill="none" stroke={T.save} strokeWidth="12" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={line.len} strokeDashoffset={line.offset} />
        <circle cx={x(a1)} cy={y(top)} r={22 * m} fill={T.gold} stroke={T.gold_edge} strokeWidth="6" />
      </svg>
      <div style={{fontSize: F.number, fontWeight: 700, color: T.save, lineHeight: 1, ...rise(m, 30)}}>{g.value}</div>
      <div style={{fontSize: F.subhead, fontWeight: 600, color: T.muted, ...rise(m, 20)}}>{g.label}</div>
    </Center>
  );
};

// One of Bea's five steps
const StepCard: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const s = b(0, 10);
  const items: string[] = g.items || [];
  return (
    <Center gap={24}>
      {g.items_have_money ? <ExampleTag config={config} /> : null}
      <div style={{display: "flex", alignItems: "center", gap: 30, transform: `scale(${0.7 + 0.3 * s})`, opacity: s}}>
        <div style={{width: 150, height: 150, borderRadius: 75, background: T.gold, color: T.ink, fontSize: 100, fontWeight: 700, display: "flex", alignItems: "center", justifyContent: "center"}}>{g.step}</div>
        <div>
          <div style={{fontSize: F.subhead, fontWeight: 700, color: T.muted}}>Step {g.step}</div>
          <div style={{fontSize: F.title, fontWeight: 700, lineHeight: 1.05, maxWidth: 760}}>{g.title}</div>
        </div>
      </div>
      <div style={{display: "flex", flexDirection: "column", gap: 16, alignSelf: "stretch", paddingLeft: 60}}>
        {items.map((it, i) => {
          const v = b(i + 1);
          return (
            <div key={i} style={{display: "flex", alignItems: "center", gap: 22, fontSize: F.subhead, fontWeight: 600, opacity: v, transform: `translateX(${(1 - v) * -60}px)`}}>
              <svg width="52" height="52" viewBox="0 0 52 52"><circle cx="26" cy="26" r="24" fill={T.save} /><path d="M14 27 L22 35 L38 17" fill="none" stroke="#fff" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" /></svg>
              <span>{it}</span>
            </div>
          );
        })}
      </div>
    </Center>
  );
};

// Final comparison: money vs memories for each person (memories are an illustrative scale)
const MoneyMemories: React.FC<P> = ({g, beats, config}) => {
  const b = useBeats(beats);
  const T = config.theme;
  const F = config.layout.fonts;
  const top = Math.max(...g.rows.map((r: any) => r.money_value));
  return (
    <Center gap={18}>
      <div style={{alignSelf: "stretch", display: "flex", justifyContent: "space-between", alignItems: "center"}}>
        <div style={{fontSize: F.subhead, fontWeight: 700}}>{g.title}</div>
        <div style={{fontSize: F.label, fontWeight: 600, color: T.muted, border: `3px solid ${T.line}`, borderRadius: 999, padding: "2px 22px"}}>Example figures · memories illustrative</div>
      </div>
      {g.rows.map((r: any, i: number) => {
        const v = b(i, 14);
        return (
          <div key={i} style={{alignSelf: "stretch", display: "flex", alignItems: "center", gap: 24, padding: "12px 20px", borderRadius: 26, border: `4px solid ${T.line}`, opacity: v, transform: `translateX(${(1 - v) * -60}px)`}}>
            <Img src={staticFile(r.src)} style={{width: 120, height: 130, objectFit: "contain", objectPosition: "50% 100%"}} />
            <div style={{width: 150, fontSize: F.subhead, fontWeight: 700}}>{r.name}</div>
            <div style={{flex: 1, display: "flex", flexDirection: "column", gap: 10}}>
              {[["Money", r.money_value / top, r.money, T.save], ["Memories", r.memories, r.memories_label, T.gold_edge]].map(([lab, frac, txt, col]: any, k) => (
                <div key={k} style={{display: "flex", alignItems: "center", gap: 16}}>
                  <div style={{width: 200, fontSize: F.label, fontWeight: 600, color: T.muted}}>{lab}</div>
                  <div style={{width: Math.max(14, 360 * frac * v), height: 34, borderRadius: 12, background: col}} />
                  <div style={{fontSize: F.label, fontWeight: 700, color: col}}>{txt}</div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
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
  list: List,
  tiles: Tiles,
  payment_plan: PaymentPlan,
  compare: CompareGroups,
  rising: Rising,
  card_debt: CardDebt,
  share_bar: ShareBar,
  habit: Habit,
  cta: Cta,
  brochure: Brochure,
  stamp_card: StampCard,
  energy_chart: EnergyChart,
  growth_chart: GrowthChart,
  step: StepCard,
  money_memories: MoneyMemories,
};

export const GraphicView: React.FC<P> = (p) => {
  const View = VIEWS[p.g.type];
  if (!View) throw new Error(`Unknown graphic type: ${p.g.type}`);
  return <View {...p} />;
};
