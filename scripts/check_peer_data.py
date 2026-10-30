"""Check index arithmetic from bundled numeric observations, not PDF transcription.
No external packages, network access or university login required.
"""
from pathlib import Path
from collections import defaultdict
import csv, statistics
R=Path(__file__).resolve().parents[1]
def read(p):
    with (R/p).open() as f: return list(csv.DictReader(f))
def close(a,b):
    assert abs(float(a)-float(b))<1e-8,(a,b)
cpi={r['date']:float(r['value']) for r in read('peer-evidence/data/derived/september2026/cpi-quarterly-vintage.csv')}
rows=read('peer-evidence/data/derived/september2026/point-paths.csv')
groups=defaultdict(list)
for r in rows:
    close(r['cpi'],cpi[r['date']]);close(r['baseline_cpi'],cpi[r['baseline']])
    value=100*(float(r['annual_salary'])/float(r['baseline_salary']))/(float(r['cpi'])/float(r['baseline_cpi']))
    close(value,r['real_index'])
    groups[(r['baseline'],r['date'],r['university'])].append(value)
for r in read('peer-evidence/data/derived/september2026/recent-paths.csv'):
    a=groups[(r['baseline'],r['date'],r['university'])];assert len(a)==4
    close(statistics.mean(a),r['real_index']);close(min(a),r['min_index']);close(max(a),r['max_index'])
rows=read('peer-evidence-unsw/data/derived/six-university-comparison/historical-point-paths.csv')
bases={(r['university'],r['classification']):r for r in rows if r['date']=='2003-09-01'}
for r in rows:
    b=bases[(r['university'],r['classification'])]
    close(r['cpi'],cpi[r['date']])
    close(r['real_index'],100*(float(r['annual_salary'])/float(b['annual_salary']))/(float(r['cpi'])/float(b['cpi'])))
print('PASS: peer indices, four-position averages and CPI references match the bundled numeric inputs.')
