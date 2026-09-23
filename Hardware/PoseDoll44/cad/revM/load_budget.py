"""Full-body gravity budget and conservative frame screening; no rated capacity."""
from final_model import *
RHO={'peek':1.31,'steel_17_4':7.75,'silicone':1.15,'frame':1.24,'shell':1.24,'metal':7.85,'fastener':7.85,'spring':7.85,'bush':1.41,'pom':1.41,'lining':1.30,'thrust':7.85,'aluminum':2.70,'aluminum_7075':2.81,'brass':8.50,'nylon':1.14,'magnet':7.50,'pcb':1.85,'pcb_component':3.0,'titanium':4.43,'ptfe_composite':4.0,'bronze':8.80}

def budget(A,harness=None):
 parents={n['id']:n['parent'] for n in A.profile['nodes']}
 def downstream(owner,node):
  while owner is not None:
   if owner==node:return True
   owner=parents[owner]
  return False
 masses=[]
 for q in A.parts:
  if q['role']=='reservation':continue
  rho=RHO[q['material']];s=q['local_shape'];m=q.get('mass_kg_override',s.Volume()*rho/1e6)
  masses.append(dict(name=q['name'],owner=q['owner'],kg=m,local_com_mm=list(s.Center().toTuple()),material=q['material']))
 # Covers and six populated node boards are now included in the CAD model.
 # Only cabling, restraint clips and labels retain a named provisional budget.
 additions=[('chest',.040,[0,0,40]),('pelvis',.035,[0,0,-15]),('head',.006,[0,0,35])]
 for side in ('l','r'):
  for owner,end,m in [(f'upperarm_{side}',f'elbow_{side}',.016),(f'forearm_{side}',f'hand_{side}',.013),(f'thigh_{side}',f'calf_{side}',.020),(f'calf_{side}',f'foot_{side}',.015),(f'foot_{side}',f'ball_{side}',.005)]:
   com=(A.T0[end][:3,3]-A.T0[owner][:3,3])*.5;additions.append((owner,m,com.tolist()))
 provisional=[dict(name='HARNESS_ALLOWANCE_'+o,owner=o,kg=m,local_com_mm=c,material='allowance') for o,m,c in additions]
 if harness is not None:provisional=harness['mass_lumps']
 from full_body_audit import poses
 cases,_=poses(A)
 for yaw in (-70,0,70):
  for pitch in (-45,0,55):
   for roll in (-35,0,35):cases[f'head_{yaw}_{pitch}_{roll}']={'head.yaw':yaw,'head.pitch':pitch,'head.roll':roll}
 result=[]
 sources=dict(A.joints)
 for n in A.profile['nodes']:
  axis=n.get('axis_id','')
  if not axis or axis.startswith('pelvis.') or axis in sources:continue
  known=axis.startswith('upperarm_') and axis.rsplit('.',1)[-1] in ('flex','abduct')
  reff=2/3*(12.5**3-4.15**3)/(12.5**2-4.15**2)
  sources[axis]=dict(rotor=n['id'],size='RevL_shoulder' if known else 'preload_not_yet_designed',meta=dict(nominal_torque_Nm=.15*552*reff/1000 if known else None))
 for axis,j in sources.items():
  owners=[m for m in masses+provisional if downstream(m['owner'],j['rotor'])];worst=None
  for label,pose in cases.items():
   T,axes=h.fk(A.profile,pose);origin=axes[axis]['origin'];n=axes[axis]['direction'];moment=np.zeros(3)
   for m in owners:
    c=T[m['owner']][:3,:3]@m['local_com_mm']+T[m['owner']][:3,3];moment+=m['kg']*(c-origin)/1000
   torque=9.80665*np.linalg.norm(np.cross(n,moment));full=9.80665*np.linalg.norm(moment)
   if worst is None or torque>worst['worst_case_torque_Nm']:worst=dict(pose=label,worst_case_torque_Nm=float(torque),full_vector_moment_Nm=float(full))
  nominal=j['meta']['nominal_torque_Nm'];result.append(dict(axis=axis,family=j['size'],downstream_mass_kg=sum(m['kg'] for m in owners),nominal_clutch_Nm=nominal,clutch_margin=nominal/max(worst['worst_case_torque_Nm'],1e-8) if nominal is not None else None,**worst))
 return dict(pose_count=len(cases),model_mass_kg=sum(m['kg'] for m in masses),allowance_mass_kg=sum(m['kg'] for m in provisional),allowances=provisional,parts=masses,axes=result,notes=['Any gravity direction bound at sampled relative poses, includes named provisional mass allowances.','No acceleration, squeezing, cable spring force, impact, friction variability, fatigue or creep rating.','Simple frame stress screening must precede assigning structural material; geometric collision clearance is not a strength result.'])

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  print('Load model',name,flush=True);A,meta=build(name);print('Load calculation',name,len(A.parts),flush=True);harness=json.loads((ROOT/f'harness/{name}_revM.json').read_text(encoding='utf-8'));b=budget(A,harness);b['source_cad_sha256']=meta['source_sha256'];b['source_harness_sha256']=hashlib.sha256((ROOT/f'harness/{name}_revM.json').read_bytes()).hexdigest();out[name]=b;h.save(ROOT/'verification/revM_load_work.json',out)
  print(json.dumps(dict(character=name,model_mass_kg=b['model_mass_kg'],allowance_mass_kg=b['allowance_mass_kg'],lowest_clutch_margins=sorted([a for a in b['axes'] if a['clutch_margin'] is not None],key=lambda a:a['clutch_margin'])[:10])),flush=True)
 h.save(ROOT/'verification/revM_load_work.json',out)
if __name__=='__main__':main()
