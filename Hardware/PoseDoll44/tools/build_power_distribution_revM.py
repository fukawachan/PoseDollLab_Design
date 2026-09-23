"""Six protected 5 V branches, native KiCad project. No fabrication release.
External regulated 5 V / 3 A supply only, no battery or mains circuits.
"""
from pathlib import Path
import json,uuid,subprocess,re,xml.etree.ElementTree as ET
import pcbnew as pcb
import build_regional_revM as g
R=Path(__file__).resolve().parents[1];O=R/'electronics/power_revM';O.mkdir(exist_ok=True)
g.OUT=O;g.NAME='PoseDoll_PD41_Power_revM';g.NS=uuid.UUID('57acebf7-f8f6-450a-8f48-1ecb08e8c9d0');g.comps=[]
old_custom=g.custom_symbol

def custom(name):
 if name!='AO4409':return old_custom(name)
 defs=[(1,'S','passive'),(2,'S','passive'),(3,'S','passive'),(4,'G','input'),(5,'D','passive'),(6,'D','passive'),(7,'D','passive'),(8,'D','passive')];ps=[]
 for i,(n,lab,typ) in enumerate(defs):
  sg=-1 if i<4 else 1;y=3.81-2.54*(i%4);a=0 if sg<0 else 180
  ps.append(f'(pin {typ} line (at {sg*17.78} {y} {a}) (length 5.08) (name "{lab}" {g.effect()}) (number "{n}" {g.effect()}))')
 return f'(symbol "AO4409" (pin_names (offset 0.5)) (in_bom yes) (on_board yes) (property "Reference" "Q" (at 0 8.89 0) {g.effect()}) (property "Value" "AO4409" (at 0 11.43 0) {g.effect()}) (symbol "AO4409_0_1" (rectangle (start -12.7 6.35) (end 12.7 -6.35) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "AO4409_1_1" {" ".join(ps)}))'
g.custom_symbol=custom

def components():
 for i,(x,y) in enumerate([(36,40),(62,40),(36,55),(62,55),(36,70),(62,70)],1):
  net=f'NODE{i}_5V';g.part(f'J{i+1}','Connector_Generic','Conn_01x02',f'N{i}: +5V / GND','Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical',{1:net,2:'GND'},(x,y),section='output')
  left=x<50;g.part(f'F{i}','Device','Polyfuse','1206L075/13.2WR / 0.75A hold','Fuse:Fuse_1206_3216Metric',{1:net if left else '+5V_BUS',2:'+5V_BUS' if left else net},(45 if left else 55,y),section='output')
 g.part('J1','Connector','Barrel_Jack_Switch','PJ-002AH / regulated 5V center +','PoseDoll:PJ_002AH_verified',{1:'RAW_5V',2:'GND',3:'GND'},(50,86.3),angle=90,section='input')
 g.part('F0','Device','Fuse','0451003.MRL / 3A','Fuse:Fuse_Littelfuse-NANO2-451_453',{1:'RAW_5V',2:'FUSED_5V'},(60,86.3),section='input')
 g.part('Q1','PoseDoll','AO4409','AO4409 / reverse polarity','Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',{1:'+5V_BUS',2:'+5V_BUS',3:'+5V_BUS',4:'GATE',5:'FUSED_5V',6:'FUSED_5V',7:'FUSED_5V',8:'FUSED_5V'},(50,80),section='input')
 g.resistor('R1','100k','GATE','GND',(42,83),angle=180,section='input')
 g.part('C1','Device','C_Polarized','EEEFP1C101AP / 100u 16V','Capacitor_SMD:CP_Elec_6.3x5.8',{1:'+5V_BUS',2:'GND'},(40,91),section='input')
 g.resistor('R2','1k','+5V_BUS','LED_A',(62,93),section='indicator')
 g.part('D1','Device','LED','LTST-C190KGKT / green','LED_SMD:LED_0603_1608Metric',{1:'GND',2:'LED_A'},(62,96),section='indicator')
 for i,(x,y) in enumerate([(33,33),(67,33),(33,88),(67,88)],1):g.part(f'H{i}','Mechanical','MountingHole','M2 clearance','MountingHole:MountingHole_2.2mm_M2',{},(x,y),section='mount')

