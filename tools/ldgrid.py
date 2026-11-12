#!/usr/bin/env python3
"""ASCII occupancy map of a wall: for column X (side wall, runs along Z) or row Z (front/rear wall, runs along X),
show which solid part owns each hole cell, per layer. usage: ldgrid.py model --x -400 | --z 190"""
import sys,os,argparse
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldflat import find
from ldcheck import parse_model, flatten_model, merged_bores, SHAFTS, STUDIO_FIX
ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--x',type=float); ap.add_argument('--z',type=float)
ap.add_argument('--lo',type=float,default=-170); ap.add_argument('--hi',type=float,default=230)
a=ap.parse_args()
m,o=parse_model(a.model); parts=flatten_model(m,o,a.model)
own={}; tags={}
for p in parts:
    b=p['ref'].replace('.dat','')
    if not find(p['ref']) or b in SHAFTS: continue
    fx=STUDIO_FIX.get(p['ref'],np.zeros(3))
    for q,ax,lo,hi in merged_bores(p['ref']):
        A=p['M']@ax; A/=np.linalg.norm(A); Q=p['M']@(q+fx)+p['P']
        for t in (np.arange(lo+10,hi-9,20) if hi-lo>=20 else [(lo+hi)/2]):
            c=np.round((Q+A*t)/10)*10
            k=tuple(c.astype(int)); own.setdefault(k,set()).add(p['id'])
letters={}
def tag(pid):
    if pid not in letters: letters[pid]=chr(ord('A')+len(letters)%26)+('' if len(letters)<26 else "'")
    return letters[pid]
axis_vals=list(range(int(a.lo)//20*20+10,int(a.hi),20)) if a.x is not None else list(range(int(a.lo)//20*20,int(a.hi),20))
print(('Z' if a.x is not None else 'X')+' : '+' '.join(f'{v:>4}' for v in axis_vals))
for y in range(-150,1,20):
    row=[]
    for v in axis_vals:
        k=(int(a.x),y,v) if a.x is not None else (v,y,int(a.z))
        s=own.get(k,set())
        row.append('  . ' if not s else (' '+'/'.join(tag(i) for i in sorted(s))).ljust(4)[:4] if len(s)==1 else ' XX ')
    print(f'Y{y:>4}: '+' '.join(row))
for pid,t in letters.items():
    p=parts[pid]; print(f'  {t}: #{pid} {p["ref"]} @({p["P"][0]:.0f},{p["P"][1]:.0f},{p["P"][2]:.0f})')
