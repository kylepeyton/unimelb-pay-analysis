"""Extract frozen UNSW salary schedules. Requires Poppler; no network access.
Printed amounts are retained; discrepancies are reported, never silently fixed.
"""
from pathlib import Path
import re,csv,json,subprocess,hashlib
from html.parser import HTMLParser
from functools import lru_cache
R=Path(__file__).resolve().parents[1];RAW=R/'data/raw/peers/unsw';O=R/'data/derived/unsw';O.mkdir(parents=True,exist_ok=True)
A=[f'{l}{s}' for l,n in zip('ABCDE',[8,6,6,4,1]) for s in range(1,n+1)]
P=[f'HEW{l}.{s}' for l,n in enumerate([5,2,5,3,5,3,4,5,3,1],1) for s in range(1,n+1)]
num=re.compile(r'(?<![\d.,])(?:\d{2,3},\d{3}|\d{5,6})(?![\d.,])')
cells=[];groups={};hashes={}
@lru_cache(None)
def pages(name,raw=False):
 p=RAW/name;b=p.read_bytes();hashes[name]=hashlib.sha256(b).hexdigest()
 return subprocess.check_output(['pdftotext','-raw' if raw else '-layout',str(p),'-']).decode().split('\f')
def store(name,keys,rows,dates,notes):
 assert len(rows)==len(keys),(name,len(rows),len(keys))
 groups[name]={}
 for k,(pg,vals) in zip(keys,rows):
  assert len(vals)==len(dates),(name,k,len(vals),len(dates))
  groups[name][k]=vals
  for j,(d,v) in enumerate(zip(dates,vals)):
   cells.append(dict(source=name,pdf_page=pg,classification=k,column=j,effective_date=d,annual_salary=v,date_note=notes[j] if isinstance(notes,list) else notes))
def table(name,pp,n):
 out=[]
 for pg in pp:
  text=pages(name)[pg-1]
  if 'CLINICAL LOADINGS' in text:text=text.split('CLINICAL LOADINGS')[0]
  for line in text.splitlines():
   line=re.sub(r'(\d),\s+(\d{3})(?!\d)',r'\1,\2',line) # printed 76, 519 spacing in2010 HEW6.3
   vals=[int(v.replace(',','')) for v in num.findall(line)]
   if len(vals)==n:out.append((pg,vals))
 return out
# The pre-rise column is a source check only; its date is not used as an entitlement.
a03=['prior_rate','2003-06-01','2003-11-01','2004-06-01','2004-11-01','2005-06-01','2005-11-01']
store('academic-ea2003.pdf',A,table('academic-ea2003.pdf',[45,46],7),a03,'First full pay period after date; June2003 column includes recurring $3000 from certification, verified before September baseline.')
# Professional2003 introduces new step numbering. Use NEW steps, not superseded old steps.
s=pages('general-ea2003.pdf')[57];rows=[]
for line in s.splitlines():
 vals=[int(v.replace(',','')) for v in num.findall(line)]
 if 'New Step' in line and len(vals)>=7:rows.append((58,vals[-7:]))
 elif 'Minimum' in line and len(vals)==8:rows.append((58,vals[-7:]))
store('general-ea2003.pdf',P,rows,['certification']+a03[1:],'New classification steps; dated increases apply first full pay period after nominated date.')
d06=['2005-11-01','endorsement2006','2006-12-01','2007-06-01','2007-12-01','2008-06-01','2008-12-01']
store('academic-ea2006.pdf',A,table('academic-ea2006.pdf',[43,44],7),d06,'First full pay period after date; endorsement precedes verified18August2006 lodgement. No exact endorsement payday inferred.')
# Dollar tokens preserve the rows that wrap across lines in the professional2006 PDF.
rows=[];buf=[]
for pg in [42,43]:
 for v in re.findall(r'\$(\d{2,3},\d{3})',pages('general-ea2006.pdf')[pg-1]):
  buf.append(int(v.replace(',','')))
  if len(buf)==7:rows.append((pg,buf));buf=[]
