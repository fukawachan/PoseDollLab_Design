"""H2 metal-load-path friction cartridge; engineering prototype, not release.
Printed lever, magnet carrier, retaining bridge and PCB carrier. Precision metal
and POM parts are supplied to drawings; users are not expected to machine them.
"""
from design import *
from fits import clearance

COLORS={"printed":(.23,.52,.66),"aluminum":(.70,.72,.73),"pom":(.88,.88,.78),"lining":(.52,.28,.12),"spring":(.40,.41,.45),"fastener":(.56,.57,.59),"pcb":(.10,.38,.23),"magnet":(.8,.18,.2)}

def cylinder(radius,z,h):return rod((0,0,z),(0,0,z+h),radius)
def annulus(ro,ri,z,h):return cylinder(ro,z,h).cut(cylinder(ri,z-1,h+2))
def drill_z(shape,x,y,r,z0=-20,z1=65):return bore(shape,(x,y,z0),(x,y,z1),r)
def hexagon(af,z,h):return cq.Workplane("XY").polygon(6,af/math.cos(math.pi/6)).extrude(h).translate((0,0,z)).val()
def dprofile(diameter,flat_x,z,h):return cylinder(diameter/2,z,h).cut(cube((10,12,h+2),(flat_x+5,0,z+h/2)))
def spring(z,inverted=False):
 # Actual 000300 envelope at 0.188mm nominal deflection, geometric illustration only.
 points=[(1.6,.062),(4,0),(4,.3),(1.6,.362)]
 if inverted:points=[(x,.362-y) for x,y in points]
 return cq.Workplane("XZ").polyline(points).close().revolve(360,(0,0),(0,1)).translate((0,0,z)).val()

