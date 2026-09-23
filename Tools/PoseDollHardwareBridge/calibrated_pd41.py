"""Translate a calibrated PD41 raw frame to the existing UE sensor protocol.
Offline conversion only by default; this module never opens a serial port/socket.
"""
import argparse,hashlib,json,math,sys,uuid
from pathlib import Path
from full_diagnose import analyze
from calibrate_pd41 import ROOT
from posedoll_sim.core import DeviceProfile,IDENTITY_FIELDS,SensorDecoder

class CalibratedSource:
 def __init__(self,bundle,device_id,session=None):
  self.profile=DeviceProfile(Path(bundle));p=self.profile;c=p.calibration
  if c.get('status')!='bench_zero_direction_checked' or c.get('device_id')!=device_id:raise ValueError('Hardware calibration identity mismatch or uncalibrated bundle')
  if c.get('profile_sha256')!=p.profile_hash:raise ValueError('Calibration was made for a different geometry profile')
  self.hello=p.hello(session or str(uuid.uuid4()),True);self.hello.update(device_id=device_id,source_kind='hardware_pd41')
  self.decoder=SensorDecoder(p);self.decoder.handshake(self.hello);self.last_sequence=0;self.boot=None
 def translate(self,row):
  if row['device_id']!=self.hello['device_id']:raise ValueError('Gateway device changed')
  if self.boot is not None and self.boot!=row['boot_id']:raise ValueError('Gateway restarted; reconnect explicitly')
  self.boot=row['boot_id']
  if row['sequence']<=self.last_sequence:raise ValueError('Stale hardware frame')
  self.last_sequence=row['sequence'];raw=[];states=[]
  for i,a in enumerate(row['axes']):
   if a['axis_id']!=self.profile.order[i]:raise ValueError('Axis order changed')
   states.append(a['status']);raw.append(None if a['count'] is None else a['count']*2*math.pi/16384)
  packet={k:self.hello[k] for k in IDENTITY_FIELDS};packet.update(type='sample',sequence=str(row['sequence']),sender_monotonic_us=str(row['sender_monotonic_us']),raw_angles_rad=raw,axis_status=states)
  # Return faults as explicit rejected snapshots. Do not replay a held valid pose.
  try:
   angles=self.decoder.sample(packet);valid=True;error=None
  except ValueError as exc:
   angles=None;valid=False;error=str(exc);self.decoder.reset();self.decoder.handshake(self.hello)
  return dict(packet=packet,pose_valid=valid,angles_rad=angles,rejection=error)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 _,rows,report=analyze(a.input)
 if not rows or report['framing_or_session_errors'] or report['trailing_partial_frame_bytes']:raise ValueError('Input capture is empty or corrupt')
 src=CalibratedSource(a.bundle,rows[0]['device_id'])
 with a.out.open('x',encoding='utf-8') as f:
  f.write(json.dumps({'type':'recording_header','hello':src.hello})+'\n')
  for row in rows:f.write(json.dumps(src.translate(row),allow_nan=False)+'\n')
 print('Offline calibrated recording:',a.out)
if __name__=='__main__':main()
