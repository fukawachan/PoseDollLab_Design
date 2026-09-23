"""Read-only H1 capture and offline analysis; never sends pose data to UE."""
import argparse,json,time,statistics,sys,threading
from pathlib import Path
from h1_protocol import Decoder
MAX_CAPTURE_BYTES=64*1024*1024
def summary(samples,errors):
    valid=[v for v in samples if v["status"]=="valid"]
    degrees=[];last=None
    for v in valid:
        x=v["raw_degrees"]
        if last is not None:x=last+(x-last+180)%360-180
        degrees.append(x);last=x
    durations=(samples[-1]["sender_monotonic_us"]-samples[0]["sender_monotonic_us"])/1e6 if len(samples)>1 else 0
    gaps=sum(max(0,b["sequence"]-a["sequence"]-1) for a,b in zip(samples,samples[1:]))
    return {"frames":len(samples),"valid_frames":len(valid),"framing_or_session_errors":errors,"sequence_gaps":gaps,
      "raw_noise_rms_deg":statistics.pstdev(degrees) if len(degrees)>1 else None,
      "raw_peak_to_peak_deg":max(degrees)-min(degrees) if degrees else None,
      "time_span_source_s":durations,"received_source_rate_hz":(len(samples)-1)/durations if durations>0 else None,
      "max_read_window_us":max((v["read_window_us"] for v in samples),default=None),
      "interpretation":"Noise metrics require a mechanically fixed axis. Sequence gaps are dropped epochs. No accuracy or hardware-pass claim."}
def output_paths(dest):
    return [Path(str(dest)+s) for s in (".bin",".jsonl",".summary.json")]
def check_destination(dest):
    paths=output_paths(dest)
    if any(p.exists() for p in paths):raise ValueError("Output exists; choose a new recording name")
    paths[0].parent.mkdir(parents=True,exist_ok=True)
    return paths
def write_record(dest,data,rows,report):
    paths=check_destination(dest)
    # Exclusive creation avoids silently overwriting another capture.
    with paths[0].open("xb") as f:f.write(data)
    with paths[1].open("x",encoding="utf8") as f:
        for row in rows:f.write(json.dumps(row)+"\n")
    with paths[2].open("x",encoding="utf8") as f:json.dump(report,f,indent=2)
def capture(port,seconds,dest,stop=None,progress=None):
    import serial
    if not 0<seconds<=3600:raise ValueError("seconds must be in (0,3600]")
    check_destination(dest)
    d=Decoder();rows=[];raw=bytearray();error=None;cancelled=False
    s=serial.Serial(port=None,baudrate=115200,timeout=.1,write_timeout=.1)
    s.dtr=False;s.rts=False;s.port=port
    # Deassert before opening. Some OS/drivers may nevertheless toggle control lines.
    s.open();deadline=time.monotonic()+seconds
    try:
        with s:
            while time.monotonic()<deadline:
                if stop is not None and stop.is_set():cancelled=True;break
                block=s.read(4096);raw.extend(block)
                if len(raw)>MAX_CAPTURE_BYTES:raise RuntimeError("Capture budget exceeded")
                for v in d.feed(block):
                    rows.append(v)
                    if progress and len(rows)%10==0:progress(v,len(rows),d.errors)
    except Exception as exc:error=f"{type(exc).__name__}: {exc}"
    report=summary(rows,d.errors);report.update(cancelled=cancelled,transport_error=error,port=port,
        requested_seconds=seconds,trailing_partial_frame_bytes=len(d.buffer))
    write_record(dest,raw,rows,report)
    return report
def list_ports():
    import serial.tools.list_ports
    return [{"port":v.device,"description":v.description,"hwid":v.hwid} for v in serial.tools.list_ports.comports()]
def main():
    p=argparse.ArgumentParser();p.add_argument("--ports",action="store_true");p.add_argument("--port");p.add_argument("--input",type=Path);p.add_argument("--seconds",type=float,default=10);p.add_argument("--out",type=Path,default=Path("h1_measurement"))
    args=p.parse_args()
    if args.ports:print(json.dumps(list_ports(),ensure_ascii=False,indent=2));return
    if bool(args.port)==bool(args.input):p.error("Choose --input recording.bin or an explicitly verified --port COMn")
    if args.input:
        if args.input.stat().st_size>MAX_CAPTURE_BYTES:p.error("Input exceeds 64 MiB budget")
        d=Decoder();data=args.input.read_bytes();rows=d.feed(data);report=summary(rows,d.errors);report["trailing_partial_frame_bytes"]=len(d.buffer)
        write_record(args.out,data,rows,report)
    else:
        report=capture(args.port,args.seconds,args.out,progress=lambda v,n,e:print(json.dumps({"frames":n,"errors":e,**v})) if n%100==0 else None)
    print(json.dumps(report,indent=2))
    if not report["frames"] or report["frames"]!=report["valid_frames"] or report["framing_or_session_errors"] or report.get("transport_error"):sys.exit(2)
if __name__=="__main__":main()
