"""Prepare planes and local offline Specctra routing input; no network upload."""
from pathlib import Path
import json
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'electronics/regional_revM';NAME='PoseDoll_PD41_Regional_revM'
b=p.LoadBoard(str(D/'placement.kicad_pcb'))
# Circuit copper layers: outer signals, uninterrupted inner GND and 3V3 planes.
for layer,net in ((p.In1_Cu,'/GND'),(p.In2_Cu,'/+3V3')):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(b.FindNet(net));z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.2))
 poly=z.Outline();poly.NewOutline()
 for x,y in ((80.3,80.3),(119.7,80.3),(119.7,165.7),(80.3,165.7)):poly.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
b.BuildConnectivity();p.ZONE_FILLER(b).Fill(b.Zones())
p.SaveBoard(str(D/'route_input.kicad_pcb'),b)
assert p.ExportSpecctraDSN(b,str(D/'route_input.dsn'))
records=[]
for f in b.GetFootprints():
 for pad in f.Pads():
  records.append(dict(ref=f.GetReference(),pad=pad.GetNumber(),net=pad.GetNetname(),xy_mm=[p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)],layers=[p.LayerName(l) for l in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu) if pad.IsOnLayer(l)]))
(D/'pad_map.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('DSN ready; two inner planes; native unconnected count remains to be routed')
