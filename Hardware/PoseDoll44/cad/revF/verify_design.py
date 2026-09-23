"""Rev F integration audit: numerical CAD checks are not manufacturing release."""
from common import *
from datetime import datetime,timezone

def sources():
 paths=list((ROOT/'cad').rglob('*.py'))+list(HERE.glob('*.html'))
 paths += [ROOT/'tools/Build-RevF.ps1',ROOT/'tools/report_revF.py',ROOT/'electronics/sensor_revB/mechanical_interface.json',ROOT/'mechanical_manifest/print_fit_profile_revB.json',REPO/'Shared/Profiles/virtual_humanoid_44_v1.json',ROOT/'tools/run_cad.py',HERE.parent/'model.py',HERE.parent/'revE/character_reference.py',HERE.parent/'revC/clutch.py',HERE.parent/'build.py',ROOT/'generated/revC/step/sensor_revB.step',ROOT/'verification/revE_proportion_baselines.json']
 paths += [ROOT/'mechanical_manifest'/('physical_'+n+'_44_revE_proportion.json') for n in ('manny','quinn')]
 return {str(p.relative_to(REPO)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths)) if p.exists()}

def begin():
 save(ROOT/'verification/revF_build_start.json',{'utc':datetime.now(timezone.utc).isoformat(),'sources':sources()})
 print('Rev F source snapshot recorded before build.',flush=True)

