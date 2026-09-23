from girdle_integration import *
A,_=get_body('quinn',shoulder.build);C=A.A0['chest.yaw']['origin'];a=cq.Shape.importBrep(str(ROOT/'generated/revM/cache/probe_chest_stage_5.brep'))
for xyz in [(-57,8,34),(-57,8,33),(-57,10,32),(-56.5,8,34),(-57,7,35),(-57,0,35)]:
 b=h.rod(C+list(xyz),C+[-57,30,130],3.5);s=a.fuse(b)
 print(xyz,s.Volume(),len(s.Solids()),'lost',a.cut(s).Volume(),flush=True)
