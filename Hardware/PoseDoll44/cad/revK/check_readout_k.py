from compact_twist import *
from verify_k import poses_all
import hashlib
def main():
    result={'physical_sensor_tested':False,'raw_sensor_sign_calibrated':False,'channels':{},'isolated_twist_sweep':[]}
    for name in ('manny','quinn'):
        p,parts,meta=build(name);T0,A0=h.fk(p,{})
        rows=[]
        for label,angles in poses_all().items():
            T,A=h.fk(p,angles)
            for c in meta['sensor_channels']:
                z=np.array(c['module_normal_neutral'],float);x=np.array(c['module_xdir_neutral'],float);y=np.cross(z,x)
                B0=np.eye(4);B0[:3,:3]=np.column_stack((x,y,z));B0[:3,3]=c['module_origin_neutral_mm']
                fixed=T[c['fixed_owner']]@np.linalg.inv(T0[c['fixed_owner']])@B0
                rotor=T[c['magnet_owner']]@np.linalg.inv(T0[c['magnet_owner']])@B0
                rel=np.linalg.inv(fixed)@rotor
                geom=math.degrees(math.atan2(rel[1,0],rel[0,0]));expect=c['geometric_angle_sign']*angles.get(c['axis_id'],0)
                err=(geom-expect+180)%360-180
                m=(rotor@np.array([0,0,c.get('magnet_face_mm',36.5),1]))[:3]
                cpos=(fixed@np.array([0,0,c.get('package_face_mm',j.PCB_DATUM-2.595),1]))[:3]
                d=cpos-m;n=fixed[:3,2];gap=float(np.dot(d,n));lateral=float(np.linalg.norm(np.cross(d,n)))
                assert abs(err)<1e-6 and lateral<1e-5 and abs(gap-c['package_to_magnet_gap_mm'])<1e-5
                rows.append(dict(pose=label,axis_id=c['axis_id'],angle_error_deg=err,lateral_axis_error_mm=lateral,package_face_gap_mm=gap))
        result['channels'][name]=rows
    parts=[dict(q,role='reservation' if q['owner']=='reservation' else 'sensor_candidate') for q in module()]
    parts += [dict(name='cradle_'+str(i),shape=s,role='sensor_candidate',owner='fixed') for i,s in enumerate(fixed_cradle())]
    for angle in range(-90,91,10):
        transformed=[dict(q,shape=q['shape'].rotate((0,0,0),(0,0,1),angle)) if q['owner']=='rotor' else q for q in parts]
        hits=h.collisions(transformed);assert not hits,hits
        result['isolated_twist_sweep'].append(dict(angle_deg=angle,hits=hits))
    result['source_sensor_step_sha256']=hashlib.sha256((R/'generated/revK/components/sensor_revC_mini.step').read_bytes()).hexdigest()
    h.save(R/'verification/revK_readout_check.json',result)
    print(json.dumps(dict(channel_checks=sum(len(x) for x in result['channels'].values()),isolated_sweep=len(result['isolated_twist_sweep']))),flush=True)
if __name__=='__main__':main()
