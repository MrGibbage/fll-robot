#!/usr/bin/env python3
"""Technic connection checker for Stud.io LDraw exports.
For every pin/axle (shaft) find the holes it passes through; build a part-connectivity
graph; report floating parts/assemblies, pins that grab only one part, and per-part links."""
import sys, os, re, functools, argparse
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from ldflat import find, load

HOLE = re.compile(r'^(beamhol|connhol|npeghol|peghole|axlehol\d|axl\dhol|axlehole|axleho\d|connhole)', re.I)
# shaft parts: pins/axles. axis = longest bbox dim of the part geometry
SHAFTS = {'2780','6558','43093','11214','4519','3706','3705','60485','32062','4274','3673','87082',
          '15100','32054','3707','3708','3737','23948','32073','6587','99008','44294','24316','42003'}
# NOTE 42003 is a cross block - not a shaft; removed below
SHAFTS.discard('42003')
HOLED_SHAFTS={'15100','87082'}
# Stud.io's geometry differs from the official LDraw part for some IDs: local-coordinate shift
STUDIO_FIX={'37308c01.dat':np.array([0.,0.,49.])}

def geom_vertices(name, M=np.eye(3), P=np.zeros(3), depth=0, out=None):
    if out is None: out=[]
    p=find(name)
    if not p or depth>15: return out
    for line in open(p,encoding='utf-8',errors='replace'):
        t=line.split()
        if not t: continue
        if t[0]=='1' and len(t)>=15:
            v=list(map(float,t[2:14]))
            m=np.array([[v[3],v[4],v[5]],[v[6],v[7],v[8]],[v[9],v[10],v[11]]])
            geom_vertices(' '.join(t[14:]), M@m, M@np.array(v[:3])+P, depth+1, out)
        elif t[0] in '2345' and len(t)>=8:
            n=int(t[0]) if t[0]!='5' else 2
            c=list(map(float,t[2:2+3*n]))
            for i in range(n): out.append(M@np.array(c[3*i:3*i+3])+P)
    return out

@functools.lru_cache(None)
def part_bores(name):
    """holes in part-local coords: list of (point_on_axis, unit_axis, lo, hi)"""
    res=[]
    def walk(nm,M,P,d):
        kids=load(nm)
        if kids is None or d>12: return
        for sub,m,p in kids:
            M2=M@m; P2=M@p+P
            b=os.path.basename(sub.replace('\\','/')).lower()
            if HOLE.match(b):
                ax=M2@np.array([0.,1.,0.]); ax=ax/np.linalg.norm(ax)
                vs=geom_vertices(sub,M2,P2)
                if vs:
                    pr=[float(np.dot(v-P2,ax)) for v in vs]; lo,hi=min(pr),max(pr)
                else: lo,hi=0.0,float(np.linalg.norm(M2@np.array([0,1.,0])))
                res.append((P2,ax,lo,hi))
            else:
                walk(sub,M2,P2,d+1)
    walk(name,np.eye(3),np.zeros(3),0)
    return res


@functools.lru_cache(None)
def merged_bores(name, gap=21.0):
    """merge collinear hole primitives of one part into continuous through-holes"""
    lines=[]  # [point, axis, [intervals]]
    for q,ax,lo,hi in part_bores(name):
        for L in lines:
            P0,A,iv=L
            if abs(np.dot(A,ax))>0.98:
                d=q-P0; perp=d-np.dot(d,A)*A
                if np.linalg.norm(perp)<1.0:
                    s=float(np.dot(d,A)); sg=np.sign(np.dot(A,ax))
                    iv.append(tuple(sorted((s+sg*lo,s+sg*hi)))); break
        else:
            lines.append([q,ax,[(lo,hi)]])
    out=[]
    for P0,A,iv in lines:
        iv.sort(); cur=list(iv[0])
        for a,b in iv[1:]:
            if a<=cur[1]+gap: cur[1]=max(cur[1],b)
            else: out.append((P0,A,cur[0],cur[1])); cur=[a,b]
        out.append((P0,A,cur[0],cur[1]))
    return tuple(out)

