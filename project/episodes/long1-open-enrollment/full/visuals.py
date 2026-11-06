"""Full episode story graphics built on the approved native v3 pilot compositor."""
from pathlib import Path
import sys,json,math,importlib.util,functools
from PIL import Image,ImageDraw
F=Path(__file__).resolve().parent;B=F.parent;sys.path.insert(0,str(B))
spec=importlib.util.spec_from_file_location('approved_long1_pilot',B/'render.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
W,H=1280,720;INK,GREEN,CREAM,MUTED=p.INK,p.GREEN,p.CREAM,p.MUTED
A,C=p.A,p.C;DOLLAR=lambda x:f'${x:,}'
MED=Image.open(F/'assets/medical-props.png').convert('RGBA')
MEDPROPS={k:MED.crop(box) for k,box in {'jar':(195,20,600,495),'clipboard':(935,10,1345,495),'pills':(240,535,555,1010),'baby':(985,535,1290,1015)}.items()}
@functools.lru_cache(maxsize=24)
def medical_size(name,width):
 a=MEDPROPS[name];return a.resize((width,round(a.height*width/a.width)),Image.Resampling.LANCZOS)
def medical(im,name,x,y,width):
 a=medical_size(name,width);im.paste(a,(x,y),a)

def text(d,xy,s,size=36,fill=INK):p.txt(d,xy,s,size,fill)
def center(d,y,s,size=44,fill=INK):p.center(d,y,s,size,fill)
def card(d,box,fill=CREAM,outline=GREEN):d.rounded_rectangle(box,22,fill=fill,outline=outline,width=3)
def heading(d,title,subtitle='Illustrative example • check your own plan'):
 center(d,42,title,44);center(d,105,subtitle,25,GREEN)
def row(d,x,y,label,value,width=500):
 text(d,(x,y),label,28,MUTED);text(d,(x,y+40),value,48);d.line((x,y+105,x+width,y+105),fill='#D3DCD0',width=2)
def check(d,x,y,scale=1):d.line((x,y+12*scale,x+10*scale,y+23*scale,x+31*scale,y),fill=GREEN,width=max(2,round(5*scale)))
def office(lines,clip,n):
 im=p.OFFICE.copy();a=p.actor(clip,n);im.paste(a,(-300,33),a)
 for xy,s,size in lines:im=p.textbox(im,xy,s,size)
 return im
MOTIFS={
 'annual':('ren','Before the first doctor’s bill'),
 'forecast':('graphic','Employer costs, not your premium'),
 'group':('graphic','Three opinions. Zero calculations.'),
 'neighbor':('graphic','Next door: three better questions'),
 'questions':('graphic','Start with three questions'),
 'illustrative':('ren','Not a quote for your coverage'),
 'ppo_premium':('graphic','Plan A • PPO'),
 'ppo_bad':('graphic','Plan A • covered in-network bad year'),
 'hdhp_premium':('graphic','Plan B • HSA-eligible HDHP'),
 'hdhp_bad':('graphic','Plan B • before employer HSA value'),
 'employer':('graphic','Employer funding is separate value'),
 'bad_compare':('graphic','Bad-year net comparison'),
 'cashflow':('ren','A higher deductible needs cash'),
 'limits':('graphic','Know what the limit excludes'),
 'used_care':('graphic','Question 2 • the actual year'),
 'ppo_normal':('graphic','Plan A • illustrative normal year'),
 'hdhp_cash':('graphic','Plan B • cash outflow'),
 'hdhp_net':('graphic','Plan B • after employer HSA value'),
 'normal_compare':('graphic','Same example. Different economics.'),
 'not_rebate':('ren','Potential value, not a cash rebate'),
 'check_services':('graphic','Compare the actual plan details'),
 'priya':('graphic','Question 3 • where does it go?'),
 'redirect':('graphic','Give the premium difference a job'),
 'contributions':('graphic','Contributions before spending'),
 'withdrawal':('graphic','If the HSA pays '+DOLLAR(A['hsa_illustrative_withdrawal'])+' of care'),
 'outside_cash':('graphic','If care is paid from other cash'),
 'hsa_rules':('graphic','Eligibility and current annual limits'),
 'money_job':('ren','Give the money a job'),
 'warning':('ren','Cheapest premium does not always win'),
 'needs':('graphic','The PPO could be the better deal'),
 'network':('graphic','Read both plans'),
 'early_bills':('ren','Bills can arrive before HSA funding'),
 'marketplace':('graphic','Marketplace is a separate process'),
 'deadline':('graphic','Check current enrollment deadlines'),
 'employer_deadline':('ren','Your employer has its own deadline'),
 'choice':('ren','Make a deliberate choice'),
 'cheaper':('ren','Lower premiums do not settle it'),
 'recap':('graphic','Bad year. Real year. Where it goes.'),
 'forty':('graphic','Forty minutes, once a year'),
 'next':('ren','Next: another box on the benefits page'),
 'close':('ren','Make the next click count')}
def picture(motif,n=36,frames=84,clip='thinking',progress=None):
 q=(n/max(1,frames-1)) if progress is None else progress;kind,title=MOTIFS[motif]
 if kind=='ren':
  lines={
   'annual':[((710,100),'Before the first doctor’s bill',35),((770,265),DOLLAR(C['ppo_annual_premium'])+' / year',58)],
   'illustrative':[((710,100),'Example numbers',42),((710,265),'Check your own plan',34)],
   'cashflow':[((710,100),'Higher deductible',40),((710,275),'Enough cash when care happens?',34)],
   'not_rebate':[((710,100),'Potential net value',38),((710,265),'Not an instant cash rebate',34)],
   'money_job':[((710,100),'Give the money a job',39),((710,280),'Eligibility + state rules matter',30)],
   'warning':[((710,100),'The HDHP does not always win',36)],
   'early_bills':[((710,100),'Care can come first',38),((710,275),'HSA funding can come later',34)],
   'employer_deadline':[((710,100),'Check your employer’s deadline',36)],
   'choice':[((710,100),'Check the numbers',42),((710,265),'Choose deliberately',38)],
   'cheaper':[((710,100),'Lower premiums',40),((710,265),'Do not always mean cheaper care',33)],
   'next':[((710,100),'Next: another box on the benefits page',34)],
   'close':[((710,100),'Thanks for watching',40),((710,265),'Make money matter',38)]}[motif]
  return office(lines,clip,min(n,131))
 im=Image.new('RGB',(W,H),CREAM);d=ImageDraw.Draw(im);heading(d,title)
 if motif=='forecast':
  center(d,245,'2027 employer-cost forecast',42,GREEN);center(d,330,'Source check required',52);center(d,510,'Never label this as everyone’s premium increase',29)
 elif motif=='group':
  im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im);center(d,45,title,44,CREAM)
  for j,(name,msg) in enumerate([('Alex','“Pick the best.”'),('Danny','“Pick the cheapest.”'),('Uncle Gary','“I never look.”')]):
   y=150+j*150
   if q<j*.22:continue
   arrival=p.ease((q-j*.22)/.06);dx=round(70*(1-arrival));card(d,(110+dx,y,1170+dx,y+115),'#EDF0E6');text(d,(140+dx,y+15),name,26,GREEN);text(d,(370+dx,y+27),msg,38)
  # Gary's boat is an icon attached to his fictional message, not a character substitute.
  x=1060;y=500
  if q<.44:return im
  d.polygon([(x-55,y+40),(x+55,y+40),(x+30,y+65),(x-35,y+65)],fill=GREEN);d.line((x,y-30,x,y+40),fill=INK,width=3);d.polygon([(x+5,y-20),(x+5,y+30),(x+40,y+30)],fill='#BACABB')
 elif motif=='neighbor':
  p.driveway(im);d=ImageDraw.Draw(im);p.prop(im,'used_car',155,285,575)
  card(d,(815,210,1140,545),'#DFE8D9');d.rectangle((850,245,1100,545),fill='#A8BCA4');d.ellipse((1064,382,1074,392),fill=INK);text(d,(830,575),'Three questions',26,GREEN)
 elif motif in ['questions','recap']:
  labels=['Worst year?','Actual year?','Where does it go?']
  for j,label in enumerate(labels):
   y=170+j*145;card(d,(125,y,1155,y+115),'#E3EBDD' if q>(j+1)/5 else '#F8F7EF');text(d,(160,y+25),str(j+1),44,GREEN);text(d,(280,y+27),label,43)
 elif motif in ['ppo_premium','hdhp_premium']:
  key='ppo' if motif=='ppo_premium' else 'hdhp';monthly=A[key]['premium_monthly'];annual=C[key+'_annual_premium']
  card(d,(100,185,590,570));card(d,(690,185,1180,570),'#E5EDDF');text(d,(155,230),'Per month',34,GREEN);text(d,(155,320),DOLLAR(monthly),94);text(d,(745,230),'Per year',34,GREEN);text(d,(745,320),DOLLAR(annual),94)
  center(d,620,DOLLAR(monthly)+' × 12 = '+DOLLAR(annual),38)
 elif motif in ['ppo_bad','hdhp_bad','ppo_normal','hdhp_cash','hdhp_net']:
  data={
   'ppo_bad':('Annual premium',C['ppo_annual_premium'],'In-network OOP maximum',A['ppo']['in_network_oop_max'],'Premium + covered in-network limit',C['ppo_bad_year_covered_in_network'],'+'),
   'hdhp_bad':('Annual premium',C['hdhp_annual_premium'],'In-network OOP maximum',A['hdhp']['in_network_oop_max'],'Before employer HSA value',C['hdhp_bad_year_before_hsa'],'+'),
   'ppo_normal':('Annual premium',C['ppo_annual_premium'],'Illustrative copays',A['ppo']['normal_year_patient_share'],'Normal-year total',C['ppo_normal_year'],'+'),
   'hdhp_cash':('Annual premium',C['hdhp_annual_premium'],'Illustrative care paid',A['hdhp']['normal_year_patient_share'],'Cash outflow before HSA value',C['hdhp_normal_year_cash'],'+'),
   'hdhp_net':('Cash outflow',C['hdhp_normal_year_cash'],'Employer HSA value',A['employer_hsa'],'Net economic cost',C['hdhp_normal_year_net'],'-')}[motif]
  l1,v1,l2,v2,lt,vt,op=data
  card(d,(85,170,1195,615));row(d,130,195,l1,DOLLAR(v1),450);row(d,700,195,l2,DOLLAR(v2),440)
  center(d,390,lt,33,GREEN);center(d,440,DOLLAR(vt),94)
  # Completed equation is fixed from the shared source on every frame.
  center(d,635,f'{DOLLAR(v1)} {op} {DOLLAR(v2)} = {DOLLAR(vt)}',36)
 elif motif=='employer':
  card(d,(110,195,660,565));text(d,(150,230),'Employer HSA funding',35,GREEN);text(d,(230,330),DOLLAR(A['employer_hsa']),96)
  card(d,(745,215,1170,555),'#E4EDDE');text(d,(790,270),'Separate asset',37);text(d,(790,345),'Not a discount\non the bill',32)
 elif motif in ['bad_compare','normal_compare']:
  bad=motif=='bad_compare';values=[C['ppo_bad_year_covered_in_network'],C['hdhp_bad_year_net']] if bad else [C['ppo_normal_year'],C['hdhp_normal_year_net']];gap=C['bad_year_net_gap'] if bad else C['potential_normal_year_net_gap']
  for j,(label,val) in enumerate(zip(['Plan A • PPO','Plan B • after HSA value'],values)):
   y=180+j*155;card(d,(100,y,1180,y+130),'#E3EDDF' if j else CREAM);text(d,(140,y+15),label,31,GREEN);text(d,(140,y+55),DOLLAR(val),63)
   width=round(470*val/max(values)*p.ease(min(1,q*2)));d.rounded_rectangle((660,y+65,660+max(2,width),y+90),8,fill=GREEN if j else INK)
  center(d,555,DOLLAR(gap)+' apart' if bad else DOLLAR(gap)+' potential net difference',43)
  center(d,630,'Covered in-network care; not every possible bill' if bad else 'Illustrative net value, not guaranteed cash savings',28,GREEN)
 elif motif=='limits':
  for j,label in enumerate(['Premiums are additional','Uncovered services may be extra','Out-of-network bills may be extra']):
   y=180+j*140;card(d,(105,y,1175,y+110));text(d,(155,y+30),label,38)
 elif motif=='used_care':
  card(d,(100,180,650,570));text(d,(145,225),'Covered care in this example',31,GREEN);text(d,(230,335),DOLLAR(A['hdhp']['normal_year_patient_share']),90)
  card(d,(730,205,1180,560),'#E5ECDD');text(d,(770,245),'PPO patient share',31,GREEN);text(d,(825,340),DOLLAR(A['ppo']['normal_year_patient_share']),84);center(d,630,'Example plan rules, not a real quotation',29,GREEN)
 elif motif in ['check_services','network','needs']:
  labels={'check_services':['Services and negotiated prices','Prescriptions and formulary','Your doctors in each network'],'network':['Doctor network','Drug coverage','Deductible + out-of-pocket limits'],'needs':['A baby or planned surgery','Regular specialist care','Expensive prescriptions']}[motif]
  for j,label in enumerate(labels):
   y=180+j*145;card(d,(110,y,1170,y+115),'#E5EDDF')
   if motif=='needs':medical(im,['baby','clipboard','pills'][j],155,y+9,62);d=ImageDraw.Draw(im)
   else:check(d,150,y+40)
   text(d,(270 if motif=='needs' else 220,y+30),label,37)
 elif motif=='priya':
  im=Image.new('RGB',(W,H),INK);d=ImageDraw.Draw(im);center(d,45,title,44,CREAM);p.prop(im,'phone',810,110,310)
  card(d,(90,210,715,515),'#E3EBDD');text(d,(130,250),'The next question',33,GREEN);text(d,(130,325),'Where would the\ndifference go?',44);text(d,(850,245),'Priya',28,GREEN)
  if q>.40:
   dy=round(25*(1-p.ease((q-.40)/.06)));text(d,(850,325+dy),'Pay the\ndifference\nto yourself.',26)
 elif motif=='redirect':
  card(d,(90,180,590,555));text(d,(135,220),'Premium difference',33,GREEN);text(d,(160,310),DOLLAR(C['premium_gap_monthly']),84);text(d,(215,410),'per month',31)
  card(d,(725,180,1190,555),'#E1EBD9');text(d,(765,220),'Personal HSA funding',31,GREEN);text(d,(775,310),DOLLAR(C['personal_hsa_annual']),84);text(d,(830,410),'per year',31)
  x=580+165*p.ease(q);d.ellipse((x-13,343,x+13,369),fill=GREEN);center(d,620,'If affordable and eligible',31,GREEN)
 elif motif=='contributions':
  row(d,120,180,'Personal contribution',DOLLAR(C['personal_hsa_annual']),450);row(d,740,180,'Employer contribution',DOLLAR(A['employer_hsa']),400)
  center(d,380,'Total CONTRIBUTED',38,GREEN);center(d,440,DOLLAR(C['hsa_total_contributed']),95);center(d,625,'Before spending, fees or growth',30,GREEN);medical(im,'jar',1010,360,135);text(ImageDraw.Draw(im),(1040,428),'HSA',25)
 elif motif in ['withdrawal','outside_cash']:
  paid=motif=='withdrawal';value=C['hsa_after_illustrative_withdrawal'] if paid else C['hsa_total_contributed']
  card(d,(100,185,700,575),'#E1EADB');text(d,(140,225),'HSA remaining',36,GREEN);text(d,(240,330),DOLLAR(value),98)
  card(d,(785,225,1180,560));text(d,(825,265),'Medical bills',32,GREEN);text(d,(840,330),DOLLAR(A['hsa_illustrative_withdrawal']),76);text(d,(825,430),'Paid from HSA' if paid else 'Paid from other cash',25)
  center(d,625,'No other withdrawals, fees or growth assumed',28,GREEN)
 elif motif=='hsa_rules':
  for j,label in enumerate(['Check HSA eligibility','Check the current IRS limit','Employer money counts too']):
   y=180+j*140;card(d,(115,y,1165,y+110),'#E5ECDC');text(d,(175,y+30),label,40)
 elif motif in ['marketplace','deadline']:
  for j,(label,sub) in enumerate([('Marketplace','Check HealthCare.gov + your state'),('Employer plan','Check your employer’s enrollment notice')]):
   y=180+j*220;card(d,(110,y,1170,y+170),'#E6EDDF' if j else CREAM);text(d,(150,y+20),label,42,GREEN);text(d,(150,y+95),sub,31)
 elif motif=='forty':
  p.clock(d,345,350,155,2*math.pi*p.ease(q)*A['review_minutes']/60);text(d,(225,550),'40:00',72,GREEN);card(d,(670,215,1165,550),'#E4ECDE');text(d,(720,275),'Once a year',47);text(d,(720,365),'Before you click',36)
 return im

def boards():
 target=F/'build/boards';target.mkdir(parents=True,exist_ok=True)
 for k in MOTIFS:picture(k).save(target/(k+'.jpg'))
 keys=list(MOTIFS)
 for page in range(0,len(keys),12):
  batch=keys[page:page+12];sheet=Image.new('RGB',(1280,180*math.ceil(len(batch)/4)),CREAM)
  for j,k in enumerate(batch):sheet.paste(Image.open(target/(k+'.jpg')).resize((320,180)),((j%4)*320,(j//4)*180))
  sheet.save(target/f'contact-{page//12+1}.jpg')
 print(f'{len(keys)} visual boards saved; not a finished film or timed edit')
if __name__=='__main__':boards()
