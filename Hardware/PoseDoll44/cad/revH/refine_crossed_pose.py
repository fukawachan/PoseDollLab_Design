"""Refine a modestly asymmetric crossed-arm pose; keep all earlier failures."""
from shoulder_mechanism import *
base={'upperarm_l.flex':65,'upperarm_r.flex':70,'elbow_l.flex':115,'elbow_r.flex':90,'upperarm_l.abduct':-20,'upperarm_r.abduct':-20,'upperarm_l.twist':65,'upperarm_r.twist':35}
adjustments=[{'upperarm_r.flex':75},{'upperarm_l.flex':60},{'upperarm_r.flex':75,'upperarm_l.flex':60},{'upperarm_l.twist':70},{'upperarm_r.twist':30},{'elbow_l.flex':110},{'upperarm_r.flex':75,'upperarm_r.twist':30},{'upperarm_l.flex':60,'upperarm_l.twist':70}]
models={n:build(n) for n in ('manny','quinn')};tested=[];selected=None
for change in adjustments:
 q=base|change;result={}
 for name,(p,parts,meta) in models.items():
  items,_,_=scene(parts,p,q);result[name]=collisions(items)
 tested.append({'pose':q,'hits':result})
 print(json.dumps({'tested':len(tested),'hits':{n:len(v) for n,v in result.items()}}),flush=True)
 if not any(result.values()):selected=q;break
save(ROOT/'verification/revH_crossed_pose_refinement.json',{'tested':tested,'selected':selected,'scope':'Local arms only; final hand and torso pose not validated'})
print(json.dumps({'selected':selected}),flush=True)
