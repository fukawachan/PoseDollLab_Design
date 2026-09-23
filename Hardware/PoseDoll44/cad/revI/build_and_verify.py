from shoulder_integration import *
import hashlib
from collision_policy import classify_hit

def poses_all():
 out=dict(h.cases())
 # Boundary samples preserve original limits. They are extra evidence, not continuous clearance.
 for label,angles in [('flex',[-50,-25,0,45,90,135,160]),('abduct',[-30,0,30,60,90,120,150]),('twist',[-90,-60,-30,0,30,60,90])]:
  for deg in angles:
   key=f'scan_{label}_{deg}'
   candidate={f'upperarm_{s}.{label}':deg for s in ('l','r') if deg!=0}
   if candidate not in out.values():out[key]=candidate
 return out

def main():
 for name in ('manny','quinn'):
  p,parts,meta=build(name);folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
  neutral,T0,A0=h.scene(parts,p,{})
  assy=cq.Assembly(name=name+'_RevI_shoulder_assembly');rows=[]
  for item in neutral:
   sh=item['shape'];bb=sh.BoundingBox()
   assy.add(sh,name=item['name'],color=cq.Color(*COL[item['material']]))
   rows.append({k:v for k,v in item.items() if k not in ('shape','local_shape')}|
    {'valid':sh.isValid(),'solids':len(sh.Solids()),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen],'volume_mm3':sh.Volume()})
   if '_clutch_' in item['name'] or item['name'] in meta['changed_frames']:
    cq.exporters.export(sh,str(folder/(item['name']+'.step')))
  assy.save(str(folder/(name.title()+'_shoulder_assembly.step')))
  checks=[]
  for label,q in poses_all().items():
   current,T,A=h.scene(parts,p,q);hits=h.collisions(current)
   # Actual cylindrical journal/bush features already constructed on these axis lines.
   # Keep numerical checks for symmetric bearing sleeves; eccentric flanged shafts do not use COM.
   errors=[]
   for item in current:
    n=item['name'];side=n[0]
    if side not in ('l','r'):continue
    axis=None
    if '_yaw_bush_' in n:axis=f'clavicle_{side}.protract'
    elif '_elev_bush_' in n:axis=f'clavicle_{side}.elevate'
    elif '_flex_bush_' in n or n==side+'_flex_clutch_radial_bush':axis=f'upperarm_{side}.flex'
    elif '_abduct_bush_' in n or n==side+'_abduct_clutch_radial_bush':axis=f'upperarm_{side}.abduct'
    elif n.endswith('_twist_bush'):axis=f'upperarm_{side}.twist'
    if axis:
     off=np.array(item['shape'].Center().toTuple())-A[axis]['origin']
     errors.append(float(np.linalg.norm(np.cross(off,A[axis]['direction']))))
   assert max(errors)<1e-5
   check=dict(pose=label,angles_deg=q,hits=hits,bearing_axis_alignment_max_mm=max(errors),bearing_axis_checks=len(errors))
   checks.append(check)
   owners={r['name']:r['owner'] for r in rows}
   local=sum(classify_hit(x,owners)['classification']=='structural' for x in hits)
   print(json.dumps(dict(character=name,pose=label,structural=local,pose_contacts=len(hits)-local,first=hits[:2])),flush=True)
  # New components are also checked against parts with the SAME FK owner, once in neutral.
  # Existing untouched same-owner joins are outside this focused audit.
  audit=[]
  for i,a in enumerate(neutral):
   for b in neutral[i+1:]:
    if a['owner']!=b['owner']:continue
    if a['role']=='reservation' or b['role']=='reservation':continue
    if '_clutch_' not in a['name'] and '_clutch_' not in b['name']:continue
    aa=a['shape'].BoundingBox();bb=b['shape'].BoundingBox()
    if not all(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
    v=a['shape'].intersect(b['shape']).Volume()
    if v<=.02:continue
    pa=a['name'].split('_clutch_');pb=b['name'].split('_clutch_')
    allowed=len(pa)==len(pb)==2 and pa[0]==pb[0] and intentional_threads(pa[1],pb[1])
    audit.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4),intentional_thread=allowed))
  loads=[]
  # Unit wrist load only, unchanged definition from Rev H.
  for check in checks:
   _,A=h.fk(p,check['angles_deg'])
   for side in ('l','r'):
    target=A[f'hand_{side}.flex']['origin']
    for key in ('flex','abduct'):
     axis=f'upperarm_{side}.{key}';at=A[axis]
     value=abs(float(np.dot(at['direction'],np.cross((target-at['origin'])*.001,[0,0,-.980665]))))
     loads.append(dict(pose=check['pose'],axis=axis,torque_nm_per_100g_at_wrist=value))
  record=classify_checks(dict(meta=meta,parts=rows,motion_checks=checks,new_same_owner_assembly_contacts=audit,
   unexpected_new_assembly_contacts=[x for x in audit if not x['intentional_thread']],
   unit_payload_loads=loads,unit_payload_note='100g at wrist; excludes real assembly mass, hand forces and torso tilt; not a holding rating',
   neutral_reservation_contacts=[x for x in h.collisions(neutral,True) if x['reservation_involved']],
   manufacturing_released=False,physical_tested=False))
  h.save(ROOT/f'verification/revI_{name}.json',record)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in neutral if q['role']!='reservation'],folder/'neutral.png',name.title()+' | Rev I shoulder holding integration',camera=(1000,-1500,600))
  print(json.dumps(dict(character=name,assembly_unexpected=record['unexpected_new_assembly_contacts'])),flush=True)
if __name__=='__main__':main()
