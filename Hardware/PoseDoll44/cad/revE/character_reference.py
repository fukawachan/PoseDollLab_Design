"""Manny/Quinn mesh-derived N-pose and uniform-scale 44-axis design baselines.
Physical packaging and manufacturing are separate, explicitly pending stages.
"""
from pathlib import Path
import sys,json,math,hashlib
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(HERE.parent))
from model import fk,rotation,keyposes
SCALE=1/3
SWAP=np.array([[0,1,0],[1,0,0],[0,0,1.]])
OUT=ROOT/'generated/revE';OUT.mkdir(parents=True,exist_ok=True)
REF=ROOT/'reference/ue58'
BASE=json.loads((REPO/'Shared/Profiles/virtual_humanoid_44_v1.json').read_text(encoding='utf8'))
def save(path,x):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def qmatrix(q):
 x,y,z,w=np.array(q)/np.linalg.norm(q)
 return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def transform(v):
 T=np.eye(4);T[:3,:3]=qmatrix(v['rotation_xyzw'])@np.diag(v['scale']);T[:3,3]=v['translation'];return T

def align(a,b):
 a=np.array(a,dtype=float);b=np.array(b,dtype=float);a/=np.linalg.norm(a);b/=np.linalg.norm(b)
 v=np.cross(a,b);c=float(np.dot(a,b));s=np.linalg.norm(v)
 if s<1e-12:
  if c>0:return np.eye(3)
  w=np.cross(a,[1,0,0] if abs(a[0])<.9 else [0,1,0]);return rotation(w,180)
 K=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
 return np.eye(3)+K+K@K*((1-c)/(s*s))

def reference_character(name):
 probe=json.loads((REF/(name+'_mesh_probe.json')).read_text(encoding='utf8'))
 geo=json.loads((REF/(name+'_geometry.json')).read_text(encoding='utf8'))
 bones=probe['mesh_reference'];names=[b['name'] for b in bones];index={n:i for i,n in enumerate(names)}
 parents=[b['parent_index'] for b in bones];local=[transform(b['local']) for b in bones];ref=[transform(b['global']) for b in bones]
 if [b['name'] for b in sorted(geo['bone_info'],key=lambda b:b['index'])]!=names:raise ValueError('Skin bone index mismatch')
 overrides={}
 def evaluate():
  G=[]
  for i,b in enumerate(bones):
   t=local[i].copy() if parents[i]<0 else G[parents[i]]@local[i]
   if names[i] in overrides:t[:3,:3]=overrides[names[i]]
   G.append(t)
  return G
 # Match the existing adapter's explicit N-pose axis conventions using EACH mesh's own bone lengths.
 for side in ('l','r'):
  for bone,child,direction in [(f'upperarm_{side}',f'lowerarm_{side}',[0,0,-1]),(f'lowerarm_{side}',f'hand_{side}',[0,0,-1]),(f'hand_{side}',f'middle_01_{side}',[0,0,-1]),(f'thigh_{side}',f'calf_{side}',[0,0,-1]),(f'calf_{side}',f'foot_{side}',[0,0,-1]),(f'foot_{side}',f'ball_{side}',[0,1,0])]:
   G=evaluate();i=index[bone];j=index[child]
   overrides[bone]=align(G[j][:3,3]-G[i][:3,3],direction)@G[i][:3,:3]
 for side in ('l','r'):
  G=evaluate();h=index['hand_'+side];p=G[h][:3,3]
  v=np.cross(G[index['index_01_'+side]][:3,3]-p,G[index['pinky_01_'+side]][:3,3]-p)*(-1 if side=='l' else 1)
  v[2]=0;v/=np.linalg.norm(v);target=np.array([0,1,0]);angle=math.degrees(math.atan2(np.cross(v,target)[2],np.dot(v,target)))
  overrides['hand_'+side]=rotation([0,0,1],angle)@G[h][:3,:3]
 neutral=evaluate();positions=np.array(geo['positions_cm']);skin=np.zeros_like(positions);sum_weights=np.zeros(len(positions));dominant=[]
 # No approximation of the weights: same imported per-vertex influences, normalized only after validation.
 bybone=[[] for _ in bones]
 for vi,weights in enumerate(geo['skin_weights']):
  dominant.append(max(weights,key=lambda x:x[1])[0])
  for bi,w in weights:bybone[bi].append((vi,w))
 for bi,weighted in enumerate(bybone):
  if not weighted:continue
  ids=np.array([v[0] for v in weighted]);w=np.array([v[1] for v in weighted]);delta=neutral[bi]@np.linalg.inv(ref[bi])
  skin[ids]+=(positions[ids]@delta[:3,:3].T+delta[:3,3])*w[:,None];sum_weights[ids]+=w
 if np.max(np.abs(sum_weights-1))>2e-4:raise ValueError('Invalid skin weight normalization')
 skin/=sum_weights[:,None]
 neutral_pts=np.array([g[:3,3] for g in neutral])
 # Transform UE left-handed mesh axes into the protocol's right-handed +X forward,+Y left,+Z up.
 raw_vertices=skin@SWAP.T*10*SCALE;raw_bones=neutral_pts@SWAP.T*10*SCALE
 shift=np.array([-raw_bones[index['pelvis'],0],-raw_bones[index['pelvis'],1],-raw_vertices[:,2].min()])
 vertices=raw_vertices+shift;points=raw_bones+shift;point={n:points[i] for i,n in enumerate(names)}
 def descendants(n):
  ids=set();want=index[n]
  for i in range(len(names)):
   j=i
   while j>=0:
    if j==want:ids.add(i);break
    j=parents[j]
  return ids
 dominant=np.array(dominant)
 def surface_for(n):return vertices[np.isin(dominant,list(descendants(n)))]
 surfaces={n:surface_for(n) for n in ('head','hand_l','hand_r','foot_l','foot_r')}
 height=float(vertices[:,2].max()-vertices[:,2].min())
 result={'name':name,'probe':probe,'geometry':geo,'names':names,'index':index,'parents':parents,'reference':ref,'neutral':neutral,'local':local,'vertices_mm':vertices,'points':point,'surfaces':surfaces,'height_mm':height,'shift_mm':shift,'weights_sum_error':float(np.max(np.abs(sum_weights-1)))}
 return result

