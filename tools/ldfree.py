#!/usr/bin/env python3
"""List parts whose (Stud.io) geometry intrudes into an axis-aligned box. usage: ldfree.py model x0 x1 y0 y1 z0 z1"""
import sys,os
os.environ['LDGEOM']='studio'
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldcheck import parse_model, flatten_model, geom_vertices
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

f=sys.argv[1]; x0,x1,y0,y1,z0,z1=map(float,sys.argv[2:8])
m,o=parse_model(f); parts=flatten_model(m,o,f)
_set_frame(_detect(parts))
hit=0
for p in parts:
    v=np.array(geom_vertices(p['ref']))
    if not len(v): continue
    w=v@p['M'].T+p['P']
    s=(w[:,0]>x0)&(w[:,0]<x1)&(w[:,1]>y0)&(w[:,1]<y1)&(w[:,2]>z0)&(w[:,2]<z1)
    if s.sum()>2:
        q=w[s]; hit+=1
        print(f"  {p['ref']:12s} at {name(p['P'])}: X[{q[:,0].min():.0f},{q[:,0].max():.0f}] Y[{q[:,1].min():.0f},{q[:,1].max():.0f}] Z[{q[:,2].min():.0f},{q[:,2].max():.0f}]")
print('  EMPTY' if not hit else f'  {hit} parts intrude')
