"""Removable arm covers secured to the rigid segment with captive M2 nuts."""
from wire_saddles import *
import wire_saddles as body

def attach(A,owner,frame_name,names,zs,y=0):
 origin=A.T0[owner][:3,3];fq,fw=world_part(A,frame_name);fw=fw.translate(tuple(-origin));pieces={}
 for face,name in names.items():
  q,w=world_part(A,name);pieces[face]=(q,w.translate(tuple(-origin)))
 rows=[];affected=[frame_name,*names.values()]
 for i,z in enumerate(zs):
  # The closed lug replaces the local hollow beam section only at the bolt.
  lug=cube((12,abs(y)+6,6),(0,y/2,z))
  for _,wall_shape in pieces.values():
   for delta in ((.25,0,0),(-.25,0,0),(0,.25,0),(0,-.25,0),(0,0,.25),(0,0,-.25)):
    lug=lug.cut(wall_shape.translate(delta))
  fw=fuse_checked(fw,lug,owner+'_shell_lug')
  fw=fw.cut(h.axis_cyl(0,-7,7,1.2,(0,y,z)))
  xl=cq.Location(cq.Plane(origin=(0,y,z),normal=(1,0,0),xDir=(0,1,0)))
  for face,sg in (('front',1),('back',-1)):
   q,w=pieces[face];probe=h.axis_cyl(0,*sorted((sg*6,sg*60)),3.9,(0,y,z));wall=probe.intersect(w)
   assert wall.Volume()>.1,(q['name'],z,'no shell at mount')
   bb=wall.BoundingBox();end=bb.xmax-.25 if sg>0 else bb.xmin+.25
   boss=h.axis_cyl(0,*sorted((sg*6.1,end)),3.9,(0,y,z));w=fuse_checked(w,boss,q['name']+'_mount')
   w=w.cut(h.axis_cyl(0,-65,65,1.2,(0,y,z)))
   if sg>0:w=w.cut(h.axis_cyl(0,10,65,2.1,(0,y,z)))
   else:w=w.cut(hexagon(4.2,-65,-8).moved(xl))
   pieces[face]=(q,w)
  bolt=h.axis_cyl(0,-10,10,1,(0,y,z)).fuse(h.axis_cyl(0,10,12,1.9,(0,y,z))).cut(hexagon(1.5,10.7,12.1).moved(xl))
  nut=hexagon(4,-9.6,-8).cut(cyl(-9.7,-7.9,.8));nut=nut.moved(xl)
  bn=owner+f'_cover_M2x20_{i}';nn=owner+f'_cover_nut_M2_{i}'
  A.add(bn,bolt.translate(tuple(origin)),'metal',owner,'M2x20 socket screw; straight front access; cover attachment only')
  A.add(nn,nut.translate(tuple(origin)),'metal',owner,'M2 regular nut in AF4.2 rear cover pocket; install before cover closure');A.thread_pairs.append([bn,nn]);affected.extend((bn,nn))
  rows.append(dict(owner=owner,local_z_mm=z,local_y_mm=y,screw=bn,nut=nn,nominal_clearance_to_beam_mm=.1,front_tool_axis=[1,0,0],function='removable cover only; joint preload independent'))
 replace_world(A,fq,fw.translate(tuple(origin)),fq['note']+'; closed local shell lugs and M2.4 through bores','frame')
 for face,(q,w) in pieces.items():replace_world(A,q,w.translate(tuple(origin)),'1.8 mm partial rigid arm cover; '+('two' if len(zs)==2 else 'one')+' M2x20 through captive rear nuts into closed centreline rail lugs; front straight hex access, remove before servicing joints; pose clearance sampled digitally','shell')
 return rows,affected

def apply_mounts(A,meta):
 rows=[];affected=[]
 for side in ('l','r'):
  r,a=attach(A,'upperarm_'+side,f'elbow_{side}_flex_M_upperarm_carrier',{f:f'{side}_arm_upperarm_shell_{f}' for f in ('front','back')},[-48.,-64.],14 if side=='l' else -14);rows+=r;affected+=a
  r,a=attach(A,'forearm_'+side,f'forearm_{side}_twist_M_distal_forearm_carrier',{f:f'{side}_arm_forearm_shell_{f}_distal' for f in ('front','back')},[-29.]);rows+=r;affected+=a
 return A,dict(meta,arm_cover_mounts=rows,affected_arm_cover_mounts=affected)

def build(name):return apply_mounts(*body.build(name))
if __name__=='__main__':
 from full_body_audit import poses
 from final_model import build as frozen_base
 from collision_cache import CollisionCache
 out={}
 for name in ('manny','quinn'):
  A,meta=frozen_base(name);cache=CollisionCache(A);rows=[];cases,_=poses(A)
  for label,pose in (dict(neutral={}).items() if '--probe' in sys.argv else cases.items()):
   raw=cache.contacts(pose,affected=set(meta['affected_arm_cover_mounts']),skip_same_owner=label!='neutral')
   review=classify_all(raw,A.parts);bad=[r for r in review if r['classification']=='structural'];rows.append(dict(pose=label,review=review));
   if bad or len(rows)%20==0:print(json.dumps(dict(character=name,done=len(rows),bad=bad)),flush=True)
  out[name]=dict(mounts=meta['arm_cover_mounts'],checks=rows);h.save(ROOT/'verification/revM_arm_cover_mounts.json',out)
