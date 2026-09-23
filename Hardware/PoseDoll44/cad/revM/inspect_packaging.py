from foot_shells import *
A,meta=build('quinn')
for q in A.parts:
 if q['material'] in ('bush','pom') and not '_M_radial_bush' in q['name']:
  w=h.move(q['local_shape'],A.T0[q['owner']]);bb=w.BoundingBox();O=A.A0['upperarm_'+q['name'][0]+'.twist']['origin'] if q['name'][0] in 'lr' and 'twist' in q['name'] else A.T0['chest'][:3,3]
  print(json.dumps(dict(name=q['name'],owner=q['owner'],min=(np.array([bb.xmin,bb.ymin,bb.zmin])-O).tolist(),max=(np.array([bb.xmax,bb.ymax,bb.zmax])-O).tolist())),flush=True)
for n in ('pelvis_M_body_frame','chest_M_body_frame'):
 q,w=world_part(A,n);cq.exporters.export(w,str(ROOT/'generated/revM/quinn'/(n+'.step')))
h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],ROOT/'generated/revM/quinn/packaging_work.png','Quinn | current assembly | work in progress',camera=(1700,-2800,1100))
