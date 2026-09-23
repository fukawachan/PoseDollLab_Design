from foot_shells import *
for name in ('manny','quinn'):
 A,_=build(name)
 for side in ['l']:
  for own in ['pelvis','waist','chest','head','ball_'+side,'toe_tip_'+side,'sole_'+side]:print(name,own,A.T0[own][:3,3].tolist(),flush=True)
 print(name,'owners',sorted(set(q['owner'] for q in A.parts)),flush=True)
