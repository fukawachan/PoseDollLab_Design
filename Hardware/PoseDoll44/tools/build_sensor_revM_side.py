"""Deterministic KiCad-native sensor schematic and placement study.
Uses installed KiCad symbols and pcbnew from KiCad 10. All pins retain electrical types.
"""
from pathlib import Path
import json,re,uuid,math,csv,subprocess
import xml.etree.ElementTree as ET
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"electronics/sensor_revM_side"
OUT.mkdir(parents=True,exist_ok=True)
LIB=Path(r"D:/ProgramFiles/KiCad/10.0/share/kicad")
NS=uuid.UUID("6c8efb3b-53a5-481a-9aba-0f1a6c2e784f")
def uid(s):return str(uuid.uuid5(NS,s))
def q(s):return json.dumps(str(s),ensure_ascii=False)
def parse(s):
    toks=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s)
    stack=[];root=None
    for t in toks:
        if t=="(":
            a=[]
            if stack:stack[-1].append(a)
            else:root=a
            stack.append(a)
        elif t==")":stack.pop()
        else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
    return root
def prop(a,key):return next((v for v in a if isinstance(v,list) and v and v[0]==key),None)
def children(a,key):return [v for v in a if isinstance(v,list) and v and v[0]==key]
def extract(lib,name):
    text=(LIB/"symbols"/(lib+".kicad_sym")).read_text(encoding="utf8")
    start=text.index('(symbol "'+name+'"');level=0;quoted=False;escape=False
    for i in range(start,len(text)):
        c=text[i]
        if escape:escape=False;continue
        if c=="\\" and quoted:escape=True;continue
        if c=='"':quoted=not quoted
        if not quoted:
            if c=="(":level+=1
            elif c==")":
                level-=1
                if level==0:return text[start:i+1]
    raise ValueError(name)
def pins(tree):
    return [x for s in children(tree,"symbol") for x in children(s,"pin")]
