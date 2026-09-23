"""Character-derived rigid toe cap, independent of the exposed toe hinge."""
from foot_shells import *
import foot_shells as feet
from character_reference import reference_character

def foot_loft(rows):
 return cq.Solid.makeLoft([cq.Workplane(cq.Plane(origin=(x,cy,cz),normal=(1,0,0),xDir=(0,1,0))).ellipse(ry,rz).val() for x,cy,cz,ry,rz in rows],True)

def add_toe(A,name,side):
 own='ball_'+side;B=A.A0[own+'.flex']['origin'];T=A.T0['toe_tip_'+side][:3,3];v=reference_character(name)['surfaces']['foot_'+side]*1.5-B;length=T[0]-B[0];rows=[]
 for x in (18.,23.,28.,length-1.):
  band=v[np.abs(v[:,0]-x)<2.5];assert len(band)>3,(name,side,x,len(band))
  lo=band.min(0);hi=band.max(0);rows.append((x,float((lo[1]+hi[1])/2),float((lo[2]+hi[2])/2),max(5.,float((hi[1]-lo[1])/2)+1),max(5.,float((hi[2]-lo[2])/2)+1)))
 rows.append((length+1,rows[-1][1],rows[-1][2],3.,4.));outer=foot_loft(rows)
 inner=[(x,cy,cz,ry-1.8,rz-1.8) for x,cy,cz,ry,rz in rows];inner[0]=(17.5,*inner[0][1:]);inner[-1]=(length,*inner[-1][1:]);inner_volume=foot_loft(inner);assert outer.isValid() and inner_volume.isValid();wall=outer.cut(inner_volume)
 sy=1 if side=='l' else -1;bend=np.array([28,-sy*4.525,14]);end=.9*(T-B);P=(bend+end)/2
 if '--verbose' in sys.argv:print(name,side,'sections',rows,'lug',P.tolist(),flush=True)
 frame,old=world_part(A,own+'_M_forefoot_frame');j=A.joints[own+'.flex'];dry=Assembly(A.profile);w=dry.plate(j,'rotor').moved(j['loc']).translate(tuple(-B));plate=w;start=np.array([14,-sy*4.525,0]);elbow=np.array([26,-sy*4.525,0]);w=union_checked([w,h.rod(start,elbow,2),h.rod(elbow,bend,3),h.rod(bend,end,4)],'forefoot_raised_rail');lug=cube((8,10,14),tuple(P)).intersect(inner_volume);w=fuse_checked(w,lug,'toe_cover_lug')
 # Form bosses by removing them from the cavity before subtracting it.
 # This avoids coincident curved faces in a shell/boss Boolean union.
 shell={};mount_z=(P[2]-4,P[2]+4);x,y=float(P[0]),float(P[1])
 for face,sg in [('left',1),('right',-1)]:
  cavity=inner_volume
  for z in mount_z:cavity=cavity.cut(h.axis_cyl(1,*sorted((y+sg*5.05,y+sg*80)),4,(x,0,z)))
  sh=outer.cut(cavity).intersect(cube((200,200,200),(0,y+sg*100.15,0)))
  sh=sh.cut(h.rod(start,elbow,2.3)).cut(h.rod(elbow,bend,3.3)).cut(h.rod(bend,end,4.3))
  cleat=world_part(A,j['prefix']+'D_output_cleat')[1].translate(tuple(-B))
  for obstruction in (plate,cleat):
   bb=obstruction.BoundingBox();sh=sh.cut(cube((bb.xlen+.6,bb.ylen+.6,bb.zlen+.6),((bb.xmin+bb.xmax)/2,(bb.ymin+bb.ymax)/2,(bb.zmin+bb.zmax)/2)))
  for z in mount_z:
   sh=sh.cut(h.axis_cyl(1,y-85,y+85,1.2,(x,0,z)))
   if face=='left':sh=sh.cut(h.axis_cyl(1,y+10,y+85,2.1,(x,0,z)))
   else:
    loc=cq.Location(cq.Plane(origin=(x,y,z),normal=(0,1,0),xDir=(1,0,0)))
    sh=sh.cut(hexagon(4.2,-85,-8).moved(loc))
  shell[face]=sh
  if '--verbose' in sys.argv:print(name,side,face,'shell',round(sh.Volume(),2),flush=True)
 for i,z in enumerate(mount_z):
  w=w.cut(h.axis_cyl(1,y-6,y+6,1.2,(x,0,z)))
  loc=cq.Location(cq.Plane(origin=(x,y,z),normal=(0,1,0),xDir=(1,0,0)))
  bolt=cyl(-10,10,1).fuse(cyl(10,12,1.9)).cut(hexagon(1.5,10.7,12.1)).moved(loc)
  nut=hexagon(4,-9.6,-8).cut(cyl(-9.7,-7.9,.8)).moved(loc);bn=own+f'_cap_M2x20_{i}';nn=own+f'_cap_nut_M2_{i}'
  A.add(bn,bolt.translate(tuple(B)),'metal',own,'M2x20 cross bolt; two spaced fasteners prevent cap rotation');A.add(nn,nut.translate(tuple(B)),'metal',own,'M2 captured nut, open side pocket');A.thread_pairs.append([bn,nn])
 replace_world(A,frame,w.translate(tuple(B)),frame['note']+'; two spaced cross-holes for removable toe cap','frame')
 for face,sh in shell.items():A.add(own+'_M_toecap_'+face,sh.translate(tuple(B)),'shell',own,'Rigid character-derived toe cap; 1.8 mm wall, toe joint proximal 18 mm left exposed; two M2 fasteners, no deforming skin')
 return dict(side=side,sections_mm=rows,wall_mm=1.8,proximal_open_mm=18.,fasteners='2 x M2x20 + 2 x M2 nuts')

def build(name):
 A,meta=feet.build(name);caps=[add_toe(A,name,s) for s in ('l','r')];return A,dict(meta,toe_caps=caps)

def main():
 out={}
 for name in ('manny','quinn'):
  A,meta=build(name);print(name,'toe assembly built',flush=True);aff={q['name'] for q in A.parts if q['name'].startswith('ball_') and ('_cap_' in q['name'] or '_toecap_' in q['name'] or q['name'].endswith('_M_forefoot_frame'))};cache=CollisionCache(A);checks=[]
  for a in (-20,0,60):
   for d in (-45,0,30):
    for r in (-25,0,25):
     pose={f'{j}_{s}.{k}':v for s in ('l','r') for j,k,v in [('ball','flex',a),('foot','dorsiflex',d),('foot','invert',r)]};review=classify_all(cache.contacts(pose,aff,False),A.parts);bad=[x for x in review if x['classification']=='structural'];checks.append(dict(pose=pose,review=review));print(json.dumps(dict(character=name,angles=[a,d,r],structural=bad[:3],count=len(bad))),flush=True)
  out[name]=dict(meta=meta,checks=checks);h.save(ROOT/'verification/revM_toe_caps_work.json',out)
if __name__=='__main__':main()
