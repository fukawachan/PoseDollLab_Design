from foot_shells import *
for name in ('manny','quinn'):
 A,_=build(name);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin']
 for label,pose in h.cases().items():
  items={q['name']:q for q in A.scene(pose)}
  for n in ('l_clavicle_output_frame','r_clavicle_output_frame','l_flex_clutch_reaction_plate','r_flex_clutch_reaction_plate'):
   s=items[n]['shape'].intersect(items['chest_M_body_frame']['shape']);vol=s.Volume()
   if vol>.02:print(name,label,n,vol,s.Center().toTuple(),'neck',N.tolist(),flush=True)
 for d in (-45,0,30):
  pose={'foot_l.invert':25,'foot_l.dorsiflex':d};T,_=h.fk(A.profile,pose);items={q['name']:q for q in A.scene(pose)};s=items['calf_l_M_centreline_frame']['shape'].intersect(items['foot_l_M_low_shoe']['shape']);vol=s.Volume()
  if vol>.02:
   s=h.move(s,A.T0['foot_l']@np.linalg.inv(T['foot_l']));bb=s.BoundingBox();F=A.A0['foot_l.dorsiflex']['origin'];S=A.T0['sole_l'][:3,3];print(name,'shoe',d,vol,[float(bb.xmin-F[0]),float(bb.xmax-F[0]),float(bb.ymin-F[1]),float(bb.ymax-F[1]),float(bb.zmin-S[2]),float(bb.zmax-S[2])],flush=True)
