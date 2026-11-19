#!/usr/bin/env python3
"""Measure complete wall rows below drive axles and clearance above the contact plane.
Constraints are explicit metadata: WALL_ROWS_BELOW_AXLE N, MIN_GROUND_CLEARANCE mm.
Ground is inferred from parallel across-robot drive wheels and rear 4185 rollers;
a pitched contact plane is used, rather than the bottom of an unpitched render.
"""
import os
os.environ['LDGEOM']='studio'
import sys
from pathlib import Path
import numpy as np
from ldcheck import parse_model,flatten_model,merged_bores,geom_vertices,SHAFTS,STUDIO_FIX
from frame import detect
from ldcoord import set_frame,name
DRIVE={'44771.dat','41897.dat','39367pb01.dat'}
ROLLERS={'4185.dat','4185a.dat'}
ROTATING=DRIVE|ROLLERS|{'15038p01.dat','41896.dat'}

def contact_plane(drive,roller):
    # Each support is (center_y, center_z, radius); the two circles share a tangent.
    yd,zd,rd=drive;yc,zc,rc=roller
    def f(m):return yc-yd-m*(zc-zd)+(rc-rd)*np.sqrt(1+m*m)
    low,high=-.5,.5
    if f(low)*f(high)>0:raise ValueError('Cannot infer a near-level contact plane')
    for _ in range(70):
        middle=(low+high)/2
        if f(low)*f(middle)<=0:high=middle
        else:low=middle
    m=(low+high)/2;b=yd-m*zd+rd*np.sqrt(1+m*m)
    return m,b

def measure(parts):
    fr=detect(parts);set_frame(fr);vertices={};wallparts=set();cells=set();supports={'drive':[],'roller':[]}
    for p in parts:
        v=np.array(geom_vertices(p['ref']))
        if not len(v):raise ValueError('Missing geometry '+p['ref'])
        w=v@p['M'].T+p['P'];vertices[p['id']]=w
        if p['ref'] in DRIVE|ROLLERS:
            ext=v.max(0)-v.min(0);axis=int(np.argmin(ext))
            if abs((p['M']@np.eye(3)[axis])[0])<.99:raise ValueError('Support wheel axle is not across the robot')
            center=p['M']@((v.max(0)+v.min(0))/2)+p['P']
            radius=np.delete(ext,axis).max()/2
            supports['drive' if p['ref'] in DRIVE else 'roller'].append((center[1],center[2],radius))
        if p['ref'].replace('.dat','') in SHAFTS:continue
        for q,a,lo,hi in merged_bores(p['ref']):
            A=p['M']@a;Q=p['M']@(q+STUDIO_FIX.get(p['ref'],np.zeros(3)))+p['P']
            ts=np.arange(lo+10,hi-9,20) if hi-lo>=20-1e-6 else [(lo+hi)/2]
            for t in ts:
                c=np.round((Q+A*t)/20)*20
                if np.linalg.norm(c-(Q+A*t))>3:continue
                x,y,z=map(int,c)
                if (x in (fr['LX'],fr['RX']) and min(fr['FZ'],fr['RZ'])<=z<=max(fr['FZ'],fr['RZ'])) or (z in (fr['FZ'],fr['RZ']) and fr['LX']<=x<=fr['RX']):
                    cells.add((x,y,z));wallparts.add(p['id'])
    if not supports['drive'] or not supports['roller']:raise ValueError('Need drive wheels and rear rollers to infer the contact plane')
    drive=np.mean(supports['drive'],axis=0);roller=np.mean(supports['roller'],axis=0)
    m,b=contact_plane(drive,roller);axle_y=drive[0]
    z0,z1=sorted((int(fr['FZ']),int(fr['RZ'])))
    walls={'left':[(int(fr['LX']),z) for z in range(z0,z1+1,20)],
           'right':[(int(fr['RX']),z) for z in range(z0,z1+1,20)],
           'front':[(x,int(fr['FZ'])) for x in range(int(fr['LX']),int(fr['RX'])+1,20)],
           'rear':[(x,int(fr['RZ'])) for x in range(int(fr['LX']),int(fr['RX'])+1,20)]}
    ys=sorted({c[1] for c in cells if c[1]>axle_y+9.9})
    rows={label:[y for y in ys if all((x,y,z) in cells for x,z in line)] for label,line in walls.items()}
    wall_vertices=np.concatenate([vertices[i] for i in wallparts]);distance=(m*wall_vertices[:,2]+b-wall_vertices[:,1])/np.sqrt(1+m*m)
    minimum=float(distance.min())*.4;wallbottom=float(wall_vertices[:,1].max())
    below=[]
    for p in parts:
        if p['ref'] in ROTATING:continue
        if vertices[p['id']][:,1].max()>wallbottom+.5:below.append(p)
    return dict(rows=rows,pitch=float(np.degrees(np.arctan(m))),minimum_mm=minimum,
                axle_clearance_mm=float((m*drive[1]+b-wallbottom)/np.sqrt(1+m*m)*.4),below=below)

def main(path):
    expected=None;minimum=None
    for line in Path(path).read_text().splitlines():
        t=line.split()
        if t[:3]==['0','!FLL','WALL_ROWS_BELOW_AXLE']:expected=int(t[3])
        if t[:3]==['0','!FLL','MIN_GROUND_CLEARANCE']:minimum=float(t[3])
    m,o=parse_model(path);parts=flatten_model(m,o,path)
    if not (any(p['ref'] in DRIVE for p in parts) and any(p['ref'] in ROLLERS for p in parts)):
        print('Contact-plane check not applicable: supported drive wheels and 4185 rollers are required.')
        return int(expected is not None or minimum is not None)
    r=measure(parts)
    print('Complete wall rows below drive axle: '+', '.join(f'{k}={len(v)}' for k,v in r['rows'].items()))
    print(f"Contact-plane pitch: {abs(r['pitch']):.2f} degrees; clearance at drive axle {r['axle_clearance_mm']:.2f} mm; minimum perimeter clearance {r['minimum_mm']:.2f} mm")
    bad=expected is not None and any(len(v)!=expected for v in r['rows'].values())
    if bad:print(f'VIOLATION: expected {expected} full wall rows below the axle')
    if minimum is not None and r['minimum_mm']<minimum-.05:
        bad=True;print(f'VIOLATION: minimum ground clearance must be {minimum:.2f} mm')
    for p in r['below']:print(f"VIOLATION: {p['ref']} at {name(p['P'])} hangs below the wall bottom")
    return int(bad or bool(r['below']))
if __name__=='__main__':sys.exit(main(sys.argv[1]))
