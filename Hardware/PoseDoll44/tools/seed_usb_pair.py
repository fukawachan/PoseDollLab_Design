"""USB pair pre-routing with explicit source resistors and a continuous F.Cu trunk.
This is a digital-layout candidate. Vendor stack-up confirmation and an electrical
USB check on populated boards remain required.
"""
from pathlib import Path
import pcbnew as p, math,json
D=Path(__file__).resolve().parents[1]/'electronics/regional_revM'
b=p.LoadBoard(str(D/'power_seed.kicad_pcb'));mm=p.FromMM
v=lambda a:p.VECTOR2I(mm(a[0]),mm(a[1]));xy=lambda a:(p.ToMM(a.x),p.ToMM(a.y))
fps={f.GetReference():f for f in b.GetFootprints()}
pt=lambda r,n:xy(next(q for q in fps[r].Pads() if q.GetNumber()==str(n)).GetPosition())
log=[]
def route(net,points,width=.26,layer=p.F_Cu):
 length=0.
 for a,z in zip(points,points[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetStart(v(a));t.SetEnd(v(z));t.SetWidth(mm(width));t.SetLayer(layer);t.SetNet(b.FindNet('/'+net));t.SetLocked(True);b.Add(t);length+=math.dist(a,z)
 log.append(dict(net=net,points=points,width_mm=width,layer=p.LayerName(layer),length_mm=length))
def offset_line(points,d):
 normals=[]
 for a,z in zip(points,points[1:]):
  dx,dy=z[0]-a[0],z[1]-a[1];l=math.hypot(dx,dy);normals.append((-dy/l,dx/l))
 out=[(points[0][0]+d*normals[0][0],points[0][1]+d*normals[0][1])]
 for i,q in enumerate(points[1:-1],1):
  a,c=normals[i-1],normals[i];den=1+a[0]*c[0]+a[1]*c[1];out.append((q[0]+d*(a[0]+c[0])/den,q[1]+d*(a[1]+c[1])/den))
 out.append((points[-1][0]+d*normals[-1][0],points[-1][1]+d*normals[-1][1]));return out
center=[(84.5,105.5),(80.86,109.14),(80.86,145.86),(84.5,149.5),(98.5,149.5)]
for pol,d,rr,pin in [('DP',-.225,'R11',1),('DM',.225,'R12',2)]:
 path=offset_line(center,d)
 if pol=='DP':
  y=path[-1][1];hh=1.665;path=path[:-1]+[(88,y),(88+hh,y-hh),(88.6+hh,y-hh),(88.6+2*hh,y)]+path[-1:]
 route('USB_'+pol+'_SW',[pt(rr,1)]+path+[pt('U4',pin)])
# Neckdowns are confined to the immediate module and 0603 pads.
route('USB_DP_IC',[pt('U1',14),(87.725,105.25),pt('R11',2)],.26)
route('USB_DM_IC',[pt('U1',13),(87.295,103.98),pt('R12',2)],.26)
# Host path: paired main run, controlled short divergence into the ESD array.
route('USB_DP_HOST',[pt('U4',8),(101.1,149.75),(102.15,150.8),(102.15,153.1125),pt('D2',1)])
route('USB_DM_HOST',[pt('U4',7),(100.99,150.25),(101.7,150.96),(101.7,152.2625),pt('D2',2)])
route('USB_DP_HOST',[pt('D2',1),(100.75,155.6),pt('J4','B6')],.2)
route('USB_DM_HOST',[pt('D2',2),(99.25,155.6),pt('J4','B7')],.2)
route('USB_DM_HOST',[(99.25,157.4),(100.25,157.4),pt('J4','A7')],.15)
def via(net,at):
 t=p.PCB_VIA(b);t.SetPosition(v(at));t.SetWidth(mm(.5));t.SetDrill(mm(.25));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu);t.SetNet(b.FindNet('/'+net));t.SetLocked(True);b.Add(t)
# One short cross-under joins the reversible USB-C duplicated D+ pins.
route('USB_DP_HOST',[(100.75,156.2),(101.35,156.8)],.15)
route('USB_DP_HOST',[(101.35,156.8),(101.35,160),(99.75,160),(99.75,159.8)],.26,p.B_Cu)
route('USB_DP_HOST',[(99.75,159.8),pt('J4','A6')],.15)
for at in ((101.35,156.8),(99.75,159.8)):via('USB_DP_HOST',at)
for at in ((102.05,156.1),(102.05,157.0),(98.95,160),(99.75,161)):via('GND',at)
# Ground reference island directly beneath the short back-layer crossover.
z=p.ZONE(b);z.SetLayer(p.In2_Cu);z.SetNet(b.FindNet('/GND'));z.SetAssignedPriority(1);z.SetLocalClearance(mm(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(mm(.2));poly=z.Outline();poly.NewOutline()
for at in ((98.3,155.6),(102.5,155.6),(102.5,161.6),(98.3,161.6)):poly.Append(mm(at[0]),mm(at[1]))
b.Add(z)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(D/'usb_seed.kicad_pcb'),b)
(D/'usb_seed.kicad_pro').write_bytes((D/'placement.kicad_pro').read_bytes())
(D/'usb_seed_routes.json').write_text(json.dumps(dict(routes=log,trunk_gap_mm=.19,trunk_width_mm=.26,reference='In1.Cu GND',stackup_confirmed=False,impedance_target_ohm=90,impedance_tolerance_percent=10,source='https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html'),indent=2),encoding='utf8')
print([(r['net'],round(r['length_mm'],3)) for r in log])
