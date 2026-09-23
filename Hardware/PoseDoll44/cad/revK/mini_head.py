"""Mini head geometry and measured packaging probes; not an installed sensor."""
from pathlib import Path
import sys,json,math
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revJ'))
import shoulder_revision as j
import build_and_verify as jverify
import cadquery as cq
import numpy as np
R=j.ROOT; h=j.h

def head(datum):
    solids=cq.importers.importStep(str(R/'generated/revK/components/sensor_revC_mini.step')).val().Solids()
    expected={'AS5048A':(0,0),'C1':(2.3,3.7),'C2':(2.3,-3.75),'R1':(-2.3,3.7),'R2':(-2.3,-3.7)}
    labeled={}
    for sh in solids:
        b=sh.BoundingBox()
        if b.xlen>11.9:
            labeled['board']=sh;continue
        center=((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2)
        name=min(expected,key=lambda k:math.dist(center,expected[k]))
        assert math.dist(center,expected[name])<.1 and name not in labeled,(name,center)
        labeled[name]=sh
    assert set(labeled)==set(expected)|{'board'}
    out=[dict(name=name,shape=labeled[name].rotate((0,0,0),(1,0,0),180).translate((0,0,datum)),kind='actual_KiCad_STEP') for name in [*expected,'board']]
    # Full outside dimension including terminals; upper tolerance, no vendor 3D supplied.
    out.append(dict(name='J1_dimension_envelope',shape=h.cube((5.15,3.15,1.0),(0,-.25,datum+.5)),kind='manufacturer_dimension_envelope'))
    # 0.2 mm compatible FPC, short straight inserted end only, not whole moving harness.
    out.append(dict(name='FPC_short_tail',shape=h.cube((3.5,4,.2),(0,3.25,datum+.3)),kind='short_tail_reservation'))
    return out

def loc_info(side,kind,S):
    sy=1 if side=='l' else -1
    if kind=='flex':
        return (0,-sy,0),(1,0,0),63.995,f'clavicle_{side}',f'upperarm_{side}.flex_frame',sy
    return (0,0,1),(0,1,0),15.795,f'upperarm_{side}.abduct_frame',f'upperarm_{side}',-sy

def main():
    report=[]
    for name in ('manny','quinn'):
        p,parts,meta=j.build(name);T0,A0=h.fk(p,{})
        # Old twist shaft must be shortened from Z10 to 8; probe intentionally checks
        # only sensor head and FPC stub; magnet, cradle and drive are not yet installed.
        for side in ('l','r'):
            S=A0[f'upperarm_{side}.flex']['origin']
            for kind in ('flex','twist'):
                n,xd,datum,fixed,rotor,sign=loc_info(side,kind,S)
                loc=j.previous.frame_transform(n,xd,S)
                probes=[dict(q,local=q['shape'].moved(loc).translate(tuple(-T0[fixed][:3,3]))) for q in head(datum)]
                checks=[]
                for label,angles in jverify.poses_all().items():
                    items,T,A=h.scene(parts,p,angles);hits=[]
                    for q in probes:
                        sh=h.move(q['local'],T[fixed]);bb=sh.BoundingBox()
                        for item in items:
                            if item['role']=='reservation':continue
                            b=item['shape'].BoundingBox()
                            if not all(min(getattr(bb,k+'max'),getattr(b,k+'max'))-max(getattr(bb,k+'min'),getattr(b,k+'min'))>1e-4 for k in 'xyz'):continue
                            v=sh.intersect(item['shape']).Volume()
                            if v>.02:hits.append(dict(probe=q['name'],part=item['name'],volume_mm3=round(v,4)))
                    checks.append(dict(pose=label,hits=hits))
                rec=dict(character=name,axis=f'upperarm_{side}.{kind}',board_datum_mm=datum,checks=checks)
                report.append(rec)
                print(json.dumps(dict(character=name,axis=rec['axis'],failed=[q for q in checks if q['hits']])),flush=True)
    h.save(R/'verification/revK_mini_packaging_probe.json',dict(status='EARLY_STRAIGHT_PROBE_NOT_CURRENT_TWIST_INSTALLATION',scope='Actual head, connector dimensional envelope, 4 mm short FPC tail only. No mount/retention/full harness.',physical_tested=False,probes=report))
if __name__=='__main__':main()
