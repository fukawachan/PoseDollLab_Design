from girdle_integration import *
A,_=get_body('quinn',shoulder.build)
print('hfile',h.__file__,flush=True)
p,raw,_=h.build('quinn');old=next(q for q in raw if q['name']=='common_chest_bearing_frame')
world=h.move(old['local_shape'],A.T0[old['owner']]);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];cr=A.joints['chest.roll'];ny=A.joints['head.yaw']
parts=[world,A.plate(cr,'rotor').moved(cr['loc']),rails([C+[7,0,-20],C+[7,0,0],C+[-57,0,0],C+[-57,0,35]],3)]
parts += [rails([C+[-57,0,35],C+[-57,sy*10,35]],3.5) for sy in (-1,1)]
parts += [A.plate(ny,'fixed').moved(ny['loc']),rails([C+[-57,10,35],C+[-57,30,130],N+[27,20,-42],N+[27,0,-42]],3.5)]
s=parts[0]
for i,b in enumerate(parts):
 if i:s=s.fuse(b)
 bb=s.BoundingBox();print('FUSE',i,'incoming',b.Volume(),len(b.Solids()),'result',s.Volume(),len(s.Solids()),s.isValid(),bb.zmin,bb.zmax,flush=True)
 s.exportBrep(str(ROOT/f'generated/revM/cache/probe_chest_stage_{i}.brep'))
