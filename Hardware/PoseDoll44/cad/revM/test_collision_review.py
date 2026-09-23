"""Policy tests protect the boundary between pose restrictions and design faults."""
from pathlib import Path
import sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
from collision_review import classify
class CollisionReviewTests(unittest.TestCase):
 def kind(self,a,b):return classify(dict(a='one',b='two',volume_mm3=2.5),{'one':a,'two':b})['classification']
 def test_same_arm_elbow_is_structural(self):self.assertEqual(self.kind('upperarm_l','elbow_l'),'structural')
 def test_forearm_wrist_is_structural(self):self.assertEqual(self.kind('forearm_l','hand_l.flex_frame'),'structural')
 def test_girdle_neck_is_structural(self):self.assertEqual(self.kind('clavicle_l','head.yaw_frame'),'structural')
 def test_opposite_arms_are_pose_restriction(self):self.assertEqual(self.kind('forearm_l','forearm_r'),'pose_restriction')
 def test_hand_pelvis_is_pose_restriction(self):self.assertEqual(self.kind('hand_l','pelvis'),'pose_restriction')
 def test_hip_pelvis_is_structural(self):self.assertEqual(self.kind('thigh_r.flex_frame','pelvis'),'structural')
 def test_unknown_is_not_downgraded(self):self.assertEqual(self.kind('unmapped','forearm_r'),'structural')
 def test_report_retains_raw_volume(self):self.assertEqual(classify(dict(a='x',b='y',volume_mm3=3.7),{'x':'hand_l','y':'pelvis'})['volume_mm3'],3.7)
if __name__=='__main__':unittest.main()
