from special_travel_stops import *
for name in ('manny','quinn'):
 A,_=build(name);C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];d=28.
 shape=rails([C+[-57,10,35],C+[-57,35,35],C+[65,35,35],C+[65,0,35],[C[0]+65,0,N[2]-d],N+[15,0,-d],N+[15,0,-30],N+[6.3,0,-30]],3)
 pose={'head.pitch':55};T=h.fk(A.profile,pose)[0] if False else None
 q=next(x for x in A.scene(pose) if x['name']=='head_M_shell_front');inter=q['shape'].intersect(shape)
 # Assembly pose matrices use the same FK helper as the collision scene.
 from collision_cache import CollisionCache
 c=CollisionCache(A)
 print(name, 'N',N.tolist(), 'world_hit',inter.BoundingBox().__dict__,flush=True)
 for part in A.parts:
  if part['name']=='head_M_shell_front':
   print('partkeys',list(part.keys()),flush=True)
