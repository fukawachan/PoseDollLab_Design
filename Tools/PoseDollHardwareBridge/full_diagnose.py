"""PD41 full-body capture and offline reports. No UE connection or calibration claim."""
import argparse,json,time,math,statistics,sys
from pathlib import Path
from pd41_protocol import Decoder,CFG
from diagnose import MAX_CAPTURE_BYTES,check_destination,write_record,list_ports

def summary(samples,errors):
 axes=[]
 for i,aid in enumerate(CFG['protocol_order']):
  counts={k:0 for k in ('valid','invalid','missing','fixed')};runs=[];current=[];previous=None;last_seq=None;flags=0
  for row in samples:
   a=row['axes'][i];counts[a['status']]+=1;flags|=a['flags']
   if a['status']!='valid':
    if current:runs.append(current)
    current=[];previous=None;last_seq=None;continue
   raw=a['count']*360/16384
   if last_seq is not None and row['sequence']!=last_seq+1:
    if current:runs.append(current)
    current=[];previous=None
   value=raw if previous is None else previous+(raw-previous+180)%360-180
   current.append(value);previous=value;last_seq=row['sequence']
  if current:runs.append(current)
  axes.append(dict(axis_id=aid,states=counts,fault_flags_seen=flags,valid_run_count=len(runs),
   max_contiguous_run_peak_to_peak_deg=max((max(r)-min(r) for r in runs),default=None),
   max_contiguous_run_stddev_deg=max((statistics.pstdev(r) for r in runs if len(r)>1),default=None)))
 span=(samples[-1]['sender_monotonic_us']-samples[0]['sender_monotonic_us'])/1e6 if len(samples)>1 else 0
 return dict(type='posedoll.pd41.diagnostic_report/1',frames=len(samples),complete_valid_frames=sum(r['pose_valid'] for r in samples),
  framing_or_session_errors=errors,sequence_gaps=sum(max(0,b['sequence']-a['sequence']-1) for a,b in zip(samples,samples[1:])),
  time_span_source_s=span,received_source_rate_hz=(len(samples)-1)/span if span>0 else None,
  maximum_transport_envelope_us=max((r['sample_window_us'] for r in samples),default=None),
  node_present_frames={str(n):sum(bool(r['node_presence_mask']&(1<<(n-1))) for r in samples) for n in range(1,7)},
  axes=axes,calibrated=False,physical_acceptance=False,
  interpretation='Raw spread describes each continuous valid run. Keep the doll mechanically stationary to interpret it as noise. Gaps and faults split runs. This is not absolute angle accuracy or an assembly pass.')

def capture(port,seconds,dest,stop=None,progress=None):
 import serial
 if not 0<seconds<=3600:raise ValueError('seconds must be in (0,3600]')
 check_destination(dest);decoder=Decoder();rows=[];raw=bytearray();error=None;cancelled=False
 connection=serial.Serial(port=None,baudrate=115200,timeout=.1,write_timeout=.1);connection.dtr=False;connection.rts=False;connection.port=port
 connection.open();deadline=time.monotonic()+seconds
 try:
  with connection:
   while time.monotonic()<deadline:
    if stop is not None and stop.is_set():cancelled=True;break
    data=connection.read(4096);raw.extend(data)
    if len(raw)>MAX_CAPTURE_BYTES:raise RuntimeError('Capture budget exceeded')
    for row in decoder.feed(data):
     rows.append(row)
     if progress and len(rows)%6==0:progress(row,len(rows),decoder.errors)
 except Exception as exc:error=f'{type(exc).__name__}: {exc}'
 report=summary(rows,decoder.errors);report.update(cancelled=cancelled,transport_error=error,port=port,requested_seconds=seconds,trailing_partial_frame_bytes=len(decoder.buffer))
 write_record(dest,raw,rows,report);return report

def analyze(path):
 path=Path(path)
 if path.stat().st_size>MAX_CAPTURE_BYTES:raise ValueError('Input exceeds 64 MiB budget')
 data=path.read_bytes();d=Decoder();rows=d.feed(data);report=summary(rows,d.errors);report['trailing_partial_frame_bytes']=len(d.buffer);return data,rows,report

def main():
 p=argparse.ArgumentParser();p.add_argument('--ports',action='store_true');g=p.add_mutually_exclusive_group();g.add_argument('--port');g.add_argument('--input',type=Path);p.add_argument('--seconds',type=float,default=10);p.add_argument('--out',type=Path);a=p.parse_args()
 if a.ports:print(json.dumps(list_ports(),ensure_ascii=False,indent=2));return
 if not a.port and not a.input:p.error('Choose an offline --input or an explicitly verified --port')
 if a.input:
  data,rows,report=analyze(a.input)
  if a.out:write_record(a.out,data,rows,report)
 else:
  if not a.out:p.error('Live capture requires an explicit --out recording prefix')
  report=capture(a.port,a.seconds,a.out)
 print(json.dumps(report,ensure_ascii=False,indent=2))
 if not report['frames'] or report['complete_valid_frames']!=report['frames'] or report['framing_or_session_errors'] or report.get('transport_error') or report.get('trailing_partial_frame_bytes'):sys.exit(2)
if __name__=='__main__':main()
