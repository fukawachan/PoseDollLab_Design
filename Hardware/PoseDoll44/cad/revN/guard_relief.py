"""Clear the moving shoulder twist tab from a fixed frame lip, retain end stops."""
from pathlib import Path
import sys,json,math,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'cad/revM'))
import final_model as M

def apply(A):
 changes=[]
 for side,sy in [('l',1)]:
  q=next(p for p in A.parts if p['name']==side+'_abduct_ring_and_twist_seat');old=q['local_shape'];S=A.A0[f'upperarm_{side}.twist']['origin']
  loc=M.cq.Location(M.cq.Plane(origin=tuple(S),xDir=(sy,0,0),normal=(0,0,1)))
  # Tab occupies R10.35..12 above Z-10. Preserve all bearing/friction geometry
  # inside R9.5. Stop the relief 0.2 deg before each end sector; preserve its angular faces.
  tool=M.sector(10.15,12.2,-12.2,-9.0,-52.8,142.8).moved(loc).translate(tuple(-A.T0[q['owner']][:3,3]))
  new=old.cut(tool);assert new.isValid() and len(new.Solids())==1
  removed=old.Volume()-new.Volume();assert 0<=removed<old.Volume()*.02,(side,removed,old.Volume())
  protected=M.cyl(-20,10,9.5).moved(loc).translate(tuple(-A.T0[q['owner']][:3,3]));assert old.intersect(protected).Volume()-new.intersect(protected).Volume()<1e-5
  q.update(local_shape=new,note=q['note']+'; Rev N1 local travel-tab relief outside R10.15, protected bearing/friction region R<=9.5 unchanged; original end-stop angular faces retained, strength not rated')
  changes.append(dict(part=q['name'],owner=q['owner'],removed_volume_mm3=removed,original_volume_mm3=old.Volume(),only_subtraction=True,one_valid_solid=True,protected_radius_mm=9.5,nominal_extra_stop_approach_deg=0.0))
 return changes

def main():
 out={}
 for name in ('manny','quinn'):
  A,meta=M.build(name);changes=apply(A);checks=[]
  for side in ('l','r'):
   a=next(p for p in A.parts if p['name']==side+'_abduct_ring_and_twist_seat');b=next(p for p in A.parts if p['name']==side+'_twist_rotor_face')
   for angle in range(-91,92):
    T,_=M.h.fk(A.profile,{f'upperarm_{side}.twist':angle});rel=M.np.linalg.inv(T[a['owner']])@T[b['owner']];hit=a['local_shape'].intersect(M.h.move(b['local_shape'],rel));v=hit.Volume();outside=abs(angle)>90
    checks.append(dict(side=side,angle_deg=angle,volume_mm3=v,outside=outside))
    assert v>.02 if outside else v<.005,(name,side,angle,v)
   print(name,side,'full -90..90 at 1deg plus outside stops PASS',flush=True)
  out[name]=dict(source_sha256=meta['source_sha256'],generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),changes=changes,checks=checks,continuous_sweep_proved=False,physical_tested=False)
  p=R/'verification/revN_guard_relief.json';p.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(name,changes,flush=True)
if __name__=='__main__':main()
