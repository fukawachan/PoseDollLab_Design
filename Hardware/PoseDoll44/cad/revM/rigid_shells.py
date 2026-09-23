"""Rigid segment covers; shoulders, neck, waist, elbows and hips remain exposed.
Leg shells follow character surface-section proportions and attach to printed rails.
"""
from full_packaging import *
import full_packaging as body
from hand_shells import loft

def leg_shell(A,name,side,kind):
 owner=f'{kind}_{side}';upper=A.T0[owner][:3,3]
 distal=f'calf_{side}' if kind=='thigh' else f'foot_{side}';lower=A.T0[distal][:3,3];length=upper[2]-lower[2]
 # Leave the large moving clusters and screw access fully exposed.
 a,b=(116.,length-42.) if kind=='thigh' else (45.,length-48.)
 assert b-a>30,(name,owner,length,a,b)
 ref=json.loads((ROOT/'verification/revG_surface_envelopes.json').read_text(encoding='utf-8'))['characters'][name]['thigh' if kind=='thigh' else 'shin']['sections']
 fractions=np.array([q['fraction'] for q in ref]);rx=np.array([q['depth_x_mm'] for q in ref])*.75;ry=np.array([q['width_y_mm'] for q in ref])*.75
 rows=[]
 for d in np.linspace(a,b,5):
  rxx=max(10.,float(np.interp(d/length,fractions,rx)));ryy=max(10.,float(np.interp(d/length,fractions,ry)))
  rows.append((-d,rxx,ryy))
 rows.sort();outer=loft(rows);innerrows=[(z,x-1.8,y-1.8) for z,x,y in rows];innerrows[0]=(innerrows[0][0]-.5,*innerrows[0][1:]);innerrows[-1]=(innerrows[-1][0]+.5,*innerrows[-1][1:])
 wall=outer.cut(loft(innerrows));shapes={'front':wall.intersect(cube((200,200,2*length),(100.15,0,-length/2)))}
 if kind=='calf':
  # The upper rear calf compresses against the thigh in a deep fold. Keep it bare.
  shapes['back']=wall.intersect(cube((200,200,2*length),(-100.15,0,-length/2))).intersect(cube((200,200,2*length),(0,0,-75-length)))
 frame,rail=world_part(A,f'{kind}_{side}_M_centreline_frame');rail=rail.translate(tuple(-upper))
 ma=max(a,75.) if kind=='calf' else a
 for i,d in enumerate((ma+(b-ma)/3,ma+2*(b-ma)/3)):
  z=-d;lug=cube((12,8,6),(0,0,z));rail=fuse_checked(rail,lug,owner+'_shell_lug')
  rail=rail.cut(h.axis_cyl(0,-7,7,1.2,(0,0,z)))
  for face,sg in [('front',1)]+([('back',-1)] if kind=='calf' else []):
   boss=h.axis_cyl(0,*sorted((sg*6.05,sg*50)),4,(0,0,z)).intersect(outer).cut(h.axis_cyl(0,-55,55,1.2,(0,0,z)))
   shapes[face]=fuse_checked(shapes[face],boss,owner+'_'+face+'_boss')
  xloc=cq.Location(cq.Plane(origin=(0,0,z),normal=(1,0,0),xDir=(0,1,0)))
  seat,tip,nutfront=(10,-6,-4) if kind=='thigh' else (9,-11,-9)
  shapes['front']=shapes['front'].cut(h.axis_cyl(0,seat,60,2.1,(0,0,z)))
  if kind=='calf':shapes['back']=shapes['back'].cut(hexagon(4.2,-60,nutfront).moved(xloc))
  else:rail=rail.cut(hexagon(4.2,-6.1,nutfront).moved(xloc))
  bolt=h.axis_cyl(0,tip,seat,1,(0,0,z)).fuse(h.axis_cyl(0,seat,seat+2,1.9,(0,0,z))).cut(hexagon(1.5,seat+.7,seat+2.1).moved(xloc))
  nut=hexagon(4,nutfront-1.6,nutfront).cut(cyl(nutfront-1.7,nutfront+.1,.8));nut=nut.moved(xloc)
  bn=owner+f'_shell_M2x{seat-tip}_{i}';nn=owner+f'_shell_nut_M2_{i}'
  A.add(bn,bolt.translate(tuple(upper)),'metal',owner,f'M2x{seat-tip}, recessed straight hex access through front cover; no joint-preload function')
  A.add(nn,nut.translate(tuple(upper)),'metal',owner,'M2 nut in printed AF4.2 capture pocket');A.thread_pairs.append([bn,nn])
 replace_world(A,frame,rail.translate(tuple(upper)),frame['note']+'; two printed shell attachment lugs with through M2.4 holes','frame')
 for face,shape in shapes.items():A.add(owner+'_M_shell_'+face,shape.translate(tuple(upper)),'shell',owner,'Rigid removable '+kind+' cover following 1:2 character surface-section width/depth; 1.8 mm wall, 0.30 mm seam; posterior thigh and proximal 75 mm of rear calf intentionally exposed for deep flexion')
 return dict(owner=owner,proximal_gap_mm=a,distal_gap_mm=length-b,length_mm=b-a,wall_mm=1.8,seam_mm=.30,mount_screws='2 x M2x16' if kind=='thigh' else '2 x M2x20',rear_coverage='none' if kind=='thigh' else 'distal of knee +75 mm',rows_mm=rows)

