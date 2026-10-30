"""Offline September2026 peer comparison. Standard-library Python; no network.
Salary inputs are frozen previously audited fixed-position paths. All CPI history
is re-imported from September2026 Table17. Only UQ adds a July–September rise.
Preserves all pre-existing June files unchanged.
"""
from pathlib import Path
import csv,datetime,hashlib,html,json,re,statistics,zipfile,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[1]; RAW=R/'data/raw/september2026';O=R/'data/derived/september2026';O.mkdir(parents=True,exist_ok=True)
inputs=[]
def read(p):
 if p.startswith('data/derived/'):p='data/raw/september2026/prior-audit/'+p
 inputs.append(p);return list(csv.DictReader((R/p).open()))
def save(n,rows):
 with (O/n).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def plain(p):
 inputs.append(str(p.relative_to(R)));return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',p.read_text())))
# Resolve named Data1 worksheet, series header, metadata and dates, not fixed cells alone.
p=RAW/'cpi-quarterly-sep2026.xlsx';inputs.append(str(p.relative_to(R)));z=zipfile.ZipFile(p);ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
strings=[''.join(x.itertext()) for x in E.fromstring(z.read('xl/sharedStrings.xml'))]
wb=E.fromstring(z.read('xl/workbook.xml'));rel=E.fromstring(z.read('xl/_rels/workbook.xml.rels'))
rid=next(x.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'] for x in wb.find('s:sheets',ns) if x.attrib['name']=='Data1')
target=next(x.attrib['Target'] for x in rel if x.attrib['Id']==rid);sheet=E.fromstring(z.read('xl/'+target))
cs={}
for c in sheet.findall('.//s:c',ns):
 v=c.find('s:v',ns)
 if v is not None:cs[c.attrib['r']]=strings[int(v.text)] if c.attrib.get('t')=='s' else v.text
col=re.sub(r'\d','',next(k for k,v in cs.items() if v=='A2325846C'))
assert cs[col+'3']=='Original' and cs[col+'5']=='Quarter' and 'All groups CPI' in cs[col+'1']
cpi={};cpir=[]
for i in range(11,1000):
 if col+str(i) not in cs:continue
 date=(datetime.date(1899,12,30)+datetime.timedelta(days=float(cs['A'+str(i)]))).isoformat();v=float(cs[col+str(i)]);cpi[date]=v
 cpir.append(dict(date=date,quarter_end=(datetime.date.fromisoformat(date).replace(day=28)+datetime.timedelta(days=4)).replace(day=1)-datetime.timedelta(days=1),series_id='A2325846C',value=v,worksheet='Data1',cell=col+str(i),vintage='September2026'))
assert {d:cpi[d] for d in ['2017-06-01','2017-12-01','2019-12-01','2026-06-01','2026-09-01']}=={'2017-06-01':76.88,'2017-12-01':77.87,'2019-12-01':80.7,'2026-06-01':102.31,'2026-09-01':103.64}
save('cpi-quarterly-vintage.csv',cpir)
# Original inherited position definitions; no substitutions or progression.
pts=read('data/derived/anu/historical-point-paths.csv')
pts += [r for r in read('data/derived/uq/recent-point-paths.csv') if r['university']=='UQ']
pts=[dict(date=r['date'],university=r['university'],classification=r['classification'],annual_salary=float(r['annual_salary'])) for r in pts if r['date']>='2017-06-01']
# Recovered approved/corrected2014 agreement final January2017 column. Parent
# audit checks58 positions against March2018 floors; one known printed HEW4.3
# typo is separate and does not alter2017 starting rates or2026 endpoints.
uq17={r['classification']:float(r['annual_salary']) for r in read('data/derived/uq-history/salary-cells.csv') if r['effective_date']=='2017-01-01'}
assert len(uq17)==58
for base in ['2017-06-01','2017-12-01']:
 for k in ['B1','C4','HEW5.1','HEW7.1']:pts.append(dict(date=base,university='UQ',classification=k,annual_salary=uq17[k]))
# Parse actual July published salary levels; cross-check every point against Feb.
uq={};checks=[]
for group,fname in [('Academic','uq-academic.html'),('Professional','uq-professional.html')]:
 s=plain(RAW/fname);blocks=re.split(r'Level ([A-E]):' if group=='Academic' else r'HEW Level (\d+) Effective from',s)
 for i in range(1,len(blocks),2):
  lev=blocks[i];chunk=blocks[i+1]
  def get(when):
   # Professional split consumes first "Effective from" only.
   suffix=chunk.split(when,1)[1].split('Effective from',1)[0]
   return {int(step):float(v.replace(',','')) for step,v in re.findall(r'(\d+)\s+\$([0-9,]+\.[0-9]{2})\s+\$[0-9,]+\.[0-9]{2}',suffix)}
  jul=get('11 July 2026');feb=get('7 February 2026');assert set(jul)==set(feb)
  for step,v in jul.items():
   k=lev+str(step) if group=='Academic' else 'HEW'+lev+'.'+str(step);uq[k]=v
   err=v/feb[step]-1-.02;assert abs(err)<.000001
   checks.append(dict(university='UQ',classification=k,before=feb[step],after=v,check='July11 published rate versus February7 times1.02',residual_dollars=v-feb[step]*1.02))
assert len(uq)==58
ends=[]
for r in pts:
 if r['date']=='2026-06-01':
  v=uq[r['classification']] if r['university']=='UQ' else r['annual_salary']
  ends.append(dict(**{**r,'date':'2026-09-01','annual_salary':v}))
assert len(ends)==20;pts+=ends
# Validate non-UQ final dollars against archived current schedules / agreement cells.
for uni,files in [('Monash',['monash-academic-archived.html','monash-professional-archived.html']),('ANU',['anu-academic.html','anu-professional.html'])]:
 text=' '.join(plain(RAW/f) for f in files)
 for r in ends:
  if r['university']==uni:
   assert format(int(r['annual_salary']),',') in text,(uni,r)
   checks.append(dict(university=uni,classification=r['classification'],before=r['annual_salary'],after=r['annual_salary'],check='Unchanged endpoint present in current salary schedule',residual_dollars=0))
# Sydney retained final column, which is identical whichever June/July date applies.
syd=read('data/derived/sydney/all-point-endpoints.csv')
for r in ends:
 if r['university']=='Sydney':assert any(float(s['end_salary'])==r['annual_salary'] for s in syd)
# All comparisons derive directly from annual salaries and same CPI vintage.
lookup={(r['university'],r['classification'],r['date']):r['annual_salary'] for r in pts};assert len(lookup)==len(pts)
bases=['2017-06-01','2017-12-01','2019-12-01'];pointpaths=[];paths=[];comparisons=[]
for base in bases:
 for r in pts:
  if r['date']<base or (r['university'],r['classification'],base) not in lookup:continue
  b=lookup[r['university'],r['classification'],base];val=100*r['annual_salary']/b/(cpi[r['date']]/cpi[base])
  pointpaths.append(dict(baseline=base,**r,baseline_salary=b,cpi=cpi[r['date']],baseline_cpi=cpi[base],real_index=val))
 for u,d in sorted({(r['university'],r['date']) for r in pointpaths if r['baseline']==base}):
  selected=[r for r in pointpaths if r['baseline']==base and r['university']==u and r['date']==d];assert len(selected)==4
  values=[r['real_index'] for r in selected]
  paths.append(dict(baseline=base,date=d,university=u,real_index=statistics.mean(values),min_index=min(values),max_index=max(values)))
  if d in ['2026-06-01','2026-09-01']:
   comparisons.append(dict(baseline=base,end=d,university=u,real_change_pct=statistics.mean(values)-100,min_point_change_pct=min(values)-100,max_point_change_pct=max(values)-100,nominal_change_pct=100*(statistics.mean(r['annual_salary']/r['baseline_salary'] for r in selected)-1),cpi_change_pct=100*(cpi[d]/cpi[base]-1),points=4))
allpoints=[]
for uni in ['ANU','Sydney','UQ']:
 rows=read('data/derived/'+uni.lower()+'/all-point-endpoints.csv')
 for r in rows:
  base=r.get('baseline','2019-12-01');start=float(r.get('start_salary',r.get('baseline_salary')));end=uq[r['classification']] if uni=='UQ' else float(r['end_salary'])
  k=r.get('classification') or r['level']+'.'+r['step']+' ('+r['hours_schedule']+'h)'
  allpoints.append(dict(university=uni,baseline=base,end='2026-09-01',classification=k,group=r['group'],start_salary=start,end_salary=end,real_change_pct=100*(end/start/(cpi['2026-09-01']/cpi[base])-1)))
for base in ['2017-06-01','2017-12-01']:
 for k,start in uq17.items():
  allpoints.append(dict(university='UQ',baseline=base,end='2026-09-01',classification=k,group='Professional' if k.startswith('HEW') else 'Academic',start_salary=start,end_salary=uq[k],real_change_pct=100*(uq[k]/start/(cpi['2026-09-01']/cpi[base])-1)))
save('salary-observations.csv',pts);save('point-paths.csv',pointpaths);save('recent-paths.csv',paths);save('comparisons.csv',comparisons);save('all-point-endpoints.csv',allpoints);save('salary-checks.csv',checks)
# June preservation/reproduction check in original June CPI units (same values).
old=read('data/derived/uq/historical-comparisons.csv');errors=[]
for r in old:
 if r['start'] not in bases or r['end']!='2026-06-01':continue
 v=next(x for x in comparisons if x['baseline']==r['start'] and x['end']==r['end'] and x['university']==r['university']);errors.append(abs(v['real_change_pct']-float(r['real_change_pct'])))
assert len(errors)==13 and max(errors)<1e-10
summary=[]
for u,b in sorted({(r['university'],r['baseline']) for r in allpoints}):
 vals=[r['real_change_pct'] for r in allpoints if r['university']==u and r['baseline']==b]
 summary.append(dict(university=u,baseline=b,points=len(vals),min_real_pct=min(vals),max_real_pct=max(vals),negative_points=sum(v<0 for v in vals),positive_points=sum(v>0 for v in vals)))
save('classification-summary.csv',summary)
v=dict(cpi_series='A2325846C',cpi_september=103.64,cpi_june=102.31,cpi_quarter_change_pct=100*(103.64/102.31-1),june_comparisons_reproduced=len(errors),max_june_error=max(errors),uq_july_points_checked=58,selected_positions=20,baselines=bases,salary_observation_convention='quarter-end entitlement; dates encode quarter by first day of final month',input_hashes={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in sorted(set(inputs))})
(O/'verification.json').write_text(json.dumps(v,indent=2)+'\n')
for r in comparisons:
 if r['end']=='2026-09-01':print(r)
print(summary)
