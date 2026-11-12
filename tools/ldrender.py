#!/usr/bin/env python3
"""Quick software render of a Stud.io LDraw model to PNG (painter's algorithm, flat shading).
usage: ldrender.py model.ldr out.png [--view iso|front|top|side|rear|left] [--highlight 54696,37308c01] [--xray]"""
import sys, os, argparse, functools, re
os.environ.setdefault('LDGEOM','studio')  # render what Stud.io shows
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ldflat import find
from ldcheck import parse_model, flatten_model, STUDIO_FIX
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from config import LDRAW_LIB as LIB
COL={}
for line in open(LIB+'/LDConfig.ldr',encoding='utf-8',errors='replace'):
    m=re.search(r'CODE\s+(\d+)\s+VALUE\s+#([0-9A-Fa-f]{6})',line)
    if m: COL[int(m.group(1))]=tuple(int(m.group(2)[i:i+2],16)/255 for i in (0,2,4))
@functools.lru_cache(None)
def tris(name):
    out=[]  # (color, 3x3 verts)
    def walk(nm,M,P,c,d):
        p=find(nm)
        if not p or d>15: return
        for line in open(p,encoding='utf-8',errors='replace'):
            t=line.split()
            if not t: continue
            cc=int(t[1]) if len(t)>1 and t[1].isdigit() else 16
            cc=c if cc in (16,24) else cc
            if t[0]=='1' and len(t)>=15:
                v=list(map(float,t[2:14])); m=np.array([[v[3],v[4],v[5]],[v[6],v[7],v[8]],[v[9],v[10],v[11]]])
                walk(' '.join(t[14:]),M@m,M@np.array(v[:3])+P,cc,d+1)
            elif t[0] in '34' and len(t)>=2+3*int(t[0]):
                n=int(t[0]); c3=np.array(list(map(float,t[2:2+3*n]))).reshape(n,3)@M.T+P
                out.append((cc,c3[[0,1,2]]))
                if n==4: out.append((cc,c3[[0,2,3]]))
    walk(name,np.eye(3),np.zeros(3),-1,0)
    return out
VIEWS={'end+':(0,180),'end-':(0,0),'under':(-90,0),'iso':(35,-50),'front':(0,0),'rear':(0,180),'top':(90,0),'side':(0,90),'left':(0,-90),'iso2':(30,-130),'low':(-20,-40)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('out')
    ap.add_argument('--view',default='iso'); ap.add_argument('--highlight',default='')
    ap.add_argument('--xray',action='store_true'); ap.add_argument('--clip',default='',help='zmin,zmax world Z clip')
    a=ap.parse_args()
    models,order=parse_model(a.model); parts=flatten_model(models,order,a.model)
    hl=[h for h in a.highlight.split(',') if h]
    polys=[];cols=[]
    for pt in parts:
        base=pt['ref'].replace('.dat','')
        if a.clip:
            z0,z1=map(float,a.clip.split(','))
            if not (z0<=pt['P'][2]<=z1): continue
        fx=np.zeros(3) if os.environ['LDGEOM']=='studio' else STUDIO_FIX.get(pt['ref'],np.zeros(3))
        for c,v in tris(pt['ref']):
            c=pt['col'] if c==-1 else c
            rgb=COL.get(c,(0.6,0.6,0.6))
            if hl:
                rgb=(1,0.1,0.1) if any(base.startswith(h) for h in hl) else tuple(0.75+0.25*x for x in rgb)
            w=(v+fx)@pt['M'].T+pt['P']
            polys.append(w); cols.append(rgb)
    if not polys: print('nothing'); return
    V=np.array(polys)  # n,3,3 ; LDraw: -Y up. convert to x, z(depth), -y(up)
    W=np.stack([V[...,0],V[...,2],-V[...,1]],-1)
    el,az=VIEWS.get(a.view,VIEWS['iso']); el,az=np.radians(el),np.radians(az)
    # camera basis
    fwd=np.array([np.cos(el)*np.sin(az),-np.cos(el)*np.cos(az),np.sin(el)])  # toward viewer
    right=np.array([np.cos(az),np.sin(az),0.]); up=np.cross(fwd,right)
    X=W@right; Y=W@up; D=W@fwd
    n=np.cross(W[:,1]-W[:,0],W[:,2]-W[:,0]); nn=np.linalg.norm(n,axis=1)+1e-9; n/=nn[:,None]
    light=np.array([0.3,-0.5,0.8]); light/=np.linalg.norm(light)
    shade=0.55+0.45*np.abs(n@light)
    C=np.clip(np.array(cols)*shade[:,None],0,1)
    order_=np.argsort(D.mean(1))
    fig=plt.figure(figsize=(12,9),dpi=110); ax=fig.add_axes([0,0,1,1])
    pc=PolyCollection(np.stack([X,Y],-1)[order_],facecolors=C[order_],edgecolors='none',alpha=0.35 if a.xray else 1.0)
    ax.add_collection(pc); ax.set_aspect('equal'); ax.autoscale(); ax.axis('off')
    ax.set_title(f"{os.path.basename(a.model)}  view={a.view}",fontsize=10)
    fig.savefig(a.out); print('wrote',a.out,len(polys),'polys')
if __name__=="__main__": main()
