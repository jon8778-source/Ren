"""Update external caption timing for the new opening; preserve retained caption text."""
from pathlib import Path
import re,json
H=Path(__file__).resolve().parent;B=H.parent;S=json.loads((H/'source.json').read_text());T=json.loads((H/'timing.json').read_text());old=json.loads((B/'full/audio-timing.json').read_text());cut=S['cut_seconds'];shift=T['hook_audio_seconds']-cut
text=json.loads((H/'segments.json').read_text())[0]['text'];matches=list(re.finditer(r"[a-z]+(?:['’][a-z]+)?",text,re.I));assert len(matches)==len(T['words']);new=[]
for i,w in enumerate(T['words']):new.append({**w,'display':text[matches[i].start():matches[i+1].start() if i+1<len(matches) else len(text)]})
cues=[];row=[]
for w in new:
 if row and (len(''.join(x['display'] for x in row+[w]).strip())>44 or w['end']-row[0]['start']>3.5):cues.append((row[0]['start'],row[-1]['end'],''.join(x['display'] for x in row).strip()));row=[]
 row.append(w)
if row:cues.append((row[0]['start'],row[-1]['end'],''.join(x['display'] for x in row).strip()))
def seconds(t):
 h,m,s=t.split(':');return int(h)*3600+int(m)*60+float(s.replace(',','.'))
kept=[]
for part in (B/'full/deliverables/captions.srt').read_text().strip().split('\n\n'):
 lines=part.splitlines();a,b=[seconds(x) for x in lines[1].split(' --> ')];value='\n'.join(lines[2:])
 if b<=cut:continue
 if a<cut:
  words=[w for w in old['words'] if w['start']>=cut and w['start']>=a-.001 and w['end']<=b+.001];assert words;a=words[0]['start'];value=''.join(w['display'] for w in words).strip()
 kept.append((a+shift,b+shift,value))
cues+=kept
for a,b,_ in cues:assert 0<=a<b
assert all(cues[i][1]<=cues[i+1][0]+.001 for i in range(len(cues)-1))
body=[]
for segment in old['segments']:
 words=[w for w in old['words'] if w['segment']==segment['id'] and w['start']>=cut]
 if words:body.append(''.join(w['display'] for w in words).strip())
assert ' '.join(c[2] for c in kept)==' '.join(body),'Retained caption text changed'
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
(H/'deliverables/Ren_Health_Plan_Revised_Opening.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{v}' for i,(a,b,v) in enumerate(cues))+'\n');(H/'deliverables/Revised_Narration.txt').write_text(text+'\n\n'+'\n\n'.join(body)+'\n');report={'caption_count':len(cues),'retained_caption_text_unchanged':True,'retained_caption_shift_seconds':shift,'timing_basis':'Existing source captions/word timings, new approved opening local forced alignment','independent_transcription':False};(H/'caption-update.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
