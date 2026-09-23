"""Refresh one independently checked pose after refinement, preserving other cases."""
from shoulder_mechanism import *
def main():
 for name in ('manny','quinn'):
  p,parts,meta=build(name);q=cases()['crossed_clearance_candidate'];items,T,A=scene(parts,p,q);hits=collisions(items);assert not hits
  errors=[]
  for item in items:
   n=item['name'];side=n[0];axis=None
   if side not in ('l','r'):continue
   if '_yaw_bush_' in n or n.endswith('_yaw_shaft'):axis=f'clavicle_{side}.protract'
   elif '_elev_bush_' in n or n.endswith('_elev_shaft'):axis=f'clavicle_{side}.elevate'
   elif '_flex_bush_' in n or n.endswith('_flex_stub'):axis=f'upperarm_{side}.flex'
   elif '_abduct_bush_' in n or '_abduct_stub_' in n:axis=f'upperarm_{side}.abduct'
   elif n.endswith('_twist_bush') or n.endswith('_twist_shaft'):axis=f'upperarm_{side}.twist'
   if axis:errors.append(float(np.linalg.norm(np.cross(np.array(item['shape'].Center().toTuple())-A[axis]['origin'],A[axis]['direction']))))
  assert max(errors)<1e-5
  file=ROOT/f'verification/revH_{name}.json';record=json.loads(file.read_text('utf8'))
  row=next(c for c in record['motion_checks'] if c['pose']=='crossed_clearance_candidate')
  row.update(angles_deg=q,hits=hits,bearing_axis_alignment_max_mm=max(errors),bearing_axis_checks=len(errors))
  record['unit_payload_loads']=[x for x in record['unit_payload_loads'] if x['pose']!='crossed_clearance_candidate']
  for side in ('l','r'):
   target=A[f'hand_{side}.flex']['origin']
   for prefix,axes in [(f'clavicle_{side}',('protract','elevate')),(f'upperarm_{side}',('flex','abduct','twist')),(f'elbow_{side}',('flex',))]:
    for key in axes:
     axis=prefix+'.'+key;item=A[axis]
     value=abs(float(np.dot(item['direction'],np.cross((target-item['origin'])*.001,[0,0,-.1*9.80665]))))
     record['unit_payload_loads'].append({'pose':'crossed_clearance_candidate','axis':axis,'torque_nm_per_100g_at_wrist':value,'sample_has_collision':False})
  save(file,record);print(name+': refined crossing verified',flush=True)
if __name__=='__main__':main()
