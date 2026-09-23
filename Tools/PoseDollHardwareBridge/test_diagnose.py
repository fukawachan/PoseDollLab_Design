import unittest,tempfile,sys,json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from test_h1_protocol import packet
from h1_protocol import Decoder
from diagnose import capture,summary,write_record
class TestDiagnostic(unittest.TestCase):
    def test_wrap_and_dropped_epochs(self):
        rows=Decoder().feed(packet(count=16380)+packet(seq=3,us=30000,count=4))
        r=summary(rows,0)
        self.assertLess(r["raw_noise_rms_deg"],.1);self.assertEqual(r["sequence_gaps"],1)
    def test_disconnect_preserves_raw_evidence(self):
        raw=packet()+packet(seq=2,us=20000,count=0,diag=0,flags=8)
        class Fake:
            def __init__(self,**kwargs):self.dtr=True;self.rts=True;self.is_open=False;self.reads=0
            def open(self):
                assert not self.is_open and not self.dtr and not self.rts
                self.is_open=True
            def __enter__(self):return self
            def __exit__(self,*args):self.is_open=False
            def read(self,n):
                self.reads+=1
                if self.reads==1:return raw
                raise OSError("test unplug")
        with tempfile.TemporaryDirectory() as t,patch.dict(sys.modules,{"serial":SimpleNamespace(Serial=Fake)}):
            dest=Path(t)/"raw"
            r=capture("TEST_PORT",10,dest)
            self.assertEqual(r["frames"],2);self.assertEqual(r["valid_frames"],1)
            self.assertIn("test unplug",r["transport_error"])
            self.assertEqual(Path(str(dest)+".bin").read_bytes(),raw)
            rows=[json.loads(v) for v in Path(str(dest)+".jsonl").read_text().splitlines()]
            self.assertIsNone(rows[1]["count"])
    def test_never_overwrite_record(self):
        with tempfile.TemporaryDirectory() as t:
            dest=Path(t)/"raw";write_record(dest,b"first",[],{})
            with self.assertRaises(ValueError):write_record(dest,b"second",[],{})
            self.assertEqual(Path(str(dest)+".bin").read_bytes(),b"first")
if __name__=="__main__":unittest.main()
