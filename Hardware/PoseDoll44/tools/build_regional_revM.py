"""Native KiCad common nine-port PD41 regional board, generated from reviewed pin maps.
Intermediate placement; ERC/DRC, routing and electro-mechanical integration are separate gates.
"""
from pathlib import Path
import json,math,uuid,re,subprocess,sys,xml.etree.ElementTree as ET
import pcbnew as pcb
from build_sensor_revC_mini import extract,parse,prop,children,pins,q,effect,LIB
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'electronics/regional_revM';OUT.mkdir(parents=True,exist_ok=True)
NAME='PoseDoll_PD41_Regional_revM';NS=uuid.UUID('31232018-853a-4f31-b864-81f2db58c71c')
def uid(s):return str(uuid.uuid5(NS,str(s)))
RFP='Resistor_SMD:R_0603_1608Metric';CFP='Capacitor_SMD:C_0603_1608Metric'
CS=[2,4,5,6,7,8,9,10,14]
comps=[]
def part(ref,lib,sym,value,fp,nets,xy,angle=0,back=False,section='control'):
 c=dict(ref=ref,lib=lib,sym=sym,value=value,fp=fp,nets={str(k):v for k,v in nets.items()},pcb=xy,angle=angle,back=back,section=section);comps.append(c);return c

def resistor(ref,value,a,b,xy,**kw):return part(ref,'Device','R',value,RFP,{1:a,2:b},xy,**kw)
def capacitor(ref,value,a,b,xy,fp=CFP,**kw):return part(ref,'Device','C',value,fp,{1:a,2:b},xy,**kw)

