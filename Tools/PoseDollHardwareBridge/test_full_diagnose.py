import unittest
from full_diagnose import summary
from pd41_protocol import Decoder, encode_diagnostic, FIXED, FAULT, MISSING, NODE_INDICES

def record(seq, value=100, *, absent=None, fault=None):
 words=[FIXED]*3+[value]*41;timing=[[10,3000] for _ in range(6)];presence=63
 if absent:
  for i in NODE_INDICES[absent]:words[i]=MISSING
  timing[absent-1]=[0,0];presence &= ~(1<<(absent-1))
 if fault:words[fault[0]]=FAULT|fault[1]
 return encode_diagnostic(words,timing,123,456,seq,seq*16667,3010,presence)

class FullDiagnosticTests(unittest.TestCase):
 def report(self, packets):
  d=Decoder();samples=d.feed(b''.join(packets));return summary(samples,d.errors)
 def test_period_boundary_and_fixed_reference(self):
  r=self.report([record(1,16380),record(2,4)])
  self.assertAlmostEqual(r['axes'][3]['max_contiguous_run_peak_to_peak_deg'],8*360/16384)
  self.assertEqual(r['axes'][0]['states']['fixed'],2)
  self.assertIsNone(r['axes'][0]['max_contiguous_run_peak_to_peak_deg'])
  self.assertFalse(r['calibrated']);self.assertFalse(r['physical_acceptance'])
 def test_missing_fault_and_gap_split_noise_runs(self):
  r=self.report([record(1,100),record(2,3000,absent=1),record(3,9000,fault=(3,8)),record(5,12000)])
  a=r['axes'][3]
  self.assertEqual(a['states'],dict(valid=2,invalid=1,missing=1,fixed=0))
  self.assertEqual(a['fault_flags_seen'],8);self.assertEqual(a['valid_run_count'],2)
  self.assertEqual(a['max_contiguous_run_peak_to_peak_deg'],0)
  self.assertEqual(r['sequence_gaps'],1);self.assertEqual(r['complete_valid_frames'],2)
  self.assertEqual(r['node_present_frames']['1'],3)
 def test_replayed_frames_rejected_and_empty_report(self):
  r=self.report([record(1),record(1),record(2)])
  self.assertEqual(r['frames'],2);self.assertEqual(r['framing_or_session_errors'],1)
  e=summary([],0);self.assertEqual(e['frames'],0);self.assertIsNone(e['received_source_rate_hz'])
  self.assertIsNone(e['maximum_transport_envelope_us'])

if __name__=='__main__':unittest.main()