def registry():
 characters={};ids=None
 for name in ('manny','quinn'):
  path=ROOT/'mechanical_manifest'/('physical_'+name+'_44_revE_proportion.json');profile=json.loads(path.read_text(encoding='utf8'));T,axes=fk(profile,{})
  current=[a['id'] for a in profile['axes']]
  assert len(current)==44 and len(set(current))==44
  if ids is not None:assert ids==current
  ids=current;records=[]
  for spec in profile['axes']:
   aid=spec['id'];prefix=aid.split('.')[0];a=axes[aid]
   if prefix in ('pelvis','waist'):family='L8'
   elif prefix=='chest' or prefix.startswith(('thigh','calf')):family='H6'
   elif prefix.startswith(('upperarm','elbow','foot')):family='M6'
   else:family='S6'
   built=aid in ('elbow_l.flex','hand_l.flex')
   records.append({'id':aid,'node':a['node'],'neutral_axis_point_mm':a['origin'].tolist(),'neutral_axis_direction':a['direction'].tolist(),'limits_deg':np.degrees(spec['limits_rad']).tolist(),'friction_component_candidate':family,'component_size_selection_validated_for_full_body':False,'integration_status':'POPULATED_IN_PARTIAL_LEFT_ARM' if built else 'FRAME_OR_MULTI_AXIS_INTEGRATION_PENDING','reference_axis_line_may_be_offset_for_packaging':False})
  distance=lambda a,b:float(np.linalg.norm(axes[a]['origin']-axes[b]['origin']))
  characters[name]={'source_profile_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'axes':records,'critical_centre_distances_mm':{'clavicle_roots':distance('clavicle_l.protract','clavicle_r.protract'),'shoulder_centres':distance('upperarm_l.flex','upperarm_r.flex'),'hip_centres':distance('thigh_l.flex','thigh_r.flex'),'pelvis_to_waist':distance('pelvis.yaw','waist.yaw'),'waist_to_chest':distance('waist.yaw','chest.yaw')}}
 result={'status':'ALL_44_AXES_TRACKED_PARTIAL_MECHANICAL_INTEGRATION','manufacturing_released':False,'profiles_modified':False,'units':'mm and degrees','characters':characters,'integration_constraints':['Keep the Rev E rotation lines and link dimensions; any future change requires an explicit profile revision and FK comparison.','Use shared frames for shoulder/hip/torso/shoulder-girdle multi-axis joints. Do not stack 44 independent fork fixtures.','Shoulder datum plate in arm STEP is provisional and is not the shoulder joint.','Right-side asymmetric fasteners, sensors and cable routing require a separate mirrored assembly check.']}
 save(ROOT/'mechanical_manifest/dual_character_mechanics_revF.json',result)
 return result

def load_checks(name,arms,pivots):
 from arm_packaging import neutral_arm
 parts,meta=neutral_arm(name);F=meta['forearm_mm'];rows=[]
 neutral=[(p['owner'],mass(p)/1000,np.array(p['shape'].Center().toTuple())) for p in parts]
 # An independent rigid-body moment sum. Gravity direction may vary when the arm is moved at the shoulder.
 for sample in arms['pose_checks']:
  e,w=sample['elbow_deg'],sample['wrist_deg'];er=rotation((0,-1,0),e);wr=rotation((0,-1,0),w);wc=np.array([0.,0.,-F]);moving=[]
  for owner,m,c in neutral:
   if owner=='upperarm':pos=c
   elif owner=='forearm':pos=er@c
   else:pos=er@(wc+wr@(c-wc))
   moving.append((owner,m,pos))
  for label,owners,centre,family in [('elbow',('forearm','hand'),np.zeros(3),'M6'),('wrist',('hand',),er@wc,'S6')]:
   axis=np.array([0.,-1.,0.]);moment=sum((m*(c-centre) for owner,m,c in moving if owner in owners),np.zeros(3))
   bound=9.80665*np.linalg.norm(np.cross(axis,moment))/1000
   upright=abs(float(np.dot(np.cross(moment,np.array([0.,0.,-9.80665])),axis)))/1000
   estimate=pivots['families'][family]['friction_estimate_Nm_mu_0p15']
   rows.append({'joint':label,'elbow_deg':e,'wrist_deg':w,'gravity_torque_upright_Nm':upright,'gravity_torque_any_whole_arm_orientation_bound_Nm':float(bound),'with_1p5_gravity_margin_Nm':float(bound*1.5),'friction_estimate_mu_0p15_Nm':estimate,'estimate_exceeds_partial_load_bound':bool(estimate>=1.5*bound)})
 out={}
 for label in ('elbow','wrist'):
  selected=[r for r in rows if r['joint']==label];worst=max(selected,key=lambda r:r['with_1p5_gravity_margin_Nm'])
  out[label]={'worst_sample':worst,'all_sampled_partial_load_estimates_pass':all(r['estimate_exceeds_partial_load_bound'] for r in selected)}
 return {'scope':'Actual parts in this partial assembly only; no hand, other arm axes, cables, acceleration, human interaction or impact. Friction coefficient and preload are assumptions. No rated payload or measured holding torque is established.','summary':out,'samples':rows}

def main():
 if '--begin' in sys.argv:begin();return
 stamp=json.loads((ROOT/'verification/revF_build_start.json').read_text(encoding='utf8'))
 assert stamp['sources']==sources(),'A source changed during the build. Rebuild sequentially.'
 reports={k:json.loads((ROOT/'verification'/v).read_text(encoding='utf8')) for k,v in [('pivot','revF_pivot_components.json'),('fork','revF_fork_joints.json'),('arm','revF_arm_packaging.json')]}
 for k in ('pivot','fork','arm'):
  assert (ROOT/'verification'/('revF_'+{'pivot':'pivot_components','fork':'fork_joints','arm':'arm_packaging'}[k]+'.json')).stat().st_mtime>=datetime.fromisoformat(stamp['utc']).timestamp(),'Report is older than source snapshot.'
 failures=[];counts={'standalone_component_rotation_samples':0,'complete_fork_rotation_samples':0,'arm_pose_samples':0};printed=[]
 for kind,items in [('pivot',reports['pivot']['families']),('fork',reports['fork']['families']),('arm',reports['arm']['characters'])]:
  for key,r in items.items():
   if r['unplanned_assembly_hits']:failures.append(kind+'/'+key+': assembly overlap')
   samples=r['pose_checks'] if kind=='arm' else r['rotation_samples']
   ck={'pivot':'standalone_component_rotation_samples','fork':'complete_fork_rotation_samples','arm':'arm_pose_samples'}[kind];counts[ck]+=len(samples)
   if any(s['hits'] for s in samples):failures.append(kind+'/'+key+': motion overlap')
   for p in r['parts']:
    if not p['valid'] or p['mass_g']<=0:failures.append(kind+'/'+key+'/'+p['name']+': invalid or empty shape')
    if p['material']=='printed':
     fit=all(v<=180 for v in p['bbox_mm']);single=p['solid_count']==1
     printed.append({'assembly':kind+'/'+key,'name':p['name'],'bbox_mm':p['bbox_mm'],'one_solid':single,'fits_180mm_box_in_recorded_orientation':fit})
     if not fit or not single:failures.append(kind+'/'+key+'/'+p['name']+': print envelope or solid count')
   if kind=='arm':
    for pose in samples:
     if abs(pose['forearm_length_mm']-r['meta']['forearm_mm'])>1e-6:failures.append(key+': forearm length changed')
 reg=registry();loads={n:load_checks(n,reports['arm']['characters'][n],reports['pivot']) for n in ('manny','quinn')}
 result={'status':'DIGITAL_DEVELOPMENT_CHECKS_COMPLETE' if not failures else 'DIGITAL_CHECK_FAILURE','utc':datetime.now(timezone.utc).isoformat(),'source_snapshot_utc':stamp['utc'],'sources':sources(),'manufacturing_released':False,'physical_tested':False,'numeric_intersection_threshold_mm3':.02,'numeric_checks_pass':not failures,'failures':failures,'counts':counts,'printed_part_envelope_checks':printed,'print_scope':'Bounding boxes only. Orientation, support, bridging, slicer settings and real dimensions not validated. Mass uses solid CAD material, not slicer infill.','partial_arm_loads':loads,'remaining':['All-body and all-axis shared-frame integration, right-side assemblies','Continuous clearance, hands/tools/access, hard stops, connector mating and full cable bend envelopes','Shaft finish, wear, lining material, preload tolerance, holding torque, backlash and fatigue validation','Whole-device mass, stand and grip-force calculations','Rev E extreme-neck position error','Quinn UE adapter and real hardware calibration']}
 save(ROOT/'verification/revF_design_audit.json',result)
 print(json.dumps({'checks_pass':not failures,'failures':failures,'sample_counts':counts,'worst_partial_arm_loads':{n:r['summary'] for n,r in loads.items()}},ensure_ascii=False),flush=True)
 if failures:raise SystemExit(1)
if __name__=='__main__':main()
