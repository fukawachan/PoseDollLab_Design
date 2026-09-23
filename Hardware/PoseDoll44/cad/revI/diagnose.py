from shoulder_integration import *
p,parts,meta=build('manny')
for label in ['arms_crossed','crossed_staggered','arms_overhead','crossed_clearance_candidate']:
 items,T,A=h.scene(parts,p,h.cases()[label])
 hits=h.collisions(items)
 print(label,hits,flush=True)
 for hit in hits:
  if hit['a'][0]!=hit['b'][0]:continue
  a=next(q for q in items if q['name']==hit['a']);b=next(q for q in items if q['name']==hit['b'])
  cross=a['shape'].intersect(b['shape'])
  for owner in [a['owner'],b['owner']]:
   # Pose is a rigid transform; express overlap centre relative to the owning frame.
   c=np.array(cross.Center().toTuple());v=np.linalg.inv(T[owner])@np.r_[c,1]
   print(owner, v[:3].tolist(),flush=True)