assert not buf
store('general-ea2006.pdf',P,rows,d06,'DOE column equals2.5% rise then$500; lodgement18August2006. Subsequent rises first full pay period after date.')
d10=['2009-07-10','2010-01-08','2010-07-09','2011-01-07','2011-07-08','2012-01-06','2012-07-06','2013-01-04','2013-07-05']
store('academic-ea2011.pdf',A,table('academic-ea2011.pdf',[58,59],10),d10+['2014-01-03'],'Dated salary schedule; earlier rises paid before agreement approval.')
store('professional-ea2010.pdf',P,table('professional-ea2010.pdf',[57],9),d10,'Dated salary schedule; first three rises already paid before approval.')
d15=['2014-01-03','2014-07-04','2015-01-02','2015-07-03','2016-01-01','2016-07-01','2017-01-01','2017-07-01','2018-01-01']
store('academic-ea2015.pdf',A,table('academic-ea2015.pdf',[61,62],8),d15[1:],'First full pay period on or after date.')
store('professional-ea2015.pdf',P,table('professional-ea2015.pdf',[60],9),d15,'35-hour schedule; first full pay period on or after date.')
d18=['2018-01-01','2018-10-05','2019-07-01','2020-07-01','2021-01-01','2021-07-01','2022-01-01']
store('academic-ea2018-approved.pdf',A,table('academic-ea2018-approved.pdf',[57,58,59],7),d18,'First rise5October2018 confirmed by UNSW17October2018 announcement; later dates first full pay period on/after.')
store('professional-ea2018-approved.pdf',P,table('professional-ea2018-approved.pdf',[53,54],7),d18,'35-hour schedule; first rise5October2018 confirmed by UNSW; printed September label superseded by actual implementation announcement.')
d23=['2023-09-01','2024-07-01','2025-07-01','2026-07-01']
store('academic-ea2023.pdf',A,table('academic-ea2023.pdf',[81],4),d23,'6% implemented administratively1September2023 before10Novemberapproval commencement; later rises first full pay period on/after.')
name='2023-11-unsw-enterprise-agreement-professional-2023.pdf';rows=[]
for pg in range(72,77):
 s=pages(name,True)[pg-1]
 for m in re.finditer(r'Annual Base Salary \(35\s+hour week\):\s*((?:[\d,]+\s+){3}[\d,]+)',s):rows.append((pg,[int(v.replace(',','')) for v in m[1].split()]))
store(name,P,rows,d23,'35-hour schedule;6% implemented1September2023; later dates first full pay period on/after.')
# Fresh university webpages independently verify all2023–2026 printed rates.
class Tables(HTMLParser):
 def __init__(self):super().__init__();self.tables=[];self.t=None;self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='table':self.t=[]
  if t=='tr' and self.t is not None:self.row=[]
  if t in ['th','td'] and self.row is not None:self.cell=''
 def handle_data(self,s):
  if self.cell is not None:self.cell+=s
 def handle_endtag(self,t):
  if t in ['th','td'] and self.cell is not None:self.row.append(' '.join(self.cell.split()));self.cell=None
  if t=='tr' and self.row is not None:self.t.append(self.row);self.row=None
  if t=='table' and self.t is not None:self.tables.append(self.t);self.t=None
checks=[]
def ck(k,what,observed,expected,tol=1.1):checks.append(dict(classification=k,check=what,observed=observed,expected=expected,residual=observed-expected,tolerance=tol,passed=abs(observed-expected)<=tol))
for kind,keys,src in [('academic',A,'academic-ea2023.pdf'),('professional',P,name)]:
 p=RAW/(kind+'-salary-oct2026.html');t=Tables();t.feed(p.read_text());hashes[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
 rows=([row[1:] for tab in t.tables[:5] for row in tab[1:]] if kind=='academic' else [row[1:] for tab in t.tables for row in tab if row[0]=='Annual Base Salary (35 hour week):'])
 assert len(rows)==len(keys),(kind,len(rows))
 for k,row in zip(keys,rows):
  for j,v in enumerate(row):ck(k,'2023–2026 printed schedule versus fresh website',int(v.replace(',','')),groups[src][k][j],0)
for src,g in groups.items():
 for k,v in g.items():
  for j in range(1,len(v)):
   factor=1.02;addition=0
   if '2003' in src and k.startswith('HEW'):pass
   elif '2003' in src:
    addition=3000 if j==1 else -60
   elif '2006' in src:
    factor=1.025;addition=500 if j==1 and k.startswith('HEW') else 0
   elif '2015' in src:factor=1.01 if src.startswith('professional') and j==1 else 1.015
   elif '2018' in src:factor=1.02 if j<=2 else 1.01
   elif '2023' in src:factor=1.04 if j==3 else 1.035
   ck(k,src+' column'+str(j),v[j],v[j-1]*factor+addition)
# Cross-agreement reconciliation: no implicit freeze in an agreement gap.
for prev,nxt,factor in [('academic-ea2003.pdf','academic-ea2006.pdf',1),('general-ea2003.pdf','general-ea2006.pdf',1),('academic-ea2006.pdf','academic-ea2011.pdf',1.02),('general-ea2006.pdf','professional-ea2010.pdf',1.02),('academic-ea2011.pdf','academic-ea2015.pdf',1.01),('professional-ea2010.pdf','professional-ea2015.pdf',1.02),('academic-ea2015.pdf','academic-ea2018-approved.pdf',1),('professional-ea2015.pdf','professional-ea2018-approved.pdf',1),('academic-ea2018-approved.pdf','academic-ea2023.pdf',1.01*1.06),('professional-ea2018-approved.pdf',name,1.01*1.06)]:
 for k in groups[prev]:ck(k,prev+' → '+nxt,groups[nxt][k][0],groups[prev][k][-1]*factor,1.6 if '2023' in nxt else 1.1)
def save(n,rows):
 with (O/n).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
save('salary-cells.csv',cells);save('checks.csv',checks);bad=[x for x in checks if not x['passed']]
(O/'exceptions.json').write_text(json.dumps(bad,indent=2)+'\n');(O/'source-hashes.json').write_text(json.dumps(hashes,indent=2)+'\n')
print(json.dumps(dict(cells=len(cells),checks=len(checks),exceptions=bad),indent=2))
