from body_integration import *
A,_=build('quinn');C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin']
for y in (-20,-15,-10,10,15,20):
 sh=rails([C+[-57,10,35],C+[-57,30,130],N+[27,y,-42],N+[27,0,-42]],3.5);hits=[]
 for label,pose in [('neutral',{}),('head_turn',{'head.yaw':75}),('head_other',{'head.yaw':-75}),('head_nod',{'head.pitch':55})]:
  for q in A.scene(pose):
   if q['role']=='reservation' or not (q['name'].startswith('head_') or q['name'] in ('l_clavicle_output_frame','r_clavicle_output_frame','l_elev_fixed_face','r_elev_fixed_face')):continue
   v=sh.intersect(q['shape']).Volume()
   if v>.02:hits.append((label,q['name'],round(v,4)))
 print(json.dumps(dict(route_y=y,hits=hits)),flush=True)
