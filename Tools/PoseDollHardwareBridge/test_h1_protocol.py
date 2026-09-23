import unittest,struct,zlib
from h1_protocol import *
def packet(seq=1,us=10000,boot=1,count=8192,diag=0x180,flags=0,axis=17):
    raw=FORMAT.pack(b"PDH1",1,1,56,0x102030405060,boot,seq,us,300,axis,count,diag,4000,0,flags)
    return cobs_encode(raw+struct.pack("<I",zlib.crc32(raw)))+b"\0"
class TestH1(unittest.TestCase):
    def test_crc_reference(self):self.assertEqual(zlib.crc32(b"123456789"),0xcbf43926)
    def test_cobs(self):
        for d in (b"",b"\0",bytes(range(256)),bytes([255])*600):self.assertEqual(cobs_decode(cobs_encode(d)),d)
    def test_fragmented(self):
        d=Decoder();p=packet();out=[]
        for b in p:out+=d.feed(bytes([b]))
        self.assertEqual(out[0]["raw_degrees"],180);self.assertEqual(d.errors,0)
    def test_crc_fault_recovers(self):
        p=bytearray(cobs_decode(packet()[:-1]));p[30]^=1;p=cobs_encode(p)+b"\0";d=Decoder()
        self.assertEqual(d.feed(p),[]);self.assertEqual(len(d.feed(packet(2,20000))),1);self.assertEqual(d.errors,1)
    def test_duplicate_and_old_time(self):
        d=Decoder();self.assertEqual(len(d.feed(packet())),1)
        self.assertFalse(d.feed(packet()));self.assertFalse(d.feed(packet(2,9999)));self.assertEqual(d.errors,2)
    def test_restart_requires_reconnect(self):
        d=Decoder();d.feed(packet());self.assertFalse(d.feed(packet(2,20000,boot=2)));self.assertEqual(d.errors,1)
    def test_magnet_fault(self):
        v=Decoder().feed(packet(count=0,diag=0x580,flags=8))[0];self.assertIsNone(v["count"])
    def test_fake_health_rejected(self):self.assertFalse(Decoder().feed(packet(diag=0x580)))
    def test_invalid_count_rejected(self):self.assertFalse(Decoder().feed(packet(count=8192,flags=8)))
    def test_wrong_axis_rejected(self):self.assertFalse(Decoder().feed(packet(axis=0)))
    def test_bounds_and_resync(self):
        d=Decoder();self.assertFalse(d.feed(b"x"*10000));self.assertLessEqual(len(d.buffer),MAX_FRAME)
        self.assertEqual(len(d.feed(b"\0"+packet())),1)
if __name__=="__main__":unittest.main()
