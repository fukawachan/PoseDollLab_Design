"""Compact light-duty neck, derived from the completed D4 shoulder twist stack.
The running/preload cartridge is separate from anatomical pivot placement.
Integral metal sockets avoid the broad M3 output ears of the S6 modules.
"""
from twist_completion import *
from cad_cache import get_body
from girdle_integration import world_part,replace_world
import twist_completion as source_body

@lru_cache(None)
def light_module():
 B,_=get_body('quinn',source_body.build);S=B.A0['upperarm_l.twist']['origin'];parts=[];mapping={}
 for q in B.parts:
  n=q['name']
  if n in ('l_twist_rotor_face','l_twist_lining') or n.startswith(('l_twist_sensor_','l_twist_M_')):
   if n=='l_twist_sensor_arm_radial_M2x6':continue
   name=n.removeprefix('l_twist_');s=h.move(q['local_shape'],B.T0[q['owner']]).translate(tuple(-S));owner='fixed' if q['owner']=='upperarm_l.abduct_frame' else 'rotor'
   parts.append(dict(name=name,shape=s,material=q['material'],owner=owner,note=q['note'],role=q['role']));mapping[n]=name
 # Flanged radial bushing, trapped between its housing shoulder and lining face.
 bush=ring(-8,5,3,2.03).fuse(ring(-8.8,-8,3.7,2.03))
 parts.append(dict(name='flanged_POM_bush',shape=bush,material='pom',owner='fixed',note='D6 nominal radial sleeve, D4.06 running bore, D7.4 x0.8 flange; nominal dimensions require fit qualification',role='candidate_solid'))
 lining=next(q for q in parts if q['name']=='lining')
 for sg in (-1,1):lining['shape']=lining['shape'].fuse(cube((2,2,1),(sg*8.7,0,-9.5)))
 housing=ring(-9,5.5,6.5,3.005).fuse(ring(-9,-8,10,3.005));housing=housing.cut(cyl(-9.1,-8,3.8))
 housing=housing.fuse(ring(-10,-9,10,9).cut(lining['shape']))
 for sg in (-1,1):
  post=cube((2.7,4,12.495-1.8-3.5),(sg*8.5,0,(12.495-1.8+3.5)/2)).fuse(cube((3.5,2,2),(sg*6.75,0,4.4)))
  post=post.cut(cyl(12.495-5.5,12.495-1.7,.8).translate((sg*8.5,0,0)));housing=fuse_checked(housing,post,'T4_sensor_post')
 parts.append(dict(name='fixed_housing',shape=housing,material='aluminum_7075',owner='fixed',note='Integral load sleeve, trapped radial bush, lining tabs and metal sensor posts; this housing merges into the supporting frame',role='candidate_solid'))
 socket=ring(-24,-20.5,4,0.01).cut(dshape(-24.1,-20.4,2.05,1.55)).cut(h.axis_cyl(0,1.4,4.1,1.1,(0,0,-22.5)))
 parts.append(dict(name='D4_output_socket',shape=socket,material='aluminum_7075',owner='rotor',note='Machined D4.1 socket, 8 mm outside diameter; integral with output link, positive D drive',role='candidate_solid'))
 bolt=h.axis_cyl(0,1,4,1,(0,0,-22.5)).cut(cube((.5,.35,1),(3.9,0,-22.5)))
 parts.append(dict(name='socket_M2x3',shape=bolt,material='brass',owner='rotor',note='Flush slotted M2x3 radial retainer; D face carries torque',role='candidate_solid'))
 allow=[[mapping[a],mapping[b]] for a,b in B.thread_pairs if a in mapping and b in mapping]
 allow += [['fixed_housing','sensor_board_cap_M2x6_'+str(i)] for i in range(2)]
 allow += [['sensor_integral_magnet_shaft','socket_M2x3']]
 for q in parts:assert q['shape'].isValid() and len(q['shape'].Solids())==1,q['name']
 return parts,allow

def joint4(A,axis,normal,xdir,off):
 node=next(n for n in A.profile['nodes'] if n.get('axis_id')==axis);O=A.A0[axis]['origin']+np.array(normal)*off
 loc=cq.Location(cq.Plane(origin=tuple(O),normal=normal,xDir=xdir));prefix=axis.replace('.','_')+'_T4_';parts,allow=light_module()
 for q in parts:A.add(prefix+q['name'],q['shape'].moved(loc),q['material'],node['parent'] if q['owner']=='fixed' else node['id'],q['note'],q['role'])
 A.thread_pairs += [[prefix+x for x in pair] for pair in allow]
 j=dict(axis=axis,loc=loc,origin=O,prefix=prefix,fixed=node['parent'],rotor=node['id'],size='T4_light',meta=dict(nominal_torque_Nm=.28861,clutch_force_nominal_N=294,magnet_face_mm=9,package_face_mm=10.5,gap_mm=1.5))
 A.joints[axis]=j;A.channels.append(dict(axis_id=axis,kind='AS5048A_direct',fixed_owner=j['fixed'],magnet_owner=j['rotor'],origin_neutral_mm=O.tolist(),normal_neutral=list(normal),xdir_neutral=list(xdir),geometric_sign=float(np.dot(A.A0[axis]['direction'],normal)),magnet_face_mm=9,package_face_mm=10.5,gap_mm=1.5,family='T4_light',calibrated=False))
 return j

