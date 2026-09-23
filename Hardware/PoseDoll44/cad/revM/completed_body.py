"""Complete rigid assembly; manufacture candidate, physical qualification pending."""
from large_sensor_heads import *
import large_sensor_heads as body


def build(name):
 A,meta=body.build(name);changed=[];reliefs=[]
 # Murata max .95 mm body plus .10 mm solder seating allowance.
 for c in channels41(A,name):
  large=c['axis_id'].startswith('upperarm_') and c['axis_id'].endswith('.abduct')
  pre=c['part_prefix'];key=next(q['name'] for q in A.parts if q['name'].startswith(pre) and q['name'].endswith('pcb_passive_3' if large else 'pcb_C2'))
  q,w=world_part(A,key)
  loc=cq.Location(cq.Plane(origin=tuple(c['origin_neutral_mm']),normal=tuple(c['normal_neutral']),xDir=tuple(c['xdir_neutral'])))
  datum=c['package_face_mm']+(2.595 if large else 1.995);rot=c.get('board_rotation_deg',0)
  x,y=(5.7,2.3) if large else (2.3,3.75)
  height=1.05;board_face=datum-(1.595 if large else .995)
  cap=cube((2.3,1.45,height),(x,y,board_face-height/2)).rotate((0,0,0),(0,0,1),rot).moved(loc)
  replace_world(A,q,cap,'Murata GRM219R61E106KA12D 10 uF 25 V X5R, max .95 mm body + .10 mm solder seating allocation','pcb_component');changed.append(key)
 # Relieve only removable cover edges, using the moving shell coordinate frame.
 limits={q['id']:np.degrees(q['limits_rad']) for q in A.profile['axes']}
 for side in ('l','r'):
  rotor,rw=world_part(A,f'clavicle_{side}_protract_G4_D4_friction_rotor')
  joint=A.joints[f'clavicle_{side}.protract'];loc=joint['loc'];bb=rw.moved(loc.inverse).BoundingBox()
  tool=cube((bb.xlen+1.6,bb.ylen+1.6,bb.zlen+1.6),((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2)).moved(loc)
  tool=tool.translate(tuple(-A.T0[rotor['owner']][:3,3]));cutters=[];owner=f'upperarm_{side}'
  for angle in np.linspace(limits[f'upperarm_{side}.abduct'][0],0,11):
   T,_=h.fk(A.profile,{f'upperarm_{side}.abduct':float(angle)})
   world=h.move(tool,T[rotor['owner']]);cutters.append(h.move(h.move(world,np.linalg.inv(T[owner])),A.T0[owner]))
  for face in ('front','back'):
   q,w=world_part(A,f'{side}_arm_upperarm_shell_{face}');before=w.Volume()
   for cutter in cutters:w=w.cut(cutter)
   replace_world(A,q,w,q['note']+'; proximal shoulder-rotor sweep relieved with .8 mm bounding clearance',q['material'])
   changed.append(q['name']);reliefs.append(dict(part=q['name'],removed_mm3=before-w.Volume()))
 return A,dict(meta,final_rigid_parts=changed,proximal_arm_shell_reliefs=reliefs,sensor_C2='GRM219R61E106KA12D')


def main():
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name);cache=CollisionCache(A);cases,_=poses(A);checks=[]
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,set(meta['final_rigid_parts']),label!='neutral'),A.parts)
   checks.append(dict(pose=label,angles_deg=pose,review=review));bad=[r for r in review if r['classification']=='structural']
   if bad:print(json.dumps(dict(character=name,pose=label,structural=bad)),flush=True)
  out[name]=dict(changes=meta['proximal_arm_shell_reliefs'],checks=checks,readout=readout(A,channels41(A,name),cases))
  h.save(ROOT/'verification/revM_completed_rigid_work.json',out)
  print(name,'completed rigid',len(checks),'failed',sum(any(r['classification']=='structural' for r in q['review']) for q in checks),flush=True)
if __name__=='__main__':main()
