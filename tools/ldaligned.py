#!/usr/bin/env python3
"""Find unfilled, compatible holes in adjacent mating parts.
Checks pin/pin and pin/axle joints with nearly abutting faces and adequate depth.
Occupied holes, intentional pin breaks, rotating parts and distant coaxial holes
are not invitations to add another pin. Named exceptions require a model comment:
0 !FLL CONNECTION_EXCEPTION x y z explanation (at the proposed joint center).
This is a local mating-hole audit, not a general assembly or insertion-path solver.
"""
import sys
from pathlib import Path
import numpy as np
from ldcheck import parse_model,flatten_model,typed_bores,STUDIO_FIX,connection_records,SHAFTS,HOLED_SHAFTS
from frame import detect
from ldcoord import set_frame,name
ROTATING={'4185.dat','4185a.dat','44771.dat','41897.dat','15038p01.dat','41896.dat','39367pb01.dat',
          '32270.dat','32269.dat','3647.dat','3648.dat','94925.dat'}

def opportunities(parts):
    records=connection_records(parts);holes=[]
    for p in parts:
        if p['ref'] in ROTATING or p['ref'].replace('.dat','') in SHAFTS-HOLED_SHAFTS:continue
        for q,a,lo,hi,kind in typed_bores(p['ref']):
            if kind not in ('pin','axle') or not 17<=hi-lo<=22:continue
            center=p['M']@(q+a*((lo+hi)/2)+STUDIO_FIX.get(p['ref'],np.zeros(3)))+p['P']
            axis=p['M']@a;axis/=np.linalg.norm(axis)
            if axis[np.argmax(np.abs(axis))]<0:axis=-axis
            half=(hi-lo)/2;occupied=False
            for r in records:
                if p['id'] not in r['hits'] and p['id']!=r['owner']:continue
                if abs(r['axis']@axis)<.98:continue
                d=r['center']-center
                if np.linalg.norm(d-(d@axis)*axis)>2:continue
                sg=np.sign(r['axis']@axis);s=d@axis;l,h=sorted((s+sg*r['lo'],s+sg*r['hi']))
                if min(half,h)-max(-half,l)>3:occupied=True;break
            holes.append(dict(part=p,center=center,axis=axis,half=half,kind=kind,occupied=occupied))
    candidates=[]
    for i,a in enumerate(holes):
        if a['occupied']:continue
        for b in holes[i+1:]:
            if b['occupied'] or a['part']['id']==b['part']['id']:continue
            if a['kind']==b['kind']=='axle':continue # requires a deliberate axle/retention design
            if abs(a['axis']@b['axis'])<.98:continue
            delta=b['center']-a['center'];along=delta@a['axis']
            if np.linalg.norm(delta-along*a['axis'])>1:continue
            gap=abs(along)-a['half']-b['half']
            if abs(gap)>2:continue
            sign=np.sign(along)
            joint=a['center']+a['axis']*sign*(a['half']+gap/2)
            candidates.append(dict(a=a['part'],b=b['part'],point=joint,axis=a['axis'],
                connector='2780.dat' if a['kind']==b['kind']=='pin' else '43093.dat'))
    return candidates

def main(path):
    m,o=parse_model(path);parts=flatten_model(m,o,path);set_frame(detect(parts));exceptions=[]
    for line in Path(path).read_text().splitlines():
        t=line.split()
        if t[:3]==['0','!FLL','CONNECTION_EXCEPTION']:
            if len(t)<7:raise ValueError('Connection exceptions require x y z and a reason')
            exceptions.append((np.array(list(map(float,t[3:6]))),' '.join(t[6:])))
    bad=[]
    for item in opportunities(parts):
        exception=next((reason for point,reason in exceptions if np.linalg.norm(point-item['point'])<1),None)
        if exception:print(f"EXCEPTION at {name(item['point'])}: {exception}")
        else:
            bad.append(item)
            print(f"MISSING CONNECTION: {item['a']['ref']} + {item['b']['ref']} at {name(item['point'])}; consider {item['connector']}")
    print(f'{len(bad)} unfilled adjacent compatible-hole connections')
    return int(bool(bad))
if __name__=='__main__':sys.exit(main(sys.argv[1]))
