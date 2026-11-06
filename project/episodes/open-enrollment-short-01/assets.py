"""Export reusable sharp SVG interfaces from shared assumptions."""
from pathlib import Path
import json,hashlib,html,datetime,subprocess
B=Path(__file__).resolve().parent;ROOT=B.parents[2];A=json.loads((B/'assumptions.json').read_text());F=B/'assets/ui';F.mkdir(exist_ok=True)
assert datetime.date.fromisoformat(A['publication_date']).weekday()==0
assert datetime.date.fromisoformat(A['full_video_teaser_date']).weekday()==1
head='<svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600"><rect x="3" y="3" width="894" height="594" rx="25" fill="#FAF6EE" stroke="#172A3A" stroke-width="3"/><g font-family="Fredoka,sans-serif" fill="#172A3A">'
def t(x,y,s,size=52):return f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(s)}</text>'
ui={'email.svg':t(50,100,'Open enrollment')+t(50,185,'closes Friday.')+'<rect x="50" y="290" width="650" height="140" rx="20" fill="#3F665B"/>'+t(85,380,'Keep My Plan'),
'stopwatch.svg':'<circle cx="180" cy="270" r="110" fill="none" stroke="#172A3A" stroke-width="9"/><path d="M180 270V190 M180 140V100" stroke="#3F665B" stroke-width="9"/>'+t(340,310,'4 SEC',100),
'comparison.svg':t(45,120,f"${A['comparison_a']:,} vs ${A['comparison_b']:,}",78)+t(45,270,f"Difference: ${A['comparison_a']-A['comparison_b']:,}",72)+t(45,400,'Illustrative, not plan quotations.',36)+t(45,460,'Not guaranteed savings.',36),
'tuesday.svg':t(50,150,'FULL STORY',80)+t(50,270,'TUESDAY',110)+t(50,390,'NOVEMBER 10, 2026',48),
'disclaimer.svg':t(40,180,'Educational content only,',46)+t(40,260,'not financial advice.',46)}
for i,value in enumerate(['Worst-year cost?','What did I use?','Where does the difference go?']):ui[f'question-{i+1}.svg']=t(45,115,f'QUESTION {i+1}',38)+t(45,250,value,48)
for name,value in ui.items():(F/name).write_text(head+value+'</g></svg>\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
files=[{'file':str(p.relative_to(B)),'sha256':sha(p),'status':'New reusable episode asset'} for p in sorted((B/'assets').rglob('*')) if p.is_file()]
files.extend([{'file':str(p.relative_to(ROOT)),'sha256':sha(p),'status':'Reused approved source, unchanged'} for p in [ROOT/'project/prototypes/coffee-minute-v3/assets/office.png',ROOT/'assets/ren_library/ren_nod_yes.mp4',ROOT/'project/remotion/public/fonts/fredoka-latin-600-normal.woff2']])
(B/'asset-manifest.json').write_text(json.dumps({'reused':['Approved v3 office/reference','Native 1280×720 nod_yes animation','Fredoka / navy / sage / cream typography and palette','Actual approved v3 rendering/matte methods'], 'generated':['One reference-based seated Ren office pose (pending prototype approval)','Eight code-generated reusable SVG interface assets','Original sample-free lo-fi and UI effects','New locally generated US narration'], 'assets':files},indent=2)+'\n')
print(len(ui),'reusable SVG assets exported')
if __name__=='__main__':pass
