import unittest
from can_cohort import *
class CohortTests(unittest.TestCase):
 def setUp(self):
  self.c=Cohort(123,{n:100+n for n in NODE_INDICES})
  for n in NODE_INDICES:self.c.acknowledge_epoch(n,123,100+n)
  self.c.begin(1,1000)
 def fill(self,node,value=555,seq=1):
  vals=[value]*len(NODE_INDICES[node]);vals+=([FIXED] if len(vals)%2 else [])
  for g in range(len(vals)//2):self.c.pair(node,seq,g,vals[2*g:2*g+2],2000)
  return self.c.end(node,seq,100,900,3000)
 def test_all_six_nodes_form_exact_41_measurements(self):
  for n in NODE_INDICES:self.fill(n)
  d=self.c.finish(4000);self.assertEqual(d['presence'],63);self.assertEqual(d['words'],[FIXED]*3+[555]*41)
 def test_partial_node_does_not_reuse_last_pose(self):
  for n in NODE_INDICES:self.fill(n)
  self.c.finish(4000);self.c.begin(2,20000)
  self.assertFalse(self.c.pair(3,1,0,[666,666],21000))
  self.c.pair(3,2,0,[666,666],21000);self.assertFalse(self.c.end(3,2,100,3000,22000))
  d=self.c.finish(34000);self.assertTrue(all(d['words'][i]==MISSING for i in NODE_INDICES[3]))
 def test_duplicate_pair_invalidates_that_node(self):
  self.c.pair(3,1,0,[555,555],2000);self.assertFalse(self.c.pair(3,1,0,[555,555],2001));self.fill(3)
  self.assertEqual(self.c.finish(15000)['presence'],0)
 def test_reboot_after_end_invalidates_current_node(self):
  self.fill(2);self.c.boot(2,999);self.assertFalse(self.c.acknowledge_epoch(2,122,999));self.assertEqual(self.c.finish(15000)['presence'],0)
 def test_prior_boot_cannot_rearm_node(self):
  self.c.boot(2,999);self.assertFalse(self.c.acknowledge_epoch(2,123,102));self.assertFalse(self.fill(2))
 def test_sensor_fault_is_present_but_not_valid_pose(self):
  self.fill(2,0x8008);d=self.c.finish(15000);self.assertEqual(d['presence'],2);self.assertEqual(d['words'][6],0x8008)
 def test_late_end_is_not_accepted(self):
  self.c.pair(1,1,0,[111,111],14000);self.c.pair(1,1,1,[111,FIXED],14000)
  self.assertFalse(self.c.end(1,1,0,3000,15000));self.assertEqual(self.c.finish(15000)['presence'],0)
 def test_transport_delay_is_in_conservative_envelope(self):
  self.fill(1);d=self.c.finish(15000);self.assertEqual(d['timings'][0],[0,2000]);self.assertEqual(d['window_us'],2000)
 def test_impossible_sensor_timing_invalidates_node(self):
  self.c.pair(1,1,0,[111,111],2000);self.c.pair(1,1,1,[111,FIXED],2000)
  self.assertFalse(self.c.end(1,1,0,7000,3000));self.assertEqual(self.c.finish(15000)['presence'],0)
 def test_fixed_cannot_fill_a_measured_port(self):
  self.assertFalse(self.c.pair(1,1,0,[FIXED,111],2000));self.assertEqual(self.c.finish(15000)['presence'],0)
if __name__=='__main__':unittest.main()
