"""Rev L shoulder flex encoder, candidate geometry in mm; no physical release."""
from pathlib import Path
import sys, math, json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revK'))
import compact_twist as k
from verify_k import poses_all
import numpy as np
h=k.h;cq=k.cq;j=k.j
R=ROOT=k.R;OUT=R/'generated/revL';COL=dict(k.COL,titanium=(.63,.66,.7))
cyl=k.cyl;ring=k.ring;cube=k.cube;hexagon=k.hexagon
BASE=43.;CAP_BOTTOM=BASE+j.CAP_BOTTOM;CAP_TOP=BASE+j.TOP
HEAD_H=1.65;HEAD_R=2.85
MAG_BOTTOM=CAP_TOP+HEAD_H+.15+.6
MAG_TOP=MAG_BOTTOM+2.5
GAP=1.5;P=MAG_TOP+GAP+1.995
POST_Y=11.9;POST_TOP=P-2
BOARD_ROTATION=90

def radial(a,b,r,z):return h.axis_cyl(1,a,b,r,(0,0,z))
def cut_d(sh,a,b,flat):return sh.cut(cube((30,40,b-a+2),(flat+15,0,(a+b)/2)))

def stop_cap():
    cap=cyl(CAP_BOTTOM,CAP_TOP,7)
    cap=cut_d(cap,CAP_BOTTOM,CAP_TOP,5.8)
    cap=cap.cut(j.dshape(CAP_BOTTOM-.01,BASE+j.SHAFT_END+.01,6.1,2.55)).cut(cyl(CAP_BOTTOM-1,CAP_TOP+1,1.65))
    for sg in (-1,1):cap=cap.cut(radial(*sorted((sg*2.9,sg*7.1)),.8,CAP_TOP-1.45))
    return cap

def button_screw():
    # Conservative cylindrical head envelope, actual corner profile not supplied.
    sh=cyl(CAP_TOP-8,CAP_TOP,1.5).fuse(cyl(CAP_TOP,CAP_TOP+HEAD_H,HEAD_R))
    return sh.cut(hexagon(2,CAP_TOP+HEAD_H-1.04,CAP_TOP+HEAD_H+.1))

