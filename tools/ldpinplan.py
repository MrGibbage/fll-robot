"""Plan friction pins through free compatible round-hole runs.
Molded pins and explicit axle-pins reserve their receiving holes. Negative relief
primitives and axle holes are never treated as round holes for friction pins.
"""
import numpy as np
from ldcheck import typed_bores,shaft_def,SHAFTS,HOLED_SHAFTS,STUDIO_FIX,builtin_pin_segments
from ldaligned import ROTATING
VP=np.array([[0,0,1],[1,0,0],[0,1,0]])
ZP=np.array([[0,0,1],[0,1,0],[-1,0,0]])
def pin_plan(parts,axes=(0,1,2)):
    cells={axis:set() for axis in axes};segments=[]
    for p in parts:
        base=p['ref'].replace('.dat','')
        if base in SHAFTS:
            c,a,lo,hi=shaft_def(p['ref']);segments.append((p['M']@c+p['P'],p['M']@a,lo,hi))
        segments+=builtin_pin_segments(p)
        if p['ref'] in ROTATING or base in SHAFTS-HOLED_SHAFTS:continue
        for q,a,lo,hi,kind in typed_bores(p['ref']):
            if kind!='pin' or not 17<=hi-lo<=22:continue
            A=p['M']@a;axis=int(np.argmax(np.abs(A)))
            if axis not in cells or abs(A[axis])<.99:continue
            c=p['M']@(q+a*((lo+hi)/2)+STUDIO_FIX.get(p['ref'],np.zeros(3)))+p['P']
            grid=np.round(c/10)*10
            if np.linalg.norm(c-grid)<2.5:cells[axis].add(tuple(map(int,grid)))
    planned=[]
    for axis,axis_cells in cells.items():
        other=[i for i in range(3) if i!=axis];free={}
        for cell in axis_cells:
            C=np.array(cell);occupied=False
            for q,a,lo,hi in segments:
                if abs(a[axis])<.99:continue
                d=C-q;t=d@a
                if np.linalg.norm(d-t*a)<2 and lo+3<t<hi-3:occupied=True;break
            if not occupied:free.setdefault(tuple(cell[i] for i in other),set()).add(cell[axis])
        for key,positions in sorted(free.items()):
            runs=[]
            for value in sorted(positions):
                if runs and value==runs[-1][-1]+20:runs[-1].append(value)
                else:runs.append([value])
            for run in runs:
                n=len(run);parity=sum(abs(v)//20 for v in key)%2
                patterns={2:[2],3:[3],4:[2,2],5:([3,2] if parity else [2,3]),
                          6:([3,3] if parity else [2,2,2]),7:([3,2,2] if parity else [2,2,3])}
                if n==1:continue
                if n not in patterns:raise ValueError(('unplanned hole run',axis,key,run))
                k=0
                for size in patterns[n]:
                    point=np.zeros(3);point[other]=key;point[axis]=np.mean(run[k:k+size])
                    planned.append(dict(ref='2780.dat' if size==2 else '6558.dat',col=0 if size==2 else 1,
                        P=point,M=[np.eye(3),VP,ZP][axis].copy()))
                    k+=size
    return planned

def vertical_pin_plan(parts):return pin_plan(parts,axes=(1,))
