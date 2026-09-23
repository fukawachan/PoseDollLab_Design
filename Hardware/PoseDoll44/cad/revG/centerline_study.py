"""Rev G centreline arm and split-shell space study.
Mechanical details of preload adjustment and the offset angle pickup are NOT released.
"""
from pathlib import Path
import sys,json,math,hashlib
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'generated/revG'
sys.path.insert(0,str(HERE.parent));from model import rotation
sys.path.insert(0,str(HERE.parent/'revE'));from character_reference import reference_character,make_profile
from build import render
COL={'frame':(.29,.48,.57),'metal':(.64,.69,.73),'lining':(.62,.38,.21),'sensor_space':(.16,.50,.29),'transfer_space':(.89,.61,.19),'shell':(.78,.83,.85),'bush':(.85,.84,.71),'spring_space':(.44,.46,.48)}
WALL=1.8;OUTER_ALLOWANCE=.8;FACTOR=1.5
ELBOW_RELIEF_SLOPE=2.5;ELBOW_RELIEF_REACH_MM=24.0

def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def cube(d,c):return cq.Workplane('XY').box(*d).translate(c).val()
def rod(a,b,r):
 a=np.array(a);d=np.array(b)-a;return cq.Solid.makeCylinder(r,float(np.linalg.norm(d)),cq.Vector(*a),cq.Vector(*(d/np.linalg.norm(d))))
def cy(r,y,h,z=0):return rod((0,y,z),(0,y+h,z),r)
def ring(ro,ri,y,h,z=0):return cy(ro,y,h,z).cut(cy(ri,y-1,h+2,z))
def beam(z0,z1,w,h):return cube((w,h,z1-z0),(0,0,(z1+z0)/2)).cut(cube((w-4,h-4,z1-z0+2),(0,0,(z1+z0)/2)))
def rotate(s,deg):return s.rotate((0,0,0),(0,-1,0),deg)
def pose_parts(parts,q):return [dict(p,shape=rotate(p['shape'],q)) if p['owner']=='forearm' else p for p in parts]
def pair_hits(parts):
 hits=[];bb=[p['shape'].BoundingBox() for p in parts]
 for i,a in enumerate(parts):
  for j,b in enumerate(parts[i+1:],i+1):
   if a['owner']==b['owner']:continue
   if a['role']=='reservation' or b['role']=='reservation':continue
   if not all(min(getattr(bb[i],x+'max'),getattr(bb[j],x+'max'))-max(getattr(bb[i],x+'min'),getattr(bb[j],x+'min'))>1e-4 for x in 'xyz'):continue
   v=a['shape'].intersect(b['shape']).Volume()
   if v>.02:hits.append({'a':a['name'],'b':b['name'],'intersection_mm3':float(v)})
 return hits

def shell_loft(rows,offset=0,inner=False):
 wire=[]
 for r in rows:
  z,cx,cyy,rx,ry=r;rx-=offset;ry-=offset
  wire.append(cq.Workplane('XY',origin=(cx,cyy,z)).ellipse(rx,ry).val())
 return cq.Solid.makeLoft(wire,True)

def shell_rows(name,part,elbow_z,U,F):
 env=json.loads((ROOT/'verification/revG_surface_envelopes.json').read_text(encoding='utf8'))['characters'][name][part]
 rows=[]
 for r in env['sections']:
  if part=='upperarm' and not .25<=r['fraction']<=.9:continue
  if part=='forearm' and not .1<=r['fraction']<=.75:continue
  # A simplified anatomical oval, fitted to the section's extents, not a copy of the skin mesh.
  cx,cyy=np.array(r['offset_bbox_centre_mm'])*FACTOR
  z=(r['z_mm_at_one_third']-elbow_z)*FACTOR
  rows.append((z,cx,cyy,r['depth_x_mm']*FACTOR/2+OUTER_ALLOWANCE,r['width_y_mm']*FACTOR/2+OUTER_ALLOWANCE))
 return sorted(rows)

