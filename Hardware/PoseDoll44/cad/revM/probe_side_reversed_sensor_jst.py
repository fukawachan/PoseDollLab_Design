"""Alternative direct cable connector envelope; does not change production CAD."""
from retained_bushes import *
from full_body_audit import channels41,poses
out={}
for name in ('quinn','manny'):
 A,_=build(name);changed=[]
 for c in channels41(A,name):
  loc=cq.Location(cq.Plane(origin=tuple(c['origin_neutral_mm']),normal=tuple(c['normal_neutral']),xDir=tuple(c['xdir_neutral'])))
  matches=[q for q in A.parts if q['name'].startswith(c['part_prefix']) and q['name'].endswith('J1_dimension_envelope')]
  if not matches:
   print('Existing full-size connector retained',c['axis_id'],[q['name'] for q in A.parts if q['name'].startswith(c['part_prefix']) and 'J1' in q['name']],flush=True);continue
  q=matches[0]
  z=c['package_face_mm']+1.995
  sh=cube((9.4,8.8,3.2),(0,-2.1,z+1.6)).rotate((0,0,0),(0,0,1),c.get('board_rotation_deg',0)).moved(loc)
  replace_world(A,q,sh,'Candidate JST SH6 side-entry mated plug enclosure, no cable bend yet','pcb_component');changed.append(q['name'])
 cache=CollisionCache(A);cases,_=poses(A);rows=[]
 for label,pose in cases.items():
  raw=cache.contacts(pose,set(changed),label!='neutral');review=classify_all(raw,A.parts);bad=[q for q in review if q['classification']=='structural'];rows.append(dict(pose=label,angles_deg=pose,review=review))
  if bad:print(json.dumps(dict(character=name,pose=label,structural=bad)),flush=True)
 out[name]=rows;h.save(ROOT/'verification/revM_side_reversed_sensor_JST_probe.json',out);print(name,'completed',len(rows),'failing',sum(any(q['classification']=='structural' for q in r['review']) for r in rows),flush=True)