def components():
 m={str(i):None for i in range(1,42)};m.update({'1':'GND','2':'+3V3','3':'EN','10':'CAN_TX','11':'CAN_RX','13':'USB_DM_IC','14':'USB_DP_IC','19':'SPI_MOSI','20':'SPI_SCK','21':'SPI_MISO','27':'BOOT_N','36':'UART_RX','37':'UART_TX','40':'GND','41':'GND'})
 io_pin={2:38,4:4,5:5,6:6,7:7,8:12,9:17,10:18,14:22}
 for i,gpio in enumerate(CS,1):m[str(io_pin[gpio])]=f'CS{i}_MCU'
 part('U1','RF_Module','ESP32-S3-WROOM-1','ESP32-S3-WROOM-1-N8','RF_Module:ESP32-S3-WROOM-1',m,(100,94))
 part('U2','Regulator_Switching','TPS62162DSG','TPS62162DSGR','Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm',{1:'GND',2:'+5V_IN',3:'+5V_IN',4:'GND',5:'GND',6:'+3V3',7:'SW_BUCK',8:'PG',9:'GND'},(90,104),back=True,section='power')
 part('L1','Device','L','LSXND4040TKL2R2MDG / 2.2uH','Inductor_SMD:L_Taiyo-Yuden_NR-40xx',{1:'SW_BUCK',2:'+3V3'},(95,104),back=True,section='power')
 capacitor('C1','10u X5R 25V / CL21A106KAYNNNE','+5V_IN','GND',(88,101),fp='Capacitor_SMD:C_0805_2012Metric',back=True,section='power')
 capacitor('C2','22u X5R 16V / CL21A226MOYNNNE','+3V3','GND',(99,104),fp='Capacitor_SMD:C_0805_2012Metric',back=True,section='power')
 capacitor('C3','100n X7R','+5V_IN','GND',(87,104),back=True,section='power')
 capacitor('C4','22u X5R 16V / CL21A226MOYNNNE','+3V3','GND',(92,95),fp='Capacitor_SMD:C_0805_2012Metric',back=True,section='power')
 capacitor('C5','100n X7R','+3V3','GND',(96,95),back=True,section='power')
 resistor('R1','10k','+3V3','EN',(98,98),back=True)
 capacitor('C6','1u X7R','EN','GND',(101,98),back=True)
 resistor('R2','10k','+3V3','BOOT_N',(104,98),back=True)
 resistor('R3','100k','+3V3','PG',(90,108),back=True,section='power')
 for ref,net,xy in [('SW1','EN',(86,91)),('SW2','BOOT_N',(114,91))]:part(ref,'Switch','SW_Push','RESET' if ref=='SW1' else 'BOOT','Button_Switch_SMD:SW_SPST_TL3305A',{1:net,2:'GND'},xy)
 part('J1','Connector_Generic','Conn_01x02','5V from fused pelvis star','Connector_JST:JST_PH_B2B-PH-SM4-TB_1x02-1MP_P2.00mm_Vertical',{1:'+5V_IN',2:'GND'},(87,111),section='power')
 part('J2','Connector_Generic','Conn_01x03','CAN IN / GND-L-H','Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical',{1:'GND',2:'CAN_L',3:'CAN_H'},(101,111),section='can')
 part('J3','Connector_Generic','Conn_01x03','CAN OUT / GND-L-H','Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical',{1:'GND',2:'CAN_L',3:'CAN_H'},(111,111),section='can')
 part('U3','Interface_CAN_LIN','TCAN332','TCAN332DR','Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',{1:'CAN_TX',2:'GND',3:'+3V3',4:'CAN_RX',5:None,6:'CAN_L',7:'CAN_H',8:None},(109,104),back=True,section='can')
 capacitor('C7','100n X7R','+3V3','GND',(114,104),back=True,section='can')
 resistor('R4','10k','+3V3','CAN_TX',(111,99),back=True,section='can')
 resistor('R5','120R 1% 0.33W / CRCW0603120RFKEAHP','CAN_H','TERM_R',(106,96),back=True,section='can')
 part('JP1','Jumper','Jumper_2_Open','CAN TERM: close endpoints only','Connector_PinHeader_2.00mm:PinHeader_1x02_P2.00mm_Vertical',{1:'TERM_R',2:'CAN_L'},(110,96),back=True,section='can')
 part('D1','PoseDoll','PESD5V0S2BT','PESD5V0S2BT,215','Package_TO_SOT_SMD:SOT-23',{1:'CAN_L',2:'CAN_H',3:'GND'},(105,108),back=True,section='can')
 # Data-only USB, electrically disconnected unless both local power and host VBUS exist.
 usb={'A1':'GND','A4':'VBUS_USB','A5':'CC1','A6':'USB_DP_HOST','A7':'USB_DM_HOST','A8':None,'A9':'VBUS_USB','A12':'GND','B1':'GND','B4':'VBUS_USB','B5':'CC2','B6':'USB_DP_HOST','B7':'USB_DM_HOST','B8':None,'B9':'VBUS_USB','B12':'GND','SH':'GND'}
 part('J4','Connector','USB_C_Receptacle_USB2.0_16P','USB data only; external 5V required','PoseDoll:USB_C_Data_Port',usb,(100,153),angle=180,section='usb')
 part('U4','PoseDoll','TS3USB221ERSE','TS3USB221ERSER','Package_DFN_QFN:Texas_UQFN-10_1.5x2mm_P0.5mm',{1:'USB_DP_SW',2:'USB_DM_SW',3:None,4:None,5:'GND',6:'USB_OE_N',7:'USB_DM_HOST',8:'USB_DP_HOST',9:'GND',10:'+3V3'},(100,146),section='usb')
 part('Q1','Transistor_BJT','MMBT3904','MMBT3904','Package_TO_SOT_SMD:SOT-23',{1:'VBUS_BASE',2:'GND',3:'USB_OE_N'},(105,146),section='usb')
 resistor('R6','100k','VBUS_USB','VBUS_BASE',(110,146),section='usb')
 resistor('R7','100k','VBUS_BASE','GND',(113,146),section='usb')
 resistor('R8','100k','+3V3','USB_OE_N',(106,149),section='usb')
 resistor('R9','5.1k 1%','CC1','GND',(93,148),section='usb')
 resistor('R10','5.1k 1%','CC2','GND',(93,151),section='usb')
 resistor('R11','22R','USB_DP_SW','USB_DP_IC',(96,144),section='usb')
 resistor('R12','22R','USB_DM_SW','USB_DM_IC',(96,146),section='usb')
 capacitor('C8','100n X7R','+3V3','GND',(102,143),section='usb')
 part('D2','Power_Protection','TPD2E2U06DCK','TPD2E2U06DCKR','Package_TO_SOT_SMD:SOT-323_SC-70',{1:'USB_DP_HOST',2:'USB_DM_HOST',3:'GND'},(97,150),section='usb')
 # Each sensor port is a separate star cable. SCK/MOSI outputs and MISO input gate use CS.
 for i,gpio in enumerate(CS,1):
  x=88+12*((i-1)%3);y=119+9*((i-1)//3);tag=f'P{i}';cs=f'CS{i}_MCU';sec=f'port{i}'
  part(f'U{10+i}','PoseDoll','LVC125_QUAD','SN74LVC125APWR','Package_SO:TSSOP-14_4.4x5mm_P0.65mm',{1:cs,2:'SPI_SCK',3:tag+'_SCK_DRV',4:cs,5:'SPI_MOSI',6:tag+'_MOSI_DRV',7:'GND',8:'SPI_MISO',9:tag+'_MISO',10:cs,11:tag+'_CS_DRV',12:cs,13:'GND',14:'+3V3'},(x,y),section=sec)
  part(f'J{10+i}','Connector_Generic','Conn_01x06',f'{tag} sensor / CS GPIO{gpio}','Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical',{1:'GND',2:'+3V3',3:tag+'_SCK',4:tag+'_MOSI',5:tag+'_MISO',6:tag+'_CS'},(x,y),back=True,section=sec)
  n=100+i*10
  for j,signal in enumerate(('SCK','MOSI','CS')):resistor(f'R{n+j}','100R',tag+'_'+signal+'_DRV',tag+'_'+signal,(x-4+j*3,y+3.5),section=sec)
  resistor(f'R{n+3}','10k','+3V3',cs,(x-4,y-3.5),section=sec)
  resistor(f'R{n+4}','47k',tag+'_SCK','GND',(x-4,y-3),back=True,section=sec)
  resistor(f'R{n+5}','47k',tag+'_MOSI','GND',(x,y-3),back=True,section=sec)
  resistor(f'R{n+6}','100k',tag+'_MISO','GND',(x+4,y-3),back=True,section=sec)
  resistor(f'R{n+7}','10k','+3V3',tag+'_CS',(x+2,y-3.5),section=sec)
  capacitor(f'C{20+i}','100n X7R','+3V3','GND',(x+4,y+3),back=True,section=sec)
 for i,net in enumerate(('+5V_IN','+3V3','GND','VBUS_USB')):part(f'#FLG0{i+1}','power','PWR_FLAG','PWR_FLAG','',{1:net},(0,0),section='power')
 for i,(net,xy) in enumerate([('UART_TX',(86,98)),('UART_RX',(86,100)),('GND',(86,102)),('PG',(86,104))],1):part(f'TP{i}','Connector','TestPoint',net,'TestPoint:TestPoint_Pad_D1.0mm',{1:net},xy,section='control')
 for c in comps:
  ref=c['ref']
  if ref in ('SW1','SW2'):c['angle']=90;c['pcb']=(86 if ref=='SW1' else 114,94)
  if ref=='JP1':c['pcb']=(113,160)
  if ref=='R5':c['pcb']=(112,156)
  if ref=='R3':c['pcb']=(115,108)
  if ref=='J1':c['pcb']=(88,110)
  if ref in ('J2','J3'):c['pcb']=(102 if ref=='J2' else 111,110)
  if ref in ('R11','R12'):c['pcb']=(94 if ref=='R11' else 97,109);c['back']=True
  if ref.startswith('TP'):c['pcb']=(86,99+int(ref[2:])*2)
  if c['section']=='usb' and ref not in ('R11','R12'):
   x,y=c['pcb'];c['pcb']=(x,y+9)
  if c['section'].startswith('port'):
   i=int(c['section'][4:]);x0,y0=88+12*((i-1)%3),119+9*((i-1)//3);x,y=c['pcb'];dy=y-y0
   if abs(dy)>=3:dy=4.3 if dy>0 else -4.3
   c['pcb']=(x,118+11*((i-1)//3)+dy)
 fix={'R1':(94,99.6),'R113':(83,113.7),'U3':(109,102),'R4':(116,102),'C8':(107,152),'TP3':(83,104),'L1':(85.5,103.5),'C1':(94.5,101.5),'C2':(85.5,108),'C3':(93,103.9),'C4':(93,97),'C5':(94,93),'C7':(116,104),'D1':(106,110),'D2':(100,155.5),'R3':(116,108),'R8':(105,150),'U4':(100,150),'J1':(85.4,153),'J2':(100,109),'J3':(112,109),'R11':(86,106.2),'R12':(86,104.45),'TP4':(83,101),'TP2':(88.25,101)}
 for c in comps:
  if c['ref'] in fix:c['pcb']=fix[c['ref']]
  if c['ref'] in ('J2','J3'):c['back']=True
  if c['ref'] in ('D1','R3','R4','R11','R12'):c['back']=False
  if c['ref']=='J4':c['angle']=0
  if c['ref']=='D2':c['angle']=-90
  if c['ref'] in ('C1','C2','C3'):c['angle']=180
  if c['ref']=='L1':c['angle']=0
 return comps

def custom_symbol(name):
 if name=='LVC125_QUAD':
  defs=[(1,'1OE_N','input'),(2,'1A','input'),(3,'1Y','tri_state'),(4,'2OE_N','input'),(5,'2A','input'),(6,'2Y','tri_state'),(7,'GND','power_in'),(8,'3Y','tri_state'),(9,'3A','input'),(10,'3OE_N','input'),(11,'4Y','tri_state'),(12,'4A','input'),(13,'4OE_N','input'),(14,'VCC','power_in')]
 elif name=='PESD5V0S2BT':defs=[(1,'CAN1','passive'),(2,'CAN2','passive'),(3,'GND','passive')]
 else:defs=[(1,'1D+','bidirectional'),(2,'1D-','bidirectional'),(3,'2D+','bidirectional'),(4,'2D-','bidirectional'),(5,'GND','power_in'),(6,'OE_N','input'),(7,'D-','bidirectional'),(8,'D+','bidirectional'),(9,'S','input'),(10,'VCC','power_in')]
 body=[];half=(len(defs)+1)//2;hh=(half+1)*1.27
 for j,(n,label,typ) in enumerate(defs):
  side=-1 if j<half else 1;y=(half-1)*1.27-2.54*(j%half);a=0 if side==-1 else 180
  body.append(f'(pin {typ} line (at {side*17.78} {y} {a}) (length 5.08) (name {q(label)} {effect()}) (number "{n}" {effect()}))')
 return f'(symbol "{name}" (pin_names (offset 0.5)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {hh+2.54} 0) {effect()}) (property "Value" "{name}" (at 0 {hh+5.08} 0) {effect()}) (symbol "{name}_0_1" (rectangle (start -12.7 {hh}) (end 12.7 {-hh}) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{name}_1_1" {" ".join(body)}))'

def resolve(lib,name):
 raw=custom_symbol(name) if lib=='PoseDoll' else extract(lib,name);tree=parse(raw);ex=prop(tree,'extends')
 if ex:
  parent=resolve(lib,ex[1]);raw=parent.replace('"'+ex[1]+'"','"'+name+'"').replace('"'+ex[1]+'_','"'+name+'_')
 return raw

def schematic():
 libs={};body=[];rootid=uid('root')
 # Each labelled component occupies a 85 x 76 mm cell; grouped by function.
 for i,c in enumerate(comps):
  key=c['lib']+':'+c['sym']
  if key not in libs:libs[key]=resolve(c['lib'],c['sym']).replace('(symbol "'+c['sym']+'"','(symbol "'+key+'"',1)
  tree=parse(libs[key]);x=round((55+85*(i%12))/1.27)*1.27;y=round((55+76*(i//12))/1.27)*1.27;c['schematic_xy']=[x,y]
  spec=f'(symbol (lib_id {q(key)}) (at {x} {y} 0) (unit 1) (in_bom {"no" if c["ref"].startswith("TP") else "yes"}) (on_board yes) (dnp no) (uuid "{uid(c["ref"])}")'
  for j,(k,v) in enumerate((('Reference',c['ref']),('Value',c['value']),('Footprint',c['fp']),('Datasheet',''))):spec+=f'(property {q(k)} {q(v)} (at {x} {y-33+j*2.54} 0) {effect(j>=2)})'
  seen=set()
  for pin in pins(tree):
   num=prop(pin,'number')[1];spec+=f'(pin "{num}" (uuid "{uid(c["ref"]+"pin"+num)}"))';assert num in c['nets'],(c['ref'],num)
  spec+=f'(instances (project "{NAME}" (path "/{rootid}" (reference "{c["ref"]}") (unit 1)))))';body.append(spec)
  for pin in pins(tree):
   num=prop(pin,'number')[1];_,px,py,a=prop(pin,'at');px=x+float(px);py=y-float(py);net=c['nets'][num]
   if (px,py) in seen:continue
   seen.add((px,py))
   if net is None:body.append(f'(no_connect (at {px} {py}) (uuid "{uid(c["ref"]+num+"nc")}"))');continue
   rad=math.radians(float(a));ex=round(px-5.08*math.cos(rad),6);ey=round(py+5.08*math.sin(rad),6)
   body.append(f'(wire (pts (xy {px} {py}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid "{uid(c["ref"]+num+"wire")}"))')
   body.append(f'(label {q(net)} (at {ex} {ey} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid "{uid(c["ref"]+num+"label")}"))')
  # Extra net keys on the symbol are prohibited: connector pad maps must be explicit.
  assert set(c['nets'])=={prop(p,'number')[1] for p in pins(tree)},(c['ref'],set(c['nets'])-{prop(p,'number')[1] for p in pins(tree)})
 text=f'(kicad_sch (version 20250114) (generator "posedoll_hw44") (uuid "{rootid}") (paper "User" 1100 1100) (lib_symbols '+''.join(libs.values())+') '+''.join(body)+' (embedded_fonts no))'
 (OUT/(NAME+'.kicad_sch')).write_text(text,encoding='utf-8')
 local=OUT/'symbols';local.mkdir(exist_ok=True);libsets={}
 for c in comps:libsets.setdefault(c['lib'],{})[c['sym']]=resolve(c['lib'],c['sym'])
 for lib,syms in libsets.items():(local/(lib+'.kicad_sym')).write_text('(kicad_symbol_lib (version 20241209) (generator "posedoll_hw44") '+''.join(syms.values())+')',encoding='utf-8')
 (OUT/'sym-lib-table').write_text('(sym_lib_table '+''.join(f'(lib (name {q(lib)}) (type "KiCad") (uri {q("${KIPRJMOD}/symbols/"+lib+".kicad_sym")}) (options "") (descr "Project-pinned symbol copied or resolved from KiCad 10 / named datasheet"))' for lib in libsets)+')',encoding='utf-8')
 if not (OUT/(NAME+'.kicad_pro')).exists():
  (OUT/(NAME+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':NAME+'.kicad_pro','version':1}},indent=2),encoding='utf-8')
 return rootid

def board(rootid):
 exe=str(LIB.parents[1]/'bin/kicad-cli.exe');subprocess.run([exe,'sch','export','netlist','--format','kicadxml','-o',str(OUT/'netlist.xml'),str(OUT/(NAME+'.kicad_sch'))],check=True)
 b=pcb.BOARD();b.SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.2));nets={};netmap={}
 for el in ET.parse(OUT/'netlist.xml').findall('./nets/net'):
  net=pcb.NETINFO_ITEM(b,el.attrib['name'],int(el.attrib['code']));b.Add(net);nets[el.attrib['name']]=net
  for n in el.findall('node'):netmap[(n.attrib['ref'],n.attrib['pin'])]=net
 for c in comps:
  if not c['fp']:continue
  lib,fp=c['fp'].split(':');folder=OUT/'PoseDoll.pretty' if lib=='PoseDoll' else LIB/'footprints'/(lib+'.pretty');f=pcb.FootprintLoad(str(folder),fp);assert f,c['fp']
  f.SetFPID(pcb.LIB_ID(lib,fp));f.SetReference(c['ref']);f.SetValue(c['value']);f.SetPosition(pcb.VECTOR2I(*[pcb.FromMM(v) for v in c['pcb']]));f.SetOrientationDegrees(c['angle']);b.Add(f)
  if c['back']:f.Flip(f.GetPosition(),False)
  edges=[g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() in (pcb.F_CrtYd,pcb.B_CrtYd)]
  if edges and c['ref']!='U1':
   left=min(bb.GetLeft() for bb in edges);right=max(bb.GetRight() for bb in edges);top=min(bb.GetTop() for bb in edges);bottom=max(bb.GetBottom() for bb in edges)
   delta=pcb.VECTOR2I(round((left+right)/2),round((top+bottom)/2))-f.GetPosition();f.SetPosition(f.GetPosition()-delta)
  pp=pcb.KIID_PATH();pp.push_back(pcb.KIID(rootid));pp.push_back(pcb.KIID(uid(c['ref'])));f.SetPath(pp)
  for p in f.Pads():
   net=netmap.get((c['ref'],p.GetNumber()))
   if net:p.SetNet(net)
  f.Value().SetVisible(False);f.Reference().SetVisible(False)
  if c['ref']=='J4':
   for g in list(f.GraphicalItems()):
    if g.GetLayer()==pcb.F_SilkS and g.GetBoundingBox().GetBottom()>pcb.FromMM(165.6):f.Remove(g)
 for a,z in zip([(80,80),(120,80),(120,166),(80,166)],[(120,80),(120,166),(80,166),(80,80)]):
  line=pcb.PCB_SHAPE();line.SetShape(pcb.SHAPE_T_SEGMENT);line.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v) for v in a]));line.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v) for v in z]));line.SetLayer(pcb.Edge_Cuts);line.SetWidth(pcb.FromMM(.05));b.Add(line)
 pcb.SaveBoard(str(OUT/'placement.kicad_pcb'),b)
 pro=json.loads((ROOT/'electronics/sensor_revB/PoseDoll_AS5048A_revB.kicad_pro').read_text(encoding='utf-8'));pro['meta']['filename']=NAME+'.kicad_pro';rules=pro['board']['design_settings']['rules'];rules.update(min_track_width=.15,min_clearance=.15,min_copper_edge_clearance=.3,min_through_hole_diameter=.2);pro['net_settings']['classes'][0].update(track_width=.2,clearance=.15)
 for fname in (NAME,'placement'):(OUT/(fname+'.kicad_pro')).write_text(json.dumps(pro,indent=2),encoding='utf-8')
 (OUT/'connectivity.json').write_text(json.dumps(comps,ensure_ascii=False,indent=2),encoding='utf-8')
 print('Native schematic + placement generated:',len(comps),'components,',len(nets),'nets. NOT routed or released.')
