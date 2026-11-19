"""A two-pin bar can still be a hinge: distinguish a common support from two pivots."""
import sys
from pathlib import Path
import unittest
import tempfile
import subprocess
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ldmotorbrace import risks
from ldcheck import connection_records,builtin_pin_defs
I=np.eye(3);VP=np.array([[0,0,1],[1,0,0],[0,1,0]])
def p(i,ref,pos,m=I):return dict(id=i,ref=ref+'.dat',P=np.array(pos,float),M=np.array(m,float))
class MotorBracing(unittest.TestCase):
    def fixture(self,common):
        ps=[p(0,'54675',[120,-20,20],[[0,-1,0],[-1,0,0],[0,0,-1]]),
            p(1,'43857',[100,-80,70])]
        if common:ps.append(p(2,'43857',[100,-60,70]))
        else:
            ps.extend([p(2,'18654',[100,-60,60]),p(3,'18654',[100,-60,80])])
        for z in [60,80]:ps.append(p(len(ps),'2780',[100,-70,z],VP))
        return ps
    def test_two_pins_in_same_support_are_fixed(self):self.assertEqual(risks(self.fixture(True)),[])
    def test_two_pivots_in_separate_supports_are_flagged(self):
        self.assertEqual([x['id'] for x in risks(self.fixture(False))],[1])
    def test_molded_pins_join_cross_block_to_beam(self):
        m=np.array([[0,1,0],[0,0,1],[1,0,0]])
        ps=[p(0,'2393',[0,0,0],m),p(1,'32523',[0,-20,0],[[0,0,1],[0,1,0],[-1,0,0]])]
        records=connection_records(ps)
        self.assertEqual(len(records),2)
        self.assertTrue(all(r['owner']==0 and r['hits']=={1} for r in records))
        self.assertEqual(len(builtin_pin_defs('48989.dat')),4)
    def test_molded_pin_contact_is_valid_but_double_filling_fails(self):
        good='0 FILE built.ldr\n1 0 0 0 0 0 1 0 0 0 1 1 0 0 2393.dat\n1 1 0 -20 0 0 0 1 0 1 0 -1 0 0 32523.dat\n'
        tool=Path(__file__).resolve().parents[1]/'tools/ldcheck.py'
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'built.ldr';path.write_text(good)
            r=subprocess.run([sys.executable,str(tool),str(path)],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stdout+r.stderr)
            path.write_text(good+'1 0 20 -10 0 0 0 1 1 0 0 0 1 0 2780.dat\n')
            r=subprocess.run([sys.executable,str(tool),str(path)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)
            self.assertIn('(built-in pin)',r.stdout)
if __name__=='__main__':unittest.main()
