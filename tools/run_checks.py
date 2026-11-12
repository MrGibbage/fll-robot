#!/usr/bin/env python3
"""Run every check on a model and print a short summary (full output with -v)."""
import sys, os, subprocess
here=os.path.dirname(os.path.abspath(__file__)); py=sys.executable
if len(sys.argv)<2: sys.exit('usage: run_checks.py MODEL.ldr [-v]')
model=sys.argv[1]; verbose='-v' in sys.argv
CHECKS=[('connections / collisions / tires','ldcheck.py',[]),('brick bond (seams)','ldseam.py',[]),
        ('empty wall holes','ldholes.py',[]),('pin anchoring (>=2 spread)','ldanchor.py',[]),
        ('pins sticking out','ldpinsout.py',['-I']),('mirror symmetry','ldsym.py',[]),
        ('hub charge port + side ports','ldclear.py',['-I']),('parts owned','ldbom.py',['-I'])]
for title,tool,flags in CHECKS:
    r=subprocess.run([py,*flags,os.path.join(here,tool),model],capture_output=True,text=True,cwd=here)
    out=(r.stdout+r.stderr).strip()
    print(f"\n=== {title}  [{tool}]")
    if verbose or r.returncode: print(out); continue
    keep=[l for l in out.splitlines() if l and not l.startswith('  ') or any(k in l for k in ('VIOLATION','FLOATING','sticks','!!','above','below','shared seams','nearest'))]
    print('\n'.join(keep[:25]) + ('\n  …(-v for all)' if len(keep)>25 else ''))
