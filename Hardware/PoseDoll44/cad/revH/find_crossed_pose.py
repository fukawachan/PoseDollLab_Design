"""Find a physically separated crossed-arm candidate, keeping original failures."""
from shoulder_mechanism import *
import itertools
def point_segment(x,a,b):
 v=b-a;t=np.clip(np.dot(x-a,v)/np.dot(v,v),0,1)
 return float(np.linalg.norm(x-a-t*v))
def segment_distance(a,b,c,d):
 u=b-a;v=d-c;st=np.linalg.lstsq(np.column_stack((u,-v)),c-a,rcond=None)[0]
 vals=[point_segment(a,c,d),point_segment(b,c,d),point_segment(c,a,b),point_segment(d,a,b)]
 if all(0<=x<=1 for x in st):vals.append(float(np.linalg.norm(a+st[0]*u-c-st[1]*v)))
 return min(vals)
models={n:build(n) for n in ('manny','quinn')}
candidates=[]
for lf,rf,le,re,lt,rt in itertools.product((50,65,80,95),(40,55,70),(100,115,130),(90,105,120),(45,65),(35,65)):
 q={'upperarm_l.flex':lf,'upperarm_r.flex':rf,'elbow_l.flex':le,'elbow_r.flex':re,'upperarm_l.abduct':-20,'upperarm_r.abduct':-20,'upperarm_l.twist':lt,'upperarm_r.twist':rt}
 clearance=1000;crossed=True
 for name,(p,parts,meta) in models.items():
  T,A=fk(p,q)
  L=[A[x]['origin'] for x in ('upperarm_l.flex','elbow_l.flex','hand_l.flex')]
  R=[A[x]['origin'] for x in ('upperarm_r.flex','elbow_r.flex','hand_r.flex')]
  crossed &= L[2][1]<0 and R[2][1]>0
  clearance=min(clearance,*(segment_distance(L[i],L[i+1],R[j],R[j+1]) for i in (0,1) for j in (0,1)))
 if crossed and clearance>35:
  cost=abs(lf-65)+abs(rf-65)+.6*(abs(le-115)+abs(re-115))+.35*(abs(lt-60)+abs(rt-60))
  candidates.append((cost,-clearance,q))
candidates.sort(key=lambda x:(x[0],x[1]))
tested=[];selected=None
for cost,clearance,q in candidates[:12]:
 result={}
 for name,(p,parts,meta) in models.items():
  items,_,_=scene(parts,p,q);result[name]=collisions(items)
 tested.append({'pose':q,'minimum_bone_segment_distance_mm':-clearance,'hits':result})
 print(json.dumps({'tested':len(tested),'clearance':-clearance,'hits':{n:len(v) for n,v in result.items()} }),flush=True)
 if not any(result.values()):selected=q;break
save(ROOT/'verification/revH_crossed_pose_search.json',{'coarse_candidates':len(candidates),'tested':tested,'selected':selected,'scope':'Shoulder and arm CAD only; no torso surface, hand or head collision claim'})
print(json.dumps({'selected':selected}),flush=True)
