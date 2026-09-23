"""Synthetic offline calibration fixtures; never copied to a hardware profile."""
import copy,json,math,tempfile,unittest
from pathlib import Path
from calibrate_pd41 import build_bundle,fit_axis,profile_data,TAU
from calibrated_pd41 import CalibratedSource
from pd41_protocol import CFG

class CalibrationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.dest=Path(self.temp.name)/'bundle';self.rows=[]
  p=profile_data('quinn');self.q={};self.zeros={};self.signs={}
  for i,a in enumerate(p['axes'][3:]):
   lo,hi=a['limits_rad'];mid=(lo+hi)/2;self.q[a['id']]=mid;sign=(-1)**i;zero=(i*.137+6.20)%TAU;self.zeros[a['id']]=zero;self.signs[a['id']]=sign
   for delta in (-.2,0,.2):self.rows.append(dict(axis_id=a['id'],known_joint_rad=mid+delta,mean_raw_rad=(zero+sign*(mid+delta))%TAU,spread_deg=.02,samples=60,device_id='0123456789ab',character='quinn',source_capture_sha256='0'*64))
 def tearDown(self):self.temp.cleanup()
 def build(self):return build_bundle('quinn',self.rows,'SYNTHETIC_UNIT_TEST_ONLY',self.dest)
 def raw(self):
  axes=[dict(axis_id=a,status='fixed',count=None,flags=0) for a in CFG['protocol_order'][:3]]
  for a in CFG['protocol_order'][3:]:axes.append(dict(axis_id=a,status='valid',count=round(((self.zeros[a]+self.signs[a]*self.q[a])%TAU)*16384/TAU)%16384,flags=0))
  return dict(device_id='0123456789ab',boot_id='10',sequence=1,sender_monotonic_us=10000,axes=axes)
 def test_both_signs_and_wrapped_zero(self):
  c=self.build()
  for a in c['axes'][3:]:self.assertAlmostEqual(a['zero_raw_rad'],self.zeros[a['axis_id']]);self.assertEqual(a['sign'],self.signs[a['axis_id']])
 def test_all_axes_roundtrip_and_fixed_root(self):
  self.build();source=CalibratedSource(self.dest,'0123456789ab');r=source.translate(self.raw());self.assertTrue(r['pose_valid'])
  self.assertEqual(r['packet']['axis_status'][:3],['fixed']*3);self.assertEqual(r['packet']['raw_angles_rad'][:3],[None]*3)
  for a,q in self.q.items():self.assertLess(abs(r['angles_rad'][a]-q),TAU/16384)
 def test_missing_axis_blocks_bundle(self):
  self.rows=[r for r in self.rows if r['axis_id']!='head.yaw']
  with self.assertRaisesRegex(ValueError,'All 41'):self.build()
 def test_two_references_not_enough(self):
  self.rows.pop()
  with self.assertRaisesRegex(ValueError,'three distinct'):self.build()
 def test_inaccurate_reference_rejected(self):
  self.rows[0]['mean_raw_rad']=(self.rows[0]['mean_raw_rad']+.1)%TAU
  with self.assertRaisesRegex(ValueError,'reference check'):self.build()
 def test_unstable_rejected(self):
  self.rows[0]['spread_deg']=1
  with self.assertRaisesRegex(ValueError,'stability'):self.build()
 def test_nan_rejected(self):
  self.rows[0]['mean_raw_rad']=float('nan')
  with self.assertRaisesRegex(ValueError,'Non-finite'):self.build()
 def test_mixed_gateway_rejected(self):
  self.rows[0]['device_id']='other'
  with self.assertRaisesRegex(ValueError,'Mixed devices'):self.build()
 def test_no_overwrite(self):
  self.build()
  with self.assertRaisesRegex(ValueError,'new directory'):self.build()
 def test_gateway_identity(self):
  self.build()
  with self.assertRaisesRegex(ValueError,'identity'):CalibratedSource(self.dest,'other')
 def test_missing_sensor_never_becomes_zero(self):
  self.build();src=CalibratedSource(self.dest,'0123456789ab');r=self.raw();r['axes'][10].update(status='missing',count=None)
  v=src.translate(r);self.assertFalse(v['pose_valid']);self.assertIsNone(v['angles_rad']);self.assertEqual(v['packet']['axis_status'][10],'missing')
 def test_restart_requires_explicit_reconnect(self):
  self.build();src=CalibratedSource(self.dest,'0123456789ab');r=self.raw();src.translate(r);r['sequence']=2;r['boot_id']='11'
  with self.assertRaisesRegex(ValueError,'restarted'):src.translate(r)
 def test_stale_frame_rejected(self):
  self.build();src=CalibratedSource(self.dest,'0123456789ab');r=self.raw();src.translate(r)
  with self.assertRaisesRegex(ValueError,'Stale'):src.translate(r)
 def test_geometry_hash_is_binding(self):
  self.build();f=self.dest/'Profiles/virtual_humanoid_44_v1.json';f.write_text(f.read_text(encoding='utf-8')+' ',encoding='utf-8')
  with self.assertRaisesRegex(ValueError,'geometry'):CalibratedSource(self.dest,'0123456789ab')
if __name__=='__main__':unittest.main()