@functools.lru_cache(None)
def shaft_def(name):
    vs=np.array(geom_vertices(name))
    lo,hi=vs.min(0),vs.max(0); ext=hi-lo; i=int(np.argmax(ext))
    ax=np.zeros(3); ax[i]=1
    c=(lo+hi)/2; return c,ax,lo[i]-c[i],hi[i]-c[i]

def parse_model(path):
    models={}; cur=None; order=[]
    for line in open(path,encoding='utf-8',errors='replace'):
        t=line.split()
        if len(t)>=3 and t[0]=='0' and t[1]=='FILE':
            cur=' '.join(t[2:]); models[cur]=[]; order.append(cur); continue
        if len(t)>=15 and t[0]=='1' and cur is not None:
            v=list(map(float,t[2:14]))
            models[cur].append((int(t[1]),np.array([[v[3],v[4],v[5]],[v[6],v[7],v[8]],[v[9],v[10],v[11]]]),np.array(v[:3]),' '.join(t[14:])))
    return models,order

def resolve_sub(models,ref):
    r=ref.lower().replace('.ldr','')
    for k in models:
        if k.lower().replace('.ldr','')==r: return k
    # stud.io refs like 'motor' for FILE 'Right Medium Motor' - ambiguous suffix match
    return None

def flatten_model(models,order,path):
    parts=[]
    def walk(mname,M,P,trail,lineno_base):
        for idx,(col,m,p,ref) in enumerate(models[mname]):
            M2=M@m; P2=M@p+P
            sub=resolve_sub(models,ref)
            if sub: walk(sub,M2,P2,trail+[f'{ref}#{idx+1}'],0)
            else: parts.append(dict(id=len(parts),ref=ref,col=col,M=M2,P=P2,where='/'.join(trail+[f'{mname}#{idx+1}'])))
    walk(order[0],np.eye(3),np.zeros(3),[],0)
    return parts

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--verbose','-v',action='store_true')
    ap.add_argument('--part',help='show links for parts matching this ref')
    a=ap.parse_args()
    models,order=parse_model(a.model)
    parts=flatten_model(models,order,a.model)
    missing=sorted({p['ref'] for p in parts if not find(p['ref'])})
    bores=[]  # world bores
    for p in parts:
        b0=p['ref'].replace('.dat','')
        if b0 in SHAFTS and b0 not in HOLED_SHAFTS: continue
        if not find(p['ref']): continue
        fx=STUDIO_FIX.get(p['ref'],np.zeros(3))
        for (q,ax,lo,hi) in merged_bores(p['ref']):
            bores.append((p['id'],p['M']@(q+fx)+p['P'],p['M']@ax,lo,hi))
    B_pts=np.array([b[1] for b in bores]) if bores else np.zeros((0,3))
    B_ax=np.array([b[2]/np.linalg.norm(b[2]) for b in bores]) if bores else np.zeros((0,3))
    links=defaultdict(set); shaft_report=[]
    for p in parts:
        base=p['ref'].replace('.dat','')
        if base not in SHAFTS or not find(p['ref']): continue
        c,ax,lo,hi=shaft_def(p['ref'])
        wc=p['M']@c+p['P']; wa=p['M']@ax; wa=wa/np.linalg.norm(wa)
        par=np.abs(B_ax@wa)>0.98
        d=B_pts-wc; perp=d-np.outer(d@wa,wa); pd=np.linalg.norm(perp,axis=1)
        hit=set()
        for i in np.where(par&(pd<2.5))[0]:
            pid,q,bax,blo,bhi=bores[i]
            bax=bax/np.linalg.norm(bax); s=float(np.dot(q-wc,wa)); sgn=np.sign(np.dot(bax,wa))
            b0,b1=sorted((s+sgn*blo,s+sgn*bhi))
            ov=min(hi,b1)-max(lo,b0)
            if ov>3 and pid!=p['id']: hit.add(pid)
        for h in hit: links[p['id']].add(h); links[h].add(p['id'])
        shaft_report.append((p,hit))
    # components
    seen={}; comps=[]
    for p in parts:
        if p['id'] in seen: continue
        stack=[p['id']]; comp=[]
        while stack:
            x=stack.pop()
            if x in seen: continue
            seen[x]=len(comps); comp.append(x); stack.extend(links[x])
        comps.append(comp)
    comps.sort(key=len,reverse=True)
    print(f"model: {a.model}\nparts: {len(parts)}  shafts: {len(shaft_report)}  bores: {len(bores)}")
    if missing: print("parts not in LDraw library (unchecked):",', '.join(missing))
    print(f"\nconnected assemblies: {len(comps)}  (main = {len(comps[0])} parts)")
    for c in comps[1:]:
        print("  FLOATING:", ', '.join(f"{parts[i]['ref']}@({parts[i]['P'][0]:.0f},{parts[i]['P'][1]:.0f},{parts[i]['P'][2]:.0f})" for i in c))
    print("\npins/axles engaging <2 parts:")
    for p,hit in shaft_report:
        if len(hit)<2:
            print(f"  {p['ref']:10s} @({p['P'][0]:.0f},{p['P'][1]:.0f},{p['P'][2]:.0f}) -> {[parts[h]['ref'] for h in hit]}  [{p['where']}]")
    # --- two shafts in the same hole ---
    print("\nshafts sharing a hole (pin/axle overlap):")
    sh=[]
    for p_,hit in shaft_report:
        c,ax,lo,hi=shaft_def(p_['ref']); wc=p_['M']@c+p_['P']; wa=p_['M']@ax; wa/=np.linalg.norm(wa)
        sh.append((p_,wc,wa,lo,hi))
    nso=0
    for i in range(len(sh)):
        for j in range(i+1,len(sh)):
            p1,c1,a1,l1,h1=sh[i]; p2,c2,a2,l2,h2=sh[j]
            if abs(a1@a2)<0.98: continue
            d=c2-c1; perp=d-(d@a1)*a1
            if np.linalg.norm(perp)>2: continue
            s=d@a1; ov=min(h1,s+max(l2*np.sign(a1@a2),h2*np.sign(a1@a2)))-max(l1,s+min(l2*np.sign(a1@a2),h2*np.sign(a1@a2)))
            if ov>2:
                print(f"  {p1['ref']}@({p1['P'][0]:.0f},{p1['P'][1]:.0f},{p1['P'][2]:.0f}) x {p2['ref']}@({p2['P'][0]:.0f},{p2['P'][1]:.0f},{p2['P'][2]:.0f}) overlap {ov:.0f}"); nso+=1
    print("  none" if nso==0 else f"  {nso} total")
    # --- collision heuristics ---
    print("\ncollisions (two solid parts sharing a hole cell, or a hole inside a motor/sensor body):")
    solid=[p for p in parts if find(p['ref']) and p['ref'].replace('.dat','') not in SHAFTS]
    cells=[]
    for p in solid:
        fx=STUDIO_FIX.get(p['ref'],np.zeros(3))
        for q,ax,lo,hi in merged_bores(p['ref']):
            A=p['M']@ax; A=A/np.linalg.norm(A); Q=p['M']@(q+fx)+p['P']
            for t in np.arange(lo+10,hi-9,20) if hi-lo>=20 else [ (lo+hi)/2 ]:
                cells.append((p['id'],Q+A*t))
    ncol=0
    for i in range(len(cells)):
        for j in range(i+1,len(cells)):
            if cells[i][0]!=cells[j][0] and np.linalg.norm(cells[i][1]-cells[j][1])<6:
                a_,b_=parts[cells[i][0]],parts[cells[j][0]]
                print(f"  {a_['ref']}@({a_['P'][0]:.0f},{a_['P'][1]:.0f},{a_['P'][2]:.0f}) x {b_['ref']}@({b_['P'][0]:.0f},{b_['P'][1]:.0f},{b_['P'][2]:.0f}) at {cells[i][1].round()}"); ncol+=1
    # medium motor: rectangular body (local) + round output hub cylinder r=29 along local Y
    for p in solid:
        if p['ref']!='54696.dat': continue
        lo_,hi_=np.array([-30,-36,-29])+4,np.array([30,30,150])-4
        for pid,c in cells:
            if pid==p['id']: continue
            l=np.linalg.inv(p['M'])@(c-p['P'])
            inbody=np.all(l>lo_) and np.all(l<hi_)
            inhub=(l[0]**2+l[2]**2)<25**2 and -46<l[1]<26
            if inbody or inhub:
                print(f"  {parts[pid]['ref']}@({parts[pid]['P'][0]:.0f},{parts[pid]['P'][1]:.0f},{parts[pid]['P'][2]:.0f}) hole inside {p['ref']}@({p['P'][0]:.0f},{p['P'][1]:.0f},{p['P'][2]:.0f}) at {c.round()}"); ncol+=1
    # tires/wheels: solid cylinders (Stud.io geometry) - any other part's geometry inside = collision
    import os as _os
    TIRES=('44771','41897','39367pb01','56908')   # tyres (rims excluded: their centre legitimately holds hubs/bushes)
    prev=_os.environ.get('LDGEOM'); _os.environ['LDGEOM']='studio'
    import ldflat; ldflat.find.cache_clear(); ldflat.GEOM_MODE='studio'
    wheel_ids=set()
    for p in parts:
        if not p['ref'].startswith(TIRES): continue
        v=np.array(geom_vertices(p['ref']))
        if not len(v): continue
        ext=v.max(0)-v.min(0); ax=int(np.argmin(ext)); c=(v.max(0)+v.min(0))/2
        r=np.delete(ext,ax).max()/2-3; hw=ext[ax]/2-2
        A=np.zeros(3); A[ax]=1; wc=p['M']@c+p['P']; wa=p['M']@A
        hitparts={}
        for q in parts:
            if q is p or q['ref'].startswith(TIRES+('15038','41896','56904','88517','39367')) or q['ref'].replace('.dat','') in SHAFTS: continue
            if np.linalg.norm(q['P']-wc)>r+250: continue
            qv=np.array(geom_vertices(q['ref']))
            if not len(qv): continue
            W=qv@q['M'].T+q['P']-wc; t=W@wa; rad=np.linalg.norm(W-np.outer(t,wa),axis=1)
            n=int(((np.abs(t)<hw)&(rad<r)&(rad>0.55*r)).sum())   # outer annulus = rubber + rim edge
            if n>3: hitparts[q['id']]=n
        for qid,n in hitparts.items():
            q=parts[qid]; print(f"  {q['ref']}@({q['P'][0]:.0f},{q['P'][1]:.0f},{q['P'][2]:.0f}) inside {p['ref']}@({p['P'][0]:.0f},{p['P'][1]:.0f},{p['P'][2]:.0f}) [{n} verts]"); ncol+=1
    ldflat.GEOM_MODE=prev or 'official'; ldflat.find.cache_clear()
    print("  none" if ncol==0 else f"  {ncol} total")
    if a.part:
        print(f"\nlinks for {a.part}:")
        for p in parts:
            if p['ref'].startswith(a.part):
                nb=[]
                for s in links[p['id']]:
                    others=[parts[o]['ref'] for o in links[s] if o!=p['id']]
                    nb.append(f"{parts[s]['ref']}@({parts[s]['P'][0]:.0f},{parts[s]['P'][1]:.0f},{parts[s]['P'][2]:.0f})->{others}")
                print(f"  {p['ref']} @({p['P'][0]:.0f},{p['P'][1]:.0f},{p['P'][2]:.0f}) via {len(nb)} shafts:"); [print('     ',n) for n in nb]
if __name__=="__main__": main()
