#!/usr/bin/env python3
"""Anchoring check: every solid part needs >= 2 pins/axles tying it to OTHER parts, spread apart.
A part held by one pin spins on it; two pins close together on a long liftarm barely help.
Reports parts with < 2 links, and liftarms whose pin spread is less than half their length."""
import sys,os
os.environ['LDGEOM']='studio'
sys.path.insert(0,os.path.dirname(__file__)); import numpy as np
from ldflat import find
from ldcheck import parse_model, flatten_model, merged_bores, shaft_def, SHAFTS, geom_vertices
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

f=sys.argv[1]; m,o=parse_model(f); parts=flatten_model(m,o,f)
_set_frame(_detect(parts))
# Count ordinary shafts and the molded pins of 2393/48989 consistently.
from ldcheck import connection_records
links={}
for r in connection_records(parts):
    hit=r['hits']|({r['owner']} if r['owner'] is not None else set())
    if len(hit)>=2:
        for pid in hit:links.setdefault(pid,[]).append((r['key'],r['center']))
skip=('44771','15038','41896','41897','4185','32123a','3713','55422c01',
      '32270','32269','3647','3648','94925','18654')   # tyres/rims/bushes/battery (clip fit), gears (1 axle by design), 1L (single hole)
print("parts with fewer than 2 pins/axles into other parts, or pins bunched together:")
nbad=0
for p in parts:
    b0=p['ref'].replace('.dat','')
    if b0 in SHAFTS or not find(p['ref']) or p['ref'].startswith(skip): continue
    L=links.get(p['id'],[]); pts=np.array([pt for _,pt in L]) if L else np.zeros((0,3))
    v=np.array(geom_vertices(p['ref'])); length=np.ptp(v,axis=0).max()
    spread=max((np.linalg.norm(a-b) for a in pts for b in pts),default=0)
    if len(L)<2: msg=f"{len(L)} pin(s)"
    elif length>=80 and spread < length/2: msg=f"{len(L)} pins but only {spread/20:.0f} studs apart on a {length/20:.0f}-stud piece"
    else: continue
    nbad+=1; print(f"  {p['ref']:12s} at {name(p['P']):26s} {msg}")
print("  none" if not nbad else f"  {nbad} parts")

sys.exit(int(bool(nbad)))
