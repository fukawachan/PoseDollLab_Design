"""Low rigid heel/midfoot shoe; moving ankle and toe clusters stay exposed."""
from special_travel_stops import *
import special_travel_stops as body
from collision_cache import CollisionCache

def add_shoe(A,side):
 owner='foot_'+side;F=A.A0[owner+'.dorsiflex']['origin'];B=A.A0['ball_'+side+'.flex']['origin'];S=A.T0['sole_'+side][:3,3];z=float(S[2]);a=float(F[0]-23.5);end=float(B[0]-25);length=end-a;cx=(a+end)/2;yy=float(F[1]);wall=1.8
 outer=cube((length,42,17.7),(cx,yy,z+9.15));inner=cube((length+4,38.4,30),(cx+2+wall,yy,z+17.1));shell=outer.cut(inner)
 # Leave the moving ankle-side wall open through the full heel region.
 shell=shell.cut(cube((F[0]+32-a,50,30),((a+F[0]+32)/2,yy+38 if side=='l' else yy-38,z+10)))
 frame,sh=world_part(A,owner+'_M_tray')
 for i,x in enumerate((F[0]+20,B[0]-40)):
  boss=cyl(z+7,z+11,4.5).translate((x,yy,0));sh=fuse_checked(sh,boss,'foot_nut_boss')
  sh=sh.cut(cyl(z+2.5,z+11.1,1.2).translate((x,yy,0))).cut(hexagon(4.2,z+7.2,z+11.1).translate((x,yy,0)))
  shell=fuse_checked(shell,cyl(z+.3,z+2.95,4.5).translate((x,yy,0)),'shoe_mount_boss')
  shell=shell.cut(cyl(z+.2,z+3.1,1.2).translate((x,yy,0))).cut(cyl(z+.2,z+2.3,2.1).translate((x,yy,0)))
  bolt=cyl(z+2.3,z+10.3,1).fuse(cyl(z+.3,z+2.3,1.9)).cut(hexagon(1.5,z+.2,z+1.7)).translate((x,yy,0))
  nut=hexagon(4,z+7.2,z+8.8).cut(cyl(z+7.1,z+8.9,.8)).translate((x,yy,0));bn=owner+f'_shoe_M2x8_{i}';nn=owner+f'_shoe_nut_M2_{i}'
  A.add(bn,bolt,'metal',owner,'M2x8 from underside, recessed head; no joint-preload function');A.add(nn,nut,'metal',owner,'M2 nut inserted from upper open pocket');A.thread_pairs.append([bn,nn])
 replace_world(A,frame,sh,frame['note'].replace('exterior foot shell pending','removable low shoe with two M2 mounts'),'frame')
 A.add(owner+'_M_low_shoe',shell,'shell',owner,'1.8 mm wall rigid low heel/midfoot cover; outer heel strip above and below the ankle left open for inversion; ankle and toe hinge exposed; underside 0.3 mm above original sole datum')
 return dict(side=side,outer_mm=[length,42,17.7],sole_offset_mm=.3,wall_mm=wall,fasteners='2 x M2x8 + 2 x M2 nuts')

def build(name):
 A,meta=body.build(name);rows=[add_shoe(A,s) for s in ('l','r')];return A,dict(meta,low_shoes=rows)

def main():
 out={}
 for name in ('manny','quinn'):
  A,meta=build(name);aff={q['name'] for q in A.parts if '_shoe_' in q['name'] or q['name'].endswith(('_M_low_shoe','_M_tray'))};checks=[];cache=CollisionCache(A)
  limits={q['id']:np.degrees(q['limits_rad']) for q in A.profile['axes']};cases={'neutral':{}}
  for d in [limits['foot_l.dorsiflex'][0],0,limits['foot_l.dorsiflex'][1]]:
   for inv in [limits['foot_l.invert'][0],0,limits['foot_l.invert'][1]]:
    for toe in [limits['ball_l.flex'][0],limits['ball_l.flex'][1]]:cases[f'{d}_{inv}_{toe}']={f'{j}_{s}.{k}':v for s in ('l','r') for j,k,v in [('foot','dorsiflex',d),('foot','invert',inv),('ball','flex',toe)]}
  for label,pose in cases.items():
   raw=cache.contacts(pose,aff,label!='neutral');review=classify_all(raw,A.parts);bad=[x for x in review if x['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,review=review));print(json.dumps(dict(character=name,pose=label,structural=bad[:10],count=len(bad))),flush=True)
  out[name]=dict(meta=meta,checks=checks);h.save(ROOT/'verification/revM_foot_shells_work.json',out)
if __name__=='__main__':main()
