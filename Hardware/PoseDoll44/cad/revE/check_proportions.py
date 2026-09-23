"""Independent bone-chain comparison, not a physical or Control Rig release."""
from character_reference import *

def blend(A,B,t):
 R=A.T@B;angle=math.acos(float(np.clip((np.trace(R)-1)/2,-1,1)))
 if angle<1e-10:return A.copy()
 axis=np.array([R[2,1]-R[1,2],R[0,2]-R[2,0],R[1,0]-R[0,1]])
 if np.linalg.norm(axis)<1e-8:
  vals,vectors=np.linalg.eig(R);axis=np.real(vectors[:,np.argmin(abs(vals-1))])
 return A@rotation(axis,math.degrees(angle)*t)

def expected_bones(c,p,pose):
 T,_=fk(p,pose);mapping=json.loads((REPO/'Shared/Profiles/manny_body_ue582_v1.json').read_text(encoding='utf8'))['controls']
 source=lambda s:SWAP@T[p['anatomical_segments'][s]][:3,:3]@SWAP.T
 override={}
 for m in mapping:
  delta=source(m['semantic'])
  if 'from' in m:delta=blend(source(m['from']),delta,m['weight'])
  override[m['bone']]=delta@c['neutral'][c['index'][m['bone']]][:3,:3]
 G=[]
 for i,n in enumerate(c['names']):
  parent=c['parents'][i]
  local=c['neutral'][i] if parent<0 else np.linalg.inv(c['neutral'][parent])@c['neutral'][i]
  g=local.copy() if parent<0 else G[parent]@local
  if n in override:g[:3,:3]=override[n]
  G.append(g)
 return {n:g for n,g in zip(c['names'],G)}

def physical_points(c,p,pose):
 T,A=fk(p,pose);T0,_=fk(p,{})
 out={}
 for side in ('l','r'):
  out['upperarm_'+side]=A['upperarm_'+side+'.flex']['origin']
  out['lowerarm_'+side]=A['elbow_'+side+'.flex']['origin']
  out['hand_'+side]=T['hand_'+side][:3,3]
  out['thigh_'+side]=A['thigh_'+side+'.flex']['origin']
  out['calf_'+side]=T['calf_'+side][:3,3]
  out['foot_'+side]=T['foot_'+side][:3,3]
  out['ball_'+side]=T['ball_'+side][:3,3]
  out['clavicle_'+side]=T['clavicle_'+side][:3,3]
  out['tip_'+side]=T['hand_tip_'+side][:3,3]
 out['pelvis']=T['pelvis'][:3,3]
 out['head']=T['head'][:3,3]+T['head'][:3,:3]@(c['points']['head']-T0['head'][:3,3])
 return out

def endpoint_error(c,p,pose):
 physical=physical_points(c,p,pose);target=expected_bones(c,p,pose)
 errors={n:float(np.linalg.norm(physical[n]-(SWAP@g[:3,3]*10*SCALE+c['shift_mm']))) for n,g in target.items() if n in physical}
 return errors

def solve_arm_tip(c,p,side,point,initial):
 # Four DOF numerical reach solution. Solver checks limits; collision is a separate gate.
 ids=[f'upperarm_{side}.flex',f'upperarm_{side}.abduct',f'upperarm_{side}.twist',f'elbow_{side}.flex']
 limits={a['id']:np.degrees(a['limits_rad']) for a in p['axes']}
 lo=np.array([limits[i][0] for i in ids]);hi=np.array([limits[i][1] for i in ids]);q=np.array(initial,dtype=float)
 def location(q):return fk(p,dict(zip(ids,q)))[0]['hand_tip_'+side][:3,3]
 for _ in range(100):
  error=point-location(q)
  if np.linalg.norm(error)<1e-5:break
  eps=.03;J=np.column_stack([(location(np.clip(q+np.eye(4)[j]*eps,lo,hi))-location(np.clip(q-np.eye(4)[j]*eps,lo,hi)))/(2*eps) for j in range(4)])
  delta=J.T@np.linalg.solve(J@J.T+.03*np.eye(3),error)
  q=np.clip(q+np.clip(delta,-12,12),lo,hi)
 return dict(zip(ids,q.tolist())),float(np.linalg.norm(point-location(q)))

