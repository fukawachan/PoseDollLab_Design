"""Rev H: four-axis shoulder girdle, concentric shoulders, and existing elbow arms.
Packaging CAD only: clutch preload, shaft retention, readout supports and load ratings are not released.
All geometry belongs to an explicit existing FK node; no joint centre is relocated.
"""
from pathlib import Path
import sys,json,math
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];OUT=ROOT/'generated/revH'
sys.path.insert(0,str(HERE.parent));from model import fk,rotation,keyposes
from collision_policy import classify_checks
from build import render
sys.path.insert(0,str(HERE.parent/'revG'));import centerline_study as arm
COL={'frame':(.27,.49,.59),'metal':(.63,.68,.71),'bush':(.82,.81,.70),'lining':(.60,.35,.20),'shell':(.79,.83,.85),'sensor_space':(.18,.47,.28),'transfer_space':(.85,.57,.20),'spring_space':(.42,.44,.46)}
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def cube(d,c=(0,0,0)):return cq.Workplane('XY').box(*d).translate(tuple(c)).val()
def rod(a,b,r):
 a=np.array(a,float);v=np.array(b,float)-a
 return cq.Solid.makeCylinder(r,float(np.linalg.norm(v)),cq.Vector(*a),cq.Vector(*(v/np.linalg.norm(v))))
def axis_cyl(axis,start,end,r,at=(0,0,0)):
 a=np.array(at,float);v=np.eye(3)[axis];return rod(a+v*start,a+v*end,r)
def tube(axis,start,end,ro,ri,at=(0,0,0)):return axis_cyl(axis,start,end,ro,at).cut(axis_cyl(axis,start-1,end+1,ri,at))
def union(shapes):
 s=shapes[0]
 for b in shapes[1:]:s=s.fuse(b)
 return s
