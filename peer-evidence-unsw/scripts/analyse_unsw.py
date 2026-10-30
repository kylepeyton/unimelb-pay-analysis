"""Add UNSW to the independently frozen five-university comparison.
No network access. Dates label quarters; use entitlement applying at quarter end.
"""
from pathlib import Path
import csv,json,statistics,hashlib,subprocess,sys
R=Path(__file__).resolve().parents[1];O=R/'data/derived/six-university-comparison';O.mkdir(parents=True,exist_ok=True)
def read(p):return list(csv.DictReader((R/p).open()))
def save(n,a):
 with (O/n).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=a[0]);w.writeheader();w.writerows(a)
subprocess.run([sys.executable,str(R/'scripts/audit_unsw_sources.py')],check=True)
cells=read('data/derived/unsw/salary-cells.csv');events=[]
for x in cells:
 d=x['effective_date'];note=x['date_note'];k=x['classification'];src=x['source']
 if d in ['prior_rate','certification']:continue
 if d=='endorsement2006':d='2006-09-30';note+=' Date is a conservative quarter-end bound after18August lodgement, NOT exact payday; only annual December observations are plotted.'
 if src=='academic-ea2003.pdf' and d=='2003-06-01':d='2003-08-29';note+=' Combined June rise and recurring loading in force by29August certification (AIRC register PDF298).'
 if src=='general-ea2003.pdf' and d=='2003-06-01':d='2003-07-18';note+=' New steps and retrospective June rise in force by18July certification (AIRC register PDF298).'
 events.append(dict(classification=k,entitlement_date_or_bound=d,annual_salary=float(x['annual_salary']),source=src,pdf_page=x['pdf_page'],date_note=note))
# Explicit administrative rise between EAs, not a guessed missing-year increase.
for x in cells:
 if x['source'] in ['academic-ea2018-approved.pdf','professional-ea2018-approved.pdf'] and x['effective_date']=='2022-01-01':events.append(dict(classification=x['classification'],entitlement_date_or_bound='2022-07-08',annual_salary=round(float(x['annual_salary'])*1.01),source='admin2022.html + '+x['source'],pdf_page=x['pdf_page'],date_note='UNSW7July2022 announcement:1% effective8July2022. Rounded to dollars;2023 table bridge independently checked.'))
# Duplicated carried-forward columns must agree exactly.
seen={}
for x in events:
 key=(x['classification'],x['entitlement_date_or_bound'])
 if key in seen:assert seen[key]['annual_salary']==x['annual_salary'],(seen[key],x)
 else:seen[key]=x
events=list(seen.values());save('unsw-salary-events.csv',events)
cpi={x['date']:float(x['value']) for x in read('data/derived/september2026/cpi-quarterly-vintage.csv')}
keys=['B1','C4','HEW5.1','HEW7.1'];allkeys=sorted(set(x['classification'] for x in cells));assert len(allkeys)==61
def salary(k,d):
 end=d[:8]+('30' if d[5:7] in ['06','09'] else '31')
 eligible=[x for x in events if x['classification']==k and x['entitlement_date_or_bound']<=end];return max(eligible,key=lambda x:x['entitlement_date_or_bound'])['annual_salary']
def change(k,b,e):return 100*(salary(k,e)/salary(k,b)/(cpi[e]/cpi[b])-1)
dates=sorted(set(['2003-09-01','2017-06-01','2026-06-01','2026-09-01']+[f'{y}-12-01' for y in range(2003,2026)]))
pp=read('data/derived/university-comparison/historical-point-paths.csv')
for d in dates:
 for k in keys:pp.append(dict(date=d,university='UNSW',classification=k,annual_salary=salary(k,d),cpi=cpi[d],real_index=100+change(k,'2003-09-01',d)))
save('historical-point-paths.csv',pp)
means=[]
for u,d in sorted(set((x['university'],x['date']) for x in pp)):
 vals=[float(x['real_index']) for x in pp if x['university']==u and x['date']==d];assert len(vals)==4;means.append(dict(date=d,university=u,real_index=statistics.mean(vals)))
save('historical-paths.csv',means)
comp=read('data/derived/university-comparison/comparisons.csv');windows=[('2003-09-01','2017-06-01'),('2003-09-01','2026-09-01'),('2017-06-01','2026-09-01'),('2017-12-01','2026-09-01'),('2019-12-01','2026-09-01')];full=[]
for b,e in windows:
 vals=[change(k,b,e) for k in keys];comp.append(dict(start=b,end=e,university='UNSW',real_change_pct=statistics.mean(vals),min_pct=min(vals),max_pct=max(vals),points=4))
 for k in allkeys:full.append(dict(university='UNSW',classification=k,staff_group='professional35h' if k.startswith('HEW') else 'academic',start=b,end=e,start_salary=salary(k,b),end_salary=salary(k,e),cpi_start=cpi[b],cpi_end=cpi[e],real_change_pct=change(k,b,e)))
save('comparisons.csv',comp);save('unsw-all-point-comparisons.csv',full)
# Recent path in own December2019 units, for a six-university recent figure.
recent=[]
lookup={(x['university'],x['classification'],x['date']):x for x in pp}
for x in pp:
 if x['date']<'2019-12-01':continue
 b=lookup[(x['university'],x['classification'],'2019-12-01')]
 recent.append(dict(date=x['date'],university=x['university'],classification=x['classification'],real_index=100*float(x['annual_salary'])/float(b['annual_salary'])/(float(x['cpi'])/float(b['cpi']))))
recentmeans=[]
for u,d in sorted(set((x['university'],x['date']) for x in recent)):recentmeans.append(dict(date=d,university=u,real_index=statistics.mean(x['real_index'] for x in recent if x['university']==u and x['date']==d)))
save('recent-paths.csv',recentmeans)
checks=read('data/derived/unsw/checks.csv');bad=[x for x in checks if x['passed']=='False'];assert len(bad)==1 and bad[0]['classification']=='HEW1.3'
inputs=['data/derived/university-comparison/historical-point-paths.csv','data/derived/university-comparison/comparisons.csv','data/derived/september2026/cpi-quarterly-vintage.csv','data/derived/unsw/salary-cells.csv']
(O/'verification.json').write_text(json.dumps(dict(universities=6,selected_positions=24,observations=len(pp),unsw_points_checked=61,unsw_source_cells=len(cells),unsw_numeric_checks=len(checks),unsw_exceptions=bad,source_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in inputs}),indent=2)+'\n')
for c in comp:
 if c['university']=='UNSW':print(c)
