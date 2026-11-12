#!/usr/bin/env python3
"""Bill of materials for a model, grouped by tray, with anything the team doesn't own flagged."""
import sys,os,collections
sys.path.insert(0,os.path.dirname(__file__))
from ldcheck import parse_model, flatten_model
from ldflat import find
from inventory import load, canonical, EQUIV
f=sys.argv[1]; m,o=parse_model(f); parts=flatten_model(m,o,f)
trays,inv=load()
TR={}; NAME={}
for it in inv:
    if it['pid']:
        for k in {it['pid'],it.get('equiv')}-{None}: TR.setdefault(k,it['tray'] if it['tray'] not in (None,'') else 'none'); NAME.setdefault(k,it['name'].replace('LEGO ',''))
from config import KIT
cnt=collections.Counter(p['ref'].replace('.dat','') for p in parts)
rows=collections.defaultdict(list)
for pn,n in cnt.items():
    c=canonical(pn); t=TR.get(pn, TR.get(c))
    if t=='none': key='In inventory, no tray assigned'
    elif t is not None: key=f"Tray {t} ({trays.get(t,'?')})"
    elif pn in KIT or c in KIT: key='SPIKE kit / wheels'
    elif not find(pn+'.dat'): key='Submodels'
    else: key='!! NOT OWNED - needs ordering'
    d=NAME.get(pn) or NAME.get(c) or (open(find(pn+'.dat'),errors='replace').readline()[2:].strip() if find(pn+'.dat') else pn)
    rows[key].append((pn,n,d))
print(f"Bill of materials: {os.path.basename(f)}  ({sum(cnt.values())} parts)\n")
order=sorted(rows,key=lambda k:(k.startswith('!!')==False, k.startswith('Tray')==False, int(k.split()[1]) if k.startswith('Tray') else 0, k),)
for k in sorted(rows,key=lambda k:(0 if k.startswith('!!') else 1 if k.startswith('Tray') else 2, int(k.split()[1]) if k.startswith('Tray') else 0, k)):
    print(k)
    for pn,n,d in sorted(rows[k],key=lambda r:-r[1]): print(f"   {n:4d} × {pn:10s} {d[:60]}")
