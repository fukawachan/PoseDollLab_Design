"""Rev D compact bearing/friction module with shared reaction support.
No manufacturing release. Rev C H2 remains a characterization fixture.
"""
from pathlib import Path
import sys,math,json,hashlib
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revC'))
import clutch as h2
from design import cq,np,cube,rod,bore,moved,matrix,rot,collisions,render,save,ROOT,SENSOR_STEP
from clutch import cylinder,annulus,drill_z,hexagon,dprofile,spring,COLORS
OUT=ROOT/'generated/revD'
DENSITY={'printed':1.24,'aluminum':2.70,'pom':1.14,'lining':1.80,'spring':7.85,'fastener':7.85,'pcb':1.90,'magnet':7.50}

def arm_plate(centre_radius,points,z,t,pad=4,beam=6,inner=0):
 s=cylinder(centre_radius,z,t)
 for x,y in points:
  length=math.hypot(x,y)
  bridge=cube((length,beam,t),(length/2,0,z+t/2)).rotate((0,0,0),(0,0,1),math.degrees(math.atan2(y,x)))
  s=s.fuse(bridge).fuse(cylinder(pad,z,t).translate((x,y,0)))
 if inner:s=s.cut(cylinder(inner,z-1,t+2))
 return s

def module(size='M'):
 ro={'S':13,'M':19,'L':27}[size];ri=5.2 if size!='L' else 6.2
 polar=lambda r,angles:[(r*math.cos(math.radians(a)),r*math.sin(math.radians(a))) for a in angles]
 guides=polar(ro+7,(0,120,240));adjusters=polar(ro+4.5,(60,180,300));mounts=polar(ro+8.5,(60,180,300))
 parts=[]
 def add(name,s,mat,owner,note=''):
  if not s.isValid():raise ValueError(name)
  parts.append(dict(name='D3'+size+'_'+name,shape=s,material=mat,owner=owner,note=note))
 # Two bearing supports also close the spring reaction path. The third plate slides.
 reaction=arm_plate(ro+1,guides+mounts,0,2.5,inner=5.2)
 reaction=reaction.fuse(annulus(7,5.01,-3.5,5))
 pressure=arm_plate(ro+1,guides+adjusters,6.5,2,inner=5.2)
 top=arm_plate(7,guides+adjusters,12,3,inner=5.01).fuse(annulus(7,5.01,15,2))
 for x,y in guides:
  reaction=drill_z(reaction,x,y,1.7);pressure=drill_z(pressure,x,y,3.1);top=drill_z(top,x,y,1.7)
 for x,y in adjusters:
  pressure=drill_z(pressure,x,y,1.6);top=drill_z(top,x,y,1.25)
 for x,y in mounts:
  reaction=reaction.fuse(annulus(3.5,1.25,-4,4).translate((x,y,0)))
  # M3 blind-thread envelope; 3.5mm specified usable engagement, closed at z=0.
 add('shared_reaction_bearing',reaction,'aluminum','fixed','Shared radial bearing + clutch reaction + fork mounting; precision bores and blind M3 threads')
 add('pressure_plate',pressure,'aluminum','fixed','Axial floating; guided by three metal sleeves')
 add('bearing_spider',top,'aluminum','fixed','Second radial bearing and three M3 spring adjuster threads')
 shaft=cylinder(4,-14,38).fuse(cylinder(ro+1,3.5,2))
 for z,t in ((-14,8.8),(20.2,3.8)):shaft=shaft.cut(cube((8,12,t),(7.5,0,z+t/2)))
 add('integral_flange_axle',shaft,'aluminum','rotor','8.00/-0.02 journal; positive D ends, 7.5 across flat')
 for name,z,flange in (('lower_bush',-3.5,-4.5),('upper_bush',12,17)):
  add(name,annulus(5,4.035,z,5).fuse(annulus(7,4.035,flange,1)),'pom','fixed','Housing10.02..10.04; bushOD9.99..10.00, ID8.05..8.08; supplier-machined')
 for j,z in enumerate((2.5,5.5)):add('lining'+str(j),annulus(ro,ri,z,1),'lining','fixed','1mm candidate friction sheet; COF and wear unqualified')
 for j,z in enumerate((-5.2,18)):add('thrust'+str(j),annulus(6.5,4.1,z,.5),'pom','fixed')
 # Reuse tested magnetic assembly geometry at a 10mm lower station, without its bench lever/cage.
 reuse=('D_magnet_carrier','magnet_retaining_bridge','diametric_magnet_6x2p5','AS5048A_sensor_revB',
        'nylon_M2_female_spacer','nylon_M2x6_top_screw','nylon_M2x4_board_screw','nylon_spreader',
        'nylon_M2x8_cap_screw','nylon_M2_cap_nut','M2_magnet_set_screw','M2_magnet_set_nut')
 for x in h2.cartridge(size):
  short=x['name'].split('_',1)[1]
  if any(short.startswith(n) for n in reuse):add(short,x['shape'].translate((0,0,-10)),x['material'],x['owner'],x['note'])
 # Open carrier leaves connector side accessible. Mounting screws remain nylon.
 carrier=cube((22,13,3),(0,4,39.9))
 for x,y in guides:
  bridge=rod((x,y,39.9),(0,6.5,39.9),2)
  carrier=carrier.fuse(bridge).fuse(cylinder(4,38.4,3).translate((x,y,0)))
  carrier=drill_z(carrier,x,y,1.8)
 for x in (-6.5,6.5):carrier=drill_z(carrier,x,6.5,2.1)
 add('sensor_carrier',carrier,'printed','fixed','Open connector edge; oversize holes for XY adjustment')
 # Small split output coupling replaces the 92mm characterization lever.
 hub=cylinder(13.5,-13.2,8)
 hub=hub.cut(dprofile(8.6,3.8,-14,10)).cut(cube((11,1,10),(9.5,0,-9.2)))
 hub=bore(hub,(8.5,-15,-9.2),(8.5,15,-9.2),1.3)
 for y in (-1,1):hub=hub.cut(rod((8.5,y*9.8,-9.2),(8.5,y*15,-9.2),2.4))
 pocket=hexagon(4.4,0,1.8).rotate((0,0,0),(1,0,0),90).translate((8.5,-8,-9.2))
 hub=hub.cut(pocket)
 for angle in (90,180,270):
  x,y=10*math.cos(math.radians(angle)),10*math.sin(math.radians(angle))
  hub=drill_z(hub,x,y,1.8)
  hub=hub.cut(hexagon(6, -8,2.8).translate((x,y,0)))
 add('split_output_hub',hub,'printed','rotor','Three M3 downstream mounting points, PCD20 at90/180/270deg; D flat transmits torque')
 add('M2_output_clamp',rod((8.5,-9.8,-9.2),(8.5,10.2,-9.2),1).fuse(rod((8.5,10.2,-9.2),(8.5,12.2,-9.2),1.9)),'fastener','rotor')
 add('M2_output_nut',hexagon(4,0,1.6).cut(cylinder(.85,-1,4)).rotate((0,0,0),(1,0,0),90).translate((8.5,-8,-9.2)),'fastener','rotor')
 # Input ring/fork interface: separately attached behind reaction plate, never in spring load loop.
 mount=cq.Workplane('XY').circle(ro+12).circle(16).extrude(3).translate((0,0,-7)).val()
 for x,y in mounts:mount=drill_z(mount,x,y,1.8)
 for x,y in guides:mount=drill_z(mount,x,y,3.1)
 # Two bolt-pad input ports at +Y/-Y; use as shared fork roots in body integration.
 for s in (-1,1):
  mount=mount.fuse(cube((12,8,3),(0,s*(ro+11),-5.5)))
  mount=drill_z(mount,0,s*(ro+11),1.8)
 add('input_fork_interface',mount,'printed','fixed','M3 attachments to metal reaction plate are outside spring preload path')
 for j,(x,y) in enumerate(mounts):
  add('M3_input_mount'+str(j),cylinder(1.5,-7,6).fuse(cylinder(2.75,-10,3)).translate((x,y,0)),'fastener','fixed','M3x6; blind metal thread engagement3mm; validate thread and clamp load')
 for j,(x,y) in enumerate(guides):
  for name,z,t in (('guide_sleeve',2.5,9.5),('sensor_sleeve',17.9,20)):
   add(name+str(j),annulus(3,1.7,z,t).translate((x,y,0)),'aluminum','fixed')
  add('M3_tie'+str(j),cylinder(1.5,0,45).fuse(cylinder(2.75,-3,3)).translate((x,y,0)),'fastener','fixed')
  for z in (15,41.4):
   add('tie_washer'+str(j)+'_'+str(z),annulus(3.5,1.6,z,.5).translate((x,y,0)),'fastener','fixed')
   add('tie_nut'+str(j)+'_'+str(z),hexagon(5.5,z+.5,2.4).cut(cylinder(1.3,z,4)).translate((x,y,0)),'fastener','fixed')
  add('sensor_support_washer'+str(j),annulus(3.5,1.6,37.9,.5).translate((x,y,0)),'fastener','fixed')
 for j,(x,y) in enumerate(adjusters):
  add('spring_washer'+str(j),annulus(4,1.6,8.5,.5).translate((x,y,0)),'spring','fixed')
  parallel=2 if size=='L' else 1;pack=.362+.3*(parallel-1);button_z=9+2*pack
  for k in range(parallel):
   add('spring_a'+str(j)+'_'+str(k),spring(9+.3*k).translate((x,y,0)),'spring','fixed')
   add('spring_b'+str(j)+'_'+str(k),spring(9+pack+.3*k,True).translate((x,y,0)),'spring','fixed')
  add('spring_button'+str(j),cylinder(4,button_z,1).fuse(cylinder(1.5,2.5,button_z-2.5)).translate((x,y,0)),'aluminum','fixed','Stop stem reacts against fixed reaction plate; nominal spring travel only')
  add('M3_adjuster'+str(j),cylinder(1.5,button_z+1,10).fuse(cylinder(2.75,button_z+11,3)).translate((x,y,0)),'fastener','fixed')
  add('adjuster_nut'+str(j),hexagon(5.5,15,2.4).cut(cylinder(1.3,14,5)).translate((x,y,0)),'fastener','fixed')
 return parts