def module():
    out=[]
    def add(n,sh,mat,owner,note):
        assert sh.isValid() and len(sh.Solids())==1,(n,len(sh.Solids()))
        out.append(dict(name=n,shape=sh,material=mat,owner=owner,note=note))
    carrier=cyl(CAP_BOTTOM+.2,MAG_TOP,8.7)
    d=cut_d(cyl(CAP_BOTTOM+.1,CAP_TOP+.1,7.05),CAP_BOTTOM+.1,CAP_TOP+.1,5.85)
    carrier=carrier.cut(d).cut(cyl(CAP_TOP-.01,MAG_BOTTOM-.6,3.0)).cut(cyl(MAG_BOTTOM,MAG_TOP+.1,3.1))
    # Slip cup over the already-fastened keyed cap; side screws retain it axially.
    for sg in (-1,1):
        carrier=carrier.cut(radial(*sorted((sg*6.9,sg*8.8)),1.1,CAP_TOP-1.45))
        carrier=carrier.cut(radial(*sorted((sg*5.8,sg*8.8)),.8,MAG_TOP-1.1))
    add('D_keyed_magnet_cup',carrier,'aluminum','rotor','Machined aluminum cup keyed to flat on metal stop cap; 0.05 mm nominal fit and 0.6 mm floor; install after the outer clutch M3 is tightened')
    for i,sg in enumerate((-1,1)):
        sh=radial(*sorted((sg*4.7,sg*8.7)),1,CAP_TOP-1.45).cut(cube((.35,.9,.9),(0,sg*8.6,CAP_TOP-1.45)))
        add('cap_set_M2x4_'+str(i),sh,'brass','rotor','Nominal slotted brass M2x4 retaining cup on keyed cap; 2.3 mm nominal thread engagement; exact product pending')
    add('diametric_magnet_6x2p5',cyl(MAG_BOTTOM,MAG_TOP,3),'magnet','rotor','6x2.5 diametric magnet, 0.1 mm radial adhesive gap; rotational bonding and magnetic field unverified')
    keeper=ring(MAG_TOP-2,MAG_TOP,9.5,8.75).fuse(ring(MAG_TOP,MAG_TOP+.6,9.5,2.5))
    for sg in (-1,1):keeper=keeper.cut(radial(*sorted((sg*8.6,sg*9.6)),1.1,MAG_TOP-1.1))
    add('magnet_keeper',keeper,'frame','rotor','Printed removable cover positively retains magnet face; minimum radial wall 0.75 mm, stiffness and wear unqualified')
    for i,sg in enumerate((-1,1)):
        sh=radial(*sorted((sg*6.5,sg*9.5)),1,MAG_TOP-1.1).cut(cube((.35,.9,.9),(0,sg*9.4,MAG_TOP-1.1)))
        add('keeper_set_M2x3_'+str(i),sh,'brass','rotor','Nominal slotted brass M2x3 into aluminum cup; exact purchased part pending')
    for q in k.head(P):
        sh=q['shape'].rotate((0,0,0),(0,0,1),BOARD_ROTATION)
        add('pcb_'+q['name'],sh,'pcb' if q['name']=='board' else 'sensor_space' if q['kind']=='short_tail_reservation' else 'pcb_component','reservation' if q['kind']=='short_tail_reservation' else 'fixed',q['kind'])
    for i,sg in enumerate((-1,1)):
        y=sg*POST_Y
        post=hexagon(3.5,47,POST_TOP).fuse(cyl(44.5,47,1)).cut(cyl(POST_TOP-5.5,POST_TOP+.1,.8))
        add('threaded_standoff_'+str(i),post.translate((0,y,0)),'brass','fixed','Custom AF3.5 brass male/female M2 standoff; 2.5 mm male engagement into reaction plate; nominal height %.3f mm, locking and bending pending'%(POST_TOP-47))
        lower=cube((4,8.3,1),(0,sg*9.75,P-1.5)).fuse(cube((4,7.8,1),(0,sg*10,P-.5)))
        lower=lower.cut(cyl(P-2.1,P+.1,1.1).translate((0,y,0)))
        add('board_saddle_'+str(i),lower,'frame','fixed','Separate insulating saddle, bearing edge at +/-6.1 mm in Y; installed after rotating magnet cup')
        cap=cube((4,8.3,.8),(0,sg*9.75,P+.4)).cut(cyl(P-.1,P+.9,1.1).translate((0,y,0)))
        add('board_cap_'+str(i),cap,'nylon','fixed','Removable edge cap with 1.0 mm nominal board slot; board thickness tolerance pending')
        add('board_M2x6_'+str(i),j.screw_z(P+.8,6).translate((0,y,0)),'nylon','fixed','Nominal nylon M2x6 into brass standoff, 3.2 mm nominal engagement; creep and locking pending')
    return out

