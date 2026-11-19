#!/usr/bin/env python3
"""Advisory audit of alternating-hole beams' actual directional usage.
Vertical pin occupancy is not by itself a justification for a rare beam. Report
which distinct side holes are needed and their span; never impose a stock quota.
"""
import sys
import numpy as np
from ldcheck import parse_model,flatten_model,merged_bores,connection_records,geom_vertices
from frame import detect
from ldcoord import set_frame,name
RARE={'2391.dat','6612.dat','73507.dat','71710.dat'}
def audit(parts):
    records=connection_records(parts);rows=[]
    for p in parts:
        if p['ref'] not in RARE:continue
        v=np.array(geom_vertices(p['ref']));long=p['M']@np.eye(3)[int(np.argmax(np.ptp(v,axis=0)))]
        vertical=set();horizontal=set()
        for q,a,lo,hi in merged_bores(p['ref']):
            Q=p['M']@q+p['P'];A=p['M']@a
            for r in records:
                if p['id'] not in r['hits']:continue
                if abs(A@r['axis'])<.98:continue
                d=r['center']-Q
                if np.linalg.norm(d-(d@A)*A)>2:continue
                position=round(float((Q-p['P'])@long),1)
                (vertical if abs(A[1])>.9 else horizontal).add(position);break
        span=(max(horizontal)-min(horizontal))/20 if horizontal else 0
        review=len(horizontal)<=1 or not vertical
        rows.append(dict(part=p,vertical=len(vertical),horizontal=len(horizontal),span=span,review=review))
    return rows
if __name__=='__main__':
    f=sys.argv[1];m,o=parse_model(f);parts=flatten_model(m,o,f);set_frame(detect(parts));rows=audit(parts)
    for r in rows:
        p=r['part'];flag='REVIEW' if r['review'] else 'AUDIT'
        print(f"{flag}: {p['ref']} at {name(p['P'])}: {r['vertical']} vertical / {r['horizontal']} sideways holes used; sideways span {r['span']:g} studs")
    print(f'{len(rows)} alternating-hole beams; qualitative review, no hard quantity limit')
