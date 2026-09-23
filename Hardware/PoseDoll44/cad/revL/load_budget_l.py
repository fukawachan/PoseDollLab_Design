"""Assumption-driven gravity budget, explicitly not a tested load rating."""
from flex_encoder import *
SPRING=k.SPRING
RHO={'frame':1.24,'shell':1.24,'metal':7.85,'fastener':7.85,'spring':7.85,'bush':1.41,'lining':1.30,'thrust':7.85,'aluminum':2.70,'brass':8.50,'nylon':1.14,'magnet':7.50,'pcb':1.85,'pcb_component':3.0,'titanium':4.43}
def main():
 results={}
 reff=(2/3)*(12.5**3-4.15**3)/(12.5**2-4.15**2)
 for name in ('manny','quinn'):
  p,parts,meta=build(name)
  data=json.loads((ROOT/f'verification/revL_{name}.json').read_text('utf8'))
  parents={n['id']:n['parent'] for n in p['nodes']}
  def follows(owner,node):
   while owner is not None:
    if owner==node:return True
    owner=parents[owner]
   return False
  massparts=[]
  for q in parts:
   if q['role']=='reservation':continue
   massparts.append(dict(name=q['name'],owner=q['owner'],mass_kg=q['local_shape'].Volume()*RHO[q['material']]*1e-6,
    com_local_mm=np.array(q['local_shape'].Center().toTuple())))
  samples=[]
  for c in data['motion_checks']:
   if c['hits']:continue
   T,A=h.fk(p,c['angles_deg'])
   for side in ('l','r'):
    wrist=A[f'hand_{side}.flex']['origin']*.001
    for key,node in [('flex',f'upperarm_{side}.flex_frame'),('abduct',f'upperarm_{side}.abduct_frame')]:
     aid=f'upperarm_{side}.{key}';axis=A[aid];origin=axis['origin']*.001
     moving=[q for q in massparts if follows(q['owner'],node)]
     moment=np.zeros(3)
     for q in moving:
      com=(T[q['owner']]@np.r_[q['com_local_mm'],1])[:3]*.001
      moment+=q['mass_kg']*(com-origin)
     added=.1*(wrist-origin);direction=axis['direction']
     upright=abs(float(np.dot(direction,np.cross(moment+added,[0,0,-9.80665]))))
     anygravity=9.80665*float(np.linalg.norm(np.cross(direction,moment+added)))
     samples.append(dict(pose=c['pose'],axis=aid,moving_model_mass_g=1000*sum(q['mass_kg'] for q in moving),
      modeled_only_any_gravity_Nm=9.80665*float(np.linalg.norm(np.cross(direction,moment))),
      modeled_plus_100g_wrist_upright_Nm=upright,modeled_plus_100g_wrist_any_gravity_Nm=anygravity))
  peak=max(samples,key=lambda x:x['modeled_plus_100g_wrist_any_gravity_Nm'])
  results[name]=dict(peak=peak,samples=samples,
   force_required_N_at_mu_0p15_margin_1p5=1.5*peak['modeled_plus_100g_wrist_any_gravity_Nm']/(.15*reff*.001))
 result=dict(status='ASSUMPTION_BUDGET_NOT_LOAD_RATING',densities_g_cm3_assumed=RHO,
  assumptions=['Printed geometry treated as solid PLA, not a slicer mass','Inherited metal geometry treated as steel; new hubs/journals and flex stop caps as aluminum, new button screws as titanium, radial screws/standoffs as brass; materials unqualified',
   'Unmodeled hand/wrist provision is a 100g point at wrist, not a measured part','PCB components approximated at 3.0 g/cm3; not supplier weights','Reservation volumes omitted',
   'No cable return force, dynamic load, contact force, wear, creep or tolerances','Any-gravity bound covers arbitrary gravity direction at sampled pose; not a torso assembly check'],
  friction_effective_radius_mm=reff,force_catalog_N=SPRING['catalog_force_N'],
  friction_torque_estimate_Nm_by_assumed_mu={str(mu):mu*SPRING['catalog_force_N']*reff*.001 for mu in (.08,.15,.25)},
  preload_force_validation='Not measured; force assumes catalog test height and ideal stack',
  variants=results)
 h.save(ROOT/'verification/revL_load_budget.json',result)
 print(json.dumps({name:r['peak']|{'force_required_N_at_mu_0p15_margin_1p5':r['force_required_N_at_mu_0p15_margin_1p5']} for name,r in results.items()}),flush=True)
if __name__=='__main__':main()