def footprint():
 folder=O/'PoseDoll.pretty';folder.mkdir(exist_ok=True)
 # Origin is terminal 1. Dimensions read from Same Sky drawing, 2024-09-12 p2.
 # The switched terminal and sleeve are both GND; no switched-power function.
 txt='(footprint "PJ_002AH_verified" (version 20241209) (generator "posedoll_hw44") (layer "F.Cu") (attr through_hole) (descr "Same Sky PJ-002AH: p1 center, other contacts GND; slotted holes per drawing") (property "Reference" "J" (at 0 -6 0) (layer "F.SilkS") (effects (font (size 1 1)))) (property "Value" "PJ-002AH" (at 0 7 0) (layer "F.Fab") (effects (font (size 1 1))))'
 for layer,margin in [('F.Fab',0),('F.CrtYd',.5)]:
  txt+=f'(fp_rect (start {-13.7-margin} {-4.5-margin}) (end {.7+margin} {5.2+margin}) (stroke (width 0.05) (type default)) (fill none) (layer "{layer}"))'
 for n,x,y,sx,sy,dx,dy in [(1,0,0,2.5,5,1,3.5),(2,-6,0,2.5,5,1,3.5),(3,-3,4.7,5,2.5,3,1)]:txt+=f'(pad "{n}" thru_hole oval (at {x} {y}) (size {sx} {sy}) (drill oval {dx} {dy}) (layers "*.Cu" "*.Mask"))'
 (folder/'PJ_002AH_verified.kicad_mod').write_text(txt+')',encoding='utf8')

