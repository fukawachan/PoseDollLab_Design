"""Protocol contract for the user-approved pelvis-local reference.
No hardware is read and no Unreal session is modified.
"""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/PoseDollSimulator/src'))
from posedoll_sim.core import DeviceProfile, SensorDecoder

class RootReferenceTests(unittest.TestCase):
 def setUp(self):
  self.p=DeviceProfile(ROOT/'Shared')
  cap=json.loads((ROOT/'Hardware/PoseDoll44/mechanical_manifest/physical_quinn_41_capabilities.json').read_text(encoding='utf-8'))
  # Test the existing decoder with the new declared capability. The factory
  # calibration here is only a synthetic raw-data fixture, never a hardware zero.
  self.p.capability=copy.deepcopy(cap);self.p.capability['profile_id']=self.p.data['profile_id'];self.p.fixed=cap['fixed_axis_values_rad'];self.p.validate()
  self.hello=self.p.hello('root-reference-contract',True)
  self.decoder=SensorDecoder(self.p);self.decoder.handshake(self.hello)
  q={a:0.0 for a in self.p.order};q['elbow_l.flex']=.7
  raw,states=self.p.encode_angles(q,True)
  self.sample={k:self.hello[k] for k in ('protocol','device_id','session_id','profile_id','profile_sha256','calibration_id','calibration_sha256')}
  self.sample.update(type='sample',sequence='1',sender_monotonic_us='1000000',raw_angles_rad=raw,axis_status=states)
 def test_three_fixed_and_41_measured_decode(self):
  self.assertEqual(self.sample['axis_status'].count('fixed'),3)
  self.assertEqual(self.sample['axis_status'].count('valid'),41)
  q=self.decoder.sample(self.sample)
  self.assertAlmostEqual(q['elbow_l.flex'],.7)
  for a in self.p.fixed:self.assertEqual(q[a],0.0);self.assertIsNone(self.sample['raw_angles_rad'][self.p.index[a]])
 def test_measured_joint_cannot_become_fixed(self):
  i=self.p.index['elbow_l.flex'];self.sample['axis_status'][i]='fixed';self.sample['raw_angles_rad'][i]=None
  with self.assertRaisesRegex(ValueError,'Undeclared fixed'):self.decoder.sample(self.sample)
 def test_measured_joint_missing_is_rejected(self):
  i=self.p.index['head.yaw'];self.sample['axis_status'][i]='missing';self.sample['raw_angles_rad'][i]=None
  with self.assertRaisesRegex(ValueError,'Missing/invalid'):self.decoder.sample(self.sample)
 def test_root_is_not_measured_zero(self):
  self.sample['axis_status'][0]='valid';self.sample['raw_angles_rad'][0]=0.0
  with self.assertRaisesRegex(ValueError,'Fixed axis must be fixed'):self.decoder.sample(self.sample)
if __name__=='__main__':unittest.main()