def samples(c,p):
 poses=dict(keyposes());poses['hip_abduction_arms_clear']={'thigh_l.abduct':60,'thigh_r.abduct':60,'upperarm_l.abduct':35,'upperarm_r.abduct':35}
 target=np.array([90.,0.,c['points']['upperarm_l'][2]-50])
 reach={};q={}
 for s in ('l','r'):
  pose,error=solve_arm_tip(c,p,s,target,[40,-15,30,90]);q.update(pose);reach['hands_together_'+s]={'target_mm':target.tolist(),'solver_point_error_mm':error}
 poses['hands_together_tip_contact']=q
 head=c['surfaces']['head'];z0=c['points']['head'][2]+.35*(head[:,2].max()-c['points']['head'][2]);forehead=head[(head[:,2]>z0)&(np.abs(head[:,1])<10)]
 target=forehead[np.argmax(forehead[:,0])]
 q,e=solve_arm_tip(c,p,'l',target,[130,5,-40,115]);poses['hand_to_forehead_tip_contact']=q
 reach['forehead']={'target_mm':target.tolist(),'solver_point_error_mm':e,'definition':'Most-forward central head-surface vertex above 35% of bone-to-crown height.'}
 poses['kneeling_angles']={'thigh_l.flex':10,'thigh_r.flex':10,'calf_l.flex':130,'calf_r.flex':130}
 # Deterministic samples keep error evidence separate from actual collision/comfort acceptance.
 for a in p['axes']:
  for tag,v in zip(('min','max'),a['limits_rad']):poses[a['id']+'_'+tag]={a['id']:math.degrees(v)}
 rng=np.random.default_rng(44052026)
 for j in range(128):poses[f'combined_{j:03}']={a['id']:float(rng.uniform(*np.degrees(a['limits_rad']))) for a in p['axes']}
 return poses,reach

def holdout_samples(p):
 # Independent seed plus complete 7x7x7 neck grid; excluded from pivot fitting.
 import itertools
 rng=np.random.default_rng(923741)
 poses={f'holdout_combined_{j:03}':{a['id']:float(rng.uniform(*np.degrees(a['limits_rad']))) for a in p['axes']} for j in range(512)}
 head=[a for a in p['axes'] if a['id'].startswith('head.')]
 for j,angles in enumerate(itertools.product(*[np.linspace(*np.degrees(a['limits_rad']),7) for a in head])):
  poses[f'holdout_neck_grid_{j:03}']=dict(zip([a['id'] for a in head],map(float,angles)))
 return poses

