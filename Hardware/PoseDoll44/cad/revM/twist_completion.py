"""Complete the two inherited shoulder axial clutches; metal preload path."""
from body_integration import *
import body_integration as body
COL['bronze']=(.72,.53,.30)
TWIST_SPRING=dict(article='001200',de=10,di=4.2,t=.5,free=.75,test=.563,F=294)

def apply_twist(A):
 for side,sy in [('l',1),('r',-1)]:
  S=A.A0[f'upperarm_{side}.twist']['origin'];B=f'upperarm_{side}.abduct_frame';W=f'upperarm_{side}'
  loc=cq.Location(cq.Plane(origin=tuple(S),xDir=(sy,0,0),normal=(0,0,1)))
  def update(n,shape,mat,note):
   q=next(q for q in A.parts if q['name']==n);q.update(local_shape=shape.moved(loc).translate(tuple(-A.T0[q['owner']][:3,3])),material=mat,note=note)
   assert q['local_shape'].isValid() and len(q['local_shape'].Solids())==1,n
  shaft=previous.k.j.dshape(-24,-19.3,4,1.5).fuse(cyl(-19.3,-12.1,2)).fuse(previous.k.j.dshape(-12.1,-10,4,1.5)).fuse(cyl(-10,5.7,2)).fuse(cyl(5.7,9,5.3))
  shaft=shaft.cut(cyl(6.5,9.1,3.1))
  groove=ring(-17.626,-16.426,2.1,1.5).fuse(cube((6,6,1.2),(4.1,0,-17.026)))
  shaft=shaft.cut(groove)
  for sign in (-1,1):shaft=shaft.cut(h.axis_cyl(1,*sorted((sign*3.45,sign*5.4)),.8,(0,0,8)))
  shaft=shaft.cut(h.axis_cyl(0,0,2.1,.8,(0,0,-22.5)))
  sn=side+'_twist_sensor_integral_magnet_shaft'
  update(sn,shaft,'aluminum_7075','D4 arm drive and friction rotor drive; side-assembled keyed groove on Z -17.626..-16.426, D3 / flat 1.1; no inaccessible end nut; integral magnet cup and metal thrust shoulder')
  rotor=ring(-12,-10,9,0.01).cut(previous.k.j.dshape(-12.1,-9.9,4.1,1.55))
  update(side+'_twist_rotor_face',rotor,'aluminum_7075','Positive D4 drive; axial spring force reacts into the fixed metal shoulder seat')
  seat=next(q for q in A.parts if q['name']==side+'_abduct_ring_and_twist_seat')
  face=next(q for q in A.parts if q['name']==side+'_twist_fixed_face')
  seat['local_shape']=seat['local_shape'].fuse(face['local_shape']);seat['material']='aluminum_7075';seat['note']='Machined metal shoulder abduction ring and twist reaction face; top thrust face Z5.5, radial bush does not carry preload';A.parts.remove(face)
  assert seat['local_shape'].isValid() and len(seat['local_shape'].Solids())==1
  def add(n,s,mat,owner,note):return A.add(side+'_twist_M_'+n,s.moved(loc),mat,owner,note)
  add('upper_thrust_shim',ring(5.5,5.7,5.3,3.2),'bronze',B,'0.20 mm CuSn8 thrust shim candidate; metal frame at 5.5, shaft shoulder at 5.7; flatness, wear and supplier process pending')
  add('spring_upper_washer',ring(-13,-12,5.5,2.1),'spring',W,'Ground steel washer; spring load kept away from arm coupling')
  for i in range(2):add('disc_spring_'+str(i),spring(TWIST_SPRING,-14.126+i*.563,bool(i)),'spring',W,'SCHNORR 001200 opposed pair in series; 294 N nominal at 0.563 mm each, needs physical adjustment')
  add('spring_lower_washer',ring(-14.626,-14.126,5.5,2.1),'spring',W,'Ground steel spring washer')
  # A split, positive-stop collar can be assembled radially. End nuts cannot
  # pass the unthreaded D4 arm key and integral upper magnet flange.
  cap=ring(-17.626,-14.626,6,2.05).fuse(cyl(-17.626,-16.526,2.05).cut(dshape(-17.7,-16.4,1.55,1.15)))
  for yy in (-4.5,4.5):cap=cap.fuse(cube((10,4,3),(0,yy,-16.126)))
  right=cap.intersect(cube((20,30,10),(10.1,0,-16)))
  left=cap.intersect(cube((20,30,10),(-10.1,0,-16)))
  for yy in (-4.5,4.5):
   right=right.cut(h.axis_cyl(0,0,5.1,1.1,(0,yy,-16.126))).cut(h.axis_cyl(0,5,9,2.1,(0,yy,-16.126)))
   left=left.cut(h.axis_cyl(0,-5.1,0,.8,(0,yy,-16.126)))
  add('split_stop_collar_left',left,'aluminum_7075',W,'Radial assembly into positive D3 groove; 1.1 mm axial lip; stop geometry sets nominal spring stack')
  add('split_stop_collar_right',right,'aluminum_7075',W,'Second collar half; 0.20 mm split; M2 screws join the halves without relying on friction for axial retention')
  for i,yy in enumerate((-4.5,4.5)):
   bolt=h.axis_cyl(0,-3,5,1,(0,yy,-16.126)).fuse(h.axis_cyl(0,5,7,1.9,(0,yy,-16.126)))
   bolt=bolt.cut(hexagon(1.5,5.6,7.1).rotate((0,0,0),(0,1,0),90).translate((0,yy,-16.126)))
   add('collar_M2x8_'+str(i),bolt,'brass',W,'M2x8 into tapped left collar half; 2.9 mm nominal engagement; install before arm carrier')
   A.thread_pairs.append([side+'_twist_M_split_stop_collar_left',side+'_twist_M_collar_M2x8_'+str(i)])
  for i in range(2):A.thread_pairs.append([side+'_abduct_ring_and_twist_seat',side+'_twist_sensor_board_cap_M2x6_'+str(i)])
  for tail in ('keeper_set_M2x3_0','keeper_set_M2x3_1','arm_radial_M2x6'):A.thread_pairs.append([sn,side+'_twist_sensor_'+tail])
  reff=2/3*(9**3-3.15**3)/(9**2-3.15**2)
  A.joints[f'upperarm_{side}.twist']=dict(axis=f'upperarm_{side}.twist',rotor=W,fixed=B,size='T4_294N',meta=dict(nominal_torque_Nm=.15*294*reff/1000,clutch_force_nominal_N=294,physical_tested=False))
 return A

def build(name):
 A,meta=body.build(name);apply_twist(A);return A,dict(meta,shoulder_twist_preload='294N_catalog_candidate')

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if '_twist_M_' in q['name'] or q['name'] in {s+t for s in ('l','r') for t in ('_twist_sensor_integral_magnet_shaft','_twist_rotor_face','_abduct_ring_and_twist_seat')}};checks=[]
  cases={'neutral':{},'arms_side':{'upperarm_l.abduct':90,'upperarm_r.abduct':90},'elbows_bent':{'elbow_l.flex':90,'elbow_r.flex':90},'twist':{'upperarm_l.twist':60,'upperarm_r.twist':-60},'overhead':{'upperarm_l.flex':135,'upperarm_r.flex':135}}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral');checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hits=hits)),flush=True)
  out[name]=dict(meta=meta,checks=checks)
 h.save(ROOT/'verification/revM_twist_completion_work.json',out)
if __name__=='__main__':main()
