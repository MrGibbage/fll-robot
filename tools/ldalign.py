#!/usr/bin/env python3
"""For a part (existing index or hypothetical), list its bores and the bores of other parts that are
collinear & close along the axis -> candidate pin locations. Gap = distance between facing bore ends."""
import sys,os,argparse
import numpy as np
sys.path.insert(0,os.path.dirname(__file__))
from ldflat import find
from ldcheck import parse_model, flatten_model, merged_bores, STUDIO_FIX, SHAFTS, HOLED_SHAFTS
def world_bores(p):
    fx=STUDIO_FIX.get(p['ref'],np.zeros(3)); out=[]
    for q,ax,lo,hi in merged_bores(p['ref']):
        A=p['M']@ax; A=A/np.linalg.norm(A); Q=p['M']@(q+fx)+p['P']
        a,b=Q+A*lo,Q+A*hi; out.append((a,b))
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('model'); ap.add_argument('--idx',type=int)
    ap.add_argument('--add',help='ref,x,y,z,a,b,c,d,e,f,g,h,i'); ap.add_argument('--exclude',default='')
    ap.add_argument('--maxgap',type=float,default=25)
    a=ap.parse_args(); models,order=parse_model(a.model); parts=flatten_model(models,order,a.model)
    excl={int(x) for x in a.exclude.split(',') if x}
    if a.add:
        t=a.add.split(','); v=list(map(float,t[1:]))
        tgt=dict(id=-1,ref=t[0],P=np.array(v[:3]),M=np.array(v[3:]).reshape(3,3))
    else: tgt=parts[a.idx]; excl.add(a.idx)
    others=[p for p in parts if p['id'] not in excl and find(p['ref']) and (p['ref'].replace('.dat','') not in SHAFTS or p['ref'].replace('.dat','') in HOLED_SHAFTS)]
    ob=[(p,a_,b_) for p in others for a_,b_ in world_bores(p)]
    for a1,b1 in world_bores(tgt):
        A=(b1-a1); L=np.linalg.norm(A); A/=L
        hits=[]
        for p,a2,b2 in ob:
            B=b2-a2; B/=np.linalg.norm(B)
            if abs(A@B)<0.98: continue
            d=a2-a1; perp=d-(d@A)*A
            if np.linalg.norm(perp)>2: continue
            s0,s1=sorted((float((a2-a1)@A),float((b2-a1)@A)))
            gap=max(s0-L,-s1)  # >0 separate, <0 overlapping
            if gap<=a.maxgap: hits.append(f"{p['ref']}#{p['id']}[{s0:.0f}..{s1:.0f}] gap={gap:.0f}")
        mid=(a1+b1)/2
        print(f"bore mid=({mid[0]:.0f},{mid[1]:.0f},{mid[2]:.0f}) axis=({A[0]:.0f},{A[1]:.0f},{A[2]:.0f}) len={L:.0f} :: {'; '.join(hits) if hits else '-'}")
if __name__=="__main__": main()