def make_profile(c):
 p=json.loads(json.dumps(BASE));name=c['name'];pts=c['points'];locations={}
 p['profile_id']='physical_'+name+'_44_revE_proportion';p['status']='PROPORTION_REFERENCE_NOT_ASSEMBLABLE_NOT_CALIBRATED'
 p['notes_zh']=['以 '+name.title()+' 的真实网格参考骨架生成，统一 1:3 缩放。','肩、髋、腕、踝多轴中心重合，禁止为容纳机构而任意偏移。','躯干/颈部为现有44轴表达的等效枢轴；运动误差另报。','该配置是设计基准，不是已经装配、校准或接入 UE 的实体设备。']
 locations['device_base']=np.zeros(3)
 for n in p['nodes']:
  id=n['id'];pre=id.split('.')[0]
  if id=='device_base':continue
  if pre=='pelvis':v=pts['pelvis']
  elif pre=='waist':v=(pts['spine_02']+pts['spine_03'])/2
  elif pre=='chest':v=pts['spine_04']
  elif pre=='head':v=(pts['neck_01']+pts['neck_02']+pts['head'])/3
  elif id=='head_tip':v=c['surfaces']['head'][np.argmax(c['surfaces']['head'][:,2])]
  elif pre.startswith('clavicle_'):v=pts[pre]
  elif pre.startswith('upperarm_'):v=pts[pre]
  elif pre.startswith('elbow_'):v=pts['lowerarm_'+pre[-1]]
  elif pre.startswith('forearm_'):
   side=pre[-1];v=.55*pts['lowerarm_'+side]+.45*pts['hand_'+side]
  elif pre.startswith('hand_') and not pre.startswith('hand_tip'):v=pts[pre]
  elif pre.startswith('hand_tip'):
   side=pre[-1];surface=c['surfaces']['hand_'+side];v=surface[np.argmin(surface[:,2])]
  elif pre.startswith('thigh_'):v=pts[pre]
  elif pre.startswith('calf_'):v=pts[pre]
  elif pre.startswith('foot_'):v=pts[pre]
  elif pre.startswith('ball_'):v=pts[pre]
  elif pre.startswith(('sole_','heel_','toe_tip')):
   side=pre[-1];surface=c['surfaces']['foot_'+side]
   if pre.startswith('sole_'):v=surface[np.argmin(surface[:,2])]
   elif pre.startswith('heel_'):v=surface[np.argmin(surface[:,0])]
   else:v=surface[np.argmax(surface[:,0])]
  else:raise ValueError('Unmapped '+id)
  locations[id]=np.array(v)
  n['parent_to_axis']['translation_m']=((locations[id]-locations[n['parent']])/1000).tolist()
  n['axis_to_child']['translation_m']=[0,0,0]
 p['design_reference']={'mesh_asset':c['probe']['mesh_asset'],'scale':SCALE,'mesh_N_pose_surface_height_mm':c['height_mm'],'mesh_to_protocol_axes':'[UE_Y,UE_X,UE_Z]','neutral_floor_shift_mm':c['shift_mm'].tolist()}
 return p

