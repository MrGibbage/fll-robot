#!/usr/bin/env python3
"""Left/right symmetry check: mirror every part across the robot centerline (X = CX) and list parts
whose mirror twin (same part, mirrored position) is missing."""
import sys,os,argparse
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldcheck import parse_model, flatten_model
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--cx',type=float,default=None)
ap.add_argument('--zmin',type=float,default=-1e9); ap.add_argument('--zmax',type=float,default=1e9)
a=ap.parse_args()
m,o=parse_model(a.model); parts=flatten_model(m,o,a.model)
_fr=_detect(parts); _set_frame(_fr)
if a.cx is None: a.cx=_fr['CX']
P={}
for p in parts: P.setdefault(p['ref'],[]).append(p['P'])
miss=[]
for p in parts:
    if not (a.zmin<=p['P'][2]<=a.zmax): continue
    tw=np.array([2*a.cx-p['P'][0],p['P'][1],p['P'][2]])
    if not any(np.linalg.norm(q-tw)<3 for q in P[p['ref']]): miss.append(p)
print(f"{len(miss)} parts without a mirror twin (centerline X={a.cx}):")
for p in sorted(miss,key=lambda p:(p['P'][2],p['P'][0])):
    print(f"  {p['ref']:12s} at {name(p['P'])}   (twin would be at {name(np.array([2*a.cx-p['P'][0],p['P'][1],p['P'][2]]))})")
