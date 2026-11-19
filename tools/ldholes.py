#!/usr/bin/env python3
"""List empty vertical holes in the four walls (goal: a pin in every hole)."""
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldflat import find
from ldcheck import parse_model, flatten_model, merged_bores, shaft_def, SHAFTS
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

f=sys.argv[1]
m,o=parse_model(f); parts=flatten_model(m,o,f)
FR=_detect(parts); _set_frame(FR)
FZ,RZ,LX,RX=FR['FZ'],FR['RZ'],FR['LX'],FR['RX']
ZLO,ZHI=min(FZ,RZ),max(FZ,RZ)
def onwall(c): return c[0] in (LX,RX) or c[2] in (FZ,RZ)
holes={}
for p in parts:
    if not find(p['ref']) or p['ref'].replace('.dat','') in SHAFTS: continue
    for q,ax,lo,hi in merged_bores(p['ref']):
        A=p['M']@ax; A/=np.linalg.norm(A); Q=p['M']@q+p['P']
        if abs(A[1])<0.9: continue
        for t in (np.arange(lo+10,hi-9,20) if hi-lo>=20 else []):
            c=tuple(np.round((Q+A*t)/10).astype(int)*10)
            if c[0]%20==0 and (c[2]-FZ)%20==0 and onwall(c) and LX<=c[0]<=RX and ZLO<=c[2]<=ZHI: holes[c]=p['ref']
filled=set()
for p in parts:
    if p['ref'].replace('.dat','') not in SHAFTS: continue
    c,ax,lo,hi=shaft_def(p['ref']); w=p['M']@c+p['P']; a=p['M']@ax
    if abs(a[1])<0.9: continue
    for y in np.arange(min((w+a*lo)[1],(w+a*hi)[1])+10, max((w+a*lo)[1],(w+a*hi)[1]), 20):
        filled.add((int(round(w[0]/10))*10,int(round(y/10))*10,int(round(w[2]/10))*10))
from ldcheck import builtin_pin_segments
for p in parts:
    for c,a,lo,hi in builtin_pin_segments(p):
        if abs(a[1])<.9:continue
        y0,y1=sorted(((c+a*lo)[1],(c+a*hi)[1]))
        for y in np.arange(y0+10,y1,20):
            filled.add((int(round(c[0]/10))*10,int(round(y/10))*10,int(round(c[2]/10))*10))
empty=sorted(set(holes)-filled,key=lambda c:(c[2],c[0],c[1]))
print(f"{len(holes)} vertical wall holes, {len(holes)-len(empty)} pinned, {len(empty)} empty")
isolated=[c for c in empty if (c[0],c[1]-20,c[2]) not in holes and (c[0],c[1]+20,c[2]) not in holes]
required=[c for c in empty if c not in isolated]
print(f'{len(isolated)} isolated holes (allowed); {len(required)} unfilled holes with a neighbor')
for c in required: print(f"  {name(np.array(c,float)):22s} in {holes[c]}")

sys.exit(int(bool(required)))
