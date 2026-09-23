from girdle_integration import *
A,_=get_body('quinn',shoulder.build);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin']
a=cq.Shape.importBrep(str(ROOT/'generated/revM/cache/probe_chest_stage_5.brep'));b=rails([C+[-57,10,35],C+[-57,30,130],N+[27,20,-42],N+[27,0,-42]],3.5)
for tol in (1e-6,1e-5,1e-4,.001):
 s=a.fuse(b,tol=tol);print(tol,s.Volume(),len(s.Solids()),s.isValid(),'lost_a',a.cut(s,tol=tol).Volume(),'lost_b',b.cut(s,tol=tol).Volume(),flush=True)
