"""Mechanical/electrical interface extracted from the routed mini PCB."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E
import pcbnew as pcb
R=Path(__file__).resolve().parents[1];O=R/'electronics/sensor_revC_mini'
path=O/'PoseDoll_AS5048A_revC_mini.kicad_pcb';b=pcb.LoadBoard(str(path))
footprints={};padmap=[]
for fp in b.GetFootprints():
    p=fp.GetPosition();footprints[fp.GetReference()]={'xy_from_chip_mm':[pcb.ToMM(p.x)-100,pcb.ToMM(p.y)-100],'side':'sensor' if fp.IsOnLayer(pcb.F_Cu) else 'connector','rotation_deg':fp.GetOrientationDegrees()}
    for pad in fp.Pads():
        padmap.append(dict(ref=fp.GetReference(),pad=pad.GetNumber(),net=pad.GetNetname().lstrip('/'),xy_mm=[pcb.ToMM(pad.GetPosition().x)-100,pcb.ToMM(pad.GetPosition().y)-100],size_mm=[pcb.ToMM(pad.GetSize().x),pcb.ToMM(pad.GetSize().y)]))
def netmap(path):
    return {(i.attrib['ref'],i.attrib['pin']):n.attrib['name'] for n in E.parse(path).findall('./nets/net') for i in n.findall('node') if not i.attrib['ref'].startswith('#')}
old=netmap(R/'electronics/sensor_revB/netlist.xml');new=netmap(O/'netlist.xml')
assert old==new
pro=json.loads((O/'PoseDoll_AS5048A_revC_mini.kicad_pro').read_text('utf8'))
data=dict(revision='C_mini',status='DIGITAL_CANDIDATE_NOT_RELEASED',pcb_size_mm=[12,10,1.0],corner_chamfer_mm=1.0,origin='AS5048A package XY center; KiCad +X/+Y',board_mount='Removable insulating edge saddles/caps; no holes',spi_pins={'1':'GND','2':'+3V3','3':'SCK','4':'MOSI','5':'MISO','6':'CS_N'},footprints=footprints,pads=padmap,revB_netlist_equivalent=True,connector=dict(part='Hirose FH19C-6S-0.5SH(10)',FPC_thickness_mm=.2,FPC_thickness_tolerance_mm=.03,FPC_width_mm=3.5,pitch_mm=.5,contact_count=6,body_nominal_mm=[5,2.5,.9],overall_depth_mm=3,model='Conservative 5.15 x 3.15 x 1.0 mm envelope including leads; not manufacturer STEP',source='https://www.hirose.com/en/product/document?clcode=CL0580-0409-2-10&documentid=0000917166&documenttype=2DDrawing&lang=en&productname=FH19C-6S-0.5SH%2810%29&series=FH19C__FH19SC'),rules=pro['board']['design_settings']['rules'],net_class=pro['net_settings']['classes'][0],ignored_rule_categories=[k for k,v in pro['board']['design_settings']['rule_severities'].items() if v=='ignore'],track_widths_mm=sorted({round(pcb.ToMM(x.GetWidth()),4) for x in b.GetTracks() if not isinstance(x,pcb.PCB_VIA)}),vias=sum(isinstance(x,pcb.PCB_VIA) for x in b.GetTracks()),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),manufacturing_released=False,physical_tested=False,notes=['3.3 V only; electrical netlist unchanged from Rev B','FPC pin numbering must be checked at both ends; the harness/adapter has not been designed','No EMC, SPI timing, magnetic field, hot-plug or dynamic cable life validation','0.91 mm STEP FR4 body does not include the full nominal 1.0 mm PCB stack'])
(O/'mechanical_interface.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(revB_netlist_equivalent=True,vias=data['vias'],track_widths_mm=data['track_widths_mm'])))
