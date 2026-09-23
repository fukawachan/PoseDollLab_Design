"""Additional neutral bench-assembly access, with explicit installed component lists."""
from flex_encoder import *
from compact_twist import radial
from compact_twist import P
def main():
    checks=[]
    for name in ('manny','quinn'):
        p,parts,meta=build(name);items,T,A=h.scene(parts,p,{})
        for side in ('l','r'):
            prefix=side+'_twist_sensor_';B=f'upperarm_{side}.abduct_frame';W=f'upperarm_{side}'
            S=A[f'upperarm_{side}.flex']['origin'];sy=1 if side=='l' else -1;loc=j.previous.frame_transform((0,0,1),(sy,0,0),S)
            # Bench subassembly: install the internal clutch fasteners first, then
            # rear abduction journal, then this twist shaft/head; attach outer yoke later.
            installed=[q for q in items if q['owner'] in (B,W)]
            def check(stage,tool,omit,target):
                tool=tool.moved(loc);bb=tool.BoundingBox();hits=[]
                present=[q for q in installed if q['role']!='reservation' and not omit(q)]
                for q in present:
                    qb=q['shape'].BoundingBox()
                    if not all(min(getattr(bb,k+'max'),getattr(qb,k+'max'))-max(getattr(bb,k+'min'),getattr(qb,k+'min'))>1e-4 for k in 'xyz'):continue
                    v=tool.intersect(q['shape']).Volume()
                    if v>.02:hits.append(dict(part=q['name'],volume_mm3=round(v,4)))
                checks.append(dict(character=name,side=side,stage=stage,target=target,installed_parts=[q['name'] for q in present],unexpected_contacts=hits))
            board_out=lambda q:q['name'].startswith(prefix+'pcb_') or q['name'].startswith(prefix+'board_')
            for i,sgn in enumerate((-1,1)):
                check('magnet_keeper_on_loose_shaft',radial(*sorted((sgn*6.65,sgn*26)),.6),lambda q:not q['name'].startswith(prefix) or board_out(q) or q['name']==prefix+'arm_radial_M2x6',prefix+'keeper_set_M2x3_'+str(i))
            shaft_path=j.dshape(-24,-18,4,1.5).fuse(cyl(-18,45.7,2)).fuse(cyl(5.7,49.6,6.6))
            check('completed_shaft_axial_insertion_before_saddles',shaft_path,lambda q:q['name'].startswith(prefix),prefix+'integral_magnet_shaft')
            check('arm_D_key_radial_retention' ,h.axis_cyl(0,8.1,35,1,(0,0,-22.5)),lambda q:False,prefix+'arm_radial_M2x6')
            for i,sgn in enumerate((-1,1)):
                check('PCB_edge_cap_M2',cyl(P+2.3,P+32,1).translate((sgn*8.5,0,0)),lambda q:False,prefix+'board_cap_M2x6_'+str(i))
            check('FPC_straight_insertion',cube((3.6,25,.3),(0,13.95,P+.3)),lambda q:q['name']==prefix+'pcb_J1_dimension_envelope',prefix+'pcb_J1_dimension_envelope')
            check('FPC_actuator_opening',cube((5.2,3.2,1.9),(0,-.25,P+.95)),lambda q:q['name']==prefix+'pcb_J1_dimension_envelope',prefix+'pcb_J1_dimension_envelope')
            # Conservatively extruded rectangular PCB path; cap and screws are removed.
            check('PCB_axial_insertion_before_caps',cube((12.1,10.1,20.92),(0,0,P+9.54)),lambda q:board_out(q) and not q['name'].startswith(prefix+'board_seat_saddle_'),prefix+'pcb_board')
    h.save(R/'verification/revL_twist_tool_access.json',dict(scope='Bench subassembly before installation into outer shoulder yoke. Straight tool/insertion envelopes only, no hand grip, torque or flexible cable routing.',checks=checks))
    bad=[x for x in checks if x['unexpected_contacts']]
    print(json.dumps(dict(checks=len(checks),unexpected=bad)),flush=True)
    assert not bad,bad
if __name__=='__main__':main()