def cartridge(size="M"):
 ro={"S":13,"M":19,"L":27}[size];ri=5.2 if size!="L" else 6.2
 guide=ro+7;outer=guide+4;adjust=ro+4.5
 guides=[(guide*math.cos(math.radians(a)),guide*math.sin(math.radians(a))) for a in (0,120,240)]
 adjusters=[(adjust*math.cos(math.radians(a)),adjust*math.sin(math.radians(a))) for a in (60,180,300)]
 parts=[]
 def add(code,name,s,material,owner,qty_note=""):
  if not s.isValid():raise ValueError(name)
  parts.append(dict(code=code,name="H2"+size+"_"+name,shape=s,material=material,owner=owner,note=qty_note))
 bottom=annulus(outer,5.01,0,4)
 reaction=annulus(outer,5.2,9,3)
 pressure=annulus(outer,5.2,19,3)
 top=annulus(outer,5.01,25,4)
 pcbholder=cylinder(outer,48.4,3)
 for x,y in guides:
  bottom=drill_z(bottom,x,y,1.7);reaction=drill_z(reaction,x,y,1.7)
  pressure=drill_z(pressure,x,y,3.1);top=drill_z(top,x,y,1.7)
  pcbholder=drill_z(pcbholder,x,y,clearance("M3")/2)
 for x,y in adjusters:
  top=drill_z(top,x,y,1.25) # M3 tap pilot, supplier must thread.
  pressure=drill_z(pressure,x,y,1.6) # Guide stem reaches fixed reaction plate.
 for x in (-6.5,6.5):pcbholder=drill_z(pcbholder,x,6.5,2.1)
 add("010","bottom_bearing_plate",bottom,"aluminum","fixed","10.02 bore finish tolerance in drawing notes")
 add("011","fixed_reaction_plate",reaction,"aluminum","fixed")
 add("012","floating_pressure_plate",pressure,"aluminum","fixed","Three 6.2 guide bores; axial sliding part")
 add("013","top_bearing_plate",top,"aluminum","fixed","3x M3 tapped holes; STEP represents 2.5 pilot only")
 add("020","pcb_carrier",pcbholder,"printed","fixed","4.2 holes permit XY alignment; washers spread clamp load")
 # One turned axle with an integral friction flange avoids adhesive drive coupling.
 shaft=cylinder(4,-12,46).fuse(cylinder(ro+1,14,3))
 for z,h in ((-12,10),(30.2,3.8)):shaft=shaft.cut(cube((8,12,h),(7.5,0,z+h/2)))
 add("014","flanged_axle",shaft,"aluminum","rotor","8.00/-0.02 journals, 7.5mm across D flat; no thread as a bearing")
 for code,z,flip in (("030",0,False),("031",25,True)):
  b=annulus(5,4.035,z,4)
  b=b.fuse(annulus(7,4.035,z+4 if flip else z-1,1))
  add(code,"POM_flanged_bush_"+code,b,"pom","fixed","Supplier-made; finished ID8.05..8.08, OD9.99..10.00")
 for code,z in (("032",12),("033",17)):
  add(code,"friction_lining_"+code,annulus(ro,ri,z,2),"lining","fixed","Non-asbestos friction lining candidate; material/COF qualification pending")
 # Axial shaft retention: collars and non-load-bearing thrust washers.
 for code,z in (("034",-1.7),("035",30.0)):
  add(code,"POM_thrust_washer_"+code,annulus(6.5,4.1,z,.5),"pom","fixed")
 # Printed output lever is split-clamped over a positive D flat.
 lever=cylinder(13,-10,8).fuse(cube((92,18,8),(46,0,-6)))
 lever=lever.fuse(cube((9,8,8),(8,10.5,-6))).fuse(cube((9,8,8),(8,-10.5,-6)))
 lever=lever.cut(dprofile(8.6,3.8,-11,10))
 lever=lever.cut(cube((18,1,10),(10,0,-6)))
 lever=bore(lever,(8,-18,-6),(8,18,-6),1.8)
 pocket=hexagon(6.0,0,2.8).rotate((0,0,0),(1,0,0),90).translate((8,-11.7,-6))
 lever=lever.cut(pocket)
 lever=drill_z(lever,84,0,2.4)
 add("021","split_output_lever",lever.translate((0,0,-2)),"printed","rotor","M3 transverse clamp and D flat; hand grip/hanging load hole at84mm")
 # Magnet carrier seats on the other D flat, with a positive retaining bridge.
 cup=cube((12,24,6),(0,0,31.9)).fuse(cube((6,6,6),(9,0,31.9))).fuse(cylinder(3.8,34.9,2.7))
 for y in (-8,8):cup=cup.fuse(cylinder(2.5,34.9,2.7).translate((0,y,0)))
 cup=cup.cut(dprofile(8.6,3.8,28,6.2)).cut(cylinder(7.3,28,2.7)).cut(cube((60,60,10),(0,0,24.4)))
 cup=cup.cut(cylinder(3.1,35,3))
 for y in (-8,8):
  cup=drill_z(cup,0,y,1.3)
  cup=cup.cut(hexagon(4.4,31.0,1.8).translate((0,y,0)))
  cup=cup.cut(cube((4.4,5,1.8),(0,math.copysign(10.5,y),31.9)))
  cup=cup.cut(cq.Solid.makeCone(1.3,1.4,.1,cq.Vector(0,y,37.5),cq.Vector(0,0,1)))
 cup=bore(cup,(3,0,31.9),(13,0,31.9),1.3)
 nut_pocket=hexagon(4.4,0,1.8).rotate((0,0,0),(0,1,0),90).translate((7,0,31.9))
 cup=cup.cut(nut_pocket).cut(cube((1.8,4.4,4.0),(7.9,0,33.9)))
 cup=bore(cup,(9.5,0,31.9),(13,0,31.9),1.9)
 cover=cube((7,22,.8),(0,0,38.0))
 for y in (-8,8):
  cover=drill_z(cover,0,y,1.3)
  cover=cover.cut(cq.Solid.makeCone(1.3,2.2,.9,cq.Vector(0,y,37.5),cq.Vector(0,0,1)))
 add("022","D_magnet_carrier",cup,"printed","rotor","Nominal 6.2x2.6 magnet seat; calibration remains required")
 add("023","magnet_retaining_bridge",cover,"printed","rotor","0.8 mm / four 0.2 mm layers; M2x8 nylon countersunk fasteners")
 add("040","diametric_magnet_6x2p5",cylinder(3,35,2.5),"magnet","rotor")
 pcbshape=cq.importers.importStep(str(OUT/"step/sensor_revB.step")).val().rotate((0,0,0),(1,0,0),180).translate((0,0,41.9))
 add("041","AS5048A_sensor_revB",pcbshape,"pcb","fixed","Library geometry; nominal magnet-to-package gap 1.805mm from library model; verify field physically")
 for j,(x,y) in enumerate(guides):
  for name,z,h in (("lower_spacer",4,5),("guide_spacer",12,13),("sensor_spacer",31.9,16)):
   add("050",name+str(j),annulus(3,1.7,z,h).translate((x,y,0)),"aluminum","fixed")
  add("051","M3_tie_screw"+str(j),cylinder(1.5,0,55).fuse(cylinder(2.75,-3,3)).translate((x,y,0)),"fastener","fixed","M3x55; threads simplified")
  add("070","carrier_support_washer"+str(j),annulus(3.5,1.6,47.9,.5).translate((x,y,0)),"fastener","fixed")
  for z in (29,51.4):
   add("052","M3_washer_"+str(j)+"_"+str(z),annulus(3.5,1.6,z,.5).translate((x,y,0)),"fastener","fixed")
   add("053","M3_nut_"+str(j)+"_"+str(z),hexagon(5.5,z+.5,2.4).cut(cylinder(1.3,z,4)).translate((x,y,0)),"fastener","fixed","Lower nut locks metal stack independently of printed carrier")
 for j,(x,y) in enumerate(adjusters):
  add("054","spring_base_washer"+str(j),annulus(4,1.6,22,.5).translate((x,y,0)),"spring","fixed")
  parallel=2 if size=="L" else 1
  pack_h=.362+.3*(parallel-1);button_z=22.5+2*pack_h
  for k in range(parallel):
   add("055","schnorr_000300_a"+str(j)+"_"+str(k),spring(22.5+.3*k).translate((x,y,0)),"spring","fixed")
   add("055","schnorr_000300_b"+str(j)+"_"+str(k),spring(22.5+pack_h+.3*k,True).translate((x,y,0)),"spring","fixed")
  button=cylinder(4,button_z,1).fuse(cylinder(1.5,12,button_z-12))
  add("056","spring_guide_button"+str(j),button.translate((x,y,0)),"aluminum","fixed","Stop stem passes through pressure plate and reacts against FIXED lower plate")
  add("057","M3_adjuster"+str(j),cylinder(1.5,button_z+1,10).fuse(cylinder(2.75,button_z+11,3)).translate((x,y,0)),"fastener","fixed","M3x10 with locknut; do not infer preload from screw torque")
  add("058","M3_adjuster_locknut"+str(j),hexagon(5.5,29,2.4).cut(cylinder(1.3,28,5)).translate((x,y,0)),"fastener","fixed")
 for j,x in enumerate((-6.5,6.5)):
  add("060","nylon_M2_female_spacer"+str(j),annulus(2.3,.8,41.9,6).translate((x,6.5,0)),"pom","fixed","M2 female spacer L6, threads represented by minor bore")
  add("061","nylon_M2x6_top_screw"+str(j),cylinder(1,45.9,6).fuse(cylinder(2,51.9,1.5)).translate((x,6.5,0)),"pom","fixed")
  add("071","nylon_M2x4_board_screw"+str(j),cylinder(1,40.3,4).fuse(cylinder(2,38.9,1.4)).translate((x,6.5,0)),"pom","fixed","Low-profile head max1.4mm; required for swept clearance")
  for zz in (47.9,51.4):add("062","nylon_spreader"+str(j)+"_"+str(zz),annulus(4,1.1,zz,.5).translate((x,6.5,0)),"pom","fixed")
 for j,y in enumerate((-8,8)):
  cap_screw=cylinder(1,30.4,7.1).fuse(cq.Solid.makeCone(1,2.2,.9,cq.Vector(0,0,37.5),cq.Vector(0,0,1)))
  add("064","nylon_M2x8_cap_screw"+str(j),cap_screw.translate((0,y,0)),"pom","rotor")
  add("065","nylon_M2_cap_nut"+str(j),hexagon(4,31,1.6).cut(cylinder(.85,30,3)).translate((0,y,0)),"pom","rotor")
 # Fasteners are simplified solid thread envelopes, their engagement is intentional.
 add("066","M3_lever_clamp_screw",rod((8,-15.5,-8),(8,14.5,-8),1.5).fuse(rod((8,14.5,-8),(8,17.5,-8),2.75)),"fastener","rotor")
 add("067","M2_magnet_set_screw",rod((3.5,0,31.9),(9.5,0,31.9),1).fuse(rod((9.5,0,31.9),(11.5,0,31.9),1.8)),"fastener","rotor")
 levernut=hexagon(5.5,0,2.4).cut(cylinder(1.3,-1,5)).rotate((0,0,0),(1,0,0),90).translate((8,-12.1,-8))
 add("068","M3_lever_clamp_nut",levernut,"fastener","rotor")
 setnut=hexagon(4,0,1.6).cut(cylinder(.85,-1,4)).rotate((0,0,0),(0,1,0),90).translate((7,0,31.9))
 add("069","M2_magnet_set_nut",setnut,"fastener","rotor")
 return parts

