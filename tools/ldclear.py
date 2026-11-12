#!/usr/bin/env python3
"""Measure free space in front of the SPIKE hub's micro-USB port (Stud.io geometry)."""
import sys,os
os.environ['LDGEOM']='studio'
sys.path.insert(0,os.path.dirname(__file__))
import numpy as np
from ldcheck import parse_model, flatten_model, geom_vertices
PORT_LOCAL=np.array([0.,-70.,110.]); OUT=np.array([0.,0.,1.])   # from end-view render: 18x7 LDU opening, 10 LDU below top, +Z end
if len(sys.argv)<2: sys.exit('usage: ldclear.py MODEL.ldr')
m,o=parse_model(sys.argv[1]); parts=flatten_model(m,o,sys.argv[1])
hubs=[p for p in parts if p['ref']=='bb1142c01.dat']
if not hubs: sys.exit('no SPIKE Prime hub (bb1142c01) in this model')
hub=hubs[0]
port=hub['M']@PORT_LOCAL+hub['P']; d=hub['M']@OUT
u=np.cross(d,[0,1.,0]); u/=np.linalg.norm(u); w=np.cross(d,u)
print('port world',port.round(1),'facing',d.round(2))
# plug envelope: straight micro-USB overmold ~ 11x7mm -> 28x18 LDU, check 25mm (62 LDU) out
best=None
for p in parts:
    if p is hub or p['ref'] in ('55422c01.dat',): continue
    vv=np.array(geom_vertices(p['ref']))
    if not len(vv): continue
    W=vv@p['M'].T+p['P']-port
    a=W@d; b=W@u; c=W@w
    hit=(a>0.5)&(a<120)&(np.abs(b)<14)&(np.abs(c)<9)
    if hit.any():
        dist=a[hit].min()
        if best is None or dist<best[0]: best=(dist,p['ref'],p['P'])
        print(f"  {p['ref']:12s}@({p['P'][0]:.0f},{p['P'][1]:.0f},{p['P'][2]:.0f}) blocks at {dist:.1f} LDU = {dist*0.4:.1f} mm")
print('nearest obstruction:', f"{best[0]:.1f} LDU = {best[0]*0.4:.1f} mm ({best[1]})" if best else 'none within 48 mm')

# ---- rule: long sides of the hub (motor/sensor ports A-F) need >= 1 stud (20 LDU) clear ----
print('side ports (rule: >= 20 LDU / 1 stud clear):')
for sx in (1,-1):
    face_local=np.array([70.*sx,0,0]); out_l=np.array([sx*1.,0,0])
    d=hub['M']@out_l
    nearest=None
    for p in parts:
        if p is hub or p['ref']=='55422c01.dat': continue
        vv=np.array(geom_vertices(p['ref']))
        if not len(vv): continue
        L=(vv@p['M'].T+p['P']-hub['P'])@hub['M']          # into hub-local coords
        a_=(L[:,0]-70*sx)*sx                               # distance out from the side face
        m_=(a_>0.5)&(a_<60)&(np.abs(L[:,2])<66)&(L[:,1]>-82)&(L[:,1]<-50)
        if m_.any():
            dist=a_[m_].min()
            if nearest is None or dist<nearest[0]: nearest=(dist,p['ref'],p['P'])
    side='+X (robot right)' if (hub['M']@out_l)[0]>0 else '-X (robot left)'
    if nearest: print(f"  {side}: nearest {nearest[0]:.1f} LDU ({nearest[0]/20:.2f} studs) {nearest[1]}@{nearest[2].round()}  {'OK' if nearest[0]>=20 else 'VIOLATION'}")
    else: print(f"  {side}: clear for 3 studs  OK")
