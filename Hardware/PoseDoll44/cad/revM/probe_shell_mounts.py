from final_model import *
for name in ('manny','quinn'):
 A,meta=build(name)
 for owner,pre,frame in [('upperarm_l','l_arm_upperarm_shell_', 'elbow_l_flex_M_upperarm_carrier'),('forearm_l','l_arm_forearm_shell_','forearm_l_twist_M_distal_forearm_carrier')]:
  O=A.T0[owner][:3,3]
  for z in ([-48,-54,-60,-66,-72,-78,-84,-90] if owner.startswith('upper') else [-28,-29,-30]):
   row={'character':name,'owner':owner,'z':z,'locations':[]}
   for y in (-18,-12,-6,0,6,12,18):
    vols={}
    for face in ('front','back'):
     q,w=world_part(A,pre+face+('_distal' if owner.startswith('fore') else ''));w=w.translate(tuple(-O));v=w.intersect(h.axis_cyl(0,-60,60,3.9,(0,y,z))).Volume();vols[face]=round(v,3)
    if min(vols.values())>.1:row['locations'].append([y,vols])
   print(json.dumps(row),flush=True)
