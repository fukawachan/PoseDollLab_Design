"""Reuse exact BRep contacts only when both rigid owners have identical relative poses.
Cache lifetime is one immutable assembly; structural edits invalidate the instance.
"""
from assembly_core import *
class CollisionCache:
 def __init__(self,A):
  self.A=A;self.identity=[(q['name'],id(q['local_shape'])) for q in A.parts];self.cache={};self.evaluated=0;self.reused=0
 def contacts(self,pose,affected=None,skip_same_owner=False):
  assert self.identity==[(q['name'],id(q['local_shape'])) for q in self.A.parts],'Assembly changed after cache construction'
  items=[q for q in self.A.scene(pose) if q.get('role')!='reservation'];T,_=h.fk(self.A.profile,pose);inverses={k:np.linalg.inv(v) for k,v in T.items()};rel={};allow={frozenset(q) for q in self.A.thread_pairs}
  mins=[];maxs=[]
  for q in items:
   bb=q['shape'].BoundingBox();mins.append([bb.xmin,bb.ymin,bb.zmin]);maxs.append([bb.xmax,bb.ymax,bb.zmax])
  mins=np.array(mins);maxs=np.array(maxs);out=[]
  for i,a in enumerate(items):
   c=np.flatnonzero(np.all(np.minimum(maxs[i],maxs[i+1:])-np.maximum(mins[i],mins[i+1:])>1e-5,axis=1))+i+1
   for jj in c:
    b=items[int(jj)];oa,ob=a['owner'],b['owner']
    if affected is not None and not ({a['name'],b['name']}&affected):continue
    if skip_same_owner and oa==ob:continue
    if frozenset((a['name'],b['name'])) in allow:continue
    pair=(oa,ob)
    if pair not in rel:rel[pair]=tuple(np.round(inverses[oa]@T[ob],9).ravel())
    key=(a['name'],b['name'],rel[pair])
    if key in self.cache:v=self.cache[key];self.reused+=1
    else:v=a['shape'].intersect(b['shape']).Volume();self.cache[key]=v;self.evaluated+=1
    if v>.02:out.append(dict(a=a['name'],b=b['name'],owner_a=oa,owner_b=ob,volume_mm3=round(v,4)))
  return out
