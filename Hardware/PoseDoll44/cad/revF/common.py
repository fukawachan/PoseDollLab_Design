"""Rev F mechanical geometry utilities. Dimensions mm; material properties provisional."""
from pathlib import Path
import sys,json,math,hashlib,itertools
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];REPO=ROOT.parents[1];OUT=ROOT/'generated/revF'
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(HERE.parent/'revE'))
from model import fk,rotation
from character_reference import reference_character,make_profile
sys.path.insert(0,str(HERE.parent/'revC'))
from build import render
COL={'printed':(.25,.56,.66),'aluminum':(.69,.72,.74),'pom':(.86,.86,.74),'lining':(.54,.31,.13),'spring':(.39,.41,.43),'fastener':(.51,.53,.55),'pcb':(.08,.36,.22),'magnet':(.79,.19,.19),'ptfe_composite':(.61,.58,.37)}
RHO={'printed':1.24,'aluminum':2.70,'pom':1.14,'lining':1.80,'spring':7.85,'fastener':7.85,'pcb':1.9,'magnet':7.5,'ptfe_composite':7.8}
def save(p,data):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def cube(d,c=(0,0,0)):return cq.Workplane('XY').box(*d).translate(c).val()
def rod(a,b,r):
 a=np.array(a);b=np.array(b);v=b-a;return cq.Solid.makeCylinder(r,float(np.linalg.norm(v)),cq.Vector(*a),cq.Vector(*(v/np.linalg.norm(v))))
def cyl(r,z,h):return rod((0,0,z),(0,0,z+h),r)
def ring(ro,ri,z,h):return cyl(ro,z,h).cut(cyl(ri,z-1,h+2))
def hole(s,x,y,r,z0=-30,z1=40):return s.cut(rod((x,y,z0),(x,y,z1),r))
def Dshape(d,flat,z,h):return cyl(d/2,z,h).cut(cube((12,20,h+2),(flat+6,0,z+h/2)))
def matrix(R=np.eye(3),p=(0,0,0)):
 T=np.eye(4);T[:3,:3]=R;T[:3,3]=p;return T
def orient(direction,position=(0,0,0)):
 z=np.array(direction,dtype=float);z/=np.linalg.norm(z);x=np.array([1.,0,0]) if abs(z[0])<.9 else np.array([0,1.,0]);x-=np.dot(x,z)*z;x/=np.linalg.norm(x);return matrix(np.column_stack([x,np.cross(z,x),z]),position)
def move(s,T):return s.moved(cq.Location(cq.Plane(origin=tuple(T[:3,3]),xDir=tuple(T[:3,0]),normal=tuple(T[:3,2]))))
def shape_record(name,s,material,owner,group,note='',**kwargs):
 if not s.isValid():raise ValueError('Invalid: '+name)
 return dict(name=name,shape=s,material=material,owner=owner,group=group,note=note,**kwargs)
def pair_hits(parts,skip_same_owner=False,tolerance=.02):
 boxes=[p['shape'].BoundingBox() for p in parts];hits=[]
 for i,a in enumerate(parts):
  for j in range(i+1,len(parts)):
   b=parts[j]
   if skip_same_owner and a['owner']==b['owner']:continue
   aa,bb=boxes[i],boxes[j]
   if not all(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
   v=a['shape'].intersect(b['shape']).Volume()
   if v>tolerance:hits.append({'a':a['name'],'b':b['name'],'mm3':round(v,5),'same_owner':a['owner']==b['owner']})
 return hits
def mass(p):return 2.2 if p['material']=='pcb' else p['shape'].Volume()*RHO[p['material']]/1000
