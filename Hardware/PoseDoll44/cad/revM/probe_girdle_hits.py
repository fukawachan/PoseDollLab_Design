from girdle_integration import *
A,_=build('quinn');C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];R=A.A0['clavicle_l.protract']['origin']
for label,pose in [('neutral',{}),('shrug',{'clavicle_l.elevate':30,'clavicle_r.elevate':30})]:
 sc=A.scene(pose);affected={q['name'] for q in sc if '_G4_' in q['name'] or q['name'] in ('chest_M_body_frame','l_yaw_carriage','r_yaw_carriage','l_clavicle_output_frame','r_clavicle_output_frame')};hits=fast_contacts(sc,A.thread_pairs,affected,label!='neutral');dic={q['name']:q for q in sc}
 for hit in hits:
  a,b=dic[hit['a']],dic[hit['b']];cc=np.array(a['shape'].intersect(b['shape']).Center().toTuple());hit['chest_relative_mm']=(cc-C).round(3).tolist();hit['root_relative_mm']=(cc-R).round(3).tolist()
 print(label,json.dumps(hits),flush=True)