def build(name):
    p,parts,meta=k.build(name);T0,A0=h.fk(p,{})
    inherited={q['name']:q['local_shape'] for q in parts};added=[];changed=[];channels=[]
    for side,sy in [('l',1),('r',-1)]:
        S=A0[f'upperarm_{side}.flex']['origin'];F=f'upperarm_{side}.flex_frame';E=f'clavicle_{side}'
        loc=k.previous.frame_transform((0,-sy,0),(1,0,0),S)
        def to_owner(sh,o):return sh.moved(loc).translate(tuple(-T0[o][:3,3]))
        cap=next(q for q in parts if q['name']==side+'_flex_clutch_keyed_stop_cap')
        cap.update(local_shape=to_owner(stop_cap(),F),material='aluminum',note='Rev L aluminum stop cap retains original metal stop heights and adds outside D flat for magnet cup; local contact stress and fatigue unqualified')
        screw=next(q for q in parts if q['name']==side+'_flex_clutch_outer_M3x8')
        screw.update(local_shape=to_owner(button_screw(),F),material='titanium',note='Rev L M3x8 titanium Grade 5 button screw dimension candidate (Accu SSB-M3-8-TI5); cylindrical head envelope 5.7 x 1.65, 2 mm hex, strength/procurement not released')
        plate=next(q for q in parts if q['name']==side+'_flex_clutch_reaction_plate')
        for y in (-POST_Y,POST_Y):plate['local_shape']=plate['local_shape'].cut(to_owner(cyl(42.9,47.1,.8).translate((0,y,0)),E))
        plate['note']+='; Rev L two M2 through pilot bores at +/-11.9 for separate brass sensor standoffs; 1.0 mm minimum radial ligament'
        changed.extend([cap['name'],screw['name'],plate['name']])
        for q in module():
            o=F if q['owner']=='rotor' else E
            added.append(dict(name=side+'_flex_sensor_'+q['name'],local_shape=to_owner(q['shape'],o),material=q['material'],owner=o,role='reservation' if q['owner']=='reservation' else 'sensor_candidate',note=q['note']))
        channels.append(dict(axis_id=f'upperarm_{side}.flex',fixed_owner=E,magnet_owner=F,module_origin_neutral_mm=S.tolist(),module_normal_neutral=[0,-sy,0],module_xdir_neutral=[1,0,0],geometric_angle_sign=sy,board_rotation_about_axis_deg=BOARD_ROTATION,board_datum_mm=P,magnet_face_mm=MAG_TOP,package_face_mm=P-1.995,package_to_magnet_gap_mm=GAP,raw_sensor_sign_calibrated=False,magnetic_field_verified=False))
    parts+=added;affected=set(changed)|{q['name'] for q in added}
    assert all(q['local_shape'] is inherited[q['name']] for q in parts if q['name'] not in affected)
    for q in parts:assert q['local_shape'].isValid() and len(q['local_shape'].Solids())==1,(q['name'],len(q['local_shape'].Solids()))
    meta=dict(meta,revision='L',inherited_shapes_identity_verified=True,affected_parts=sorted(affected),new_flex_sensor_parts=len(added),sensor_channels=meta['sensor_channels']+channels,remaining_readout_axes_in_shoulders=[],scope='Six geometric shoulder encoder installation candidates; shoulder girdle, elbow transfer, complete harness and full body pending')
    for s in ('l','r'):meta['datums'][s]['pending_shoulder_axes_readout']=[]
    return p,parts,meta

if __name__=='__main__':
    from probe_flex import overlap
    p,parts,meta=build('quinn');affected=set(meta['affected_parts'])
    for label in ('neutral','back_down','arms_side','forehead','arms_overhead','forward_up','scan_flex_135'):
        items,_,_=h.scene(parts,p,poses_all()[label]);bbs={q['name']:q['shape'].BoundingBox() for q in items};hits=[]
        for i,a in enumerate(items):
            if a['role']=='reservation':continue
            for b in items[i+1:]:
                if b['role']=='reservation' or not (a['name'] in affected or b['name'] in affected):continue
                v=overlap(a['shape'],b['shape'],bbs[a['name']],bbs[b['name']])
                if v>.02:hits.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4),same_owner=a['owner']==b['owner']))
        print(json.dumps(dict(character='quinn',pose=label,hits=hits)),flush=True)
    folder=OUT/'trial';folder.mkdir(parents=True,exist_ok=True)
    h.render([(q['name'],q['shape'],COL[q['material']]) for q in module() if q['owner']!='reservation']+[('stop_cap',stop_cap(),COL['aluminum']),('M3_button',button_screw(),COL['titanium'])],folder/'flex_module.png','Rev L | medial flex sensor packaging candidate',camera=(350,-550,350))
