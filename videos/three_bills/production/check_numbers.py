#!/usr/bin/env python3
"""Single source of truth for all code-rendered financial amounts."""
from pathlib import Path
import csv
p=Path(__file__).with_name('assumptions.csv')
with p.open(newline='') as f:
    data={r['key']:int(r['value']) for r in csv.DictReader(f)}
assert data['weekly_transfer']*data['contribution_weeks']==data['fund_start']
assert data['fund_start']-data['car_bill']==data['fund_after_car']
assert data['fund_after_car']-data['dental_bill']==data['fund_after_dental']
assert sum(data[k] for k in ('car_bill','dental_bill','plumber_bill'))==data['total_emergencies']
assert data['fund_after_dental']-data['plumber_bill']==data['fund_final']
assert data['fund_start']-data['total_emergencies']==data['fund_final']
assert 1 <= data['car_day']<data['dental_day']<data['plumber_day']<=30
print('MATHS OK:', {k:data[k] for k in ('fund_start','total_emergencies','fund_final')})
