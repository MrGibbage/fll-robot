#!/usr/bin/env python3
"""Flatten LDraw parts to connection primitives (holes/pins/axles) in world coords."""
import sys, os, re, functools
import numpy as np
from config import LDRAW_LIB as LIB, STUDIO_LIB
SEARCH = [LIB+'/parts', LIB+'/p', LIB+'/parts/s', LIB+'/p/48', LIB+'/unofficial/parts', LIB+'/unofficial/p', LIB+'/unofficial/parts/s']
STUDIO = STUDIO_LIB
STUDIO_DIRS = ['UnOfficial/parts','UnOfficial/p','parts','p','UnOfficial/parts/s','parts/s','p/48','UnOfficial/p/48']
@functools.lru_cache(None)
def _studio_index():
    idx={}
    for d in STUDIO_DIRS:
        base=os.path.join(STUDIO,d)
        if not os.path.isdir(base): continue
        for root,_,files in os.walk(base):
            for f in files:
                rel=os.path.relpath(os.path.join(root,f),base).replace(os.sep,'/').lower()
                idx.setdefault(rel,os.path.join(root,f))
    return idx
GEOM_MODE = os.environ.get('LDGEOM','official')   # 'studio' = prefer Stud.io geometry
def _official(n):
    for d in SEARCH:
        for cand in (os.path.join(d,n), os.path.join(d,os.path.basename(n))):
            if os.path.isfile(cand): return cand
    return None
def _studio(n):
    idx=_studio_index()
    return idx.get(n) or idx.get('s/'+os.path.basename(n)) or idx.get(os.path.basename(n))
@functools.lru_cache(None)
def find(name):
    n = name.replace('\\','/').lower()
    if GEOM_MODE=='studio':
        return _studio(n) or _official(n)
    return _official(n) or _studio(n)
@functools.lru_cache(None)
def load(name):
    p = find(name)
    if not p: return None
    out=[]
    for line in open(p, encoding='utf-8', errors='replace'):
        t=line.split()
        if len(t)>=15 and t[0]=='1':
            v=list(map(float,t[2:14])); sub=' '.join(t[14:])
            M=np.array([[v[3],v[4],v[5]],[v[6],v[7],v[8]],[v[9],v[10],v[11]]]); P=np.array(v[0:3])
            out.append((sub,M,P))
    return out
# primitives we treat as connection features
CONN = re.compile(r'^(.*/)?(beamhol|connhol|npeghol|peghole|axlehol|axleho|axl\dhol|axle\.|axlend|connect|confric|stud|technic|tooth|ring\d|cylh|beamhole|steerend)', re.I)
def flatten(name, M=np.eye(3), P=np.zeros(3), depth=0, acc=None, keep=None):
    if acc is None: acc=[]
    kids = load(name)
    if kids is None:
        acc.append(('MISSING:'+name, M, P)); return acc
    for sub,m,p in kids:
        M2 = M@m; P2 = M@p + P
        base=os.path.basename(sub.replace('\\','/')).lower()
        if keep and keep.match(base):
            acc.append((base,M2,P2)); continue
        if find(sub) and depth<12:
            flatten(sub,M2,P2,depth+1,acc,keep)
    return acc
if __name__=='__main__':
    pat = re.compile(sys.argv[2],re.I) if len(sys.argv)>2 else CONN
    for b,M,P in flatten(sys.argv[1], keep=pat):
        ax = M@np.array([0,1,0])  # primitive's local Y axis = hole/pin axis
        print(f"{b:22s} pos=({P[0]:7.1f},{P[1]:7.1f},{P[2]:7.1f}) axis=({ax[0]:5.2f},{ax[1]:5.2f},{ax[2]:5.2f})")
