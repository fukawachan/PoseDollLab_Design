"""Evaluate complete regional-node pod envelopes before selecting mounts."""
from foot_shells import *
from collision_review import region,ADJACENT
out={}
for name in ('quinn','manny'):
 A,_=build(name);C=A.T0['chest'][:3,3];P=A.T0['pelvis'][:3,3]
 candidates=[]
 for owner,origin,zs in [('chest',C,(45,)),('pelvis',P,(-20,))]:
  for x in (-105,-115):
   for y in (-46,0,46):
    for z in zs:candidates.append(dict(id=f'{owner}_{x}_{y}_{z}',owner=owner,xyz=(origin+[x,y,z]).tolist(),hits=[]))
 cases={k:v for k,v in h.cases().items() if k in ('neutral','forward','backward','shrug','down','forward_up','back_down','asymmetric','arms_forward','arms_overhead','arms_side','elbows_closed','forward_shrug_reach')}
 cases.update(trunk_bend={'waist.pitch':40,'chest.pitch':30},trunk_extend={'waist.pitch':-20,'chest.pitch':-20},waist_roll={'waist.roll':25,'chest.roll':20},sit={'thigh_l.flex':90,'thigh_r.flex':90,'calf_l.flex':90,'calf_r.flex':90},hips_back={'thigh_l.flex':-30,'thigh_r.flex':-30},hips_out={'thigh_l.abduct':65,'thigh_r.abduct':65},hip_turn={'thigh_l.twist':50,'thigh_r.twist':-50},head_nod={'head.pitch':55})
 shapes={q['id']:cube((36,44,100),q['xyz']) for q in candidates}
 for label,pose in cases.items():
  scene=A.scene(pose);T,_=h.fk(A.profile,pose)
  for q in candidates:
   sh=h.move(shapes[q['id']],T[q['owner']]@np.linalg.inv(A.T0[q['owner']]))
   rr=region(q['owner']);items=[a for a in scene if region(a['owner'])==rr or frozenset((rr,region(a['owner']))) in ADJACENT]
   items.append(dict(name=q['id'],shape=sh,owner=q['owner'],role='candidate_solid'))
   hits=fast_contacts(items,(),{q['id']})
   if hits:q['hits'].append(dict(pose=label,hits=hits))
  print(name,label,'clear_candidates',sum(not x['hits'] for x in candidates),flush=True)
  out[name]=candidates;h.save(ROOT/'verification/revM_electronics_pod_space_final_envelope.json',out)
 print(name,'CLEAR',[(q['id'],q['xyz']) for q in candidates if not q['hits']],flush=True)
