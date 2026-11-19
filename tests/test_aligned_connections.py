"""Mating-hole audit: do not miss motor rail pins or propose pins in occupied/axle holes."""
import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ldaligned import opportunities
from ldcheck import typed_bores,connection_records
from ldpinplan import vertical_pin_plan,pin_plan
I=np.eye(3);VP=np.array([[0,0,1],[1,0,0],[0,1,0]]);APA=np.array([[0,1,0],[1,0,0],[0,0,-1]])
def p(i,ref,pos,m=I):return dict(id=i,ref=ref+'.dat',P=np.array(pos,float),M=np.array(m,float))
class AlignedConnections(unittest.TestCase):
    def pair(self):return [p(0,'18654',[0,0,0]),p(1,'18654',[0,20,0])]
    def test_existing_pin_is_not_doubled(self):
        self.assertEqual(opportunities(self.pair()+[p(2,'2780',[0,10,0],VP)]),[])
    def test_unfilled_adjacent_round_holes_need_pin(self):
        found=opportunities(self.pair());self.assertEqual(len(found),1)
        self.assertEqual(found[0]['connector'],'2780.dat');np.testing.assert_allclose(found[0]['point'],[0,10,0])
    def test_distant_coaxial_holes_do_not_get_short_pin(self):
        parts=self.pair();parts[1]['P'][1]=40;self.assertEqual(opportunities(parts),[])
    def test_axle_pin_is_selected_for_axle_end(self):
        parts=[p(0,'32184',[0,0,0],APA),p(1,'18654',[20,20,0])]
        found=opportunities(parts);self.assertEqual(len(found),1)
        self.assertEqual(found[0]['connector'],'43093.dat')
    def test_motor_and_two_rails_have_eight_missing_top_pins(self):
        parts=[p(0,'54675',[120,-20,20],[[0,-1,0],[-1,0,0],[0,0,-1]]),
               p(1,'32278',[100,-80,-40]),p(2,'41239',[140,-80,-40])]
        found=opportunities(parts);self.assertEqual(len(found),8)
        self.assertEqual({round(v['point'][2]) for v in found},{40,0,-80,-120})
        for item in found:parts.append(p(len(parts),'2780',item['point'],VP))
        self.assertEqual(opportunities(parts),[])
    def test_surface_reliefs_between_real_holes_are_not_connections(self):
        parts=[p(0,'32526',[0,0,0]),p(1,'32526',[0,20,0])]
        found=opportunities(parts)
        self.assertEqual(len(found),7)
        self.assertTrue(all(abs(v['point'][0]/20-round(v['point'][0]/20))<1e-6 and abs(v['point'][2]/20-round(v['point'][2]/20))<1e-6 for v in found))
    def test_thin_end_rings_still_establish_real_pin_holes(self):
        parts=[p(0,'43857',[90,0,180],[[0,0,1],[0,1,0],[-1,0,0]]),
               p(1,'43857',[90,20,180],[[0,0,1],[0,1,0],[-1,0,0]])]
        found=opportunities(parts);self.assertEqual(len(found),2)
        planned=vertical_pin_plan(parts);self.assertEqual(len(planned),2)
        for part in planned:part['id']=len(parts);parts.append(part)
        self.assertEqual(opportunities(parts),[])
    def test_planner_connects_blind_motor_holes_to_rails(self):
        parts=[p(0,'54675',[120,-20,20],[[0,-1,0],[-1,0,0],[0,0,-1]]),
               p(1,'32278',[100,-80,-40]),p(2,'41239',[140,-80,-40])]
        planned=vertical_pin_plan(parts);self.assertEqual(len(planned),8)
        for part in planned:part['id']=len(parts);parts.append(part)
        self.assertEqual(opportunities(parts),[])
    def test_three_horizontal_mates_use_one_3l_pin(self):
        parts=[p(i,'18654',[0,0,z],VP) for i,z in enumerate([0,20,40])]
        planned=pin_plan(parts)
        self.assertEqual(len(planned),1);self.assertEqual(planned[0]['ref'],'6558.dat')
        planned[0]['id']=3
        self.assertEqual(opportunities(parts+planned),[])
    def test_pin_in_cosmetic_relief_does_not_count_as_a_connection(self):
        parts=[p(0,'32526',[0,0,0]),p(1,'32526',[0,20,0]),p(2,'2780',[10,10,80],VP)]
        records=connection_records(parts)
        self.assertEqual(len(records),1);self.assertEqual(records[0]['hits'],set())
if __name__=='__main__':unittest.main()
