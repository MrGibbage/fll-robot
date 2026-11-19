import sys
from pathlib import Path
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from ldrare import audit
I=np.eye(3);APA=np.array([[0,1,0],[1,0,0],[0,0,-1]]);VP=np.array([[0,0,1],[1,0,0],[0,1,0]])
def p(i,ref,pos,m=I):return dict(id=i,ref=ref+'.dat',P=np.array(pos,float),M=np.array(m,float))
class RareAudit(unittest.TestCase):
    def fixture(self,two):
        parts=[p(0,'2391',[0,0,0])]
        for z in ([0,40] if two else [0]):
            parts.append(p(len(parts),'18654',[20,0,z],APA));parts.append(p(len(parts),'2780',[10,0,z]))
        parts.append(p(len(parts),'18654',[0,20,20]));parts.append(p(len(parts),'2780',[0,10,20],VP))
        return parts
    def test_distinct_sideways_mounts_are_reported(self):
        row=audit(self.fixture(True))[0]
        self.assertEqual((row['vertical'],row['horizontal'],row['span']),(1,2,2))
        self.assertFalse(row['review'])
    def test_one_sideways_mount_is_reviewed_not_a_quota(self):
        row=audit(self.fixture(False))[0];self.assertEqual(row['horizontal'],1);self.assertTrue(row['review'])
if __name__=='__main__':unittest.main()