def effect(hide=False):return '(effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+')'
components=[
 dict(ref="U1",lib="Sensor_Magnetic",sym="AS5048A",value="AS5048A-HTSP-500",xy=(90,75),pcb=(100, 100),fp="Package_SO:TSSOP-14_4.4x5mm_P0.65mm",
      nets={"1":"CS_N","2":"SCK","3":"MISO_IC","4":"MOSI","5":"GND","6":None,"7":None,"8":None,"9":None,"10":None,"11":"+3V3","12":"+3V3","13":"GND","14":None}),
 dict(ref="J1",lib="Connector_Generic",sym="Conn_01x06",value="SM06B-SRSS-TB(LF)(SN)",xy=(40,70),pcb=(100, 100),fp="Connector_JST:JST_SH_SM06B-SRSS-TB_1x06-1MP_P1.00mm_Horizontal",
      nets={"1":"GND","2":"+3V3","3":"SCK","4":"MOSI","5":"MISO","6":"CS_N"}),
 dict(ref="C1",lib="Device",sym="C",value="100n X7R 16V",xy=(150,65),pcb=(102.3, 96.3),fp="Capacitor_SMD:C_0603_1608Metric",nets={"1":"+3V3","2":"GND"}),
 dict(ref="C2",lib="Device",sym="C",value="10u X5R 25V / GRM219R61E106KA12D",xy=(170,65),pcb=(102.3, 103.75),fp="Capacitor_SMD:C_0805_2012Metric",nets={"1":"+3V3","2":"GND"}),
 dict(ref="R1",lib="Device",sym="R",value="33R",xy=(150,100),pcb=(97.7, 96.3),fp="Resistor_SMD:R_0603_1608Metric",nets={"1":"MISO_IC","2":"MISO"}),
 dict(ref="R2",lib="Device",sym="R",value="10k",xy=(170,100),pcb=(97.7, 103.7),fp="Resistor_SMD:R_0603_1608Metric",nets={"1":"+3V3","2":"CS_N"}),
 dict(ref="#FLG01",lib="power",sym="PWR_FLAG",value="PWR_FLAG",xy=(35,110),fp="",nets={"1":"+3V3"}),
 dict(ref="#FLG02",lib="power",sym="PWR_FLAG",value="PWR_FLAG",xy=(55,110),fp="",nets={"1":"GND"})
]
def schematic():
    libs={};body=[];rootid=uid("schematic");name="PoseDoll_AS5048A_revM_side"
    for c in components:
        key=c["lib"]+":"+c["sym"]
        if key not in libs:libs[key]=extract(c["lib"],c["sym"]).replace('(symbol "'+c["sym"]+'"','(symbol "'+key+'"',1)
        tree=parse(libs[key]);x,y=[round(v/1.27)*1.27 for v in c["xy"]];id=uid(c["ref"])
        vals=f'(symbol (lib_id {q(key)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid "{id}")'
        for j,(k,v) in enumerate((("Reference",c["ref"]),("Value",c["value"]),("Footprint",c["fp"]),("Datasheet",""))):
            vals+=f'(property {q(k)} {q(v)} (at {x} {y-17+j*2.54} 0) {effect(j>=2)})'
        for pin in pins(tree):
            num=prop(pin,"number")[1];vals+=f'(pin "{num}" (uuid "{uid(c["ref"]+"pin"+num)}"))'
        vals+=f'(instances (project "{name}" (path "/{rootid}" (reference "{c["ref"]}") (unit 1)))))'
        body.append(vals)
        for pin in pins(tree):
            num=prop(pin,"number")[1];_,px,py,ang=prop(pin,"at");px=x+float(px);py=y-float(py)
            net=c["nets"][num]
            if net is None:
                body.append(f'(no_connect (at {px} {py}) (uuid "{uid(c["ref"]+num+"nc")}"))');continue
            rad=math.radians(float(ang));ex=round(px-5.08*math.cos(rad),5);ey=round(py+5.08*math.sin(rad),5)
            body.append(f'(wire (pts (xy {px} {py}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid "{uid(c["ref"]+num+"wire")}"))')
            body.append(f'(label "{net}" (at {ex} {ey} 0) (effects (font (size 1.0 1.0)) (justify left bottom)) (uuid "{uid(c["ref"]+num+"label")}"))')
    note="3.3V ONLY: connect VDD5V and VDD3V.\nPin 5 to GND; pins 6-10 NC. No OTP programming.\n12 x 10 x 1 mm head; JST SH6 cable connector.\nPrototype; magnetic field, wiring and power require physical validation."
    body.append(f'(text {q(note)} (at 110 140 0) {effect()} (uuid "{uid("note")}"))')
    text='(kicad_sch (version 20250114) (generator "posedoll_hw44") (uuid "'+rootid+'") (paper "A4")\n(lib_symbols\n'+"\n".join(libs.values())+')\n'+"\n".join(body)+'\n(embedded_fonts no))'
    (OUT/(name+".kicad_sch")).write_text(text,encoding="utf8")
    (OUT/(name+".kicad_pro")).write_text(json.dumps({"meta":{"filename":name+".kicad_pro","version":1}},indent=2),encoding="utf8")
    table='(sym_lib_table\n'+"\n".join(f'(lib (name "{k}") (type "KiCad") (uri "{(LIB/"symbols"/(k+".kicad_sym")).as_posix()}") (options "") (descr ""))' for k in sorted({c["lib"] for c in components}))+')'
    (OUT/"sym-lib-table").write_text(table,encoding="utf8")
    fpnames={c["fp"].split(":")[0] for c in components if c["fp"]}|{"MountingHole"}
    fptable='(fp_lib_table '+ " ".join(f'(lib (name "{k}") (type "KiCad") (uri "{(OUT/"PoseDoll.pretty" if k=="PoseDoll" else LIB/"footprints"/(k+".pretty")).resolve().as_posix()}") (options "") (descr ""))' for k in sorted(fpnames))+')'
    (OUT/"fp-lib-table").write_text(fptable,encoding="utf8")
    return rootid
