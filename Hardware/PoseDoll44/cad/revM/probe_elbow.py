from arm_integration import *
A,_=build('quinn');pose={'elbow_l.flex':145}
sc={q['name']:q for q in A.scene(pose)};T,_=h.fk(A.profile,pose)
a=sc['elbow_l_flex_M_upperarm_carrier'];b=sc['elbow_l_flex_M_proximal_forearm'];s=a['shape'].intersect(b['shape'])
c=np.array(s.Center().toTuple());print('volume',s.Volume(),'world',c.tolist(),flush=True)
for q in (a,b):
 own=q['owner'];neutral=np.linalg.inv(T[own])@np.r_[c,1];world=A.T0[own]@neutral
 loc=A.joints['elbow_l.flex']['loc'];point=cq.Vertex.makeVertex(*world[:3]).moved(loc.inverse).Center().toTuple()
 print(q['name'],'owner',own,'neutral in elbow local',point,flush=True)
 bb=s.BoundingBox();print('intersection spans',[bb.xlen,bb.ylen,bb.zlen],flush=True)
