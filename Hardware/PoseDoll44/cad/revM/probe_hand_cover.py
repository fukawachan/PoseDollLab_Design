from full_packaging import *
A,_=build('manny');side='l';W=A.A0['hand_l.flex']['origin'];v=A.T0['hand_tip_l'][:3,3]-W;L=np.linalg.norm(v);n=v/L;xd=np.array([1.,0,0]);xd-=n*np.dot(n,xd);xd/=np.linalg.norm(xd);loc=cq.Location(cq.Plane(origin=tuple(W),xDir=tuple(xd),normal=tuple(n)))
pose={'upperarm_l.abduct':15,'upperarm_r.abduct':15,'hand_l.deviate':35};T,_=h.fk(A.profile,pose);scene={q['name']:q for q in A.scene(pose)}
print('L',L,flush=True)
for a,b in [('forearm_l_twist_M_distal_forearm_carrier','hand_l_M_shell_front'),('forearm_l_twist_M_distal_forearm_carrier','hand_l_M_shell_back'),('hand_l_flex_M_fixed_mount_M3x8_1','hand_l_M_shell_front')]:
 inter=scene[a]['shape'].intersect(scene[b]['shape']);s=h.move(inter,A.T0['hand_l']@np.linalg.inv(T['hand_l'])).moved(loc.inverse)
 if s.Volume()>.001:
  bb=s.BoundingBox();print(json.dumps(dict(a=a,b=b,v=s.Volume(),center=s.Center().toTuple(),bounds=[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax])),flush=True)