def build(name):
 baseline=json.loads((ROOT/'verification/revE_proportion_baselines.json').read_text(encoding='utf8'))['characters'][name]['measurements_mm']
 U=baseline['upperarm_l']*FACTOR;F=baseline['forearm_l']*FACTOR
 landmarks=json.loads((ROOT/'generated/revE'/name/'neutral_landmarks.json').read_text(encoding='utf8'))['bone_landmarks_mm'];ez=landmarks['lowerarm_l'][2];parts=[]
 def add(n,s,m,o,role='solid_concept',note=''):
  if not s.isValid():raise ValueError(n)
  parts.append(dict(name=n,shape=s,material=m,owner=o,role=role,note=note))
 # Two slim cheeks put the force path back inside the upper-arm cross section.
 fork=None
 for y in (-8.5,6):
  cheek=cy(12,y,2.5).fuse(cube((24,2.5,35),(0,y+1.25,23)))
  cheek=cheek.cut(cy(3.15,y-1,4.5))
  fork=cheek if fork is None else fork.fuse(cheek)
 fork=fork.fuse(cube((18,17,6),(0,0,42))).fuse(beam(43,U-25,12,10))
 # Pickup axis is 24mm above elbow; detailed supports/fasteners remain unmodelled.
 for y in (-8.5,6):fork=fork.cut(cy(2.6,y-1,4.5,24))
 fork=fork.cut(cube((18.2,20,22),(0,12,25)))
 add('upperarm_centreline_fork',fork,'frame','upperarm',note='Axial preload compliance/guidance and mounting details pending; not a finalized load-rated clevis')
 rotor=ring(10,4.03,-5,10)
 rotor=rotor.fuse(beam(-F+22,-8,10,8))
 add('forearm_centreline_link',rotor,'frame','forearm',note='Elbow-to-wrist centre distance retained; distal wrist integration pending')
 add('rotor_radial_bush',ring(4,3.03,-4.9,9.8),'bush','forearm')
 for y in (-6,5):add('friction_face_'+str(y),ring(10,4.2,y,1),'lining','upperarm')
 add('smooth_pivot_pin',cy(3,-10,23).fuse(cy(4.8,-13,3)),'metal','upperarm',note='6mm stationary pin; thread/retention details not finalized')
 add('left_load_washer',ring(5.5,3.15,-10,1.5),'metal','upperarm')
 add('right_spring_seat',ring(6.5,3.15,8.5,.5),'metal','upperarm')
 add('spring_stack_reserved',ring(6.25,3.1,9,.926),'spring_space','upperarm','reservation','Two series springs: nominal envelope only, preload adjustment pending')
 add('preload_cap_reserved',ring(6.5,3.15,9.926,2),'spring_space','upperarm','reservation')
 add('preload_screw_reserved',cy(2.75,11.926,3),'spring_space','upperarm','reservation')
 # Tooth envelopes must not be interpreted as validated gears; occupied spaces are explicit.
 # The readout moves up the arm so the PCB does not add to elbow width.
 add('input_gear_reserved',ring(12.6,9.95,-2.8,2),'transfer_space','forearm','reservation','m0.6, 40T candidate pitch diameter24; teeth, fastening, backlash and tolerances pending')
 add('pickup_gear_reserved',ring(12.6,2,-2.8,2,24),'transfer_space','upperarm','reservation','1:1 external gear reading candidate; nominal sensor angle = -elbow angle; actual rotor must rotate, envelope is stationary')
 add('pickup_shaft_reserved',cy(2,-7.5,9.5,24),'transfer_space','upperarm','reservation')
 add('magnet_reserved',cy(3,2,3,24),'transfer_space','upperarm','reservation','6x3 diametric magnet dimension candidate; field and alignment untested')
 add('sensor_package_reserved',cube((6.4,1.1,5),(0,7.55,24)),'sensor_space','upperarm','reservation')
 add('sensor_PCB_reserved',cube((16,1,18),(0,8.6,24)),'sensor_space','upperarm','reservation','New board outline reservation; not routed or electrically reviewed')
 add('flat_cable_exit_reserved',cube((8,2,8),(0,8,34)),'sensor_space','upperarm','reservation','Flat cable route space; bend radius and fastening pending')
 shell_meta=[]
 for region,owner in [('upperarm','upperarm'),('forearm','forearm')]:
  rows=shell_rows(name,region,ez,U,F)
  outer=shell_loft(rows);inner_rows=list(rows);first=list(rows[0]);last=list(rows[-1]);first[0]-=1;last[0]+=1;inner_rows[0]=first;inner_rows[-1]=last
  cavity=shell_loft(inner_rows,WALL);wall=outer.cut(cavity)
  # The user requests exposed deforming regions: retract both closing shell edges.
  # This region stays open; no flexible skin, boot or floating elbow cap is required.
  k=ELBOW_RELIEF_SLOPE;reach=ELBOW_RELIEF_REACH_MM
  poly=[(-150,-300),(150,-300),(150,reach+150*k),(-150,reach-150*k)] if region=='upperarm' else [(-150,300),(150,300),(150,-reach-150*k),(-150,-reach+150*k)]
  relief=cq.Workplane('XZ').polyline(poly).close().extrude(400).translate((0,200,0)).val()
  wall=wall.cut(relief)
  # Front/back halves retain an intentional narrow seam for removable covers.
  for side in ('front','back'):
   clip=cube((200,240,500),((100.2 if side=='front' else -100.2),0,0))
   half=wall.intersect(clip)
   add(region+'_shell_'+side,half,'shell',owner,note='1.8mm axis-offset oval wall; closure bosses/latches and exact wall-thickness audit pending')
   bb=half.BoundingBox();shell_meta.append({'name':region+'_'+side,'bbox_mm':[bb.xlen,bb.ylen,bb.zlen],'one_solid':len(half.Solids())==1,'volume_mm3':half.Volume()})
 return parts,{'character':name,'scale':.5,'outer_oval_semiaxis_allowance_mm':OUTER_ALLOWANCE,'shell_policy':'rigid_segment_shells_exposed_motion_zones','elbow_relief':{'slope':ELBOW_RELIEF_SLOPE,'reach_mm':ELBOW_RELIEF_REACH_MM,'cover_required':False},'height_mm':baseline['neutral_surface_height']*FACTOR,'upperarm_mm':U,'forearm_mm':F,'shoulder_datum_mm':[0,0,U],'elbow_mm':[0,0,0],'wrist_datum_mm':[0,0,-F],'shells':shell_meta,'scope':'Elbow centreline packaging and open limb shell study; other 43 axes not mechanically integrated. Reservations are not finished parts.'}


