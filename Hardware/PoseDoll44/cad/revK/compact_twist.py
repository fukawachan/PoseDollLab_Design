"""Rev K compact twist encoder. Nominal candidate geometry, no release."""
from mini_head import *
COL=dict(j.COL,pcb_component=(.20,.23,.25),nylon=(.9,.88,.76),brass=(.71,.57,.23))
ROOT=R;OUT=R/'generated/revK';HERE=Path(__file__).resolve().parent
SPRING=j.SPRING;previous=j.previous;MOUNT_RADIUS=j.MOUNT_RADIUS;MOUNT_Y=j.MOUNT_Y;cross_cyl=j.cross_cyl;hexagon=j.hexagon;PCB_DATUM=j.PCB_DATUM
P=12.495;MAG_BOTTOM=6.5;MAG_TOP=9.;GAP=1.5
cyl=j.cyl;ring=j.ring;cube=h.cube

def radial(a,b,r,z=8):
    return h.axis_cyl(1,a,b,r,(0,0,z))
def module():
    out=[]
    def add(n,shape,mat,owner,note):
        assert shape.isValid() and len(shape.Solids())==1,(n,len(shape.Solids()))
        out.append(dict(name=n,shape=shape,material=mat,owner=owner,note=note))
    shaft=j.dshape(-24,-18,4,1.5).fuse(cyl(-18,5.7,2)).fuse(cyl(5.7,9,5.3))
    shaft=shaft.cut(cyl(6.5,9.1,3.1))
    for sign in (-1,1):
        shaft=shaft.cut(radial(*sorted((sign*3.45,sign*5.4)),.8))
    # Lower radial screw retains keyed arm coupling; the D face transmits angle.
    shaft=shaft.cut(h.axis_cyl(0,0,2.1,.8,(0,0,-22.5)))
    add('integral_magnet_shaft',shaft,'aluminum','rotor','Custom machined aluminum shaft and magnet cup in one piece; bottom D4 transmits arm rotation; torsion, bending and radial-thread fatigue unqualified')
    add('diametric_magnet_6x2p5',cyl(MAG_BOTTOM,MAG_TOP,3),'magnet','rotor','6 x 2.5 diametric magnet; 0.1 mm radial adhesive allowance; grade and field not qualified')
    cap=ring(7,9,6.5,5.35).fuse(ring(9,9.6,6.5,2.5))
    for sign in (-1,1):cap=cap.cut(radial(*sorted((sign*5.2,sign*6.7)),1.1))
    add('magnet_keeper',cap,'frame','rotor','Removable rigid cover retains outer 0.5 mm of magnet face; 0.6 mm cover, radial brass screw attachment; print durability pending')
    for i,sign in enumerate((-1,1)):
        screw=radial(*sorted((sign*3.5,sign*6.5)),1)
        slot=cube((.35,1,.9),(0,sign*6.4,8))
        add('keeper_set_M2x3_'+str(i),screw.cut(slot),'brass','rotor','Nominal slotted brass M2x3 set screw; exact purchased part and slot specification pending')
    screw=h.axis_cyl(0,0,6,1,(0,0,-22.5)).fuse(h.axis_cyl(0,6,8,1.9,(0,0,-22.5)))
    add('arm_radial_M2x6',screw,'brass','rotor','Simplified brass M2x6; 1.5 mm nominal thread engagement through the D flat; head tool recess is an envelope')
    for q in head(P):
        add('pcb_'+q['name'],q['shape'],'pcb' if q['name']=='board' else 'sensor_space' if q['kind']=='short_tail_reservation' else 'pcb_component','reservation' if q['kind']=='short_tail_reservation' else 'fixed',q['kind'])
    for i,sign in enumerate((-1,1)):
        saddle=cube((4.25,4,.8),(sign*7.725,0,P-1.4)).fuse(cube((3.75,4,1.0),(sign*7.975,0,P-.5)))
        saddle=saddle.cut(cyl(P-1.9,P+.1,1.1).translate((sign*8.5,0,0)))
        add('board_seat_saddle_'+str(i),saddle,'frame','fixed','Separate L saddle installed after complete magnet shaft; locating wall at +/-6.1, nominal 1.0 mm board slot; never fuse to base posts')
    for i,sign in enumerate((-1,1)):
        cap=cube((4.25,4,.8),(sign*7.725,0,P+.4))
        cap=cap.cut(cyl(P-.1,P+.9,1.1).translate((sign*8.5,0,0)))
        add('board_edge_cap_'+str(i),cap,'nylon','fixed','Removable insulating edge retainer; nominal 1.0 mm board stack; STEP FR4 body is 0.91 mm excluding copper/model offsets; fit requires physical verification')
        sh=j.screw_z(P+.8,6).translate((sign*8.5,0,0))
        add('board_cap_M2x6_'+str(i),sh,'nylon','fixed','Nominal nylon M2x6 into replaceable printed support; 3.4 mm engagement, creep and repeated assembly unqualified')
    chip=next(q for q in out if q['name']=='pcb_AS5048A')
    assert abs(chip['shape'].BoundingBox().zmin-(MAG_TOP+GAP))<1e-5
    return out

