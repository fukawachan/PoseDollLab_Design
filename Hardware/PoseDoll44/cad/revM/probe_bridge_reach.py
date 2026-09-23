from special_travel_stops import *
from collision_review import classify_all
out={}
for name in ('quinn','manny'):
 A,_=build(name);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];cases=dict(h.cases())
 cases.update({f'head_{y}_{p}_{r}':{'head.yaw':y,'head.pitch':p,'head.roll':r} for y in (-75,0,75) for p in (-45,0,55) for r in (-35,0,35)})
 rows=[]
 for reach in (40.,45.,50.,55.,60.):
  depth=28.
  shape=rails([C+[-57,10,35],C+[-57,35,35],C+[reach,35,35],C+[reach,0,35],[C[0]+reach,0,N[2]-depth],N+[15,0,-depth],N+[15,0,-30],N+[6.3,0,-30]],3) if depth!=30 else rails([C+[-57,10,35],C+[-57,35,35],C+[reach,35,35],C+[reach,0,35],[C[0]+reach,0,N[2]-30],N+[6.3,0,-30]],3)
  bad=[]
  for label,pose in cases.items():
   items=[q for q in A.scene(pose) if q['owner']!='chest'];items.append(dict(name='candidate_bridge',shape=shape,owner='chest',role='candidate_solid'))
   hits=fast_contacts(items,(),{'candidate_bridge'},True)
   # All shoulder, neck and head contacts are structural; far arm/hand restrictions stay separate.
   for hit in hits:
    other=hit['a'] if hit['b']=='candidate_bridge' else hit['b'];part=next(q for q in A.parts if q['name']==other)
    if part['owner'].startswith(('head','clavicle')) or other.startswith(('l_yaw','r_yaw','l_elev','r_elev')):bad.append(dict(pose=label,**hit))
  rows.append(dict(depth=depth,reach=reach,structural=bad));print(json.dumps(dict(character=name,depth=depth,reach=reach,structural=len(bad),first=bad[:5])),flush=True);h.save(ROOT/'verification/revM_bridge_reach_work.json',out|{name:rows})
  if not bad:break
 out[name]=rows