def trim_wrist_covers(A):
 for side in ('l','r'):
  W=A.A0[f'hand_{side}.flex']['origin'];v=A.T0[f'hand_tip_{side}'][:3,3]-W;L=float(np.linalg.norm(v));n=v/L;xd=np.array([1.,0,0]);xd-=n*np.dot(n,xd);xd/=np.linalg.norm(xd)
  loc=cq.Location(cq.Plane(origin=tuple(W),xDir=tuple(xd),normal=tuple(n)))
  # Keep the central fastener bosses intact; retract side walls near the wrist.
  start=max(.49*L,45.5);envelope=cube((100,100,2*L),(0,0,start+L)).fuse(cube((100,9,2*L),(0,0,L)))
  for face in ('front','back'):
   q,w=world_part(A,f'hand_{side}_M_shell_{face}');w=w.moved(loc.inverse).intersect(envelope).moved(loc)
   replace_world(A,q,w,q['note']+'; wrist-side walls start at max(49% palm length, 45.5 mm), central mounting tongue preserved')
 return A

def build(name):
 A,meta=body.build(name);trim_wrist_covers(A);covers=[]
 for side in ('l','r'):
  for kind in ('thigh','calf'):covers.append(leg_shell(A,name,side,kind))
 return A,dict(meta,leg_shells=covers)

def main():
 result={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if q['name'].startswith(('thigh_','calf_')) and ('_shell_' in q['name'] or '_centreline_frame' in q['name'])};rows=[]
  cases={'neutral':{},'sit':{'thigh_l.flex':90,'thigh_r.flex':90,'calf_l.flex':90,'calf_r.flex':90},'fold':{'thigh_l.flex':120,'thigh_r.flex':120,'calf_l.flex':145,'calf_r.flex':145},'hip_out':{'thigh_l.abduct':65,'thigh_r.abduct':65},'hip_twist':{'thigh_l.twist':50,'thigh_r.twist':-50},'ankle':{'foot_l.dorsiflex':30,'foot_r.dorsiflex':30,'foot_l.invert':25,'foot_r.invert':-25}}
  limit=max(math.degrees(q['limits_rad'][1]) for q in A.profile['axes'] if q['id']=='calf_l.flex')
  cases['deep_fold_limit']={'thigh_l.flex':120,'thigh_r.flex':120,'calf_l.flex':limit,'calf_r.flex':limit}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral');rows.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hits=hits[:12],count=len(hits))),flush=True)
  result[name]=dict(meta=meta,checks=rows)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],folder/'leg_shells_work.png',name.title()+' | rigid leg covers | candidate',camera=(1600,-2800,1100))
 h.save(ROOT/'verification/revM_leg_shells_work.json',result)
if __name__=='__main__':main()
