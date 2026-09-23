"""Strict H1 diagnostic protocol. This is not a FullBody44 production identity."""
import struct,zlib,math
FORMAT=struct.Struct("<4sBBHQQQQIHHHHHH")
MAX_FRAME=128
def cobs_encode(data):
    out=bytearray([0]);idx=0;code=1
    for b in data:
        if b==0:out[idx]=code;idx=len(out);out.append(0);code=1
        else:
            out.append(b);code+=1
            if code==255:out[idx]=code;idx=len(out);out.append(0);code=1
    out[idx]=code
    return bytes(out)
def cobs_decode(data):
    if not data or 0 in data:raise ValueError("invalid COBS bytes")
    out=bytearray();i=0
    while i<len(data):
        code=data[i];i+=1
        if i+code-1>len(data):raise ValueError("truncated COBS")
        out.extend(data[i:i+code-1]);i+=code-1
        if code<255 and i<len(data):out.append(0)
    return bytes(out)
def decode(frame):
    raw=cobs_decode(frame)
    if len(raw)!=60:raise ValueError("H1 length")
    if zlib.crc32(raw[:-4])!=struct.unpack("<I",raw[-4:])[0]:raise ValueError("CRC32 mismatch")
    magic,ver,kind,length,device,boot,seq,us,window,axis,angle,diag,mag,zero,flags=FORMAT.unpack(raw[:-4])
    if (magic,ver,kind,length)!=(b"PDH1",1,1,56):raise ValueError("version/type")
    if axis!=17 or angle>=16384 or diag>=16384 or mag>=16384 or zero>=16384 or flags&~31:raise ValueError("field range")
    if flags and angle!=0:raise ValueError("invalid sample contains a count")
    if not flags and (not diag&0x100 or diag&0xe00 or zero):raise ValueError("inconsistent sensor health")
    return dict(source_kind="H1_SINGLE_REAL_AXIS_DIAGNOSTIC",device_id=f"{device:012x}",boot_id=str(boot),
        sequence=seq,sender_monotonic_us=us,read_window_us=window,axis_index=axis,axis_id="elbow_l.flex",
        count=angle if flags==0 else None,raw_degrees=angle*360/16384 if flags==0 else None,
        diagnostic=diag,magnitude=mag,otp_zero=zero,flags=flags,status="valid" if flags==0 else "invalid")
class Decoder:
    def __init__(self):self.buffer=bytearray();self.discard=False;self.errors=0;self.identity=None;self.seq=None;self.us=None
    def feed(self,data):
        out=[]
        for b in data:
            if b==0:
                if self.buffer and not self.discard:
                    try:
                        v=decode(bytes(self.buffer));ident=(v["device_id"],v["boot_id"])
                        if ident==self.identity and (v["sequence"]<=self.seq or v["sender_monotonic_us"]<=self.us):raise ValueError("stale sequence/time")
                        if self.identity is not None and ident!=self.identity:raise ValueError("session changed; reconnect required")
                        self.identity=ident;self.seq=v["sequence"];self.us=v["sender_monotonic_us"];out.append(v)
                    except ValueError:self.errors+=1
                self.buffer.clear();self.discard=False
            elif not self.discard:
                self.buffer.append(b)
                if len(self.buffer)>MAX_FRAME:self.errors+=1;self.buffer.clear();self.discard=True
        return out