def merge_links(A,names,rails_shapes,name,owner,note):
 parts=[world_part(A,n) for n in names];shape=union_checked([q[1] for q in parts]+rails_shapes,name)
 for q,_ in parts:A.parts.remove(q)
 A.add(name,shape,'aluminum_7075',owner,note)
 # Preserve explicit thread exceptions after merging a housing into the frame.
 A.thread_pairs=[[name if n in names else n for n in pair] for pair in A.thread_pairs]

def add_light_neck(A,off=38,yaw_off=34):
 N=A.A0['head.yaw']['origin'];tip=A.T0['head_tip'][:3,3];flip=np.diag([-1,-1,1]);tip=N+flip@(tip-N)
 y=joint4(A,'head.yaw',(0,0,-1),(1,0,0),yaw_off)
 f=joint4(A,'head.pitch',(0,1,0),(1,0,0),off)
 r=joint4(A,'head.roll',(1,0,0),(0,1,0),off)
 a=off-22.25;b=off-4;ay=yaw_off-22.25
 # Metal links attach outside the precision bores; keep the central pivot open.
 merge_links(A,[y['prefix']+'D4_output_socket',f['prefix']+'fixed_housing'],[rails([N+[-3,0,-ay],N+[-20,0,-ay],N+[-20,b,-ay],N+[-20,b,0],N+[-6.3,b,0]],3)],'head_T4_yaw_pitch_frame',y['rotor'],'Integral D4 socket and pitch bearing housing, exterior routing leaves the central pivot empty')
 merge_links(A,[f['prefix']+'D4_output_socket',r['prefix']+'fixed_housing'],[rails([N+[0,a,3],N+[0,a,28],N+[b,a,28],N+[b,6.3,28],N+[b,6.3,0]],3)],'head_T4_pitch_roll_frame',f['rotor'],'Integral pitch output socket and roll bearing housing; arch above pivot')
 merge_links(A,[r['prefix']+'D4_output_socket'],[rails([N+[a,0,3],N+[a,0,14],N+[a,-24,14],N+[a,-24,70],tip+[0,0,-20]],3)],'head_T4_skull_frame',r['rotor'],'Rigid head frame retains the original head-tip datum; cover mounting pending')
 # Put the roll input behind the pivot. The real pitch limits are asymmetric:
 # -45 degrees up and +55 down. Full mechanism rotation retains its internal layout.
 turn=cq.Location(cq.Vector(*N),cq.Vector(0,0,1),180)*cq.Location(cq.Vector(*(-N)))
 for q in A.parts:
  if q['name'].startswith('head_'):
   w=h.move(q['local_shape'],A.T0[q['owner']]).moved(turn);q['local_shape']=w.translate(tuple(-A.T0[q['owner']][:3,3]))
 for j in (y,f,r):j['loc']=turn*j['loc'];j['origin']=N+flip@(j['origin']-N)
 for ch in A.channels:
  if ch['axis_id'].startswith('head.'):
   ch['origin_neutral_mm']=(N+flip@(np.array(ch['origin_neutral_mm'])-N)).tolist()
   ch['normal_neutral']=(flip@ch['normal_neutral']).tolist();ch['xdir_neutral']=(flip@ch['xdir_neutral']).tolist()
   ch['geometric_sign']=float(np.dot(A.A0[ch['axis_id']]['direction'],ch['normal_neutral']))
 return y,f,r

def main():
 result={}
 for off in ([38] if '--quick' in sys.argv else [36,38,40]):
  A=Assembly(h.profile('quinn'));add_light_neck(A,off);rows=[]
  cases={'neutral':{}}
  for ax,angles in [('yaw',[-75,75]),('pitch',range(-45,56,10)),('roll',[-35,35])]:
   for angle in angles:cases[f'{ax}_{angle}']={'head.'+ax:angle}
  if '--combined' in sys.argv:
   cases.update({f'combined_{y}_{p}_{r}':{'head.yaw':y,'head.pitch':p,'head.roll':r} for y in (-75,0,75) for p in (-45,0,55) for r in (-35,35)})
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,None,label!='neutral');rows.append(dict(pose=label,hits=hits));print(json.dumps(dict(offset=off,pose=label,hits=hits)),flush=True)
  result[str(off)]=rows
 h.save(ROOT/'verification/revM_light_neck_work.json',result)
if __name__=='__main__':main()