def main():
 report={"source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"sensor_step_sha256":hashlib.sha256(SENSOR_STEP.read_bytes()).hexdigest(),"status":"H2_DETAILED_DEVELOPMENT_NOT_MANUFACTURING_RELEASE","physical_tested":False,"families":{}}
 for size in ("S","M","L"):
  parts=cartridge(size);assy=cq.Assembly(name="H2_"+size);manifest=[]
  folder=OUT/"H2"/size;folder.mkdir(parents=True,exist_ok=True)
  for part in parts:
   s=part["shape"];assy.add(s,name=part["name"],color=cq.Color(*COLORS[part["material"]]))
   b=s.BoundingBox();entry={k:v for k,v in part.items() if k!="shape"};entry.update(solid_count=len(s.Solids()),valid=s.isValid(),volume_mm3=s.Volume(),bbox_mm=[b.xlen,b.ylen,b.zlen])
   if part["material"]=="printed":
    cq.exporters.export(s,str(folder/(part["name"]+".step")))
    cq.exporters.export(s.translate((-b.xmin,-b.ymin,-b.zmin)),str(folder/(part["name"]+".stl")),tolerance=.08,angularTolerance=.1)
   elif part["code"] in ("010","011","012","013","014","030","031","056"):
    cq.exporters.export(s,str(folder/(part["name"]+".step")))
   manifest.append(entry)
  assy.save(str(folder/("H2_"+size+"_assembly.step")))
  checks=[dict(name=x["name"],group="H2",shape=x["shape"],owner=x["owner"]) for x in parts]
  hits=collisions(checks)
  all_pairs=collisions([dict(x,owner=x["name"]) for x in checks])
  prefix="H2"+size+"_"
  allowed=set()
  def permit(a,b):allowed.add(frozenset((prefix+a,prefix+b)))
  for j in range(3):
   permit("top_bearing_plate","M3_adjuster"+str(j))
   permit("M3_adjuster"+str(j),"M3_adjuster_locknut"+str(j))
   for z in (29,51.4):permit("M3_tie_screw"+str(j),"M3_nut_"+str(j)+"_"+str(z))
  for j in range(2):
   permit("nylon_M2_female_spacer"+str(j),"nylon_M2x6_top_screw"+str(j))
   permit("nylon_M2_female_spacer"+str(j),"nylon_M2x4_board_screw"+str(j))
   permit("nylon_M2x8_cap_screw"+str(j),"nylon_M2_cap_nut"+str(j))
  permit("M3_lever_clamp_screw","M3_lever_clamp_nut");permit("M2_magnet_set_screw","M2_magnet_set_nut")
  unplanned=[x for x in all_pairs if frozenset((x["a"],x["b"])) not in allowed]
  threads=[dict(x,reason="intentional simplified thread envelope/minor-bore engagement") for x in all_pairs if frozenset((x["a"],x["b"])) in allowed]
  rho={"printed":1.24,"aluminum":2.70,"pom":1.14,"lining":1.80,"spring":7.85,"fastener":7.85,"pcb":1.90,"magnet":7.50}
  mass_g=sum((2.2 if x["material"]=="pcb" else x["shape"].Volume()*rho[x["material"]]/1000) for x in parts)
  sweep=[]
  for angle in range(0,360,15):
   moved_parts=[dict(x,shape=x["shape"].rotate((0,0,0),(0,0,1),angle)) if x["owner"]=="rotor" else x for x in checks]
   sweep.append({"angle_deg":angle,"collisions":collisions(moved_parts)})
  report["families"][size]={"parts":manifest,"fixed_rotating_intersections":hits,"sweep_15deg":sweep,"estimated_fixture_mass_g":mass_g,"assembly_unplanned_intersections":unplanned,"modeled_thread_intersections":threads,"spring_parallel_per_series_group":2 if size=="L" else 1,"spring_series_groups_per_location":2,"spring_locations":3,"catalog_nominal_total_N":624 if size=="L" else 312,"integration_status":"standalone_characterization_fixture_NOT_in_full_body_mass_BOM"}
  if size=="M":
   render([(x["name"],x["shape"],COLORS[x["material"]]) for x in parts],OUT/"images/H2_M_clutch.png","H2 M | metal preload path + polymer bearings | development")
   cutaway=cube((150,150,200),(75,75,20))
   cutitems=[]
   for part in parts:
    s=part["shape"].cut(cutaway)
    if s.Volume()>0.01:cutitems.append((part["name"],s,COLORS[part["material"]]))
   render(cutitems,OUT/"images/H2_M_section.png","H2 M | quarter-section for explanation only | not print geometry")
  print(json.dumps({"size":size,"parts":len(parts),"rotor_hits":len(hits),"sweep_hits":sum(len(x["collisions"]) for x in sweep),"unplanned_assembly_hits":len(unplanned)}),flush=True)
 save(ROOT/"verification/H2_clutch_geometry.json",report)
if __name__=="__main__":main()