def main():
 report={'status':'PROPORTION_BASELINES_CREATED_PACKAGING_PENDING','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'characters':{}}
 for name in ('manny','quinn'):
  c=reference_character(name);p=make_profile(c);T,A=fk(p,{})
  folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
  save(ROOT/'mechanical_manifest'/('physical_'+name+'_44_revE_proportion.json'),p)
  save(folder/'neutral_landmarks.json',{'bone_landmarks_mm':{k:v.tolist() for k,v in c['points'].items()},'axis_pivots_mm':{k:v['origin'].tolist() for k,v in A.items()},'surface_height_mm':c['height_mm'],'scale':SCALE,'floor_shift_mm':c['shift_mm'].tolist()})
  np.savez_compressed(folder/'surface_reference.npz',vertices_mm=c['vertices_mm'],triangles=np.array(c['geometry']['triangles']),bone_points_mm=np.array(list(c['points'].values())),bone_names=np.array(list(c['points'])))
  measures={};pairs={}
  for side in ('l','r'):
   pairs|={f'upperarm_{side}':(f'upperarm_{side}',f'lowerarm_{side}'),f'forearm_{side}':(f'lowerarm_{side}',f'hand_{side}'),f'thigh_{side}':(f'thigh_{side}',f'calf_{side}'),f'shin_{side}':(f'calf_{side}',f'foot_{side}')}
  pairs|={'shoulder_span':('upperarm_l','upperarm_r'),'hip_span':('thigh_l','thigh_r'),'pelvis_head_distance':('pelvis','head')}
  for k,(a,b) in pairs.items():measures[k]=float(np.linalg.norm(c['points'][b]-c['points'][a]))
  for side in ('l','r'):
   hand=c['surfaces']['hand_'+side];tip=hand[np.argmin(hand[:,2])]
   measures['hand_wrist_to_tip_'+side]=float(np.linalg.norm(tip-c['points']['hand_'+side]))
   measures['shoulder_to_fingertip_'+side]=measures['upperarm_'+side]+measures['forearm_'+side]+measures['hand_wrist_to_tip_'+side]
   measures['foot_length_'+side]=float(np.ptp(c['surfaces']['foot_'+side][:,0]))
   measures['foot_width_'+side]=float(np.ptp(c['surfaces']['foot_'+side][:,1]))
  measures['pelvis_to_shoulder_height']=float((c['points']['upperarm_l'][2]+c['points']['upperarm_r'][2])/2-c['points']['pelvis'][2])
  for dim,i in [('depth',0),('width',1),('height',2)]:measures['head_'+dim]=float(np.ptp(c['surfaces']['head'][:,i]))
  measures['neutral_surface_height']=c['height_mm'];measures['reference_surface_height']=2*c['probe']['imported_bounds']['extent_cm'][2]*10*SCALE
  manny_neutral_error=None
  if name=='manny':
   fixture=json.loads((REPO/'reports/rig_fixture_results.json').read_text(encoding='utf8'))
   target=next(x['bones'] for x in fixture['cases'] if x['fixture']=='neutral.sample.json')
   errors={n:float(np.linalg.norm(c['neutral'][i][:3,3]-np.array(target[n]['translation'])))*10*SCALE for i,n in enumerate(c['names']) if n in target}
   manny_neutral_error={'max_mm':max(errors.values()),'worst_bone':max(errors,key=errors.get),'errors_mm':errors}
  rig={b['name']:b for b in c['probe']['bones']}
  rig_ref_error={b['name']:float(np.linalg.norm(np.array(b['global']['translation'])-np.array(rig[b['name']]['initial']['translation'])))*10*SCALE for b in c['probe']['mesh_reference'] if b['name'] in rig}
  report['characters'][name]={'mesh':c['probe']['mesh_asset'],'scale':SCALE,'axis_count':len(A),'measurements_mm':measures,'manny_cached_adapter_neutral_comparison':manny_neutral_error,'rig_initial_vs_own_mesh_reference_max_mm':max(rig_ref_error.values()),'rig_initial_vs_own_mesh_reference_worst':max(rig_ref_error,key=rig_ref_error.get),'weight_normalization_max_error':c['weights_sum_error'],'source_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (REF/(name+'_mesh_probe.json'),REF/(name+'_geometry.json'))}}
  print(json.dumps({'name':name,'measurements':measures,'manny_neutral_error':None if manny_neutral_error is None else manny_neutral_error['max_mm'],'rig_mesh_difference':max(rig_ref_error.values())}),flush=True)
 save(ROOT/'verification/revE_proportion_baselines.json',report)
if __name__=='__main__':main()
