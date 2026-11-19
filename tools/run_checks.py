#!/usr/bin/env python3
"""Run every check on a model and print a short summary (full output with -v)."""
import sys, os, subprocess
here=os.path.dirname(os.path.abspath(__file__)); py=sys.executable
if len(sys.argv)<2: sys.exit('usage: run_checks.py MODEL.ldr [-v]')
model=os.path.abspath(sys.argv[1]); verbose='-v' in sys.argv
CHECKS=[('Stud.io electronics import IDs','ldstudio.py',[]),('declared size envelope','ldsize.py',[]),('wall rows / ground clearance','ldground.py',[]),('reserved weight pockets','ldfree.py',[]),('connections / collisions / tires','ldcheck.py',[]),('small roller swept clearance','ldwheelclear.py',[]),('brick bond (seams)','ldseam.py',[]),
        ('empty wall holes','ldholes.py',[]),('pin anchoring (>=2 spread)','ldanchor.py',[]),('drive retainer hinge risk','ldmotorbrace.py',[]),('aligned mating holes','ldaligned.py',[]),('alternating beam use (advisory)','ldrare.py',[]),
        ('pins sticking out','ldpinsout.py',['-I']),('mirror symmetry','ldsym.py',[]),
        ('hub charge port + side ports','ldclear.py',['-I']),('parts owned','ldbom.py',['-I'])]
failed=[]
for title,tool,flags in CHECKS:
    r=subprocess.run([py,*flags,os.path.join(here,tool),model],capture_output=True,text=True,cwd=here)
    out=(r.stdout+r.stderr).strip()
    print(f"\n=== {title}  [{tool}]")
    if r.returncode: failed.append(tool)
    if verbose or r.returncode: print(out); continue
    keep=[l for l in out.splitlines() if l and not l.startswith('  ') or any(k in l for k in ('VIOLATION','FLOATING','sticks','!!','above','below','shared seams','nearest'))]
    print('\n'.join(keep[:25]) + ('\n  …(-v for all)' if len(keep)>25 else ''))

print("\nFAILED: "+", ".join(failed) if failed else "\nAll checks passed.")
sys.exit(int(bool(failed)))
