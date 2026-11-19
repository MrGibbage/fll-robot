#!/usr/bin/env python3
"""Catch SPIKE electronics aliases that do not match the team's working Stud.io exports.
A DAT existing in LDraw (or even Stud.io's raw library) does not establish palette/import support.
This check covers these known electronics families, not every possible Stud.io part.
"""
import sys
from ldcheck import parse_model, flatten_model
from frame import detect
from ldcoord import set_frame, name
SUPPORTED={
    '45601.dat':'bb1142c01.dat',
    '45601c01.dat':'bb1142c01.dat',
    '45610.dat':'55422c01.dat',
    '37308.dat':'37308c01.dat',
}

def check(path):
    m,o=parse_model(path);parts=flatten_model(m,o,path)
    set_frame(detect(parts))
    bad=0
    for p in parts:
        expected=SUPPORTED.get(p['ref'].lower())
        if expected:
            print(f"VIOLATION: {p['ref']} at {name(p['P'])}: use the working Stud.io export ID {expected}")
            bad+=1
    if not bad:print('Stud.io SPIKE electronics IDs match the working sample export convention.')
    return int(bool(bad))

if __name__=='__main__':sys.exit(check(sys.argv[1]))
