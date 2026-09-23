"""Explicit buck power loops before general routing; this file does not release a PCB."""
from pathlib import Path
import pcbnew as p,json
D=Path(__file__).resolve().parents[1]/'electronics/regional_revM';b=p.LoadBoard(str(D/'placement.kicad_pcb'));mm=p.FromMM
v=lambda q:p.VECTOR2I(mm(q[0]),mm(q[1]));xy=lambda q:(p.ToMM(q.x),p.ToMM(q.y))
fps={f.GetReference():f for f in b.GetFootprints()}
pad=lambda ref,num:next(q for q in fps[ref].Pads() if q.GetNumber()==str(num))
pt=lambda ref,num:xy(pad(ref,num).GetPosition())
log=[]
def route(net,points,width=.3,layer=p.B_Cu):
 code=b.FindNet('/'+net).GetNetCode()
 for a,z in zip(points,points[1:]):
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNetCode(code);b.Add(t)
 log.append(dict(net=net,points=points,width_mm=width,layer=p.LayerName(layer)))
def via(net,at,diam=.5,drill=.25):
 t=p.PCB_VIA(b);t.SetPosition(v(at));t.SetWidth(mm(diam));t.SetDrill(mm(drill));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet('/'+net));b.Add(t)
route('SW_BUCK',[pt('U2',7),(88.5,103.75)],.3)
route('SW_BUCK',[(88.5,103.75),(88.25,103.5)],.5)
route('SW_BUCK',[(88.25,103.5),pt('L1',1)],.6)
route('+3V3',[pt('L1',2),(83.5,103.5),(83.5,108),pt('C2',1)],.6)
# VOS is a separate quiet Kelvin branch to the output capacitor.
route('+3V3',[pt('U2',6),(88.35,104.25),(88.35,106.5),(87.8,106.8),(84.55,106.8),pt('C2',1)],.15)
route('+5V_IN',[pt('U2',2),(91.4,103.75),pt('C3',1)],.3)
route('+5V_IN',[pt('U2',3),(91.3,104.25),(91.3,103.75)],.2)
route('+5V_IN',[pt('C3',1),(92.225,101.5),pt('C1',1)],.5)
route('GND',[pt('U2',1),(90.5,103.25),(90,103.4)],.2)
route('GND',[pt('U2',4),(90.5,104.75),(90,104.6)],.25)
route('GND',[pt('U2',5),(89.5,104.75),(90,104.6)],.2)
route('GND',[pt('C2',2),(90,108),(90,104.6)],.6)
route('GND',[pt('C3',2),(93.775,105.2),(90,105.2)],.5)
route('GND',[pt('C1',2),(96.3,101.5),(96.3,105.2),(93.775,105.2)],.5)
for q in ((90,103.4),(90,104.6)):via('GND',q)
route('+3V3',[(83.5,108),(83.5,108.8)],.6);via('+3V3',(83.5,108.8))
for layer,net in ((p.In1_Cu,'GND'),(p.In2_Cu,'+3V3')):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet('/'+net));z.SetLocalClearance(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.2));poly=z.Outline();poly.NewOutline()
 for a in ((80.3,80.3),(119.7,80.3),(119.7,165.7),(80.3,165.7)):poly.Append(mm(a[0]),mm(a[1]))
 b.Add(z)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'power_seed.kicad_pcb'),b);(D/'power_seed.kicad_pro').write_bytes((D/'placement.kicad_pro').read_bytes())
(D/'power_seed_routes.json').write_text(json.dumps(dict(routes=log,thermal_vias='2 x 0.25 mm drilled, 0.50 mm copper; filled and copper capped underneath U2 thermal pad',source='https://www.ti.com/lit/ds/symlink/tps62162.pdf',physical_verified=False),indent=2),encoding='utf8')
print('Explicit buck routing seeded; native DRC required')
