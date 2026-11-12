#!/usr/bin/env python3
"""Anchoring check: every solid part needs >= 2 pins/axles tying it to OTHER parts, spread apart.
A part held by one pin spins on it; two pins close together on a long liftarm barely help.
Reports parts with < 2 links, and liftarms whose pin spread is less than half their length."""
import sys,os
sys.path.insert(0,os.path.dirname(__file__)); import numpy as np
from ldflat import find
from ldcheck import parse_model, flatten_model, merged_bores, shaft_def, SHAFTS, geom_vertices
from ldcoord import name
from frame import detect as _detect
from ldcoord import set_frame as _set_frame

f=sys.argv[1]; m,o=parse_model(f); parts=flatten_model(m,o,f)
_set_frame(_detect(parts))
# reuse ldcheck's linking by running its engine
import ldcheck
bores=[]
for p in parts:
    b0=p['ref'].replace('.dat','')
    if b0 in SHAFTS and b0 not in ldcheck.HOLED_SHAFTS: continue
    if not find(p['ref']): continue
    fx=ldcheck.STUDIO_FIX.get(p['ref'],np.zeros(3))
    for (q,ax,lo,hi) in merged_bores(p['ref']): bores.append((p['id'],p['M']@(q+fx)+p['P'],p['M']@ax,lo,hi))
B=np.array([b[1] for b in bores]); BA=np.array([b[2]/np.linalg.norm(b[2]) for b in bores])
links={}   # part id -> list of (shaft id, contact point)
for p in parts:
    if p['ref'].replace('.dat','') not in SHAFTS or not find(p['ref']): continue
    c,ax,lo,hi=shaft_def(p['ref']); wc=p['M']@c+p['P']; wa=p['M']@ax; wa/=np.linalg.norm(wa)
    par=np.abs(BA@wa)>0.98; d=B-wc; pd=np.linalg.norm(d-np.outer(d@wa,wa),axis=1)
    hit={}
    for i in np.where(par&(pd<2.5))[0]:
        pid,q,bax,blo,bhi=bores[i]; bax=bax/np.linalg.norm(bax); s=float(np.dot(q-wc,wa)); sg=np.sign(bax@wa)
        b0,b1=sorted((s+sg*blo,s+sg*bhi))
        if min(hi,b1)-max(lo,b0)>3 and pid!=p['id']: hit[pid]=wc
    if len(hit)>=2:
        for pid,pt in hit.items(): links.setdefault(pid,[]).append((p['id'],pt))
skip=('44771','15038','41896','41897','4185','32123a','3713','37308c01','bb1142c01','55422c01','54675','54696',
      '32270','32269','3647','3648','94925','18654')   # tyres/rims/bushes/motors/hub, gears (1 axle by design), 1L (single hole)
print("parts with fewer than 2 pins/axles into other parts, or pins bunched together:")
nbad=0
for p in parts:
    b0=p['ref'].replace('.dat','')
    if b0 in SHAFTS or not find(p['ref']) or p['ref'].startswith(skip): continue
    L=links.get(p['id'],[]); pts=np.array([pt for _,pt in L]) if L else np.zeros((0,3))
    v=np.array(geom_vertices(p['ref'])); length=np.ptp(v,axis=0).max()
    spread=max((np.linalg.norm(a-b) for a in pts for b in pts),default=0)
    if len(L)<2: msg=f"{len(L)} pin(s)"
    elif length>=80 and spread < length/2: msg=f"{len(L)} pins but only {spread/20:.0f} studs apart on a {length/20:.0f}-stud piece"
    else: continue
    nbad+=1; print(f"  {p['ref']:12s} at {name(p['P']):26s} {msg}")
print("  none" if not nbad else f"  {nbad} parts")
