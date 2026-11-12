#!/usr/bin/env python3
"""Vertical pins in the four walls that stick out above the wall top or below the wall bottom."""
import sys,os; os.environ['LDGEOM']='studio'
sys.path.insert(0,os.path.dirname(__file__)); import numpy as np
from ldcheck import parse_model, flatten_model, geom_vertices, SHAFTS
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

f=sys.argv[1]; m,o=parse_model(f); parts=flatten_model(m,o,f)
FR=_detect(parts); _set_frame(FR)
G={}
def gv(r):
    if r not in G: G[r]=np.array(geom_vertices(r))
    return G[r]
solids=[(gv(p['ref'])@p['M'].T+p['P']) for p in parts if p['ref'].replace('.dat','') not in SHAFTS and len(gv(p['ref']))]
def span(x,z):
    lo,hi=0,-1e9
    for w in solids:
        s=(np.abs(w[:,0]-x)<9)&(np.abs(w[:,2]-z)<9)
        if s.any(): lo=min(lo,w[s,1].min()); hi=max(hi,w[s,1].max())
    return lo,hi
bad=n=0
for p in parts:
    if p['ref'].replace('.dat','') not in SHAFTS or abs(p['M'][1,0])<0.9 and abs(p['M'][1,1])<0.9: continue
    x,y,z=p['P']
    if not (abs(x-FR['LX'])<3 or abs(x-FR['RX'])<3 or abs(z-FR['RZ'])<3 or abs(z-FR['FZ'])<3): continue
    w=gv(p['ref'])@p['M'].T+p['P']
    if np.ptp(w[:,1])<np.ptp(w[:,0]) or np.ptp(w[:,1])<np.ptp(w[:,2]): continue   # not vertical
    n+=1; top,bot=span(x,z)
    if w[:,1].min()<top-1: bad+=1; print('above top:',p['ref'],name(p['P']))
    if w[:,1].max()>bot+1: bad+=1; print('below bottom:',p['ref'],name(p['P']))
print(f'{n} vertical wall pins checked, {bad} stick out')
