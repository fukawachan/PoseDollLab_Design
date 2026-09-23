"""Check delivered joint centres and end lengths against the extracted UE baselines."""
from build_harness_revM import *
def main():
 baselines=json.loads((ROOT/'verification/revE_proportion_baselines.json').read_text(encoding='utf-8'));rows={}
 for name in ('manny','quinn'):
  mf=ROOT/f'generated/revM/{name}/manufacturing_manifest.json';d=json.loads(mf.read_text(encoding='utf-8'));p=d['profile'];oldfile=ROOT/f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json';old=json.loads(oldfile.read_text(encoding='utf-8'));T=fk(p,{});B=fk(old,{})
  assert p['nodes']==old['nodes'] and p['axis_order']==old['axis_order'] and p['axes']==old['axes']
  assert p['design_reference']['scale']==.5
  length=lambda a,b:float(np.linalg.norm(T[a][:3,3]-T[b][:3,3]))
  measure={}
  for side in ('l','r'):
   measure.update({f'upperarm_{side}':length(f'upperarm_{side}',f'elbow_{side}'),f'forearm_{side}':length(f'elbow_{side}',f'hand_{side}'),f'thigh_{side}':length(f'thigh_{side}',f'calf_{side}'),f'shin_{side}':length(f'calf_{side}',f'foot_{side}'),f'hand_wrist_to_tip_{side}':length(f'hand_{side}',f'hand_tip_{side}')})
   measure[f'shoulder_to_fingertip_{side}']=sum(measure[k+'_'+side] for k in ('upperarm','forearm','hand_wrist_to_tip'))
  measure['shoulder_span']=length('upperarm_l','upperarm_r');measure['hip_span']=length('thigh_l','thigh_r')
  landmarks=json.loads((ROOT/f'generated/revE/{name}/neutral_landmarks.json').read_text(encoding='utf-8'));bones={k:np.array(v)*1.5 for k,v in landmarks['bone_landmarks_mm'].items()};pivot=(bones['neck_01']+bones['neck_02']+bones['head'])/3;assert np.linalg.norm(T['head'][:3,3]-pivot)<.001
  neck=dict(mechanical_pivot_mm=T['head'][:3,3].tolist(),UE_head_reference_point_mm=bones['head'].tolist(),head_reference_offset_from_pivot_mm=(bones['head']-pivot).tolist(),definition='Equivalent neck pivot is mean(neck_01, neck_02, head), not the UE head bone origin. Rigid head carries the reference point with this offset. Distributed-neck trajectory differs in articulated poses.')
  base=baselines['characters'][name];ratio=.5/base['scale'];errors={k:abs(v-base['measurements_mm'][k]*ratio) for k,v in measure.items()};assert max(errors.values())<.001,(name,errors)
  height=p['design_reference']['mesh_N_pose_surface_height_mm'];assert abs(height-base['measurements_mm']['neutral_surface_height']*ratio)<.001
  rows[name]=dict(source_cad_sha256=d['source_sha256'],source_manifest_sha256=hashlib.sha256(mf.read_bytes()).hexdigest(),source_half_scale_profile_sha256=hashlib.sha256(oldfile.read_bytes()).hexdigest(),mesh_asset=p['design_reference']['mesh_asset'],scale=.5,reference_surface_height_mm=height,measurements_mm=measure,neck_reference=neck,maximum_joint_origin_change_mm=max(float(np.linalg.norm(T[k]-B[k])) for k in B),maximum_length_error_from_UE_baseline_mm=max(errors.values()),arm_to_reference_height_ratio=measure['shoulder_to_fingertip_l']/height,passed=True,scope='Joint centres and defined hand-tip lengths, not a skin surface match or tested Control Rig mapping.')
 save(ROOT/'verification/revM_proportions.json',dict(characters=rows,source_baselines_sha256=hashlib.sha256((ROOT/'verification/revE_proportion_baselines.json').read_bytes()).hexdigest()))
 for name,r in rows.items():print(name,'proportions PASS',round(r['reference_surface_height_mm'],3),'mm; arm/height',round(r['arm_to_reference_height_ratio'],6))
if __name__=='__main__':main()
