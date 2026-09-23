"""All-part full-body verification; candidate geometry, never physical certification."""
from full_packaging import *
from collision_review import classify_all
import hashlib

def input_hashes():
 files=sorted((ROOT/'cad').rglob('*.py'))+[ROOT/'mechanical_manifest/network_revM.json']
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def channels41(A,name):
 result=list(A.channels)
 legacy=json.loads((ROOT/f'verification/revL_{name}.json').read_text(encoding='utf-8'))['meta']['sensor_channels']
 for old in legacy:
  side=old['axis_id'].split('_')[1].split('.')[0];kind=old['axis_id'].split('.')[1]
  result.append(dict(axis_id=old['axis_id'],kind='AS5048A_direct',fixed_owner=old['fixed_owner'],magnet_owner=old['magnet_owner'],origin_neutral_mm=old['module_origin_neutral_mm'],normal_neutral=old['module_normal_neutral'],xdir_neutral=old['module_xdir_neutral'],geometric_sign=old['geometric_angle_sign'],board_rotation_deg=old.get('board_rotation_about_axis_deg',0),magnet_face_mm=old.get('magnet_face_mm',36.5),package_face_mm=old.get('package_face_mm',39.3),gap_mm=old['package_to_magnet_gap_mm'],family='RevL_'+kind,calibrated=False,part_prefix=side+'_'+kind+'_sensor_'))
 for c in result:c.update(getattr(A,'sensor_channel_overrides',{}).get(c['axis_id'],{}))
 expected=A.profile['axis_order'][3:]
 assert len(result)==41 and len({c['axis_id'] for c in result})==41
 assert {c['axis_id'] for c in result}==set(expected)
 for c in result:
  if 'part_prefix' not in c:c['part_prefix']=A.joints[c['axis_id']]['prefix']
 return sorted(result,key=lambda c:expected.index(c['axis_id']))

def readout(A,channels,poses):
 installations=[];rows=[]
 for c in channels:
  z=np.array(c['normal_neutral'],float);x=np.array(c['xdir_neutral'],float);y=np.cross(z,x);b0=np.eye(4);b0[:3,:3]=np.column_stack((x,y,z));b0[:3,3]=c['origin_neutral_mm']
  loc=cq.Location(cq.Plane(origin=tuple(b0[:3,3]),normal=tuple(z),xDir=tuple(x)))
  group=[q for q in A.parts if q['name'].startswith(c['part_prefix'])]
  chips=[q for q in group if q['name'].endswith('pcb_AS5048A')];mags=[q for q in group if q['material']=='magnet']
  assert len(chips)==len(mags)==1,(c['axis_id'],[q['name'] for q in group])
  chip=chips[0];mag=mags[0];assert chip['owner']==c['fixed_owner'] and mag['owner']==c['magnet_owner']
  cb=h.move(chip['local_shape'],A.T0[chip['owner']]).moved(loc.inverse).BoundingBox();mb=h.move(mag['local_shape'],A.T0[mag['owner']]).moved(loc.inverse).BoundingBox()
  lateral=math.hypot((cb.xmin+cb.xmax-mb.xmin-mb.xmax)/2,(cb.ymin+cb.ymax-mb.ymin-mb.ymax)/2)
  gap=cb.zmin-mb.zmax
  assert abs(gap-c['gap_mm'])<1e-4 and lateral<1e-4,(c['axis_id'],gap,lateral)
  assert abs(cb.zmin-c['package_face_mm'])<1e-4 and abs(mb.zmax-c['magnet_face_mm'])<1e-4
  installations.append(dict(axis_id=c['axis_id'],chip=chip['name'],magnet=mag['name'],actual_BRep_gap_mm=gap,actual_BRep_lateral_mm=lateral,raw_sign_calibrated=False,magnetic_field_tested=False))
  r=math.radians(c.get('board_rotation_deg',0));rz=np.eye(4);rz[:2,:2]=[[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]]
  for label,angles in poses.items():
   T,axes=h.fk(A.profile,angles);fixed=T[c['fixed_owner']]@np.linalg.inv(A.T0[c['fixed_owner']])@b0@rz;rotor=T[c['magnet_owner']]@np.linalg.inv(A.T0[c['magnet_owner']])@b0
   rel=np.linalg.inv(fixed)@rotor;geom=math.degrees(math.atan2(rel[1,0],rel[0,0]));error=(geom+c.get('board_rotation_deg',0)-c['geometric_sign']*angles.get(c['axis_id'],0)+180)%360-180
   m=(rotor@np.array([0,0,c['magnet_face_mm'],1]))[:3];cp=(fixed@np.array([0,0,c['package_face_mm'],1]))[:3];d=cp-m;n=fixed[:3,2];gg=float(np.dot(d,n));lat=float(np.linalg.norm(np.cross(d,n)))
   assert abs(error)<1e-5 and lat<1e-5 and abs(gg-c['gap_mm'])<1e-5,(label,c['axis_id'],error,lat,gg)
   rows.append(dict(pose=label,axis_id=c['axis_id'],angle_error_deg=error,lateral_mm=lat,gap_mm=gg))
 return dict(installations=installations,pose_checks=rows,calibrated=False,scope='Actual neutral chip/magnet BRep faces plus rigid-owner FK consistency; no magnetic measurement or harness validation')

