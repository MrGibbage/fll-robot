"""Regressions: rim press-fits, missing wheel mates and envelope failures."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from ldcheck import rim_tire_pairs, hub_battery_pairs, merged_bores, STUDIO_FIX
from ldsize import check

class ValidationRegressions(unittest.TestCase):
    def wheel_parts(self):
        return [dict(id=0,ref='44771.dat',P=np.zeros(3),M=np.eye(3)),
                dict(id=1,ref='15038p01.dat',P=np.zeros(3),M=np.eye(3))]
    def test_correct_tire_press_fit(self):
        self.assertEqual(rim_tire_pairs(self.wheel_parts()), [(0,1)])
    def test_displaced_tire_is_not_connected(self):
        p=self.wheel_parts();p[1]['P'][0]=20
        self.assertEqual(rim_tire_pairs(p), [])
    def test_crossed_wheel_axes_are_not_connected(self):
        p=self.wheel_parts();p[1]['M']=np.array([[0,0,1],[0,1,0],[-1,0,0]])
        self.assertEqual(rim_tire_pairs(p), [])
    def test_hub_battery_clip_requires_same_pose(self):
        p=[dict(id=0,ref='bb1142c01.dat',P=np.zeros(3),M=np.eye(3)),
           dict(id=1,ref='55422c01.dat',P=np.zeros(3),M=np.eye(3))]
        self.assertEqual(hub_battery_pairs(p),[(0,1)])
        p[1]['P'][0]=20
        self.assertEqual(hub_battery_pairs(p),[])
    def test_sensor_substitution_preserves_mounting_holes(self):
        old=merged_bores('37308.dat');new=merged_bores('37308c01.dat')
        self.assertEqual(len(old),len(new))
        for a,b in zip(old,new):
            np.testing.assert_allclose(a[0],b[0]+STUDIO_FIX['37308c01.dat'])
            np.testing.assert_allclose(a[1],b[1])
            np.testing.assert_allclose(a[2:],b[2:])
    def test_envelope_accepts_beam_and_rejects_outside_part(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'fixture.ldr'
            base='0 FILE test.ldr\n0 !FLL ENVELOPE 3 8 3\n1 0 0 0 0 1 0 0 0 1 0 0 0 1 32524.dat\n'
            with contextlib.redirect_stdout(io.StringIO()):
                p.write_text(base);self.assertEqual(check(p),0)
                p.write_text(base+'1 0 100 0 0 1 0 0 0 1 0 0 0 1 32524.dat\n')
                self.assertEqual(check(p),1)
                p.write_text(base+'1 0 0 0 0 1 0 0 0 1 0 0 0 1 nonexistent.dat\n')
                self.assertEqual(check(p),1)

class ValidatorProcessRegressions(unittest.TestCase):
    def run_check(self, tool, model):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'fixture.ldr';path.write_text(model)
            return subprocess.run([sys.executable,str(Path(__file__).resolve().parents[1]/'tools'/tool),str(path)],capture_output=True,text=True)
    def line(self, ref, x, y, z, across=False):
        matrix='0 0 1 0 1 0 -1 0 0' if across else '1 0 0 0 1 0 0 0 1'
        return f'1 0 {x} {y} {z} {matrix} {ref}.dat\n'
    def wall_fixture(self, repeated_seam=False):
        s='0 FILE walls.ldr\n'
        for level,y in enumerate([0,-20]):
            a=level==0 or repeated_seam
            for sx in [-1,1]:
                for sz in [-1,1]:
                    corner=np.array([160*sx,y,140*sz])
                    long=np.array([-sx,0,0]) if a else np.array([0,0,-sz])
                    short=np.array([0,0,-sz]) if a else np.array([-sx,0,0])
                    z=-long;x=short;matrix=np.column_stack([x,np.cross(z,x),z])
                    pos=corner-matrix@np.array([0,0,80])
                    s+='1 0 '+' '.join(map(str,pos))+' '+' '.join(map(str,matrix.flat))+' 32526.dat\n'
                s+=self.line('40490' if a else '32316',sx*160,y,0)
            for z in [-140,140]:s+=self.line('32524' if a else '32525',0,y,z,True)
        # Its front hole gap aligns with a wall joint, but it is above the wall.
        s+=self.line('64179',60,-40,100,True)
        return s
    def test_seam_check_accepts_frame_and_rejects_repeated_wall_joint(self):
        good=self.run_check('ldseam.py',self.wall_fixture())
        self.assertEqual(good.returncode,0,good.stdout+good.stderr)
        bad=self.run_check('ldseam.py',self.wall_fixture(True))
        self.assertNotEqual(bad.returncode,0,bad.stdout+bad.stderr)
    def test_isolated_holes_are_allowed_but_adjacent_empty_holes_fail(self):
        one='0 FILE holes.ldr\n'+self.line('32524',0,0,0)
        self.assertEqual(self.run_check('ldholes.py',one).returncode,0)
        self.assertNotEqual(self.run_check('ldholes.py',one+self.line('32524',0,-20,0)).returncode,0)
    def test_official_hub_alias_and_blocked_usb(self):
        hub='0 FILE hub.ldr\n'+self.line('45601c01',0,0,0)
        good=self.run_check('ldclear.py',hub)
        self.assertEqual(good.returncode,0,good.stdout+good.stderr)
        blocked=self.run_check('ldclear.py',hub+self.line('32524',0,-70,120,True))
        self.assertNotEqual(blocked.returncode,0)
    def test_reserved_pocket_accepts_empty_space_and_rejects_intrusion(self):
        beam='0 FILE pocket.ldr\n'+self.line('32524',0,0,0)
        good=beam+'0 !FLL POCKET weight 40 60 -20 20 -80 80\n'
        bad=beam+'0 !FLL POCKET weight -20 20 -20 20 -80 80\n'
        self.assertEqual(self.run_check('ldfree.py',good).returncode,0)
        self.assertNotEqual(self.run_check('ldfree.py',bad).returncode,0)
    def test_studio_import_ids_accept_sample_convention_and_reject_original_bug(self):
        good='0 FILE ids.ldr\n'+self.line('32524',100,0,0)+self.line('bb1142c01',0,0,0)+self.line('55422c01',0,0,0)+self.line('37308c01',0,0,200)
        result=self.run_check('ldstudio.py',good)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        bad='0 FILE ids.ldr\n'+self.line('32524',100,0,0)+self.line('45601c01',0,0,0)+self.line('37308',0,0,200)
        result=self.run_check('ldstudio.py',bad)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('bb1142c01.dat',result.stdout)
        self.assertIn('37308c01.dat',result.stdout)
    def test_runner_reports_failure(self):
        result=self.run_check('run_checks.py',self.wall_fixture(True))
        self.assertNotEqual(result.returncode,0)
        self.assertIn('FAILED:',result.stdout)
        self.assertIn('ldseam.py',result.stdout.split('FAILED:')[-1])

if __name__=='__main__':unittest.main()
