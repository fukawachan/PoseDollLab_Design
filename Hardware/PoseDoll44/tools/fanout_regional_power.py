"""Seed conventional power-plane fanouts before signal routing; no remote service."""
from pathlib import Path
import pcbnew as p,json,math
D=Path(__file__).resolve().parents[1]/'electronics/regional_revM';b=p.LoadBoard(str(D/'usb_seed.kicad_pcb'));mm=p.FromMM
v=lambda q:p.VECTOR2I(mm(q[0]),mm(q[1]));xy=lambda q:(p.ToMM(q.x),p.ToMM(q.y))
layers=(p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu);pads=[q for f in b.GetFootprints() for q in f.Pads()];traces=list(b.GetTracks());log=[];failed=[]
def padclear(sh,net,layer,allnets=False):
 return not any((allnets or q.GetNetCode()!=net) and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(sh,mm(.155)) for q in pads)
def lineclear(a,z,w,net,layer):
 sh=p.SHAPE_SEGMENT(v(a),v(z),mm(w))
 return padclear(sh,net,layer) and not any(q.GetNetCode()!=net and q.IsOnLayer(layer) and q.GetEffectiveShape(layer).Collide(sh,mm(.155)) for q in traces)
def viaclear(a,net):
 if not (80.75<a[0]<119.25 and 80.75<a[1]<165.25):return False
 sh=p.SHAPE_CIRCLE(v(a),mm(.25))
 return all(padclear(sh,net,l,True) and not any(q.GetNetCode()!=net and q.IsOnLayer(l) and q.GetEffectiveShape(l).Collide(sh,mm(.155)) for q in traces) for l in layers)
def track(a,z,w,net,layer):
 if a==z:return
 q=p.PCB_TRACK(b);q.SetStart(v(a));q.SetEnd(v(z));q.SetWidth(mm(w));q.SetLayer(layer);q.SetNetCode(net);q.SetLocked(True);b.Add(q);traces.append(q)
def via(a,net):
 q=p.PCB_VIA(b);q.SetPosition(v(a));q.SetWidth(mm(.5));q.SetDrill(mm(.25));q.SetViaType(p.VIATYPE_THROUGH);q.SetLayerPair(p.F_Cu,p.B_Cu);q.SetNetCode(net);q.SetLocked(True);b.Add(q);traces.append(q)
# Four filled/capped ground vias through the module's exposed thermal pad.
for a in ((97.8,95.76),(99.2,95.76),(97.8,97.16),(99.2,97.16)):via(a,b.FindNet('/GND').GetNetCode())
offsets=sorted([(i*.25,j*.25) for i in range(-14,15) for j in range(-14,15)],key=lambda a:a[0]*a[0]+a[1]*a[1])
for q in pads:
 if q.GetNetname() not in ('/GND','/+3V3'):continue
 ref=q.GetParentFootprint().GetReference()
 if ref in ('U2','C1','C2','C3','L1') or (ref=='U1' and q.GetNumber()=='41'):continue
 net=q.GetNetCode();a=xy(q.GetPosition());layer=p.F_Cu if q.IsOnLayer(p.F_Cu) else p.B_Cu;found=None
 for w in (.2,.15):
  for t in traces:
   if isinstance(t,p.PCB_VIA) and t.GetNetCode()==net:
    z=xy(t.GetPosition())
    if math.dist(a,z)<3 and lineclear(a,z,w,net,layer):found=(z,w,True);break
  if found:break
  for dx,dy in offsets:
   z=(a[0]+dx,a[1]+dy)
   if viaclear(z,net) and lineclear(a,z,w,net,layer):found=(z,w,False);break
  if found:break
 if not found:failed.append(dict(ref=ref,pad=q.GetNumber(),net=q.GetNetname()));continue
 z,w,reuse=found;track(a,z,w,net,layer)
 if not reuse:via(z,net)
 log.append(dict(ref=ref,pad=q.GetNumber(),net=q.GetNetname(),from_mm=a,via_mm=z,width_mm=w,reused=reuse))
for q in traces:q.SetLocked(True)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'power_fanout.kicad_pcb'),b);(D/'power_fanout.kicad_pro').write_bytes((D/'placement.kicad_pro').read_bytes());assert p.ExportSpecctraDSN(b,str(D/'power_fanout.dsn'))
(D/'power_fanout_log.json').write_text(json.dumps(dict(fanouts=log,remaining=failed,physical_tested=False),indent=2),encoding='utf8');print('Power fanouts',len(log),'remaining',failed,flush=True)
