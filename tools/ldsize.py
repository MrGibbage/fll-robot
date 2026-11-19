#!/usr/bin/env python3
"""Check the modeled envelope against an explicit 0 !FLL ENVELOPE W L H (studs).
Uses full geometry, expanded submodels and robot coordinates. No limits are inferred.
"""
import os, sys
from pathlib import Path
os.environ['LDGEOM'] = 'studio'
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from ldcheck import parse_model, flatten_model, geom_vertices
from ldflat import find
from frame import detect
from ldcoord import set_frame, name

def check(path):
    limits = None
    for line in Path(path).read_text().splitlines():
        t = line.split()
        if t[:3] == ['0', '!FLL', 'ENVELOPE']:
            limits = np.array(list(map(float, t[3:6]))) * 20
    if limits is None:
        print('No explicit envelope supplied; size check not applicable.')
        return 0
    m, o = parse_model(path)
    parts = flatten_model(m, o, path)
    set_frame(detect(parts))
    vertices = []
    for p in parts:
        v = np.array(geom_vertices(p['ref']))
        if not find(p['ref']) or not len(v):
            print('ERROR: missing geometry:', p['ref'], name(p['P']))
            return 1
        vertices.append(v @ p['M'].T + p['P'])
    v = np.concatenate(vertices)
    lo, hi = v.min(0), v.max(0)
    size = (hi - lo)[[0, 2, 1]]
    print('Envelope width × length × height: ' + ' × '.join(f'{x/20:.2f}' for x in size) + ' studs')
    bad = size > limits + 0.1
    print('VIOLATION: exceeds declared envelope' if bad.any() else 'Envelope OK')
    return int(bad.any())

if __name__ == '__main__':
    sys.exit(check(sys.argv[1]))
