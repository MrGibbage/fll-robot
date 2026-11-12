#!/usr/bin/env python3
"""Robot coordinate language (studs, robot-relative):
  side:  C = centerline, R1..Rn = studs to the robot's RIGHT, L1..Ln = to its LEFT (as if driving it)
  row:   F1 = front wall row, F2 = one stud behind it, ...
  level: lvl1 = bottom wall layer, lvl2 ... upward. A pin spanning two levels shows as lvl1.5
The frame (centerline, front row, bottom layer) comes from frame.detect(); tools call set_frame() first.
usage: ldcoord.py MODEL x y z   |   ldcoord.py MODEL R3 F1 1"""
import sys, numpy as np
FRAME = None
def set_frame(fr):
    global FRAME; FRAME = fr
def _f():
    if FRAME is None: raise RuntimeError('call ldcoord.set_frame(frame.detect(parts)) first')
    return FRAME
def name(P):
    fr=_f(); x,y,z = P
    s = (x-fr['CX'])/20.0
    side = 'C' if abs(s)<0.25 else (f"R{s:g}" if s>0 else f"L{-s:g}")
    row = abs(fr['FZ']-z)/20.0+1; lvl=(fr['Y1']-y)/20.0+1
    g=lambda v: f"{v:g}" if abs(v-round(v))>0.01 else f"{int(round(v))}"
    return f"{side} F{g(row)} lvl{g(lvl)}"
def ldraw(side,row,lvl):
    fr=_f(); s = 0 if side=='C' else (float(side[1:]) * (1 if side[0]=='R' else -1))
    sgn = 1 if fr['FZ']>=fr['RZ'] else -1
    return np.array([fr['CX']+20*s, fr['Y1']-20*(lvl-1), fr['FZ']-sgn*20*(row-1)])
if __name__=='__main__':
    import os; sys.path.insert(0,os.path.dirname(__file__))
    from ldcheck import parse_model, flatten_model
    from frame import detect
    m,o=parse_model(sys.argv[1]); set_frame(detect(flatten_model(m,o,sys.argv[1])))
    a=sys.argv[2:]
    print('frame:',FRAME)
    if len(a)==3 and a[0][0] in 'CLR': print(ldraw(a[0],float(a[1].lstrip('F')),float(a[2].lstrip('lvl'))))
    elif len(a)==3: print(name(np.array(list(map(float,a)))))