def fixed_cradle():
    shapes=[]
    for sign in (-1,1):
        top=P-1.8
        post=cube((2.7,4,top-3.5),(sign*8.5,0,(top+3.5)/2))
        post=post.fuse(cube((3.5,2,2),(sign*6.75,0,4.4)))
        post=post.cut(h.axis_cyl(0,*sorted((sign*8.7,sign*10.3)),5.3))
        post=post.cut(cyl(P-5.5,top+.1,.8).translate((sign*8.5,0,0)))
        shapes.append(post)
    return shapes

def build(name):
    p,parts,meta=j.build(name);T0,A0=h.fk(p,{})
    inherited={q['name']:q['local_shape'] for q in parts}
    added=[];channels=[]
    for side,sy in [('l',1),('r',-1)]:
        S=A0[f'upperarm_{side}.flex']['origin'];B=f'upperarm_{side}.abduct_frame';W=f'upperarm_{side}'
        loc=j.previous.frame_transform((0,0,1),(sy,0,0),S)
        to_owner=lambda sh,o:sh.moved(loc).translate(tuple(-T0[o][:3,3]))
        fixed=next(q for q in parts if q['name']==side+'_abduct_ring_and_twist_seat')
        fixed['local_shape']=fixed['local_shape'].cut(to_owner(cyl(5.5,6.1,6.6),B))
        for sh in fixed_cradle():fixed['local_shape']=fixed['local_shape'].fuse(to_owner(sh,B))
        fixed['note']='Rev K top seat trimmed to Z5.5 and insulated sensor edge cradle added; original concentric axes retained'
        coupling=next(q for q in parts if q['name']==side+'_arm_coupling')
        coupling['local_shape']=coupling['local_shape'].fuse(to_owner(cyl(-24,-20.5,2.1),W))
        coupling['local_shape']=coupling['local_shape'].cut(to_owner(j.dshape(-24.1,-20.4,4.1,1.55),W))
        coupling['local_shape']=coupling['local_shape'].cut(to_owner(h.axis_cyl(0,1.4,6.1,1.1,(0,0,-22.5)),W))
        coupling['local_shape']=coupling['local_shape'].cut(to_owner(h.axis_cyl(0,6,8.1,2.0,(0,0,-22.5)),W))
        coupling['note']='Rev K D4 key and radial M2 retention on twist shaft; remaining twist face clutch preload is pending'
        parts=[q for q in parts if q['name']!=side+'_twist_shaft']
        for q in module():
            o=W if q['owner']=='rotor' else B
            added.append(dict(name=side+'_twist_sensor_'+q['name'],local_shape=to_owner(q['shape'],o),material=q['material'],owner=o,role='reservation' if q['owner']=='reservation' else 'sensor_candidate',note=q['note']))
        channels.append(dict(axis_id=f'upperarm_{side}.twist',fixed_owner=B,magnet_owner=W,module_origin_neutral_mm=S.tolist(),module_normal_neutral=[0,0,1],module_xdir_neutral=[sy,0,0],geometric_angle_sign=-sy,board_datum_mm=P,magnet_face_mm=MAG_TOP,package_face_mm=P-1.995,package_to_magnet_gap_mm=GAP,raw_sensor_sign_calibrated=False,magnetic_field_verified=False))
    parts+=added
    changed={s+suffix for s in ('l','r') for suffix in ('_abduct_ring_and_twist_seat','_arm_coupling')}
    affected=changed|{q['name'] for q in added}
    assert all(q['local_shape'] is inherited[q['name']] for q in parts if q['name'] not in affected)
    meta=dict(meta,inherited_shapes_identity_verified=True,affected_parts=sorted(affected))
    for q in parts:assert q['local_shape'].isValid() and len(q['local_shape'].Solids())==1,(q['name'],len(q['local_shape'].Solids()))
    meta=dict(meta,revision='K',new_twist_sensor_parts=len(added),sensor_channels=meta['sensor_channels']+channels,remaining_readout_axes_in_shoulders=['upperarm_l.flex','upperarm_r.flex'],scope='Four geometric shoulder encoder installations: two Rev J abduction + two Rev K twist; full harness and flex installation remain pending')
    for s in ('l','r'):meta['datums'][s]['pending_shoulder_axes_readout']=[f'upperarm_{s}.flex']
    return p,parts,meta

def main():
    p,parts,meta=build('quinn')
    for label in ('neutral','arms_side','arms_overhead','forehead','back_down','crossed_clearance_candidate','scan_abduct_60','scan_abduct_120'):
        items,_,_=h.scene(parts,p,jverify.poses_all()[label]);hits=h.collisions(items)
        print(json.dumps(dict(pose=label,hits=hits)),flush=True)
    items,_,_=h.scene(parts,p,{})
    h.render([(q['name'],q['shape'],COL[q['material']]) for q in items if q['name'].startswith('l_') and q['role']!='reservation' and '_arm_' not in q['name'] and not any(v in q['name'] for v in ('_yaw_','_elev_'))],R/'generated/revK/twist_trial.png','Rev K | compact twist encoder candidate',camera=(1000,-1500,600))
if __name__=='__main__':main()
