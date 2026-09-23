from girdle_integration import *
A,_=get_body('quinn',shoulder.build);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin']
a=cq.Shape.importBrep(str(ROOT/'generated/revM/cache/probe_chest_stage_5.brep'));pts=[C+[-57,10,35],C+[-57,30,130],N+[27,20,-42],N+[27,0,-42]]
bits=[h.rod(u,v,3.5) for u,v in zip(pts,pts[1:])]
s=a
for i,b in enumerate(bits):
 t=s.fuse(b);print('forward',i,'a',s.Volume(),'b',b.Volume(),'res',t.Volume(),len(t.Solids()),flush=True);s=t
s=a
for i,b in enumerate(reversed(bits)):
 t=s.fuse(b);print('reverse',i,'a',s.Volume(),'b',b.Volume(),'res',t.Volume(),len(t.Solids()),flush=True);s=t
s=a.fuse(*bits);print('multiple',s.Volume(),len(s.Solids()),flush=True)
for i in range(len(a.Solids())):print('a solid',i,a.Solids()[i].Volume(),a.Solids()[i].BoundingBox().zmin,flush=True)
