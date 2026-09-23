from girdle_integration import *
A,_=get_body('quinn',shoulder.build)
print('axes', {k:v['origin'].tolist() for k,v in A.A0.items() if k in ('chest.yaw','head.yaw','clavicle_l.protract')},flush=True)
q,cs=world_part(A,'chest_M_body_frame');bb=cs.BoundingBox();print('frame bbox',[(k,getattr(bb,k)) for k in ('xmin','xmax','ymin','ymax','zmin','zmax')],flush=True)
for p in [(-50.32275,10,699.09369),(-50.32275,10,680),(-50.32275,10,710),(-50.32275,-10,668.09369)]:
 print('point',p,'dist',cs.distance(cq.Vertex.makeVertex(*p)),flush=True)
print('all frame entries',[(q['name'],q['local_shape'].Volume()) for q in A.parts if 'body_frame' in q['name']],flush=True)
