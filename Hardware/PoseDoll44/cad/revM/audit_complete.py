"""Final-model whole-assembly BRep scan; raw contacts and classifications retained."""
from final_model import *
from collision_cache import CollisionCache
from full_body_audit import poses,channels41,readout

def main():
 out=dict(revision='M',physical_tested=False,manufacturing_released=False,scope='Whole rigid assembly at 164 finite poses per character; 0.02 mm3 reporting threshold; no continuous sweep or elastic cable proof',characters={})
 for name in ('manny','quinn'):
  A,meta=build(name);cases,invalid=poses(A);ep=endpoint_check(A,meta['compact_travel_guards'])+[dict(axis=g['axis'],checks=endpoint(A,g)) for g in meta['special_travel_guards']];assert len(ep)==41
  row=dict(source_sha256=meta['source_sha256'],parts=len(A.parts),endpoints=ep,readout=readout(A,channels41(A,name),cases),checks=[],independent_cache_checks=[],excluded_out_of_profile_poses=invalid);out['characters'][name]=row;cache=CollisionCache(A)
  for label,pose in cases.items():
   raw=cache.contacts(pose,skip_same_owner=label!='neutral')
   if label in ('neutral','trunk_bend','arms_forward'):
    assert raw==fast_contacts(A.scene(pose),A.thread_pairs,None,label!='neutral');row['independent_cache_checks'].append(label)
   review=classify_all(raw,A.parts);row['checks'].append(dict(pose=label,angles_deg=pose,review=review,raw_contacts=raw));bad=[r for r in review if r['classification']=='structural']
   row['structural_failed_poses']=sum(any(r['classification']=='structural' for r in q['review']) for q in row['checks'])
   h.save(ROOT/'verification/revM_complete_audit.json',out)
   if bad or len(row['checks'])%20==0:print(json.dumps(dict(character=name,done=len(row['checks']),total=len(cases),structural=bad[:8],structural_count=len(bad))),flush=True)
  print(name,'complete audit',len(cases),'structural failed poses',row['structural_failed_poses'],flush=True)
if __name__=='__main__':main()
