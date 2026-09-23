from pathlib import Path
import sys,runpy,json
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'cad/revM'))
import final_model as M
from collision_cache import CollisionCache
ns=runpy.run_path(str(R/'cad/revN/chest_clearance.py'),run_name='revN_functions')
for name in ('manny','quinn'):
 A,meta=M.build(name);ns['trim'](A);pose,info=ns['behind_pose'](A)
 cache=CollisionCache(A);raw=cache.contacts(pose,skip_same_owner=True);review=M.classify_all(raw,A.parts)
 structural=[q for q in review if q['classification']=='structural']
 d=dict(character=name,angles_deg=pose,target_info=info,raw_contacts=raw,review=review,source_sha256=meta['source_sha256'])
 ns['save'](R/f'verification/revN_behind_initial_{name}.json',d)
 print(json.dumps(dict(character=name,pose=pose,structural=structural,other_count=len(review)-len(structural)),ensure_ascii=False),flush=True)