def move(s,T):return s.moved(cq.Location(cq.Plane(origin=tuple(T[:3,3]),xDir=tuple(T[:3,0]),normal=tuple(T[:3,2]))))
def profile(name):return json.loads((ROOT/f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json').read_text('utf8'))
def scene(parts,p,pose):
 T,A=fk(p,pose)
 return [dict(x,shape=move(x['local_shape'],T[x['owner']])) for x in parts],T,A
def collisions(items,include_reservations=False):
 hits=[];bb=[p['shape'].BoundingBox() for p in items]
 for i,a in enumerate(items):
  for j in range(i+1,len(items)):
   b=items[j]
   if a['owner']==b['owner']:continue
   if not include_reservations and (a['role']=='reservation' or b['role']=='reservation'):continue
   if not all(min(getattr(bb[i],k+'max'),getattr(bb[j],k+'max'))-max(getattr(bb[i],k+'min'),getattr(bb[j],k+'min'))>1e-4 for k in 'xyz'):continue
   vol=a['shape'].intersect(b['shape']).Volume()
   if vol>.02:hits.append({'a':a['name'],'b':b['name'],'volume_mm3':round(vol,4),'reservation_involved':a['role']=='reservation' or b['role']=='reservation'})
 return hits
def cases():
 out={'neutral':{}}
 for label,pro,ele in [('forward',30,0),('backward',-20,0),('shrug',0,30),('down',0,-15),('forward_up',30,30),('back_down',-20,-15)]:
  out[label]={f'clavicle_{s}.{a}':v for s in ('l','r') for a,v in [('protract',pro),('elevate',ele)]}
 out['asymmetric']={'clavicle_l.protract':30,'clavicle_l.elevate':30,'clavicle_r.protract':-20,'clavicle_r.elevate':-15}
 for key in ('arms_forward','arms_overhead','arms_side','hands_on_hips','arms_crossed','forehead'):
  out[key]=keyposes()[key]
 out['forward_shrug_reach']={**out['forward_up'],**out['arms_forward']}
 out['elbows_closed']={'elbow_l.flex':145,'elbow_r.flex':145}
 # Preserve raw contacts as pose restrictions or structural findings; add distinct poses.
 out['down_arms_vertical']={**out['down'],**{f'upperarm_{s}.abduct':15 for s in ('l','r')}}
 out['back_down_arms_clear']={**out['back_down'],**{f'upperarm_{s}.abduct':20 for s in ('l','r')}}
 out['shrug_reach_parallel']={**out['forward_up'],**{f'upperarm_{s}.{a}':v for s in ('l','r') for a,v in [('flex',73.897886248),('abduct',25.658906274)]}}
 out['crossed_staggered']={'upperarm_l.flex':80,'upperarm_r.flex':50,'upperarm_l.abduct':-15,'upperarm_r.abduct':-15,'elbow_l.flex':115,'elbow_r.flex':115,'upperarm_l.twist':60,'upperarm_r.twist':60}
 out['crossed_clearance_candidate']={'upperarm_l.flex': 60, 'upperarm_r.flex': 75, 'elbow_l.flex': 115, 'elbow_r.flex': 90, 'upperarm_l.abduct': -20, 'upperarm_r.abduct': -20, 'upperarm_l.twist': 65, 'upperarm_r.twist': 35}
 return out
def build(name):
 p=profile(name);T0,A0=fk(p,{});parts=[];datums={}
 def add(label,s,material,owner,origin,role='structural_concept',note=''):
  if not s.isValid():raise ValueError('Invalid '+label)
  local=s.translate(tuple(np.array(origin)-T0[owner][:3,3]))
  parts.append({'name':label,'local_shape':local,'material':material,'owner':owner,'role':role,'note':note})
 # Root shafts are only 9.3 mm apart in Quinn. Common upper bearing bridge, staggered lower clutches.
 roots={s:A0[f'clavicle_{s}.protract']['origin'] for s in ('l','r')}
 mid=(roots['l']+roots['r'])/2
 fixed=[cube((14,float(abs(roots['l'][1]-roots['r'][1])+10),10),(0,0,-13))]
 fixed += [rod((-28,y,-110),(-28,y,-27),3.5) for y in (-10,10)]
 fixed += [rod((-6,y,-13),(-28,y,-27),3.5) for y in (-6,6)]
 fixed += [rod((-28,-10,-100),(-28,10,-100),3.5)]
 for side,sy in [('l',1),('r',-1)]:
  R=roots[side];off=R-mid;P=f'clavicle_{side}.protract_frame';E=f'clavicle_{side}';d=sy
  c=-45 if side=='l' else -76
  fixed.append(tube(2,c+8,c+16,5.5,3.15,off))
  fixed.append(rod(off+[-5,0,c+12],[-28,sy*10,c+12],3.5))
  add(side+'_yaw_bush_top',tube(2,-18,-8,3,2.05),'bush','chest',R)
  add(side+'_yaw_bush_lower',tube(2,c+8,c+16,3,2.05),'bush','chest',R)
  add(side+'_yaw_shaft',axis_cyl(2,c-7,-3,2),'metal',P,R,note='4 mm shaft candidate; keyed retention and bending verification pending')
  carrier=[tube(2,-7,-3,4,2.1),rod((0,0,-2),(d*44,0,-14),3)]
  for x in (27,43):
   lo,hi=sorted((d*(x-3),d*(x+3)))
   carrier += [tube(0,lo,hi,5.5,3.15),rod((d*x,0,-14),(d*x,0,-3),3)]
   add(side+'_elev_bush_'+str(x),tube(0,lo,hi,3,2.05),'bush',P,R)
  add(side+'_yaw_carriage',union(carrier),'frame',P,R,note='Front/rear offset bearings share the original elevation axis line')
  lo,hi=sorted((d*20,d*56))
  add(side+'_elev_shaft',axis_cyl(0,lo,hi,2),'metal',E,R,note='4 mm shaft candidate; final retention pending')
  S=A0[f'upperarm_{side}.flex']['origin'];sd=S-R
  # A two-bearing cantilever on the medial Y side leaves the rest of the shoulder open.
  endpoint=sd+[0,-sy*31.5,0]
  hubs=tube(0,min(d*31,d*37),max(d*31,d*37),6.5,2.1)
  link=union([hubs,rod((d*34,0,0),(d*34,sy*16,0),3.5),rod((d*34,sy*16,0),endpoint,3.5)])
  shoulder_base=[]
  for y in (-36.5,-27.5):
   lo,hi=sorted((sy*(y-2.5),sy*(y+2.5)))
   shoulder_base += [tube(1,lo,hi,6.5,4.15,sd)]
   add(side+'_flex_bush_'+str(y),tube(1,lo,hi,4,3.05,sd),'bush',E,R)
  shoulder_base += [rod(sd+[0,-sy*36.5,-5],sd+[0,-sy*27.5,-5],3)]
  link=link.fuse(union(shoulder_base))
  link=link.cut(axis_cyl(1,min(-sy*42,-sy*23),max(-sy*42,-sy*23),4.15,sd))
  add(side+'_clavicle_output_frame',link,'frame',E,R,note='No shoulder cover; connects offset elevation hub to the original shoulder axis')
  # Friction faces are geometrical candidates. The spring and adjuster are explicitly only reserved.
  for label,axis,start,fixed_owner,rot_owner,sign,center in [('yaw',2,c,'chest',P,1,R),('elev',0,48,P,E,d,R)]:
   def circ(a,b,ro,ri):
    sh=tube(axis,min(sign*a,sign*b),max(sign*a,sign*b),ro,ri)
    if label=='yaw':sh=sh.cut(cube((50,30,40),(0,-sy*20.5,c)))
    return sh
   add(side+'_'+label+'_fixed_face',circ(start,start+1,12,2.15),'metal',fixed_owner,center)
   add(side+'_'+label+'_friction',circ(start+1,start+1.5,12,2.15),'lining',fixed_owner,center)
   add(side+'_'+label+'_rotor_face',circ(start+1.5,start+3.5,12,2.1),'metal',rot_owner,center)
   add(side+'_'+label+'_preload_space',circ(start-6,start,6.5 if label=='yaw' else 11,2.15),'spring_space',fixed_owner,center,'reservation','Preload load path, spring selection and fasteners not completed')
   if label=='yaw':
    mag=axis_cyl(2,c-10,c-7,3);board=cube((18,20,1.6),(0,sy*4,c-13.9));chip=cube((6.4,5,1.1),(0,0,c-12.55))
   else:
    mag=axis_cyl(0,min(d*56,d*59),max(d*56,d*59),3);board=cube((1.6,18,20),(d*62.9,0,0));chip=cube((1.1,6.4,5),(d*61.55,0,0))
   add(side+'_'+label+'_magnet_space',mag,'transfer_space',rot_owner,center,'reservation','Magnet holder and field test pending')
   add(side+'_'+label+'_pcb_space',board,'sensor_space',fixed_owner,center,'reservation','18 x 20 outline, yaw board shifted 4 mm outward; new component layout/connector/mounts pending')
   add(side+'_'+label+'_chip_space',chip,'sensor_space',fixed_owner,center,'reservation','Nominal 2 mm magnet face gap; not magnetically validated')
  # Shoulder flex(Y), abduction(X), twist(Z) are concentric. Stub shafts leave the centre open.
  F=f'upperarm_{side}.flex_frame';B=f'upperarm_{side}.abduct_frame';W=f'upperarm_{side}'
  outer=tube(2,-3,3,22,18).cut(cube((60,50,30),(0,sy*33,0)))
  for x in (-20.5,20.5):
   outer=outer.fuse(tube(0,x-2.5,x+2.5,5,3.15))
   outer=outer.cut(axis_cyl(0,x-4,x+4,3.15))
   add(side+'_abduct_bush_'+str(x),tube(0,x-2.5,x+2.5,3,2.05),'bush',F,S)
  lo,hi=sorted((-sy*43,-sy*19))
  add(side+'_flex_stub',axis_cyl(1,lo,hi,3),'metal',F,S)
  add(side+'_flex_ring',outer,'frame',F,S,note='Concentric open shoulder yoke; lateral opening clears 90 degree abduction; clamps and bearing retention pending')
  inner=tube(2,-3,3,14,10)
  inner=inner.fuse(tube(2,-9,6,6.5,3.15))
  for y in (-1,1):inner=inner.fuse(rod((0,y*5,0),(0,y*12,0),2.2))
  for sign in (-1,1):
   add(side+'_abduct_stub_'+str(sign),axis_cyl(0,min(sign*12,sign*26),max(sign*12,sign*26),2),'metal',B,S)
  add(side+'_abduct_ring_and_twist_seat',inner,'frame',B,S)
  add(side+'_twist_bush',tube(2,-8,5,3,2.05),'bush',B,S)
  add(side+'_twist_shaft',axis_cyl(2,-24,10,2),'metal',W,S)
  add(side+'_twist_fixed_face',tube(2,-9,-8,9,3.15),'metal',B,S)
  add(side+'_twist_rotor_face',tube(2,-12,-10,9,2.1),'metal',W,S)
  add(side+'_twist_lining',tube(2,-10,-9,9,3.15),'lining',B,S)
  # Remaining shoulder clutch/encoder packages are NOT represented or collision-cleared.
  add(side+'_arm_coupling',cube((14,12,9),(0,0,-25)).cut(axis_cyl(2,-32,-18,2.1)),'frame',W,S,note='Interface only; clamps/fasteners not completed')
  arm_parts,meta=arm.build(name);Epos=A0[f'elbow_{side}.flex']['origin']
  for item in arm_parts:
   owner=W if item['owner']=='upperarm' else f'elbow_{side}'
   sh=item['shape'] if side=='l' else item['shape'].mirror('XZ')
   add(side+'_arm_'+item['name'],sh,item['material'],owner,Epos,item['role'],item['note'])
  datums[side]={'root_mm':R.tolist(),'shoulder_mm':S.tolist(),'elbow_mm':Epos.tolist(),'elevation_bearing_axis_points_mm':[(R+[d*27,0,0]).tolist(),(R+[d*43,0,0]).tolist()],'yaw_clutch_z_offset_mm':c,'bearing_offset_direction':'front' if d>0 else 'rear','pending_shoulder_axes_readout':[f'upperarm_{side}.{x}' for x in ('flex','abduct','twist')]}
 base=union(fixed)
 for R in roots.values():base=base.cut(axis_cyl(2,-90,0,3.15,R-mid))
 add('common_chest_bearing_frame',base,'frame','chest',mid,note='Shared top bearing block; minimum inter-bore web is reported, strength pending')
 return p,parts,{'character':name,'axis_count_total':44,'axis_count_articulated_in_this_assembly':12,'root_spacing_mm':float(np.linalg.norm(roots['l']-roots['r'])),'upper_bearing_min_nominal_web_mm':float(np.linalg.norm(roots['l'][:2]-roots['r'][:2])-6.3),'datums':datums,'scope':'Rigid-frame kinematic packaging; incomplete preload and readout; no soft covers; no hands, forearm twist or wrists'}
def export(name,p,parts,meta,poses=None):
 folder=OUT/name;folder.mkdir(parents=True,exist_ok=True);items,_,_=scene(parts,p,{})
 assy=cq.Assembly(name=name+'_RevH_shoulder_assembly')
 rows=[]
 for item in items:
  s=item['shape'];assy.add(s,name=item['name'],color=cq.Color(*COL[item['material']]))
  bb=s.BoundingBox();rows.append({k:v for k,v in item.items() if k not in ('shape','local_shape')}|{'valid':s.isValid(),'solids':len(s.Solids()),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen]})
  if item['material']=='frame' and not '_arm_' in item['name']:cq.exporters.export(s,str(folder/(item['name']+'.step')))
 assy.save(str(folder/(name.title()+'_shoulder_assembly.step')))
 checks=[]
 for label,q in (poses or cases()).items():
  current,T,A=scene(parts,p,q);hits=collisions(current)
  alignment=[]
  for part in current:
   n=part['name'];side=n[0];axis=None
   if side not in ('l','r'):continue
   if '_yaw_bush_' in n or n.endswith('_yaw_shaft'):axis=f'clavicle_{side}.protract'
   elif '_elev_bush_' in n or n.endswith('_elev_shaft'):axis=f'clavicle_{side}.elevate'
   elif '_flex_bush_' in n or n.endswith('_flex_stub'):axis=f'upperarm_{side}.flex'
   elif '_abduct_bush_' in n or '_abduct_stub_' in n:axis=f'upperarm_{side}.abduct'
   elif n.endswith('_twist_bush') or n.endswith('_twist_shaft'):axis=f'upperarm_{side}.twist'
   if axis:
    center=np.array(part['shape'].Center().toTuple());off=center-A[axis]['origin']
    error=float(np.linalg.norm(np.cross(off,A[axis]['direction'])))
    alignment.append({'part':n,'axis_id':axis,'axis_line_error_mm':error})
  assert max(x['axis_line_error_mm'] for x in alignment)<1e-5
  checks.append({'pose':label,'angles_deg':q,'hits':hits,'bearing_axis_alignment_max_mm':max(x['axis_line_error_mm'] for x in alignment),'bearing_axis_checks':len(alignment)})
  print(json.dumps({'character':name,'pose':label,'hits':len(hits),'first':hits[:3]},ensure_ascii=False),flush=True)
 neutral_reservations=collisions(items,True)
 loads=[]
 for check in checks:
  _,A=fk(p,check['angles_deg'])
  for side in ('l','r'):
   target=A[f'hand_{side}.flex']['origin']
   for prefix,axes in [(f'clavicle_{side}',('protract','elevate')),(f'upperarm_{side}',('flex','abduct','twist')),(f'elbow_{side}',('flex',))]:
    for key in axes:
     axis=prefix+'.'+key;item=A[axis]
     torque=abs(float(np.dot(item['direction'],np.cross((target-item['origin'])*.001,[0,0,-.1*9.80665]))))
     loads.append({'pose':check['pose'],'axis':axis,'torque_nm_per_100g_at_wrist':torque,'sample_has_collision':bool(check['hits'])})
 record={'unit_payload_note':'100 g point payload at the wrist, gravity only; excludes assembly mass and hand forces; not a rating','unit_payload_loads':loads,'meta':meta,'parts':rows,'motion_checks':checks,'neutral_reservation_contacts':[x for x in neutral_reservations if x['reservation_involved']],'manufacturing_released':False,'physical_tested':False}
 record=classify_checks(record)
 save(ROOT/f'verification/revH_{name}.json',record)
 render([(x['name'],x['shape'],COL[x['material']]) for x in items],folder/'neutral.png',name.title()+' | Rev H shoulder integration | packaging candidate',camera=(1000,-1500,600))
 return record
if __name__=='__main__':
 names=['quinn'] if '--quick' in sys.argv else ['manny','quinn']
 for name in names:
  p,parts,meta=build(name);export(name,p,parts,meta,{'neutral':{}} if '--quick' in sys.argv else None)