def render_exposed(parts,name):
 posed=pose_parts(parts,145)
 render([(p['name'],p['shape'],COL[p['material']]) for p in posed],
        OUT/'images'/(name+'_exposed_elbow_145.png'),
        name.title()+' | exposed elbow at 145 deg | packaging study',camera=(450,-1700,150))

def main():
 report={'status':'ANTHROPOMORPHIC_CENTRELINE_AND_SHELL_FEASIBILITY','manufacturing_released':False,'physical_tested':False,'selected_trial_scale':.5,'checks_scope':'Cross-owner non-reserved solids and neutral shell vs all contents; does not certify same-owner assembly, tooth engagement, moving pickup gear or the reserved spring/PCB/cable spaces.','characters':{},'not_covered':['Elbow remains intentionally exposed; soft coverings are excluded by the user decision','Preload stack compliance and adjustment','Gear tooth geometry, backlash, bearings and calibration','New sensor PCB layout and wiring','Shoulder, wrist and other axes','Shell fasteners, rounded exposed edges and continuous collision path','Full-body load, grip force, stand and physical handling']}
 for name in ('manny','quinn'):
  parts,meta=build(name);folder=OUT/'step'/name;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name=name.title()+'_centreline_shell_study');rows=[]
  for p in parts:
   assy.add(p['shape'],name=p['name'],color=cq.Color(*COL[p['material']]))
   if p['material'] in ('shell','frame'):cq.exporters.export(p['shape'],str(folder/(p['name']+'.step')))
   bb=p['shape'].BoundingBox();rows.append({k:v for k,v in p.items() if k!='shape'}|{'valid':p['shape'].isValid(),'solids':len(p['shape'].Solids()),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen]})
  assy.save(str(folder/(name.title()+'_centreline_shell_study.step')))
  samples=[]
  for q in (0,30,60,90,110,120,130,145):samples.append({'elbow_deg':q,'hits':pair_hits(pose_parts(parts,q))})
  # Even reservation-to-shell contacts matter; do not silently skip packaging failures.
  sh=[p for p in parts if p['material']=='shell'];hard=[p for p in parts if p['material']!='shell'];contacts=[]
  for a in sh:
   for b in hard:
    v=a['shape'].intersect(b['shape']).Volume()
    if v>.02:contacts.append({'shell':a['name'],'part':b['name'],'mm3':v})
  report['characters'][name]={'meta':meta,'parts':rows,'motion_samples':samples,'neutral_shell_intersections_including_reservations':contacts}
  print(json.dumps({'name':name,'shell_contacts':contacts,'samples':[(s['elbow_deg'],len(s['hits'])) for s in samples]},ensure_ascii=False),flush=True)
  render([(p['name'],p['shape'],COL[p['material']]) for p in parts if p['material']!='shell'],OUT/'images'/(name+'_internal_arm.png'),name.title()+' | centreline architecture | reserved pickup spaces in amber/green',camera=(600,-1500,250))
  render([(p['name'],p['shape'],COL[p['material']]) for p in parts if not p['name'].endswith('_front')],OUT/'images'/(name+'_cutaway_arm.png'),name.title()+' | rigid limb shells, exposed elbow | not manufacturing release',camera=(1000,-900,150))
  render_exposed(parts,name)
 save(ROOT/'verification/revG_centreline_arm.json',report)
if __name__=='__main__':main()
