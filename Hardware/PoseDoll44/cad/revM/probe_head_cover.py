from head_shells import *
A,meta=build('quinn')
N=A.A0['head.yaw']['origin']
for label,pose in [('neutral',{}),('headup',{'head.pitch':55})]:
 scene={q['name']:q for q in A.scene(pose)}
 T,_=h.fk(A.profile,pose)
 for a,b in [('head_T4_skull_frame','head_M_shell_front'),('head_T4_skull_frame','head_M_shell_back'),('chest_M_body_frame','head_M_shell_front')]:
  inter=scene[a]['shape'].intersect(scene[b]['shape'])
  if inter.Volume()<.001:continue
  local=h.move(inter,A.T0['head']@np.linalg.inv(T['head'])).translate(tuple(-N))
  for s in local.Solids():
   bb=s.BoundingBox();print(json.dumps(dict(pose=label,a=a,b=b,v=s.Volume(),center=s.Center().toTuple(),bounds=[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax])),flush=True)
