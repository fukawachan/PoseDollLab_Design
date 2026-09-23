"""Nominal encoder-frame consistency; not real AS5048A readings."""
from flex_encoder import *
import hashlib

def main():
    result=dict(physical_sensor_tested=False,raw_sensor_sign_calibrated=False,channels={},isolated_flex_sweep=[])
    for name in ('manny','quinn'):
        p,parts,meta=build(name);T0,A0=h.fk(p,{});rows=[]
        for label,angles in poses_all().items():
            T,A=h.fk(p,angles)
            for c in meta['sensor_channels']:
                z=np.array(c['module_normal_neutral'],float);x=np.array(c['module_xdir_neutral'],float);y=np.cross(z,x)
                b0=np.eye(4);b0[:3,:3]=np.column_stack((x,y,z));b0[:3,3]=c['module_origin_neutral_mm']
                mount_rotation=c.get('board_rotation_about_axis_deg',0)
                r=math.radians(mount_rotation);rz=np.eye(4);rz[:2,:2]=[[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]]
                fixed=T[c['fixed_owner']]@np.linalg.inv(T0[c['fixed_owner']])@b0@rz
                rotor=T[c['magnet_owner']]@np.linalg.inv(T0[c['magnet_owner']])@b0
                rel=np.linalg.inv(fixed)@rotor
                geom=math.degrees(math.atan2(rel[1,0],rel[0,0]));zero=-mount_rotation
                expect=c['geometric_angle_sign']*angles.get(c['axis_id'],0)
                error=(geom-zero-expect+180)%360-180
                m=(rotor@np.array([0,0,c.get('magnet_face_mm',36.5),1]))[:3]
                cpos=(fixed@np.array([0,0,c.get('package_face_mm',j.PCB_DATUM-2.595),1]))[:3]
                d=cpos-m;n=fixed[:3,2];gap=float(np.dot(d,n));lateral=float(np.linalg.norm(np.cross(d,n)))
                assert abs(error)<1e-6 and lateral<1e-5 and abs(gap-c['package_to_magnet_gap_mm'])<1e-5
                rows.append(dict(pose=label,axis_id=c['axis_id'],angle_error_deg=error,lateral_axis_error_mm=lateral,package_face_gap_mm=gap,board_datum_rotation_deg=mount_rotation,nominal_geometric_zero_offset_deg=zero))
        result['channels'][name]=rows
    local=[dict(q,role='reservation' if q['owner']=='reservation' else 'sensor_candidate') for q in module()]
    local += [dict(name='stop_cap',shape=stop_cap(),owner='rotor',role='sensor_candidate'),dict(name='button_M3',shape=button_screw(),owner='rotor',role='sensor_candidate')]
    for angle in range(-50,161,10):
        transformed=[dict(q,shape=q['shape'].rotate((0,0,0),(0,0,1),angle)) if q['owner']=='rotor' else q for q in local]
        hits=h.collisions(transformed);assert not hits,hits
        result['isolated_flex_sweep'].append(dict(angle_deg=angle,hits=hits))
    # The critical face is read from the actual transformed U1 solid.
    chip=next(q for q in module() if q['name']=='pcb_AS5048A')['shape']
    assert abs(chip.BoundingBox().zmin-MAG_TOP-GAP)<1e-6
    result.update(source_sensor_step_sha256=hashlib.sha256((R/'generated/revK/components/sensor_revC_mini.step').read_bytes()).hexdigest(),nominal_flex_board_datum_mm=P,scope='Mechanical coordinate and actual package-face checks; geometric zero is a CAD datum, not a prediction of AS5048A raw magnetic zero')
    h.save(R/'verification/revL_readout_check.json',result)
    print(json.dumps(dict(channel_checks=sum(map(len,result['channels'].values())),isolated_flex_samples=len(result['isolated_flex_sweep']))),flush=True)
if __name__=='__main__':main()
