#!/usr/bin/env python3
"""Bill of materials for a model, grouped by parts-list category, with anything not in the parts list flagged."""
import sys,os,collections
sys.path.insert(0,os.path.dirname(__file__))
from ldcheck import parse_model, flatten_model
from ldflat import find
from partslist import load, canonical
f=sys.argv[1]; m,o=parse_model(f); parts=flatten_model(m,o,f)
items=load()
CAT={}; NAME={}; ORDER={}
for it in items:
    ORDER.setdefault(it['category'],len(ORDER))
    for k in {it['pid'],it.get('equiv')}-{None}: CAT.setdefault(k,it['category']); NAME.setdefault(k,it['name'])
cnt=collections.Counter(p['ref'].replace('.dat','') for p in parts)
rows=collections.defaultdict(list)
NOT='!! NOT IN PARTS LIST - needs ordering'
for pn,n in cnt.items():
    c=canonical(pn); key=CAT.get(pn, CAT.get(c))
    if key is None: key='Submodels' if not find(pn+'.dat') else NOT
    d=NAME.get(pn) or NAME.get(c) or (open(find(pn+'.dat'),errors='replace').readline()[2:].strip() if find(pn+'.dat') else pn)
    rows[key].append((pn,n,d))
print(f"Bill of materials: {os.path.basename(f)}  ({sum(cnt.values())} parts)\n")
for k in sorted(rows,key=lambda k:(0 if k==NOT else 1, ORDER.get(k,999), k)):
    print(k)
    for pn,n,d in sorted(rows[k],key=lambda r:-r[1]): print(f"   {n:4d} × {pn:10s} {d[:60]}")
