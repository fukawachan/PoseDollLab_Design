from full_packaging import *
A,_=build('quinn');C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];out=[]
cases={k:v for k,v in h.cases().items() if k in ('neutral','shrug','backward','down')}
cases.update({f'head_pitch_{ang}':{'head.pitch':ang} for ang in range(-45,56,10)})
for label,pose in cases.items():
 sc=A.scene(pose);aff={q['name'] for q in sc if q['name']=='chest_M_body_frame' or q['name'].startswith('head_')};hits=fast_contacts(sc,A.thread_pairs,aff,label!='neutral');dic={q['name']:q for q in sc}
 for hit in hits:
  pt=np.array(dic[hit['a']]['shape'].intersect(dic[hit['b']]['shape']).Center().toTuple());hit['C']=(pt-C).round(3).tolist();hit['N']=(pt-N).round(3).tolist()
 out.append(dict(pose=label,hits=hits));print(label,json.dumps(hits),flush=True)
h.save(ROOT/'verification/revM_packaging_probe_work.json',out)
