from special_travel_stops import *
from collision_review import region,ADJACENT
out={}
for name in ('manny','quinn'):
 A,_=build(name);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];cases=dict(h.cases());limits={q['id']:np.degrees(q['limits_rad']) for q in A.profile['axes']}
 cases.update({f'head_{y}_{p}_{r}':{'head.yaw':y,'head.pitch':p,'head.roll':r} for y in (-75,0,75) for p in (-45,0,55) for r in (-35,0,35)})
 for side in ('l','r'):
  for a in np.linspace(*limits[f'clavicle_{side}.protract'],9):
   for e in [limits[f'clavicle_{side}.elevate'][0],0,limits[f'clavicle_{side}.elevate'][1]]:cases[f'girdle_{side}_{a}_{e}']={f'clavicle_{side}.protract':float(a),f'clavicle_{side}.elevate':float(e)}
 candidates=[]
 for d in (36,40,44,48):
  for ret in (15,25,35):
   sh=rails([C+[-57,10,35],C+[-57,35,35],C+[65,35,35],C+[65,0,35],[C[0]+65,0,N[2]-d],N+[ret,0,-28],N+[15,0,-28],N+[15,0,-30],N+[6.3,0,-30]],3) if ret!=15 else rails([C+[-57,10,35],C+[-57,35,35],C+[65,35,35],C+[65,0,35],[C[0]+65,0,N[2]-d],N+[15,0,-28],N+[15,0,-30],N+[6.3,0,-30]],3)
   candidates.append(dict(depth=d,ret=ret,shape=sh,hits=[]))
 for label,pose in cases.items():
  scene=[q for q in A.scene(pose) if q['owner']!='chest' and (region(q['owner']) in ('head','girdle_l','girdle_r','waist') or q['owner'].startswith('chest.'))]
  for q in candidates:
   if len(q['hits'])>3:continue
   hits=fast_contacts(scene+[dict(name='bridge',shape=q['shape'],owner='chest',role='candidate_solid')],(),{'bridge'},True)
   if hits:q['hits'].append(dict(pose=label,hits=hits))
 rows=[{k:v for k,v in q.items() if k!='shape'} for q in candidates];out[name]=rows;h.save(ROOT/'verification/revM_bridge_dogleg_work.json',out)
 print(name,json.dumps([dict(depth=q['depth'],ret=q['ret'],failing=len(q['hits']),first=q['hits'][:1]) for q in candidates]),flush=True)
