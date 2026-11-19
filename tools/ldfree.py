#!/usr/bin/env python3
"""Check geometry vertices inside reserved boxes, using Stud.io geometry when available.
usage: ldfree.py MODEL [x0 x1 y0 y1 z0 z1]
Without a box, check each 0 !FLL POCKET name x0 x1 y0 y1 z0 z1 declaration.
This is a vertex test, not an exact triangle/volume intersection test.
"""
import sys, os
from pathlib import Path
os.environ['LDGEOM']='studio'
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldcheck import parse_model, flatten_model, geom_vertices
from ldcoord import name, set_frame
from frame import detect

f=sys.argv[1]
if len(sys.argv)>2:
    boxes=[('requested box',list(map(float,sys.argv[2:8])))]
else:
    boxes=[]
    for line in Path(f).read_text().splitlines():
        t=line.split()
        if t[:3]==['0','!FLL','POCKET']:
            boxes.append((t[3],list(map(float,t[4:10]))))
if not boxes:
    print('No reserved pockets declared; check not applicable.')
    sys.exit(0)
m,o=parse_model(f);parts=flatten_model(m,o,f)
set_frame(detect(parts))
geometry=[]
for p in parts:
    v=np.array(geom_vertices(p['ref']))
    if not len(v):
        sys.exit('Missing geometry: '+p['ref'])
    geometry.append((p,v@p['M'].T+p['P']))
total=0
for label,(x0,x1,y0,y1,z0,z1) in boxes:
    hit=0
    print(label+':')
    for p,w in geometry:
        mask=(w[:,0]>x0)&(w[:,0]<x1)&(w[:,1]>y0)&(w[:,1]<y1)&(w[:,2]>z0)&(w[:,2]<z1)
        if mask.sum()>2:
            hit+=1
            print(f"  {p['ref']:12s} at {name(p['P'])} intrudes")
    print('  EMPTY' if not hit else f'  {hit} parts intrude')
    total+=hit
sys.exit(int(total>0))
