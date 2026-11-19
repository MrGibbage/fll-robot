#!/usr/bin/env python3
"""Check the swept rolling disk of small 4185 rollers against part surfaces.
Clip triangles to the wheel's axial slab, then test the projected polygon against
an annulus. This catches broad faces whose vertices lie outside the wheel.
The central axle bore and touching end faces are allowed; spokes are not clearance.
"""
import os
os.environ['LDGEOM']='studio'
import sys
from functools import lru_cache
import numpy as np
from ldcheck import parse_model, flatten_model, geom_vertices
from ldcoord import name, set_frame
from frame import detect
from ldrender import tris

ROLLERS={'4185.dat','4185a.dat'}
EPS=0.15  # LDU: disregard numerical/contact-surface noise, not a clearance allowance

@lru_cache(None)
def vertices(ref):return np.array(geom_vertices(ref))

@lru_cache(None)
def faces(ref):return np.array([v for _,v in tris(ref)])

def clip_z(poly, bound, keep_above):
    if len(poly)==0:return poly
    out=[]
    previous=poly[-1]
    prev_in=previous[2]>=bound if keep_above else previous[2]<=bound
    for current in poly:
        cur_in=current[2]>=bound if keep_above else current[2]<=bound
        if cur_in!=prev_in:
            t=(bound-previous[2])/(current[2]-previous[2])
            out.append(previous+t*(current-previous))
        if cur_in:out.append(current)
        previous=current;prev_in=cur_in
    return np.array(out)

def enters_annulus(poly, radius, bore):
    p=poly[:,:2]
    if len(p)<2:return False
    q=np.roll(p,-1,axis=0);edge=q-p
    crosses=edge[:,0]*(-p[:,1])-edge[:,1]*(-p[:,0])
    area=np.sum(p[:,0]*q[:,1]-p[:,1]*q[:,0])
    inside=abs(area)>1e-8 and (np.all(crosses>=-1e-8) or np.all(crosses<=1e-8))
    t=np.clip(-np.sum(p*edge,axis=1)/np.maximum(np.sum(edge*edge,axis=1),1e-15),0,1)
    nearest=0 if inside else np.linalg.norm(p+t[:,None]*edge,axis=1).min()
    return nearest<radius and np.linalg.norm(p,axis=1).max()>bore

def collisions(parts):
    # World AABBs are only a broad phase; they never establish an actual hit.
    boxes={}
    for p in parts:
        v=vertices(p['ref'])
        if not len(v):raise ValueError('Missing geometry: '+p['ref'])
        w=v@p['M'].T+p['P'];boxes[p['id']]=(w.min(0),w.max(0))
    hits=[]
    for wheel in parts:
        if wheel['ref'].lower() not in ROLLERS:continue
        v=vertices(wheel['ref']);lo=v.min(0);hi=v.max(0);ext=hi-lo
        ax=int(np.argmin(ext));radial=[i for i in range(3) if i!=ax]
        radius=ext[radial].max()/2-EPS;half=ext[ax]/2-EPS
        bore=6.4 # axle cross section fits; do not exempt an entire shaft or bushing
        center=wheel['M']@((lo+hi)/2)+wheel['P']
        basis=wheel['M'][:,radial+[ax]]
        axis=basis[:,2]
        extent=radius*np.sqrt(np.maximum(0,1-axis*axis))+half*np.abs(axis)
        for p in parts:
            if p is wheel:continue
            blo,bhi=boxes[p['id']]
            if np.any(bhi<=center-extent) or np.any(blo>=center+extent):continue
            f=faces(p['ref'])
            if not len(f):continue
            f=((f@p['M'].T+p['P'])-center)@basis
            mins=f.min(1);maxs=f.max(1)
            bound=np.array([radius,radius,half])
            candidates=f[np.all(maxs>-bound,axis=1)&np.all(mins<bound,axis=1)]
            for tri in candidates:
                poly=clip_z(clip_z(tri,-half,True),half,False)
                if len(poly) and enters_annulus(poly,radius,bore):
                    hits.append((wheel,p));break
    return hits

def main(path):
    m,o=parse_model(path);parts=flatten_model(m,o,path)
    set_frame(detect(parts))
    hits=collisions(parts)
    count=sum(p['ref'].lower() in ROLLERS for p in parts)
    print(f'{count} small rollers checked against swept disks, including beam faces and axle hardware')
    for wheel,p in hits:
        print(f"  COLLISION: {wheel['ref']} at {name(wheel['P'])} with {p['ref']} at {name(p['P'])}")
    print('No small-roller collisions.' if not hits else f'{len(hits)} small-roller collisions')
    return int(bool(hits))

if __name__=='__main__':sys.exit(main(sys.argv[1]))