def main():
 report={'status':'KINEMATIC_COMPARISON_NOT_PHYSICAL_CERTIFICATE','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'reference_code_sha256':hashlib.sha256((HERE/'character_reference.py').read_bytes()).hexdigest(),'characters':{}}
 for name in ('manny','quinn'):
  c=reference_character(name);p=make_profile(c);T0,A0=fk(p,{})
  invariants={'axis_order':p['axis_order']==BASE['axis_order'],'axis_definitions':p['axes']==BASE['axes'],'parent_chain':[(n['id'],n['parent']) for n in p['nodes']]==[(n['id'],n['parent']) for n in BASE['nodes']]}
  # Direct link lengths tested independently against each source mesh's reference bone positions.
  length_errors={}
  for side in ('l','r'):
   pairs=[('upperarm',f'upperarm_{side}',f'lowerarm_{side}',f'upperarm_{side}.flex',f'elbow_{side}.flex'),('forearm',f'lowerarm_{side}',f'hand_{side}',f'elbow_{side}.flex',f'hand_{side}.flex'),('thigh',f'thigh_{side}',f'calf_{side}',f'thigh_{side}.flex',f'calf_{side}.flex'),('shin',f'calf_{side}',f'foot_{side}',f'calf_{side}.flex',f'foot_{side}.dorsiflex')]
   for label,a,b,aa,ab in pairs:
    ref=np.linalg.norm(c['reference'][c['index'][b]][:3,3]-c['reference'][c['index'][a]][:3,3])*10*SCALE
    measured=np.linalg.norm(A0[ab]['origin']-A0[aa]['origin'])
    length_errors[label+'_'+side]={'expected_mm':float(ref),'profile_mm':float(measured),'relative_error':float(abs(measured-ref)/ref)}
  neutral_errors=endpoint_error(c,p,{})
  for label,a,b,aa,ab in [('shoulder_span','upperarm_l','upperarm_r','upperarm_l.flex','upperarm_r.flex'),('hip_span','thigh_l','thigh_r','thigh_l.flex','thigh_r.flex')]:
   reference=float(np.linalg.norm(c['points'][b]-c['points'][a]));measured=float(np.linalg.norm(A0[ab]['origin']-A0[aa]['origin']))
   length_errors[label]={'expected_mm':reference,'profile_mm':measured,'relative_error':abs(measured-reference)/reference}
  fixture_errors=[]
  if name=='manny':
   fixture=json.loads((REPO/'reports/rig_fixture_results.json').read_text(encoding='utf8'))
   for case in fixture['cases']:
    f=json.loads((REPO/'Shared/Fixtures'/case['fixture']).read_text(encoding='utf8'))
    pose={a:math.degrees(v-math.pi) for a,v in zip(BASE['axis_order'],f['raw_angles_rad'])}
    g=expected_bones(c,p,pose);errors={n:float(np.linalg.norm(g[n][:3,3]-np.array(case['bones'][n]['translation'])))*10*SCALE for n in physical_points(c,p,{}) if n in g and n in case['bones']}
    fixture_errors.append({'fixture':case['fixture'],'max_error_mm':max(errors.values()),'worst':max(errors,key=errors.get)})
  poses,reach=samples(c,p);design_count=len(poses);poses.update(holdout_samples(p));rows=[];worst={}
  for title,pose in poses.items():
   errors=endpoint_error(c,p,pose);mx=max(errors.values());bn=max(errors,key=errors.get)
   rows.append({'pose':title,'max_error_mm':mx,'worst_landmark':bn,'errors_mm':errors,'angles_deg':pose})
   for n,e in errors.items():
    if n not in worst or e>worst[n]['error_mm']:worst[n]={'error_mm':e,'pose':title}
  pivot_groups=[['pelvis.yaw','pelvis.pitch','pelvis.roll'],['waist.yaw','waist.pitch','waist.roll'],['chest.yaw','chest.pitch','chest.roll'],['head.yaw','head.pitch','head.roll']]
  for side in ('l','r'):
   pivot_groups +=[[f'upperarm_{side}.{a}' for a in ('flex','abduct','twist')],[f'thigh_{side}.{a}' for a in ('flex','abduct','twist')],[f'clavicle_{side}.{a}' for a in ('protract','elevate')],[f'hand_{side}.{a}' for a in ('flex','deviate')],[f'foot_{side}.{a}' for a in ('dorsiflex','invert')]]
  pivots=[{'axes':g,'maximum_separation_mm':max(float(np.linalg.norm(A0[a]['origin']-A0[b]['origin'])) for a in g for b in g)} for g in pivot_groups]
  target=c['height_mm']*.01
  report['characters'][name]={'invariants':invariants,'lengths':length_errors,'neutral_landmark_errors_mm':neutral_errors,'neutral_proportion_gate_passed':all(invariants.values()) and max(v['relative_error'] for v in length_errors.values())<.01 and max(neutral_errors.values())<=c['height_mm']*.005,'coincident_pivots':pivots,'sample_count':len(rows),'design_sample_count':design_count,'independent_sample_count':len(poses)-design_count,'worst_by_landmark':worst,'digital_position_target_mm':target,'position_gate_passed':all(w['error_mm']<=target for w in worst.values()),'fixtures_vs_actual_UE':fixture_errors,'new_physical_profile_UE_validated':False,'target_character_adapter_validated':name=='manny','contact_reach_solutions':reach,'poses':rows,
   'limitations':['Quinn prediction uses her own mesh lengths and the same rotation distribution; current shared Control Rig still uses Manny reference and is NOT validated for Quinn.','Mechanical centres are ideal design targets. Current Rev C/D friction assemblies have not been packed around them.','Spine and neck use effective single pivots whereas the UE rig distributes rotation; their residual position errors are retained here.','Reach samples enforce a single fingertip point, not hand-surface orientation, nonpenetration, or grounded balance.','Random/extreme angle combinations may collide and do not define a physically achievable motion range.']}
  save(OUT/name/'pose_samples.json',{'poses':{k:v for k,v in poses.items() if not k.startswith(('combined_','holdout_')) and not k.endswith(('_min','_max'))},'contact_targets':reach})
  print(json.dumps({'name':name,'samples':len(rows),'max_mm':max(w['error_mm'] for w in worst.values()),'gate':report['characters'][name]['position_gate_passed'],'actual_UE_fixture_errors':fixture_errors,'reach':reach}),flush=True)
 save(ROOT/'verification/revE_kinematic_comparison.json',report)
if __name__=='__main__':main()
