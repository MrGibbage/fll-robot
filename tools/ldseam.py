#!/usr/bin/env python3
"""Brick-bond check: report vertical seams (a joint between two pieces at the same position on adjacent levels)
for the side walls and the front/rear rows (frame detected from the model)."""
import sys,os
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldflat import find
from ldcheck import parse_model, flatten_model, merged_bores, SHAFTS
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

f=sys.argv[1]
m,o=parse_model(f); parts=flatten_model(m,o,f)
FR=_detect(parts); _set_frame(FR)
LX,RX,FZ,RZ=int(FR['LX']),int(FR['RX']),int(FR['FZ']),int(FR['RZ']); st=-20 if FZ>RZ else 20
own={}
for p in parts:
    if not find(p['ref']) or p['ref'].replace('.dat','') in SHAFTS: continue
    for q,ax,lo,hi in merged_bores(p['ref']):
        A=p['M']@ax; A/=np.linalg.norm(A); Q=p['M']@q+p['P']
        for t in (np.arange(lo+10,hi-9,20) if hi-lo>=20 else [(lo+hi)/2]):
            c=tuple(np.round((Q+A*t)/10).astype(int)*10); own.setdefault(c,set()).add(p['id'])
def owner(c): s=own.get(c); return min(s) if s else None
walls={'left wall':[(LX,0,z) for z in range(FZ,RZ+st,st)],'right wall':[(RX,0,z) for z in range(FZ,RZ+st,st)],
       'front F1':[(x,0,FZ) for x in range(LX,RX+1,20)],'rear':[(x,0,RZ) for x in range(LX,RX+1,20)]}
LV={l:int(FR['Y1'])-20*(l-1) for l in range(1,8)}
total=0
for wname,cells in walls.items():
    joints={}
    for l,y in LV.items():
        cs=[(c[0],y,c[2]) for c in cells]; occ=[owner(c) for c in cs]; js=set()
        filled=[i for i,o in enumerate(occ) if o is not None]
        if len(filled)<2: joints[l]=js; continue
        for i in range(len(cs)-1):
            a,b=occ[i],occ[i+1]
            if a is not None and b is not None and a!=b: js.add(i)              # two pieces butt together
            elif (a is None)!=(b is None) and filled[0]<=i<filled[-1]:          # edge of a gap INSIDE the level
                js.add(i)
        joints[l]=js
    bad=[]
    for l in range(1,7):
        for i in sorted(joints[l]&joints[l+1]):
            c1=(cells[i][0],LV[l],cells[i][2]); c2=(cells[i+1][0],LV[l],cells[i+1][2])
            bad.append(f"lvl{l}-{l+1} between {name(np.array(c1)).split()[0 if 'wall' not in wname else 1]} and {name(np.array(c2)).split()[0 if 'wall' not in wname else 1]}")
    total+=len(bad)
    print(f"{wname}: {'no shared seams' if not bad else str(len(bad))+' shared seams'}"); [print('   ',b) for b in bad]
print("(rows that aren't walls, e.g. stacked PTO frames or an open charging slot, can show seams: judge those yourself)")
