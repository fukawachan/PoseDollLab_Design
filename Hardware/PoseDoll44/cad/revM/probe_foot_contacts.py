from foot_shells import *
A,_=build('quinn');pose={'foot_l.invert':25};T,_=h.fk(A.profile,pose);items={q['name']:q for q in A.scene(pose)};shoe=items['foot_l_M_low_shoe'];F=A.A0['foot_l.dorsiflex']['origin'];S=A.T0['sole_l'][:3,3]
for name in ('foot_l_dorsiflex_M_fixed_metal_eye','foot_l_dorsiflex_M_fixed_mount_M3x8_0','calf_l_M_centreline_frame'):
 s=items[name]['shape'].intersect(shoe['shape']);s=h.move(s,A.T0['foot_l']@np.linalg.inv(T['foot_l']));bb=s.BoundingBox();print(name,s.Volume(),[bb.xmin-F[0],bb.xmax-F[0],bb.ymin-F[1],bb.ymax-F[1],bb.zmin-S[2],bb.zmax-S[2]],flush=True)
