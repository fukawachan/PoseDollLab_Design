"""Offline comparison against distributed UE bone-chain prediction; no live rig edits."""
from pathlib import Path
import sys,json,hashlib,itertools,math,numpy as np
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'cad/revE'))
import check_proportions as cp

def main():
 out=dict(scope='Offline cached mesh + existing rotation distribution prediction; not live Control Rig or physically tested motion. Random poses may have nonadjacent contacts.',characters={})
 for name in ('manny','quinn'):
  d=json.loads((ROOT/f'generated/revM/{name}/manufacturing_manifest.json').read_text());p=d['profile'];c=cp.reference_character(name);c['points']={k:v*1.5 for k,v in c['points'].items()};c['shift_mm']=c['shift_mm']*1.5
  poses={k:v['angles_deg'] for k,v in json.loads((ROOT/f'generated/revM/{name}/viewer.json').read_text())['poses'].items()};limits={q['id']:np.degrees(q['limits_rad']) for q in p['axes'] if not q['id'].startswith('pelvis.')};head=[a for a in limits if a.startswith('head.')]
  for i,vals in enumerate(itertools.product(*[np.linspace(*limits[a],7) for a in head])):poses[f'neck_grid_{i:03}']=dict(zip(head,map(float,vals)))
  rng=np.random.default_rng(190923)
  for i in range(128):poses[f'combined_{i:03}']={a:float(rng.uniform(*lim)) for a,lim in limits.items()}
  worst={};rows=[]
  for label,pose in poses.items():
   physical=cp.physical_points(c,p,pose);target=cp.expected_bones(c,p,pose);errs={n:float(np.linalg.norm(physical[n]-(cp.SWAP@g[:3,3]*5+c['shift_mm']))) for n,g in target.items() if n in physical}
   if label=='neutral':assert max(errs.values())<.001
   for n,e in errs.items():
    if n not in worst or e>worst[n]['error_mm']:worst[n]=dict(error_mm=e,pose=label)
   rows.append(dict(pose=label,angles_deg=pose,errors_mm=errs))
  threshold=p['design_reference']['mesh_N_pose_surface_height_mm']*.01
  sources=[ROOT/'cad/revE/check_proportions.py',ROOT/'cad/revE/character_reference.py',ROOT/'cad/model.py',REPO/'Shared/Profiles/manny_body_ue582_v1.json',ROOT/f'reference/ue58/{name}_mesh_probe.json',ROOT/f'reference/ue58/{name}_geometry.json']
  out['characters'][name]=dict(source_cad_sha256=d['source_sha256'],source_sha256={str(f.relative_to(REPO)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources},samples=len(rows),worst_by_landmark=worst,one_percent_reference_height_target_mm=threshold,all_landmarks_within_one_percent=all(w['error_mm']<=threshold for w in worst.values()),poses=rows,live_UE_tested=False,explanation='Limb bone lengths remain exact to scale. Spine/neck rotations are distributed across several target bones, while the mechanical model uses equivalent pivots. These trajectory errors require target-side mapping/IK review; no universal perfect pose match is claimed.')
  print(name,len(rows),'offline mapping samples; worst',max(worst.items(),key=lambda q:q[1]['error_mm']),flush=True)
 (ROOT/'verification/revM_kinematic_mapping.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
