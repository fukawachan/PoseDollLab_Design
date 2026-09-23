from rigid_shells import *
from collision_review import classify_all
out={}
for name in ('manny','quinn'):
 A,_=build(name);affected={q['name'] for q in A.parts if q['name'].startswith(('hand_l_M_shell','hand_r_M_shell'))};cases={'neutral':{}}
 for f in (-65,0,65):
  for d in (-25,0,35):cases[f'wrist_{f}_{d}']={f'hand_{side}.{axis}':angle for side in ('l','r') for axis,angle in [('flex',f),('deviate',d)]}
 rows=[]
 for label,pose in cases.items():
  hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral');review=classify_all(hits,A.parts);bad=[q for q in review if q['classification']=='structural'];rows.append(dict(pose=label,angles_deg=pose,hits=hits,review=review));print(json.dumps(dict(character=name,pose=label,structural=bad,pose_restrictions=len(review)-len(bad))),flush=True)
 out[name]=rows
h.save(ROOT/'verification/revM_wrist_cover_work.json',out)
