#!/usr/bin/env python3
"""List parts with description and world bbox; filter by Z range."""
import sys,os,argparse,functools
import numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from ldflat import find
from ldcheck import parse_model, flatten_model, geom_vertices, STUDIO_FIX
@functools.lru_cache(None)
def lbbox(ref):
    v=np.array(geom_vertices(ref)); return (v.min(0),v.max(0)) if len(v) else (np.zeros(3),np.zeros(3))
@functools.lru_cache(None)
def desc(ref):
    p=find(ref); return open(p,errors='replace').readline()[2:].strip()[:42] if p else '?'
ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--z',default='-9999,9999'); ap.add_argument('--skip',default='')
a=ap.parse_args(); z0,z1=map(float,a.z.split(','))
models,order=parse_model(a.model); parts=flatten_model(models,order,a.model)
skip=set(a.skip.split(','))
allmin=np.full(3,1e9); allmax=np.full(3,-1e9)
for i,p in enumerate(parts):
    lo,hi=lbbox(p['ref']); fx=np.zeros(3) if os.environ.get('LDGEOM')=='studio' else STUDIO_FIX.get(p['ref'],np.zeros(3))
    c=np.array([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])+fx
    w=c@p['M'].T+p['P']; wl,wh=w.min(0),w.max(0)
    allmin=np.minimum(allmin,wl); allmax=np.maximum(allmax,wh)
    if p['ref'].replace('.dat','') in skip: continue
    if z0<=p['P'][2]<=z1:
        print(f"#{i:<3} {p['ref']:12s} {desc(p['ref']):42s} X[{wl[0]:5.0f},{wh[0]:5.0f}] Y[{wl[1]:5.0f},{wh[1]:5.0f}] Z[{wl[2]:5.0f},{wh[2]:5.0f}]  {p['where']}")
print('MODEL BBOX',allmin.round(),allmax.round(),'size',(allmax-allmin).round())
