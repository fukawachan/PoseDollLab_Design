"""Reusable concentric two-axis frames and distal axial twist links.
Offsets are ONLY along each axis line. No anatomical pivot or bone length moves.
"""
from assembly_core import *

def yx_pair(A,flex_id,side_id,sy,size):
 ro=SPECS[size]['ro'];rf=2*ro+4;rd=ro+3
 f=A.joint(flex_id,size,(0,sy,0),(0,0,-1),rf,board_rotation=90 if size.startswith('H6') else 0)
 d=A.joint(side_id,size,(1,0,0),(0,0,1),rd,board_rotation=90)
 O=A.A0[flex_id]['origin'];assert np.linalg.norm(O-A.A0[side_id]['origin'])<1e-6
 frame=A.plate(f,'rotor').moved(f['loc']).fuse(A.plate(d,'fixed').moved(d['loc']))
 pts=[O+np.array(v) for v in [(0,sy*(rf-11),ro+3),(0,sy*(rf-11),ro+13),(-ro-5,sy*(rf-11),ro+15),(-ro-5,0,ro+15),(rd+6,0,ro+15)]]
 for a,b in zip(pts,pts[1:]):frame=frame.fuse(h.rod(a,b,2.5))
 A.add(f['prefix']+'intermediate_frame',frame,'aluminum_7075' if size.startswith('H6') else 'frame',f['rotor'],'Bolted frame between concentric orthogonal axes; no offset of anatomical pivot')
 return f,d

def distal_twist(A,upstream,axis_id,size):
 ro=SPECS[size]['ro'];off=-(2*ro+48);rd=ro+3;O=A.A0[axis_id]['origin']
 t=A.joint(axis_id,size,(0,0,1),(1,0,0),off,board_rotation=0)
 frame=A.plate(upstream,'rotor').moved(upstream['loc']).fuse(A.plate(t,'fixed').moved(t['loc']))
 pts=[O+np.array(v) for v in [(rd-11,0,-ro-3),(rd-11,0,-ro-13),(ro+14,0,-ro-13),(ro+14,0,off+6)]]
 for a,b in zip(pts,pts[1:]):frame=frame.fuse(h.rod(a,b,2.5))
 A.add(t['prefix']+'axial_carrier',frame,'aluminum_7075' if size.startswith('H6') else 'frame',t['fixed'],'Twist cartridge translated along the original axial line; bolt-on carrier beneath the orthogonal pair')
 return t

def distal_stem(A,j):
 sh=A.plate(j,'rotor');rx=j['meta']['rotor_mounts_mm'][0][0]
 sh=sh.fuse(cube((abs(rx)+6,12,8),(rx/2,0,-15.5))).fuse(cube((12,10,22),(0,0,-25)))
 for _,y,_ in j['meta']['rotor_mounts_mm']:sh=sh.cut(cyl(-30,-8,3).translate((rx,y,0)))
 return sh.moved(j['loc'])

def hinge_upper(A,j,end_x):
 """The proximal beam returns to the centre plane at +50 mm for deep flexion."""
 xp=j['meta']['fixed_mounts_mm'][0][0];sh=A.plate(j,'fixed')
 sh=sh.fuse(cube((50-xp,12,4),((50+xp)/2,0,6)))
 sh=sh.fuse(cube((12,12,17),(50,0,-.5)))
 sh=sh.fuse(cube((end_x-50,12,10),((end_x+50)/2,0,-5.525)))
 if end_x>58:sh=sh.cut(cube((end_x-56,8,6),((end_x+56)/2,0,-5.525)))
 for _,y,_ in j['meta']['fixed_mounts_mm']:sh=sh.cut(cyl(-4,13,1.7).translate((xp,y,0)))
 return sh.moved(j['loc'])

def hinge_lower(A,j,length):
 sh=A.plate(j,'rotor');rx=j['meta']['rotor_mounts_mm'][0][0]
 sh=sh.fuse(cube((11,12,10),(rx-11,0,-7.05)))
 sh=sh.fuse(cube((length+rx-10,12,10),((-length+rx-10)/2,0,-5.525)))
 if length>45:sh=sh.cut(cube((length-40,8,6),((-length-40)/2,0,-5.525)))
 return sh.moved(j['loc'])

def proximal_yx(A,j,root,height):
 ro=SPECS[j['size']]['ro'];rf=2*ro+4;sy=1 if j['origin'][1]>=A.A0[j['axis']]['origin'][1] else -1
 O=A.A0[j['axis']]['origin'];sh=A.plate(j,'fixed').moved(j['loc']);branches=[]
 for x in (-6,6):
  pts=[O+np.array(v) for v in [(x,sy*(rf+6),-ro-15),(-ro-9,sy*(rf+6),-ro-15),(-ro-9,sy*(rf+6),height-5),list(np.array(root)-O)]]
  for a,b in zip(pts,pts[1:]):sh=sh.fuse(h.rod(a,b,3));branches.append((a,b))
 return sh,branches