def main():
 components();footprint();root=g.schematic();schpath=O/(g.NAME+'.kicad_sch');sch=schpath.read_text(encoding='utf8');sch=re.sub(r'(\(symbol \(lib_id "Mechanical:MountingHole"\) .*?\(in_bom )yes',r'\1no',sch);schpath.write_text(sch,encoding='utf8');exe=str(g.LIB.parents[1]/'bin/kicad-cli.exe')
 subprocess.run([exe,'sch','export','netlist','--format','kicadxml','-o',str(O/'netlist.xml'),str(O/(g.NAME+'.kicad_sch'))],check=True)
 b=pcb.BOARD();b.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.6));nets={};mapping={}
 for el in ET.parse(O/'netlist.xml').findall('./nets/net'):
  n=pcb.NETINFO_ITEM(b,el.attrib['name'],int(el.attrib['code']));b.Add(n);nets[el.attrib['name'].lstrip('/')]=n
  for x in el.findall('node'):mapping[x.attrib['ref'],x.attrib['pin']]=n
 fps={}
 for c in g.comps:
  lib,fp=c['fp'].split(':');f=pcb.FootprintLoad(str(O/'PoseDoll.pretty' if lib=='PoseDoll' else g.LIB/'footprints'/(lib+'.pretty')),fp);assert f,c['fp']
  f.SetReference(c['ref']);f.SetValue(c['value']);f.SetFPID(pcb.LIB_ID(lib,fp));f.SetPosition(pcb.VECTOR2I(*[pcb.FromMM(v) for v in c['pcb']]));f.SetOrientationDegrees(c['angle']);b.Add(f)
  path=pcb.KIID_PATH();path.push_back(pcb.KIID(root));path.push_back(pcb.KIID(g.uid(c['ref'])));f.SetPath(path)
  for pad in f.Pads():
   n=mapping.get((c['ref'],pad.GetNumber()))
   if n:pad.SetNet(n)
  f.Reference().SetVisible(False);f.Value().SetVisible(False);fps[c['ref']]=f
 for a,z in zip([(30,30),(70,30),(70,100),(30,100)],[(70,30),(70,100),(30,100),(30,30)]):
  s=pcb.PCB_SHAPE();s.SetShape(pcb.SHAPE_T_SEGMENT);s.SetLayer(pcb.Edge_Cuts);s.SetWidth(pcb.FromMM(.05));s.SetStart(pcb.VECTOR2I(*[pcb.FromMM(x) for x in a]));s.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(x) for x in z]));b.Add(s)
 def pt(ref,pin):return tuple(pcb.ToMM(v) for v in next(p for p in fps[ref].Pads() if p.GetNumber()==str(pin)).GetPosition())
 def track(net,points,width=.8,layer=pcb.F_Cu):
  for a,z in zip(points,points[1:]):
   if a==z:continue
   t=pcb.PCB_TRACK(b);t.SetNet(nets[net]);t.SetWidth(pcb.FromMM(width));t.SetLayer(layer);t.SetStart(pcb.VECTOR2I(*[pcb.FromMM(x) for x in a]));t.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(x) for x in z]));b.Add(t)
 # Wide DC spine and separate fused branches, no thin autorouted power bottleneck.
 track('+5V_BUS',[(50,40),(50,74),(45,74),(45,80.635)],1.5)
 for i in (1,2,3):p=pt('Q1',i);track('+5V_BUS',[p,(45,p[1])],1.0)
 for i in range(1,7):
  left=i%2==1;inp=pt(f'F{i}',2 if left else 1);op=pt(f'F{i}',1 if left else 2);dest=pt(f'J{i+1}',1)
  track('+5V_BUS',[(50,inp[1]),inp],1.)
  track(f'NODE{i}_5V',[op,(op[0],op[1]-3),(dest[0],op[1]-3),dest] if left else [op,dest],.8)
 track('RAW_5V',[pt('J1',1),(50,84.2),(pt('F0',1)[0],84.2),pt('F0',1)],1.5)
 pp=pt('F0',2);track('FUSED_5V',[pp,(64,pp[1]),(64,77),(54,77),(54,81.905)],1.5)
 for i in (5,6,7,8):p=pt('Q1',i);track('FUSED_5V',[p,(54,p[1])],1.)
 track('GATE',[pt('Q1',4),(45,83),pt('R1',1)],.3)
 # Bulk capacitor and indicator branches are routed on the back to keep clear
 # of the DC jack body; through vias are explicit at each SMD endpoint.
 def via(net,p):
  v=pcb.PCB_VIA(b);v.SetPosition(pcb.VECTOR2I(*[pcb.FromMM(x) for x in p]));v.SetWidth(pcb.FromMM(.8));v.SetDrill(pcb.FromMM(.4));v.SetViaType(pcb.VIATYPE_THROUGH);v.SetLayerPair(pcb.F_Cu,pcb.B_Cu);v.SetNet(nets[net]);b.Add(v)
 for ref,pin,xy in [('C1',1,(35.5,88)),('R2',1,(60,91.5))]:
  pad=pt(ref,pin);track('+5V_BUS',[pad,xy],.6);via('+5V_BUS',xy);track('+5V_BUS',[xy,(35.5,xy[1]),(35.5,75),(45,75)] if ref=='C1' else [xy,(60,84),(35.5,84),(35.5,75),(45,75)],.8,pcb.B_Cu)
 via('+5V_BUS',(45,75))
 track('LED_A',[pt('R2',2),(64,93),(64,96),pt('D1',2)],.3)
 # Ground plane, with PTH/via stitching to all top-layer ground pads.
 for ref,pin,xy in [('R1',2,(43.5,85)),('C1',2,(43,91)),('D1',1,(60,97.5))]:
  track('GND',[pt(ref,pin),xy],.5);via('GND',xy)
 zone=pcb.ZONE(b);zone.SetLayer(pcb.B_Cu);zone.SetNet(nets['GND']);zone.SetLocalClearance(pcb.FromMM(.3));zone.SetThermalReliefGap(pcb.FromMM(.3));zone.SetThermalReliefSpokeWidth(pcb.FromMM(.6));zone.SetPadConnection(pcb.ZONE_CONNECTION_FULL);outline=zone.Outline();outline.NewOutline()
 for x,y in [(30.5,30.5),(69.5,30.5),(69.5,99.5),(30.5,99.5)]:outline.Append(pcb.FromMM(x),pcb.FromMM(y))
 b.Add(zone)
 b.GetDesignSettings().SetAuxOrigin(pcb.VECTOR2I(pcb.FromMM(50),pcb.FromMM(65)))
 pcb.SaveBoard(str(O/(g.NAME+'.kicad_pcb')),b)
 pro=json.loads((R/'electronics/sensor_revB/PoseDoll_AS5048A_revB.kicad_pro').read_text(encoding='utf8'));pro['meta']['filename']=g.NAME+'.kicad_pro';pro['board']['design_settings']['rules'].update(min_track_width=.25,min_clearance=.2,min_copper_edge_clearance=.3);pro['net_settings']['classes'][0].update(track_width=.3,clearance=.2)
 (O/(g.NAME+'.kicad_pro')).write_text(json.dumps(pro,indent=2),encoding='utf8')
 libs=sorted({c['fp'].split(':')[0] for c in g.comps});(O/'fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name "{lib}") (type "KiCad") (uri "'+('${KIPRJMOD}/PoseDoll.pretty' if lib=='PoseDoll' else str(g.LIB/'footprints'/(lib+'.pretty')).replace('\\','/'))+'") (options "") (descr ""))' for lib in libs)+')',encoding='utf8')
 (O/'connectivity.json').write_text(json.dumps(g.comps,indent=2),encoding='utf8');(O/'pad_map.json').write_text(json.dumps({r:{p.GetNumber():[pcb.ToMM(p.GetPosition().x),pcb.ToMM(p.GetPosition().y),p.GetNetname()] for p in f.Pads()} for r,f in fps.items()},indent=2),encoding='utf8')
 print(O,flush=True)
if __name__=='__main__':main()
