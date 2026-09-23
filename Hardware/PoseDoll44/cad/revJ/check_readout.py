"""Concentricity / sign consistency and honest packaging probes for missing axes."""
from shoulder_revision import *
from assembly_audit import pairs
from build_and_verify import poses_all

def main():
 result={'physical_sensor_tested':False,'raw_sensor_sign_calibrated':False,'channels':{},'remaining_axis_probes':[],
  'probe_scope':'Actual Rev B PCB only at a straight axial continuation; no holder. A failed probe rejects this placement, not all possible designs.'}
 for name in ('manny','quinn'):
  p,parts,meta=build(name);T0,A0=h.fk(p,{})
  channels=[]
  for label,angles in poses_all().items():
   check=dict(pose=label,angles_deg=angles)
   T,A=h.fk(p,check['angles_deg'])
   for c in meta['sensor_channels']:
    loc=previous.frame_transform(c['module_normal_neutral'],c['module_xdir_neutral'],c['module_origin_neutral_mm'])
    # Extract basis directly from the frame construction (not CAD COM).
    z=np.array(c['module_normal_neutral'],float);x=np.array(c['module_xdir_neutral'],float);y=np.cross(z,x)
    B0=np.eye(4);B0[:3,:3]=np.column_stack((x,y,z));B0[:3,3]=c['module_origin_neutral_mm']
    fixed=T[c['fixed_owner']]@np.linalg.inv(T0[c['fixed_owner']])@B0
    rotor=T[c['magnet_owner']]@np.linalg.inv(T0[c['magnet_owner']])@B0
    rel=np.linalg.inv(fixed)@rotor
    geom=math.degrees(math.atan2(rel[1,0],rel[0,0]))
    expected=c['geometric_angle_sign']*check['angles_deg'].get(c['axis_id'],0)
    err=(geom-expected+180)%360-180
    magnet=(rotor@np.array([0,0,MAGNET_TOP,1]))[:3]
    package=(fixed@np.array([0,0,PCB_DATUM-2.595,1]))[:3]
    difference=package-magnet;normal=fixed[:3,2]
    lateral=float(np.linalg.norm(np.cross(difference,normal)));gap=float(np.dot(difference,normal))
    assert abs(err)<1e-6 and lateral<1e-5 and abs(gap-PACKAGE_GAP)<1e-5
    channels.append(dict(pose=check['pose'],axis_id=c['axis_id'],geometric_angle_deg=geom,expected_deg=expected,
     angle_error_deg=err,lateral_axis_error_mm=lateral,package_face_gap_mm=gap))
  result['channels'][name]=channels
  pcb=cq.importers.importStep(str(ROOT/'generated/revC/step/sensor_revB.step')).val().rotate((0,0,0),(1,0,0),180)
  for side,sy in [('l',1),('r',-1)]:
   S=A0[f'upperarm_{side}.flex']['origin']
   for axis,normal,xd,datum,owner in [
    ('flex',(0,-sy,0),(1,0,0),70.395,f'clavicle_{side}'),
    ('twist',(0,0,1),(1,0,0),22.895,f'upperarm_{side}.abduct_frame')]:
    loc=previous.frame_transform(normal,xd,S)
    sh=pcb.translate((0,0,datum)).moved(loc).translate(tuple(-T0[owner][:3,3]))
    checks=[]
    for pose in ('neutral','arms_forward','arms_side','arms_overhead','forehead','crossed_clearance_candidate'):
     items,T,A=h.scene(parts,p,h.cases()[pose]);probe=h.move(sh,T[owner]);bb=probe.BoundingBox();hits=[]
     for q in items:
      if q['role']=='reservation':continue
      b=q['shape'].BoundingBox()
      if not all(min(getattr(bb,k+'max'),getattr(b,k+'max'))-max(getattr(bb,k+'min'),getattr(b,k+'min'))>1e-4 for k in 'xyz'):continue
      vol=probe.intersect(q['shape']).Volume()
      if vol>.02:hits.append(dict(part=q['name'],volume_mm3=round(vol,4)))
     checks.append(dict(pose=pose,hits=hits))
    result['remaining_axis_probes'].append(dict(character=name,axis_id=f'upperarm_{side}.{axis}',board_datum_from_axis_mm=datum,
     normal_neutral=list(normal),fixed_owner=owner,accepted=False,status='rejected_straight_placement' if any(q['hits'] for q in checks) else 'clear_samples_but_no_mount_design',
     checks=checks))
 module=make_encoder()
 fixed=fixed_support()
 rows=[dict(q,role='reservation' if q['owner']=='reservation' else 'sensor_candidate') for q in module]
 rows.append(dict(name='support',shape=fixed,owner='fixed',role='sensor_candidate'))
 sweeps=[]
 for angle in range(-30,151,15):
  rotated=[dict(q,shape=q['shape'].rotate((0,0,0),(0,0,1),angle)) if q['owner']=='rotor' else q for q in rows]
  hits=h.collisions(rotated)
  assert not hits,hits
  sweeps.append(dict(angle_deg=angle,unexpected_hits=hits))
 result['isolated_encoder_rotation_checks']=sweeps
 result['unclamped_D_fit']={'assumption':'Centered shaft, rigid nominal section only. Ignores translation, flange slip and elastic clamp closure.',
  'old_print_socket_total_deg':2*math.degrees(math.acos(2.5/3)-math.acos(2.6/3)),
  'new_metal_socket_total_deg':2*math.degrees(math.acos(2.5/3)-math.acos(FLAT_X/3)),
  'is_measured_backlash':False,'assembled_backlash_qualified':False}
 h.save(ROOT/'verification/revJ_readout_check.json',result)
 print(json.dumps({'channel_checks':sum(len(x) for x in result['channels'].values()),'isolated_encoder_rotation_checks':len(sweeps),
  'remaining_probes':[{k:q[k] for k in ('character','axis_id','status')} for q in result['remaining_axis_probes']]}),flush=True)
if __name__=='__main__':main()
