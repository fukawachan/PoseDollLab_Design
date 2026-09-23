"""All 41 load-side stops, combined poses, and independent cache comparison."""
from sensor_cable_heads import *
from collision_cache import CollisionCache
from full_body_audit import poses,channels41,readout,input_hashes

def main():
 out={'source_sha256':input_hashes(),'physical_tested':False,'manufacturing_released':False,'characters':{}}
 for name in (['quinn'] if '--quick' in sys.argv else ['manny','quinn']):
  A,meta=build(name);ep=endpoint_check(A,meta['compact_travel_guards'])+[dict(axis=g['axis'],checks=endpoint(A,g)) for g in meta['special_travel_guards']];assert len(ep)==41
  cache=CollisionCache(A);cases,invalid=poses(A,'--smoke' in sys.argv);read=readout(A,channels41(A,name),cases)
  row=dict(endpoint_checks=ep,readout=read,checks=[],cache_independent_comparison=[]);out['characters'][name]=row
  for label,pose in cases.items():
   raw=cache.contacts(pose,skip_same_owner=label!='neutral')
   if label in ('neutral','trunk_bend','arms_forward'):
    uncached=fast_contacts(A.scene(pose),A.thread_pairs,None,label!='neutral');assert raw==uncached,(name,label,'cache mismatch');row['cache_independent_comparison'].append(label)
   review=classify_all(raw,A.parts);bad=[q for q in review if q['classification']=='structural'];row['checks'].append(dict(pose=label,angles_deg=pose,review=review,raw_contacts=raw))
   row['cache_stats']=dict(exact=cache.evaluated,reused=cache.reused)
   h.save(ROOT/'verification/revM_all_guards_audit_work.json',out)
   print(json.dumps(dict(character=name,pose=label,structural=bad[:8],structural_count=len(bad),pose_restrictions=len(review)-len(bad),cache=row['cache_stats'])),flush=True)
if __name__=='__main__':main()
