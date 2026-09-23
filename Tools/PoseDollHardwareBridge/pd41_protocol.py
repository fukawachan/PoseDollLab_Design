"""PD41 full-body diagnostic transport, separate from the tested H1 transport.
No serial connection or UE transmission occurs on import. The three root words
are explicit fixed references. A sample with any missing/invalid measured axis
is diagnostic only and cannot be advertised as a valid full-body pose.
"""
from pathlib import Path
import json,struct,zlib
from h1_protocol import cobs_encode,cobs_decode
MANIFEST=Path(__file__).resolve().parents[2]/'Hardware/PoseDoll44/mechanical_manifest/network_revM.json'
CFG=json.loads(MANIFEST.read_text(encoding='utf-8'))
HEADER=struct.Struct('<4sBBHQQQQIHH')
WORDS=struct.Struct('<44H');TIMING=struct.Struct('<12H')
BODY_SIZE=HEADER.size+WORDS.size+TIMING.size
FRAME_SIZE=BODY_SIZE+4
FIXED=0x4000;MISSING=0xffff;FAULT=0x8000
NODE_INDICES={n['id']:[p['protocol_index'] for p in n['ports']] for n in CFG['nodes']}

def word_state(word,root=False):
 if root:
  if word!=FIXED:raise ValueError('root must be explicit fixed')
  return 'fixed',None,0
 if 0<=word<0x4000:return 'valid',word,0
 if word==MISSING:return 'missing',None,0
 if word&FAULT and 1<=word&0x7fff<=31:return 'invalid',None,word&31
 raise ValueError('reserved or undeclared fixed word')

def decode(frame):
 raw=cobs_decode(frame)
 if len(raw)!=FRAME_SIZE:raise ValueError('PD41 length')
 if zlib.crc32(raw[:-4])!=struct.unpack_from('<I',raw,BODY_SIZE)[0]:raise ValueError('CRC32 mismatch')
 magic,ver,kind,length,device,boot,seq,us,window,presence,count=HEADER.unpack_from(raw)
 if (magic,ver,kind,length,count)!=(b'PD41',1,1,BODY_SIZE,44):raise ValueError('PD41 version/type/layout')
 if not device or not boot or not seq or presence&~0x3f:raise ValueError('identity/sequence/presence range')
 if window>CFG['can']['maximum_sample_window_us']:raise ValueError('sample window exceeds contract')
 words=WORDS.unpack_from(raw,HEADER.size);timings=TIMING.unpack_from(raw,HEADER.size+WORDS.size)
 axes=[]
 for i,w in enumerate(words):
  status,count,flags=word_state(w,i<3)
  axes.append(dict(axis_id=CFG['protocol_order'][i],status=status,count=count,flags=flags))
 for node,inds in NODE_INDICES.items():
  present=bool(presence&(1<<(node-1)));delay,span=timings[2*(node-1):2*node]
  if present:
   if not span or delay+span>window or any(words[i]==MISSING for i in inds):raise ValueError('inconsistent node cohort')
  elif delay or span or any(words[i]!=MISSING for i in inds):raise ValueError('absent node contains data')
 return dict(source_kind='PD41_FULL_BODY_DIAGNOSTIC',device_id=f'{device:012x}',boot_id=str(boot),sequence=seq,sender_monotonic_us=us,
   sample_window_us=window,node_presence_mask=presence,node_timing_us=[list(timings[2*i:2*i+2]) for i in range(6)],axes=axes,
   pose_valid=all(a['status']=='valid' for a in axes[3:]),calibrated=False)

def encode_diagnostic(words,timings,device,boot,sequence,timestamp_us,window_us,presence):
 """Serializer used by offline fixtures; it never declares hardware calibration."""
 b=HEADER.pack(b'PD41',1,1,BODY_SIZE,device,boot,sequence,timestamp_us,window_us,presence,44)+WORDS.pack(*words)+TIMING.pack(*(v for t in timings for v in t))
 raw=b+struct.pack('<I',zlib.crc32(b));wire=cobs_encode(raw)
 decode(wire) # Same strict semantics on both sides of the offline reference.
 return wire+b'\0'

class Decoder:
 def __init__(self):self.buffer=bytearray();self.discard=False;self.errors=0;self.identity=None;self.seq=0;self.us=-1
 def feed(self,data):
  out=[]
  for b in data:
   if b==0:
    if self.buffer and not self.discard:
     try:
      v=decode(bytes(self.buffer));ident=(v['device_id'],v['boot_id'])
      if self.identity is not None and ident!=self.identity:raise ValueError('session changed; explicit reconnect required')
      if v['sequence']<=self.seq or v['sender_monotonic_us']<=self.us:raise ValueError('stale sequence/time')
      self.identity=ident;self.seq=v['sequence'];self.us=v['sender_monotonic_us'];out.append(v)
     except ValueError:self.errors+=1
    self.buffer.clear();self.discard=False
   elif not self.discard:
    self.buffer.append(b)
    if len(self.buffer)>FRAME_SIZE+3:self.errors+=1;self.buffer.clear();self.discard=True
  return out
