"""Shared CAD placement and mounting helpers for the full-body continuation."""
from compact_axis import *
from dataclasses import dataclass

class Assembly:
 def __init__(self,p,parts=None):
  self.profile=p;self.T0,self.A0=h.fk(p,{});self.parts=list(parts or []);self.channels=[];self.thread_pairs=[];self.joints={}
 def add(self,name,shape,material,owner,note='',role='candidate_solid'):
  assert shape.isValid() and len(shape.Solids())==1,(name,len(shape.Solids()))
  part=dict(name=name,local_shape=shape.translate(tuple(-self.T0[owner][:3,3])),material=material,owner=owner,role=role,note=note)
  self.parts.append(part);return part
 def joint(self,axis,size,normal,xdir,offset=0,board_rotation=0):
  node=next(n for n in self.profile['nodes'] if n.get('axis_id')==axis);fixed=node['parent'];rotor=node['id']
  A=self.A0[axis];origin=A['origin']+np.array(normal)*offset
  loc=cq.Location(cq.Plane(origin=tuple(origin),xDir=tuple(xdir),normal=tuple(normal)))
  items,meta=module(size,board_rotation);prefix=axis.replace('.','_')+'_M_'
  for q in items:self.add(prefix+q['name'],q['shape'].moved(loc),q['material'],fixed if q['owner']=='fixed' else rotor,q['note'],q['role'])
  self.thread_pairs += [[prefix+n for n in pair] for pair in meta['intended_thread_pairs']]
  self.channels.append(dict(axis_id=axis,kind='AS5048A_direct',fixed_owner=fixed,magnet_owner=rotor,origin_neutral_mm=origin.tolist(),normal_neutral=list(normal),xdir_neutral=list(xdir),geometric_sign=float(np.dot(A['direction'],normal)),magnet_face_mm=meta['magnet_face_mm'],package_face_mm=meta['package_face_mm'],gap_mm=meta['gap_mm'],family=size,board_rotation_deg=board_rotation,calibrated=False))
  entry=dict(axis=axis,size=size,fixed=fixed,rotor=rotor,loc=loc,origin=origin,meta=meta,prefix=prefix)
  self.joints[axis]=entry;return entry
 def plate(self,joint,which):
  """Fixed carrier fastens onto outer eye face; rotor carrier onto D cleat.
  M3 screws never put a head between the rotating cleat and stationary eye.
  """
  j=joint;meta=j['meta'];points=meta['fixed_mounts_mm'] if which=='fixed' else meta['rotor_mounts_mm'];x=points[0][0]
  a,b=(4,8) if which=='fixed' else (-12.05,-8.05);owner=j[which];name=j['prefix']+which
  plate=cube((12 if which=='fixed' else 16,20,b-a),(x,0,(a+b)/2))
  if which=='fixed':plate=plate.cut(cube((5.5,4,6),(x-3.25,0,6)))
  for i,(_,y,_) in enumerate(points):
   plate=plate.cut(cyl(a-.1,b+.1,1.7).translate((x,y,0)))
   if which=='fixed':
    bolt=screw(b,8)
    self.add(name+'_mount_M3x8_'+str(i),bolt.translate((x,y,0)).moved(j['loc']),'metal',owner,'M3x8 from outer carrier face into metal eye; 3 mm nominal threaded engagement')
    self.thread_pairs.append([name+'_mount_M3x8_'+str(i),j['prefix']+'fixed_metal_eye'])
   else:
    bolt=cyl(a,a+12,1.5).fuse(cyl(a-3,a,2.75)).cut(hexagon(2.5,a-3.1,a-1.5))
    nutbase=-3.05;nut=hexagon(5.5,nutbase,nutbase+2.4).cut(cyl(nutbase-.1,nutbase+2.5,1.25))
    self.add(name+'_mount_M3x12_'+str(i),bolt.translate((x,y,0)).moved(j['loc']),'metal',owner,'M3x12 socket screw; unmodelled helical thread')
    self.add(name+'_mount_nut_M3_'+str(i),nut.translate((x,y,0)).moved(j['loc']),'metal',owner,'M3 nut envelope; removable thread locking method pending')
    self.thread_pairs.append([name+'_mount_M3x12_'+str(i),name+'_mount_nut_M3_'+str(i)])
  return plate
 def add_local(self,j,which,name,shape):return self.add(j['prefix']+name,shape.moved(j['loc']),'frame',j[which],'PLA candidate with explicit mount pads; print fit and fatigue untested')
 def scene(self,pose):return h.scene(self.parts,self.profile,pose)[0]


def connected(shapes):
 s=h.union(shapes)
 assert s.isValid() and len(s.Solids())==1,len(s.Solids())
 return s

def hollow_between(a,b,outer=6,wall=2):
 d=np.array(b)-a;u=d/np.linalg.norm(d)
 return h.rod(a,b,outer).cut(h.rod(np.array(a)-u*.1,np.array(b)+u*.1,outer-wall))


def fast_contacts(items,allowed=(),affected=None,skip_same_owner=False):
 """Exact BRep intersection following vectorized AABB broad phase. No mesh collision."""
 items=[q for q in items if q.get('role')!='reservation'];mins=[];maxs=[]
 for q in items:
  bb=q['shape'].BoundingBox();mins.append([bb.xmin,bb.ymin,bb.zmin]);maxs.append([bb.xmax,bb.ymax,bb.zmax])
 mins=np.array(mins);maxs=np.array(maxs);allow={frozenset(x) for x in allowed};out=[]
 for i,a in enumerate(items):
  c=np.flatnonzero(np.all(np.minimum(maxs[i],maxs[i+1:])-np.maximum(mins[i],mins[i+1:])>1e-5,axis=1))+i+1
  for jj in c:
   b=items[int(jj)]
   if affected is not None and not ({a['name'],b['name']}&affected):continue
   if skip_same_owner and a['owner']==b['owner']:continue
   if frozenset((a['name'],b['name'])) in allow:continue
   v=a['shape'].intersect(b['shape']).Volume()
   if v>.02:out.append(dict(a=a['name'],b=b['name'],owner_a=a['owner'],owner_b=b['owner'],volume_mm3=round(v,4)))
 return out


def fuse_checked(a,b,label='frame_union'):
 """Guard against a valid-looking Boolean result silently losing an input body."""
 av,bv=a.Volume(),b.Volume();out=a.fuse(b)
 if out.Volume()+.01<max(av,bv):
  raise ValueError((label,'union_lost_volume',av,bv,out.Volume()))
 lost_a=a.cut(out).Volume();lost_b=b.cut(out).Volume()
 if max(lost_a,lost_b)>.02:raise ValueError((label,'union_lost_input',lost_a,lost_b))
 return out

def union_checked(parts,label='frame_union'):
 out=parts[0]
 for i,b in enumerate(parts[1:]):out=fuse_checked(out,b,label+'_'+str(i))
 return out