def poses(A,smoke=False):
 relaxed={'upperarm_l.abduct':15,'upperarm_r.abduct':15}
 out={'neutral':{},'relaxed':relaxed,'arms_forward':{'upperarm_l.flex':90,'upperarm_r.flex':90},'elbows_bent':relaxed|{'elbow_l.flex':145,'elbow_r.flex':145},'sit':relaxed|{'thigh_l.flex':90,'thigh_r.flex':90,'calf_l.flex':90,'calf_r.flex':90},'trunk_bend':relaxed|{'waist.pitch':40,'chest.pitch':30},'trunk_extend':relaxed|{'waist.pitch':-20,'chest.pitch':-20},'hips_out':relaxed|{'thigh_l.abduct':65,'thigh_r.abduct':65},'foot_toe':relaxed|{'foot_l.dorsiflex':-45,'foot_r.dorsiflex':-45,'ball_l.flex':60,'ball_r.flex':60}}
 limits={q['id']:[math.degrees(x) for x in q['limits_rad']] for q in A.profile['axes']}
 if not smoke:
  for k,v in (h.cases()|h.keyposes()).items():out['functional_'+k]=v
  for axis,(a,b) in limits.items():
   if axis.startswith('pelvis.'):continue
   for i,angle in enumerate((a,(a+b)/2,b)):out[axis+'_'+str(i)]=relaxed|{axis:angle}
  for side in ('l','r'):
   out['wrist_'+side]={'elbow_'+side+'.flex':90,'hand_'+side+'.flex':65,'hand_'+side+'.deviate':35,'forearm_'+side+'.twist':90}
   out['leg_fold_'+side]={'thigh_'+side+'.flex':120,'calf_'+side+'.flex':145,'foot_'+side+'.dorsiflex':25}
   out['leg_turn_'+side]={'thigh_'+side+'.abduct':65,'thigh_'+side+'.twist':50,'calf_'+side+'.flex':90}
 invalid={k:v for k,v in out.items() if any(a not in limits or not limits[a][0]-1e-6<=x<=limits[a][1]+1e-6 for a,x in v.items())}
 return {k:v for k,v in out.items() if k not in invalid},invalid

def main():
 out={'revision':'M-work','manufacturing_released':False,'physical_tested':False,'source_sha256':input_hashes(),'characters':{}}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);channels=channels41(A,name);cases,invalid=poses(A,'--smoke' in sys.argv);read=readout(A,channels,cases)
  print(json.dumps(dict(character=name,parts=len(A.parts),encoders=len(channels),actual_readout_installations=len(read['installations']),readout_pose_checks=len(read['pose_checks']),out_of_profile_cases=list(invalid))),flush=True)
  row=dict(meta=meta,intended_thread_pairs=A.thread_pairs,channels=channels,readout=read,checks=[],outside_profile_cases=invalid,parts=[dict(name=q['name'],owner=q['owner'],material=q['material'],role=q['role'],volume_mm3=q['local_shape'].Volume()) for q in A.parts]);out['characters'][name]=row
  if '--readout-only' not in sys.argv:
   for label,pose in cases.items():
    raw=fast_contacts(A.scene(pose),A.thread_pairs,None,label!='neutral');hits=classify_all(raw,A.parts);struct=[q for q in hits if q['classification']=='structural'];warnings=[q for q in hits if q['classification']=='pose_restriction']
    row['checks'].append(dict(pose=label,angles_deg=pose,structural=struct,pose_restrictions=warnings,raw_contacts=raw))
    h.save(ROOT/('verification/revM_full_body_'+('smoke' if '--smoke' in sys.argv else 'audit')+'_work.json'),out)
    print(json.dumps(dict(character=name,pose=label,structural=len(struct),pose_restrictions=len(warnings),first_structural=struct[:8])),flush=True)
  else:h.save(ROOT/'verification/revM_full_readout_work.json',out)
  if '--render' in sys.argv:
   folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
   h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],folder/'full_work.png',name.title()+' | 41 encoders | integration candidate',camera=(1600,-2800,1100))
if __name__=='__main__':main()
