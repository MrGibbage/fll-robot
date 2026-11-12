"""Detect a robot's wall frame from the model so tools don't hard-code coordinates.
Walls = the outermost columns/rows that carry many vertical holes. Override with env FLL_FRAME="LX,RX,FZ,RZ,Y1".
Convention: LDraw -Y is up, +Z is the robot's front (set FLL_FRONT=-z if your model faces -Z), +X robot right."""
import os, numpy as np, collections
from ldflat import find
from ldcheck import merged_bores, SHAFTS
def detect(parts):
    env=os.environ.get('FLL_FRAME')
    if env:
        LX,RX,FZ,RZ,Y1=map(float,env.split(','))
    else:
        cells=set()
        for p in parts:
            if not find(p['ref']) or p['ref'].replace('.dat','') in SHAFTS: continue
            for q,ax,lo,hi in merged_bores(p['ref']):
                A=p['M']@ax; A=A/np.linalg.norm(A); Q=p['M']@q+p['P']
                if abs(A[1])<0.9 or hi-lo<15: continue
                for t in np.arange(lo+10,hi-9,20):
                    cells.add(tuple(np.round((Q+A*t)/10).astype(int)*10))
        if not cells: raise SystemExit('frame: no vertical holes found; set FLL_FRAME')
        C=np.array(sorted(cells))
        def ends(col):
            cnt=collections.Counter(C[:,col]); thr=max(4,0.25*max(cnt.values()))
            keys=sorted(k for k,v in cnt.items() if v>=thr); return keys[0],keys[-1]
        LX,RX=ends(0); RZ,FZ=ends(2)
        if os.environ.get('FLL_FRONT','+z').lower()=='-z': FZ,RZ=RZ,FZ
        wall=C[(C[:,0]==LX)|(C[:,0]==RX)]; Y1=float(wall[:,1].max())
    LX,RX,FZ,RZ,Y1=map(float,(LX,RX,FZ,RZ,Y1))
    return dict(LX=LX,RX=RX,FZ=FZ,RZ=RZ,Y1=Y1,CX=(LX+RX)/2)
