"""Removable rigid skull cover; neck and lower compressing regions stay exposed."""
from rigid_shells import *
import rigid_shells as limbs
from character_reference import reference_character

def head_loft(rows):
 return cq.Solid.makeLoft([cq.Workplane('XY',origin=(cx,0,z)).ellipse(rx,ry).val() for z,cx,rx,ry in rows],True)

def add_head_shell(A,name):
 N=A.A0['head.yaw']['origin'];tip=A.T0['head_tip'][:3,3];v=reference_character(name)['surfaces']['head']*1.5-N
 height=tip[2]-N[2];rows=[]
 for z in (36.,50.,65.,82.,98.,height-2.):
  band=v[np.abs(v[:,2]-z)<5.]
  assert len(band)>3,(name,z,len(band))
  lo=band.min(0);hi=band.max(0);rows.append((z,float((lo[0]+hi[0])/2),max(5.,float((hi[0]-lo[0])/2)+.8),max(5.,float(max(abs(lo[1]),abs(hi[1])))+.8)))
 rows.append((height+.8,rows[-1][1],3.,4.))
 outer=head_loft(rows);ir=[(z,cx,rx-1.8,ry-1.8) for z,cx,rx,ry in rows];ir[0]=(ir[0][0]-.5,*ir[0][1:]);ir[-1]=(height-1.2,*ir[-1][1:])
 shell=outer.cut(head_loft(ir));split=10.
 shapes={face:shell.intersect(cube((200,200,300),(split+sg*100.15,0,60))) for face,sg in [('front',1),('back',-1)]}
 shapes['back']=shapes['back'].intersect(cube((300,300,300),(0,0,197)))
 shapes['front']=shapes['front'].intersect(cube((300,300,300),(0,0,200)))
 q,skull=world_part(A,'head_T4_skull_frame');skull=skull.translate(tuple(-N))
 # The first station is on the vertical skull rail, the second on its sloping top.
 bend=np.array([-15.75,24.,70.]);end=tip-N-[0,0,20];mounts=[np.array([-15.75,24.,55.]),bend+(end-bend)*((84.-70.)/(end[2]-70.))]
 for i,P in enumerate(mounts):
  x,y,z=P;skull=fuse_checked(skull,h.axis_cyl(0,x-4,x+4,3,(0,y,z)),'head_cover_lug')
  skull=skull.cut(h.axis_cyl(0,x-5,x+5,1.2,(0,y,z)))
  for face,sg in [('front',1),('back',-1)]:
   boss=h.axis_cyl(0,*sorted((x+sg*4.05,sg*100)),4,(0,y,z)).intersect(outer).cut(h.axis_cyl(0,-110,110,1.2,(0,y,z)))
   shapes[face]=fuse_checked(shapes[face],boss,'head_'+face+'_boss')
  xloc=cq.Location(cq.Plane(origin=(x,y,z),normal=(1,0,0),xDir=(0,1,0)))
  shapes['front']=shapes['front'].cut(h.axis_cyl(0,x+7,110,2.1,(0,y,z)))
  shapes['back']=shapes['back'].cut(hexagon(4.2,-110,-7).moved(xloc))
  bolt=h.axis_cyl(0,x-9,x+7,1,(0,y,z)).fuse(h.axis_cyl(0,x+7,x+9,1.9,(0,y,z))).cut(hexagon(1.5,7.7,9.1).moved(xloc))
  nut=hexagon(4,-8.6,-7).cut(cyl(-8.7,-6.9,.8));nut=nut.moved(xloc)
  bn=f'head_shell_M2x16_{i}';nn=f'head_shell_nut_M2_{i}';A.add(bn,bolt.translate(tuple(N)),'metal','head','M2x16 through integral skull lug; deep straight screwdriver access from front');A.add(nn,nut.translate(tuple(N)),'metal','head','M2 nut in AF4.2 rear cover pocket');A.thread_pairs.append([bn,nn])
 relief=rails([np.array([-15.75,24.,14.]),np.array([-15.75,24.,70.]),tip-N-[0,0,20]],3.3)
 for face in shapes:shapes[face]=shapes[face].cut(relief)
 replace_world(A,q,skull.translate(tuple(N)),q['note']+'; two drilled metal cover attachment lugs')
 for face,shape in shapes.items():A.add('head_M_shell_'+face,shape.translate(tuple(N)),'shell','head','Character-derived head-section silhouette; 1.8 mm nominal wall, 0.30 mm seam; lower front 50 mm / back 47 mm kept exposed for neck motion; surface is simplified, not exact character mesh')
 return dict(rows_mm=rows,lower_exposed_above_pivot_mm=dict(front=50,back=47),wall_mm=1.8,fasteners='2 x M2x16 + 2 x M2 nuts',surface='simplified measured head-section silhouette')

def build(name):
 A,meta=limbs.build(name);head=add_head_shell(A,name);return A,dict(meta,head_shell=head)

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);aff={q['name'] for q in A.parts if q['name'].startswith('head_')};rows=[]
  cases={'neutral':{}}
  for y in (-75,0,75):
   for p in (-45,0,55):
    for r in (-35,0,35):cases[f'head_{y}_{p}_{r}']={'head.yaw':y,'head.pitch':p,'head.roll':r}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,aff,label!='neutral');rows.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hits=hits[:12],count=len(hits))),flush=True)
  out[name]=dict(meta=meta,checks=rows)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],folder/'head_shell_work.png',name.title()+' | head and leg covers | candidate',camera=(1600,-2800,1100))
 h.save(ROOT/'verification/revM_head_shell_work.json',out)
if __name__=='__main__':main()
