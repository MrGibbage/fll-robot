#!/usr/bin/env python3
"""Flag flat drive-motor retainers that are short pivot links rather than bracing.
Two parallel pins into two separate supports do not by themselves fix a link.
Accept two pins into the same mate, or a rail spanning front and rear mounting zones.
This is a targeted support-topology check, not a general stiffness/DOF solver.
"""
import os
os.environ['LDGEOM']='studio'
import sys
import numpy as np
from ldcheck import parse_model,flatten_model,geom_vertices,connection_records
from ldcoord import name,set_frame
from frame import detect
BRACES={'43857.dat','32523.dat','32316.dat','32524.dat','40490.dat','32525.dat','41239.dat','32278.dat','32526.dat'}

def risks(parts):
    bounds={}
    for p in parts:
        if p['ref'] not in BRACES|{'54675.dat'}:continue
        v=np.array(geom_vertices(p['ref']))@p['M'].T+p['P'];bounds[p['id']]=(v.min(0),v.max(0))
    records=connection_records(parts);bad=[]
    for p in parts:
        if p['ref'] not in BRACES:continue
        lo,hi=bounds[p['id']]
        motors=[]
        for motor in parts:
            if motor['ref']!='54675.dat':continue
            ml,mh=bounds[motor['id']]
            if abs(hi[1]-ml[1])<2 and ml[0]<=p['P'][0]<=mh[0] and hi[2]>ml[2]-20 and lo[2]<mh[2]+20:motors.append(motor)
        if not motors:continue
        contact=[];mates={}
        for r in records:
            hit=r['hits']|({r['owner']} if r['owner'] is not None else set())
            if p['id'] not in hit or len(hit)<2:continue
            contact.append(r)
            for other in hit-{p['id']}:mates.setdefault(other,set()).add(r['key'])
        if any(len(keys)>=2 for keys in mates.values()):continue
        pts=np.array([r['center'] for r in contact])
        if len(pts)>=2:
            # A continuous rail reaches both mounting regions of the same motor.
            for motor in motors:
                ml,mh=bounds[motor['id']]
                if pts[:,2].min()<=ml[2]+30 and pts[:,2].max()>=mh[2]-30:break
            else:bad.append(p)
        else:bad.append(p)
    return bad

def main(path):
    m,o=parse_model(path);parts=flatten_model(m,o,path);set_frame(detect(parts))
    bad=risks(parts)
    for p in bad:print(f"HINGE RISK: {p['ref']} at {name(p['P'])}: single-pin supports without a front-to-rear rail")
    if not bad:print('Drive motor retainers have a two-pin common support or span front and rear mounts.')
    return int(bool(bad))
if __name__=='__main__':sys.exit(main(sys.argv[1]))