def allowed_pairs(size):
 p='D3'+size+'_';allowed=set()
 def permit(a,b):allowed.add(frozenset((p+a,p+b)))
 for j in range(3):
  permit('shared_reaction_bearing','M3_input_mount'+str(j))
  permit('bearing_spider','M3_adjuster'+str(j));permit('M3_adjuster'+str(j),'adjuster_nut'+str(j))
  for z in (15,41.4):permit('M3_tie'+str(j),'tie_nut'+str(j)+'_'+str(z))
 for j in range(2):
  permit('nylon_M2_female_spacer'+str(j),'nylon_M2x6_top_screw'+str(j))
  permit('nylon_M2_female_spacer'+str(j),'nylon_M2x4_board_screw'+str(j))
  permit('nylon_M2x8_cap_screw'+str(j),'nylon_M2_cap_nut'+str(j))
 permit('M2_magnet_set_screw','M2_magnet_set_nut');permit('M2_output_clamp','M2_output_nut')
 return allowed

def main():
 report={'status':'DIGITAL_DEVELOPMENT_NOT_RELEASE','physical_tested':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'revC_clutch_sha256':hashlib.sha256((HERE.parent/'revC/clutch.py').read_bytes()).hexdigest(),'sensor_step_sha256':hashlib.sha256(SENSOR_STEP.read_bytes()).hexdigest(),'families':{}}
 for size in ('S','M','L'):
  parts=module(size);folder=OUT/'modules'/size;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name='D3_'+size);records=[]
  for p in parts:
   s=p['shape'];b=s.BoundingBox();mass=2.2 if p['material']=='pcb' else s.Volume()*DENSITY[p['material']]/1000
   records.append({k:v for k,v in p.items() if k!='shape'}|{'solid_count':len(s.Solids()),'valid':s.isValid(),'volume_mm3':s.Volume(),'mass_g':mass,'com_mm':list(s.Center().toTuple()),'bbox_mm':[b.xlen,b.ylen,b.zlen]})
   assy.add(s,name=p['name'],color=cq.Color(*COLORS[p['material']]))
   if p['material']=='printed':
    cq.exporters.export(s,str(folder/(p['name']+'.step')))
    cq.exporters.export(s.translate((-b.xmin,-b.ymin,-b.zmin)),str(folder/(p['name']+'.stl')),tolerance=.08,angularTolerance=.1)
   elif any(n in p['name'] for n in ('reaction_bearing','pressure_plate','bearing_spider','flange_axle','_bush','spring_button')):cq.exporters.export(s,str(folder/(p['name']+'.step')))
  assy.save(str(folder/('D3_'+size+'_assembly.step')))
  items=[dict(p,group=size) for p in parts]
  assembly_hits=collisions([dict(p,owner=p['name']) for p in items]);allowed=allowed_pairs(size)
  unexpected=[h for h in assembly_hits if frozenset((h['a'],h['b'])) not in allowed]
  sweeps=[]
  for angle in range(0,360,15):
   sample=[dict(p,shape=p['shape'].rotate((0,0,0),(0,0,1),angle)) if p['owner']=='rotor' else p for p in items]
   sweeps.append({'angle_deg':angle,'collisions':collisions(sample)})
  mass=sum(p['mass_g'] for p in records)
  report['families'][size]={'parts':records,'estimated_mass_g':mass,'unplanned_assembly_intersections':unexpected,'expected_thread_intersections':[h for h in assembly_hits if frozenset((h['a'],h['b'])) in allowed],'rotation_samples':sweeps,'preload_nominal_N':624 if size=='L' else 312,'friction_faces':2,'friction_outer_mm':{'S':13,'M':19,'L':27}[size],'friction_inner_mm':6.2 if size=='L' else 5.2}
  print(json.dumps({'size':size,'parts':len(parts),'mass_g':mass,'assembly_hits':unexpected,'sweep_hits':sum(len(x['collisions']) for x in sweeps)}),flush=True)
  if size=='M':
   (OUT/'images').mkdir(parents=True,exist_ok=True)
   render([(p['name'],p['shape'],COLORS[p['material']]) for p in parts],OUT/'images/D3_M.png','Rev D | shared bearing and friction support | development')
   cut=cube((150,150,200),(75,75,20))
   ss=[(p['name'],p['shape'].cut(cut),COLORS[p['material']]) for p in parts];ss=[x for x in ss if x[1].Volume()>.01]
   render(ss,OUT/'images/D3_M_section.png','Rev D | metal preload loop | explanatory cutaway')
  save(ROOT/'verification/revD_compact_modules.json',report)
if __name__=='__main__':main()
