"""Small-roller regression: legal axle stack, swept spokes and the rear-brace failure."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ldwheelclear import collisions, clip_z, enters_annulus
I=np.eye(3)
ACROSS=np.array([[0,0,1],[0,1,0],[-1,0,0]])
def part(i,ref,pos,m=I):return dict(id=i,ref=ref+'.dat',P=np.array(pos),M=m)

class RollerClearance(unittest.TestCase):
    def test_legal_axle_and_bush_contact(self):
        p=[part(0,'4185',[0,0,0]),part(1,'4519',[0,0,0],ACROSS),
           part(2,'32123a',[0,0,-10]),part(3,'32123a',[0,0,10])]
        self.assertEqual(collisions(p),[])
    def test_face_with_all_vertices_outside_disk_is_detected(self):
        tri=np.array([[-50,-50,0],[50,-50,0],[0,70,0]],float)
        self.assertTrue(enters_annulus(clip_z(clip_z(tri,-4.85,True),4.85,False),29.85,6.4))
    def test_reported_rear_beam_collision_and_clear_position(self):
        wheels=[part(0,'4185',[-15,40,-120],ACROSS),part(1,'4185',[15,40,-120],ACROSS)]
        beam=part(2,'71710',[0,20,-140],ACROSS)
        hits=collisions(wheels+[beam])
        self.assertEqual({w['id'] for w,p in hits if p['id']==2},{0,1})
        # Moving the beam a full stud aft leaves clearance for this isolated stack.
        beam['P'][2]-=20
        self.assertEqual(collisions(wheels+[beam]),[])

if __name__=='__main__':unittest.main()
