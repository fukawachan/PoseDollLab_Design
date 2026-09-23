from final_model import *
from shell_mounts import apply_mounts
A,m=apply_mounts(*build('manny'))
for face in ('front','back'):
 p,w=world_part(A,'l_arm_upperarm_shell_'+face);f,fw=world_part(A,'elbow_l_flex_M_upperarm_carrier');inter=w.intersect(fw);O=A.T0[p['owner']][:3,3];b=inter.translate(tuple(-O)).BoundingBox();print(face,inter.Volume(),b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax,flush=True)
 for solid in inter.Solids():
  b=solid.translate(tuple(-O)).BoundingBox();print('solid',solid.Volume(),b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax,flush=True)
h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({}) if q['owner']=='upperarm_l'],ROOT/'verification/arm_mount_probe.png','Upper-arm cover mounts',camera=(350,-600,250))
