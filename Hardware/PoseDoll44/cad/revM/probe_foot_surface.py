from head_shells import *
for name in ('manny','quinn'):
 A,_=build(name);r=reference_character(name)
 for side in ('l',):
  F=A.A0[f'foot_{side}.dorsiflex']['origin'];B=A.A0[f'ball_{side}.flex']['origin'];T=A.T0[f'toe_tip_{side}'][:3,3];S=A.T0[f'sole_{side}'][:3,3];v=r['surfaces']['foot_'+side]*1.5
  rows=[]
  for x in np.linspace(v[:,0].min()+3,v[:,0].max()-3,9):
   b=v[np.abs(v[:,0]-x)<5];rows.append(dict(x=x,lo=b.min(0).tolist(),hi=b.max(0).tolist()))
  low=[]
  for q in A.scene({}):
   if q['owner'].startswith(('foot_'+side,'ball_'+side)) and q['role']!='reservation':low.append((q['shape'].BoundingBox().zmin,q['name']))
  print(json.dumps(dict(character=name,F=F.tolist(),B=B.tolist(),T=T.tolist(),S=S.tolist(),rows=rows,lowest_parts=sorted(low)[:6])),flush=True)
