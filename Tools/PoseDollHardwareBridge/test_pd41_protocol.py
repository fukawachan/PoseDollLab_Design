import unittest,struct,zlib
from pd41_protocol import *

class PD41Tests(unittest.TestCase):
 def fixture(self,**updates):
  d=dict(words=[FIXED]*3+[321]*41,timings=[[10,3000]]*6,device=123,boot=456,sequence=1,timestamp_us=10000,window_us=3010,presence=63);d.update(updates);return encode_diagnostic(**d)
 def corrupt_word(self,wire,index,value):
  b=bytearray(cobs_decode(wire[:-1]));struct.pack_into('<H',b,HEADER.size+index*2,value);struct.pack_into('<I',b,BODY_SIZE,zlib.crc32(b[:-4]));return cobs_encode(b)
 def test_complete_body_and_three_fixed(self):
  q=decode(self.fixture()[:-1]);self.assertTrue(q['pose_valid']);self.assertFalse(q['calibrated']);self.assertEqual([a['status'] for a in q['axes'][:3]],['fixed']*3);self.assertEqual(len(q['axes']),44)
 def test_root_cannot_be_valid_zero(self):
  with self.assertRaisesRegex(ValueError,'root'):decode(self.corrupt_word(self.fixture(),0,0))
 def test_measured_cannot_be_fixed(self):
  with self.assertRaisesRegex(ValueError,'fixed'):decode(self.corrupt_word(self.fixture(),17,FIXED))
 def test_fault_does_not_become_a_valid_count(self):
  q=decode(self.corrupt_word(self.fixture(),17,FAULT|8));self.assertFalse(q['pose_valid']);self.assertIsNone(q['axes'][17]['count']);self.assertEqual(q['axes'][17]['flags'],8)
 def test_missing_node_retains_missing_axes(self):
  words=[FIXED]*3+[321]*41
  for i in NODE_INDICES[3]:words[i]=MISSING
  times=[[10,3000] for _ in range(6)];times[2]=[0,0]
  q=decode(self.fixture(words=words,timings=times,presence=59)[:-1]);self.assertFalse(q['pose_valid']);self.assertEqual(sum(a['status']=='missing' for a in q['axes']),9)
 def test_absent_node_cannot_smuggle_previous_counts(self):
  with self.assertRaisesRegex(ValueError,'absent'):self.fixture(presence=59)
 def test_crc_rejects_transport_damage(self):
  b=bytearray(cobs_decode(self.fixture()[:-1]));b[60]^=1
  with self.assertRaisesRegex(ValueError,'CRC32'):decode(cobs_encode(b))
 def test_stale_and_new_boot_require_reconnect(self):
  d=Decoder();self.assertEqual(len(d.feed(self.fixture())),1);self.assertEqual(d.feed(self.fixture()),[])
  self.assertEqual(d.feed(self.fixture(boot=457,sequence=2,timestamp_us=20000)),[]);self.assertEqual(d.errors,2)
 def test_chunking_oversize_and_recovery(self):
  d=Decoder();w=self.fixture();self.assertEqual(d.feed(w[:35]),[]);self.assertEqual(len(d.feed(w[35:])),1)
  self.assertEqual(d.feed(b'x'*(FRAME_SIZE+30)+b'\0'),[])
  self.assertEqual(len(d.feed(self.fixture(sequence=2,timestamp_us=20000))),1)
 def test_acquisition_span_must_fit_declared_window(self):
  with self.assertRaisesRegex(ValueError,'cohort'):self.fixture(window_us=2000)
if __name__=='__main__':unittest.main()