def prepare_footprints():
 folder=OUT/'PoseDoll.pretty';folder.mkdir(exist_ok=True)
 f=pcb.FootprintLoad(str(LIB/'footprints/Connector_USB.pretty'),'USB_C_Receptacle_HRO_TYPE-C-31-M-12')
 f.SetFPID(pcb.LIB_ID('PoseDoll','USB_C_Data_Port'))
 for g in list(f.GraphicalItems()):
  if g.GetLayer()==pcb.F_SilkS and g.GetBoundingBox().GetBottom()>pcb.FromMM(3.04):f.Remove(g)
 pcb.PCB_IO_KICAD_SEXPR().FootprintSave(str(folder),f)
 assert (folder/'USB_C_Data_Port.kicad_mod').exists()
 (OUT/'fp-lib-table').write_text('(fp_lib_table (lib (name "PoseDoll") (type "KiCad") (uri "${KIPRJMOD}/PoseDoll.pretty") (options "") (descr "Project-pinned USB footprint, silkscreen clipped to board edge; copper and holes unchanged")))',encoding='utf8')
if __name__=='__main__':
 if '--prepare-footprints' in sys.argv:prepare_footprints()
 else:
  if not (OUT/'PoseDoll.pretty/USB_C_Data_Port.kicad_mod').exists():subprocess.run([sys.executable,__file__,'--prepare-footprints'],check=True)
  components();r=schematic();board(r)
