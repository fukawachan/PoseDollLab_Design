from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'cad/revM'))
import final_model as M
out={}
for name in ('manny','quinn'):
 A,meta=M.build(name);pose={'upperarm_l.flex':-50,'upperarm_l.abduct':10,'upperarm_l.twist':45,'elbow_l.flex':75,'upperarm_r.flex':-50,'upperarm_r.abduct':10,'upperarm_r.twist':45,'elbow_r.flex':75};rows=[]
 for side in ('l','r'):
  a=next(p for p in A.parts if p['name']==side+'_abduct_ring_and_twist_seat');b=next(p for p in A.parts if p['name']==side+'_twist_rotor_face')
  for angle in (0,15,30,45,60,75,90):
   current=pose|{f'upperarm_{side}.twist':angle};T,_=M.h.fk(A.profile,current);relative=M.np.linalg.inv(T[a['owner']])@T[b['owner']]
   for method,sa,sb in [('local',a['local_shape'],M.h.move(b['local_shape'],relative)),('world',M.h.move(a['local_shape'],T[a['owner']]),M.h.move(b['local_shape'],T[b['owner']]))]:
    hit=sa.intersect(sb);vol=hit.Volume();solids=hit.Solids();bb=hit.BoundingBox() if solids else None
    row=dict(side=side,angle=angle,method=method,volume_mm3=vol,valid=hit.isValid(),solids=len(solids),bounds_mm=[bb.xlen,bb.ylen,bb.zlen] if bb else None);rows.append(row);print(name,json.dumps(row),flush=True)
 out[name]=dict(source_sha256=meta['source_sha256'],checks=rows)
 (R/'verification/revN_twist_contact_precision.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
