"""Contact-plane math must distinguish nominal render height from real clearance."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ldground import contact_plane
class ContactPlane(unittest.TestCase):
    def test_equal_tangent_heights_are_level(self):
        m,b=contact_plane((0,0,50),(20,-100,30))
        self.assertAlmostEqual(m,0,places=9);self.assertAlmostEqual(b,50,places=9)
    def test_different_wheels_share_exact_tangent(self):
        d=(-20,20,86.125);c=(40,-100,30);m,b=contact_plane(d,c)
        self.assertLess(m,0)
        for y,z,r in [d,c]:self.assertAlmostEqual((m*z+b-y)/np.sqrt(1+m*m),r,places=8)
        # The front wall is closer to the floor than the wall at the drive axle.
        front=(m*180+b-50)/np.sqrt(1+m*m)
        at_axle=(m*20+b-50)/np.sqrt(1+m*m)
        self.assertLess(front,at_axle)
if __name__=='__main__':unittest.main()
