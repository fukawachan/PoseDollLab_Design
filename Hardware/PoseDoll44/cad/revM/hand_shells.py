"""Removable rigid hand grips, no finger channels or soft joint coverings."""
from wrist_integration import *
import wrist_integration as wrists


def loft(rows):
 return cq.Solid.makeLoft([cq.Workplane('XY',origin=(0,0,z)).ellipse(rx,ry).val() for z,rx,ry in rows],True)

def build(name):
 A,meta=wrists.build(name)
 for side in ('l','r'):
  W=A.A0[f'hand_{side}.flex']['origin'];T=A.T0[f'hand_tip_{side}'][:3,3];v=T-W;L=float(np.linalg.norm(v));n=v/L
  xd=np.array([1.,0,0]);xd-=n*np.dot(n,xd);xd/=np.linalg.norm(xd)
  loc=cq.Location(cq.Plane(origin=tuple(W),xDir=tuple(xd),normal=tuple(n)))
  width=19 if name=='quinn' else 21
  rows=[(.40*L,11.5,width),(.55*L,11.5,width+1),(.78*L,10.5,width-2),(.94*L,7.0,width-7),(L+.8,5.8,width-10)]
  outer=loft(rows);innerrows=[(z,rx-1.8,ry-1.8) for z,rx,ry in rows]
  innerrows[0]=(innerrows[0][0]-1,*innerrows[0][1:]);innerrows[-1]=(L-1.2,*innerrows[-1][1:])
  wall=outer.cut(loft(innerrows))
  halves={s:wall.intersect(cube((100,150,2*L),((50.15 if s=='front' else -50.15),0,L/2))) for s in ('front','back')}
  rail=next(q for q in A.parts if q['name']==f'hand_{side}_M_palm_rail')
  rw=h.move(rail['local_shape'],A.T0[rail['owner']])
  for i,z in enumerate((.52*L,.74*L)):
   lug=cube((8,8,6),(0,0,z)).cut(h.axis_cyl(0,-6,6,1.2,(0,0,z)))
   rw=rw.fuse(lug.moved(loc))
   for sign in (-1,1):rw=rw.cut(cube((20,30,8.2),(sign*14,0,z)).moved(loc))
   rw=rw.cut(h.axis_cyl(0,-20,20,1.2,(0,0,z)).moved(loc))
   for face,sign in [('front',1),('back',-1)]:
    boss=h.axis_cyl(0,*sorted((sign*4.05,sign*12)),4,(0,0,z)).intersect(outer)
    boss=boss.cut(h.axis_cyl(0,-15,15,1.2,(0,0,z)))
    halves[face]=halves[face].fuse(boss)
   halves['front']=halves['front'].cut(h.axis_cyl(0,7,20,2.1,(0,0,z)))
   xloc=cq.Location(cq.Plane(origin=(0,0,z),xDir=(0,1,0),normal=(1,0,0)))
   nutcut=hexagon(4.2,-20,-7).moved(xloc)
   halves['back']=halves['back'].cut(nutcut)
   bolt=h.axis_cyl(0,-9,7,1,(0,0,z)).fuse(h.axis_cyl(0,7,9,1.9,(0,0,z))).cut(hexagon(1.5,7.7,9.1).moved(xloc))
   nut=hexagon(4,-8.6,-7).cut(cyl(-8.7,-6.9,.8));nut=nut.moved(xloc)
   bn=f'hand_{side}_M_shell_M2x16_{i}';nn=f'hand_{side}_M_shell_nut_M2_{i}'
   A.add(bn,bolt.moved(loc),'metal',rail['owner'],'M2x16 recessed socket screw; two screws release the static hand grip')
   A.add(nn,nut.moved(loc),'metal',rail['owner'],'Captured M2 hex nut; 4.2 mm AF nominal printed pocket')
   A.thread_pairs.append([bn,nn])
  assert rw.isValid() and len(rw.Solids())==1
  rail['local_shape']=rw.translate(tuple(-A.T0[rail['owner']][:3,3]))
  for face,sh in halves.items():
   A.add(f'hand_{side}_M_shell_{face}',sh.moved(loc),'shell',rail['owner'],'Rigid removable simplified hand silhouette, 1.8 mm nominal wall and 0.30 mm split seam; no independent fingers; tip +0.8 mm allowance')
 return A,dict(meta,stage='complete_arm_geometry_candidate',channels=A.channels)

def main():
 result={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if '_M_' in q['name']}
  cases={'neutral':{},'elbows_145':{'elbow_l.flex':145,'elbow_r.flex':145},'wrist_max':{'hand_l.flex':65,'hand_r.flex':-65,'hand_l.deviate':35,'hand_r.deviate':-25},'forearm_twist':{'elbow_l.flex':90,'elbow_r.flex':90,'forearm_l.twist':90,'forearm_r.twist':-90}}
  checks=[]
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral')
   print(json.dumps(dict(character=name,pose=label,hits=hits)),flush=True);checks.append(dict(pose=label,angles_deg=pose,hits=hits))
  result[name]=dict(meta=meta,checks=checks)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name=name+'_RevM_arms')
  for q in A.scene({}):assy.add(q['shape'],name=q['name'],color=cq.Color(*COL[q['material']]))
  assy.save(str(folder/(name+'_arms.step')))
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({}) if q['role']!='reservation'],folder/'arms.png',name.title()+' | elbows, forearms, wrists and hands | integration candidate',camera=(1000,-1500,600))
 h.save(ROOT/'verification/revM_hand_work.json',result)
if __name__=='__main__':main()
