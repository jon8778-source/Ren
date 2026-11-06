"""All episode amounts derive from the shared illustrative assumptions."""
from pathlib import Path
import json
B=Path(__file__).resolve().parent

def calculate():
 a=json.loads((B/'assumptions.json').read_text());p=a['ppo'];h=a['hdhp'];e=a['employer_hsa']
 assert {k:a[k] for k in ['auto_click_seconds','review_minutes','auto_renew_years','previous_premium_monthly']}=={'auto_click_seconds':4,'review_minutes':40,'auto_renew_years':4,'previous_premium_monthly':185},'Input differs from the supplied/voiced narrative; update source text and reject stale audio first'
 assert a['backstory']=={'leased_car_age':25,'returned_car_age':28,'bank_balance':85,'payments_before':750,'payments_after':445,'used_car_years_later':8},'Backstory differs from supplied narration'
 r={'ppo_annual_premium':p['premium_monthly']*12,'hdhp_annual_premium':h['premium_monthly']*12}
 r.update(ppo_bad_year_covered_in_network=r['ppo_annual_premium']+p['in_network_oop_max'],hdhp_bad_year_before_hsa=r['hdhp_annual_premium']+h['in_network_oop_max'],ppo_normal_year=r['ppo_annual_premium']+p['normal_year_patient_share'],hdhp_normal_year_cash=r['hdhp_annual_premium']+h['normal_year_patient_share'])
 r['hdhp_bad_year_net']=r['hdhp_bad_year_before_hsa']-e;r['bad_year_net_gap']=r['hdhp_bad_year_net']-r['ppo_bad_year_covered_in_network'];r['hdhp_normal_year_net']=r['hdhp_normal_year_cash']-e;r['potential_normal_year_net_gap']=r['ppo_normal_year']-r['hdhp_normal_year_net'];r['normal_year_cash_gap']=r['ppo_normal_year']-r['hdhp_normal_year_cash']
 r['premium_gap_monthly']=p['premium_monthly']-h['premium_monthly'];r['personal_hsa_annual']=r['premium_gap_monthly']*12;r['hsa_total_contributed']=r['personal_hsa_annual']+e;r['hsa_after_illustrative_withdrawal']=r['hsa_total_contributed']-a['hsa_illustrative_withdrawal'];r['backstory_payment_reduction']=a['backstory']['payments_before']-a['backstory']['payments_after']
 expected={'ppo_annual_premium':2520,'hdhp_annual_premium':840,'ppo_bad_year_covered_in_network':6520,'hdhp_bad_year_before_hsa':7340,'hdhp_bad_year_net':6590,'bad_year_net_gap':70,'ppo_normal_year':2670,'hdhp_normal_year_cash':1440,'hdhp_normal_year_net':690,'potential_normal_year_net_gap':1980,'normal_year_cash_gap':1230,'premium_gap_monthly':140,'personal_hsa_annual':1680,'hsa_total_contributed':2430,'hsa_after_illustrative_withdrawal':1830,'backstory_payment_reduction':305}
 assert r==expected,(r,expected)
 return a,r
if __name__=='__main__':
 a,r=calculate();(B/'calculation-results.json').write_text(json.dumps({'status':'MATHS OK','assumptions':'assumptions.json','results':r,'interpretation':['HSA employer value is a separate asset, not an instant premium discount','Bad-year totals cover hypothetical covered in-network claims, not every possible cost','Contributions are not balances after medical withdrawals','No independent real plan quotes; no guaranteed savings']},indent=2)+'\n');print('MATHS OK')