def board(rootid):
    b=pcb.BOARD();b.GetDesignSettings().SetBoardThickness(pcb.FromMM(1.0));nets={}
    subprocess.run([str(LIB.parents[1]/"bin/kicad-cli.exe"),"sch","export","netlist","--format","kicadxml","-o",str(OUT/"netlist.xml"),str(OUT/"PoseDoll_AS5048A_revM_side.kicad_sch")],check=True)
    netmap={}
    for xmlnet in ET.parse(OUT/"netlist.xml").findall("./nets/net"):
        n=xmlnet.attrib["name"];i=int(xmlnet.attrib["code"])
        net=pcb.NETINFO_ITEM(b,n,i);b.Add(net);nets[n]=net
        for item in xmlnet.findall("node"):netmap[(item.attrib["ref"],item.attrib["pin"])]=n
    footprints={}
    for c in components:
        if not c["fp"]:continue
        lib,fp=c["fp"].split(":");f=pcb.FootprintLoad(str(OUT/"PoseDoll.pretty" if lib=="PoseDoll" else LIB/"footprints"/(lib+".pretty")),fp)
        if not f:raise RuntimeError("Missing footprint "+c["fp"])
        f.SetFPID(pcb.LIB_ID(lib,fp));f.SetReference(c["ref"]);f.SetValue(c["value"]);f.SetPosition(pcb.VECTOR2I(pcb.FromMM(c["pcb"][0]),pcb.FromMM(c["pcb"][1])))
        b.Add(f)
        if c["ref"]=="R1":f.SetOrientationDegrees(180)
        if c["ref"]=="J1":f.Flip(f.GetPosition(),False)
        pth=pcb.KIID_PATH();pth.push_back(pcb.KIID(rootid));pth.push_back(pcb.KIID(uid(c["ref"])));f.SetPath(pth)
        for pad in f.Pads():
            n=netmap.get((c["ref"],pad.GetNumber()))
            if n:pad.SetNet(nets[n])
        f.Reference().SetVisible(False);f.Value().SetVisible(False)
        footprints[c["ref"]]=f
    outline=[(95,95),(105,95),(106,96),(106,104),(105,105),(95,105),(94,104),(94,96)]
    for a,z in zip(outline,outline[1:]+outline[:1]):
        line=pcb.PCB_SHAPE();line.SetShape(pcb.SHAPE_T_SEGMENT);line.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v) for v in a]));line.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v) for v in z]));line.SetLayer(pcb.Edge_Cuts);line.SetWidth(pcb.FromMM(.05));b.Add(line)
    # No silkscreen reference clutter on the 12 x 10 mm sensing head. Assembly
    # drawing and copper pin-1 geometry determine orientation.
    from route_sensor_revC_mini import route
    pcb.SaveBoard(str(OUT/"placement.kicad_pcb"),b)
    import os
    os.environ['PD44_ROUTE_ORDER']='+3V3,GND,CS_N,SCK,MISO_IC,MISO,MOSI'
    logs=route(b)
    (OUT/"routing_log.json").write_text(json.dumps(logs,indent=2),encoding="utf8")
    pcb.SaveBoard(str(OUT/"PoseDoll_AS5048A_revM_side.kicad_pcb"),b)
    pads=[{"ref":r,"pad":p.GetNumber(),"net":p.GetNetname(),"x_mm":pcb.ToMM(p.GetPosition().x),"y_mm":pcb.ToMM(p.GetPosition().y)} for r,f in footprints.items() for p in f.Pads()]
    (OUT/"pad_map.json").write_text(json.dumps(pads,indent=2),encoding="utf8")
if __name__=="__main__":
    r=schematic();board(r)
    (OUT/"connectivity.json").write_text(json.dumps(components,ensure_ascii=False,indent=2),encoding="utf8")
    from sensor_revM_side_rules import configure
    configure()
    print(OUT)
