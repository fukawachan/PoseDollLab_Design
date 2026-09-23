"""Explicit staged bench assembly; no hand reach or full moving harness claim."""
from flex_encoder import *
from probe_flex import overlap

def main():
    results=[]
    for name in ('manny','quinn'):
        p,parts,meta=build(name);items,T,A=h.scene(parts,p,{})
        for side,sy in [('l',1),('r',-1)]:
            S=A[f'upperarm_{side}.flex']['origin'];loc=k.previous.frame_transform((0,-sy,0),(1,0,0),S)
            pre=side+'_flex_sensor_';clutch=side+'_flex_clutch_'
            # Loose clutch cartridge: retaining drive/yoke and outer clavicle frame
            # are attached afterwards; their separate mounting tools are checked below.
            bench=[q for q in items if q['name'].startswith((pre,clutch))]
            board=lambda q:q['name'].startswith((pre+'pcb_',pre+'board_'))
            posts=lambda q:q['name'].startswith(pre+'threaded_standoff_')
            def check(stage,sh,omit,target,full=False):
                sh=sh.moved(loc);bb=sh.BoundingBox();pool=items if full else bench
                installed=[q for q in pool if q['role']!='reservation' and not omit(q)]
                hits=[]
                for q in installed:
                    v=overlap(sh,q['shape'],bb,q['shape'].BoundingBox())
                    if v>.02:hits.append(dict(part=q['name'],volume_mm3=round(v,4)))
                results.append(dict(character=name,side=side,stage=stage,target=target,installed_parts=[q['name'] for q in installed],unexpected_contacts=hits))
            check('clutch_button_M3_before_sensor',cyl(CAP_TOP+HEAD_H+.1,CAP_TOP+40,1.3),lambda q:q['name'].startswith(pre),clutch+'outer_M3x8')
            for i,sg in enumerate((-1,1)):
                check('cup_side_set_M2_before_posts',radial(*sorted((sg*8.8,sg*35)),.65,CAP_TOP-1.45),lambda q:board(q) or posts(q),pre+'cap_set_M2x4_'+str(i))
                check('keeper_side_set_M2_before_posts',radial(*sorted((sg*9.6,sg*35)),.65,MAG_TOP-1.1),lambda q:board(q) or posts(q),pre+'keeper_set_M2x3_'+str(i))
                # Thin AF3.5 wrench approaches radially OUTWARD and grips the standoff base,
                # below the rotating cup. This is a declared tool envelope, not catalog CAD.
                wrench=cube((35,8,2),(16.5,sg*POST_Y,48.2)).cut(cube((6,3.6,2.2),(-1,sg*POST_Y,48.2)))
                wrench=wrench.rotate((0,sg*POST_Y,0),(0,sg*POST_Y,1),sg*90)
                check('standoff_AF3p5_base_wrench_before_board',wrench,lambda q:board(q) or q['name']==pre+'threaded_standoff_'+str(i),pre+'threaded_standoff_'+str(i))
                check('PCB_cap_M2',cyl(P+2.3,P+30,1).translate((0,sg*POST_Y,0)),lambda q:False,pre+'board_M2x6_'+str(i))
            # Cap/cup insertion positions. Screws go in only after each keyed part seats.
            rotating_names={pre+'D_keyed_magnet_cup',pre+'diametric_magnet_6x2p5',pre+'magnet_keeper'}|{pre+x+str(i) for x in ('cap_set_M2x4_','keeper_set_M2x3_') for i in (0,1)}
            cup=next(q['shape'] for q in module() if q['name']=='D_keyed_magnet_cup')
            for dz in (20,10,4,1,0):
                check('cup_axial_insertion_sample_'+str(dz)+'mm',cup.translate((0,0,dz)),lambda q:board(q) or posts(q) or q['name'] in rotating_names,pre+'D_keyed_magnet_cup')
            # Axially extruded AABBs of separate real PCB components conservatively
            # cover their straight insertion while retaining the empty board-edge underside.
            head_shapes=[q['shape'].rotate((0,0,0),(0,0,1),BOARD_ROTATION) for q in k.head(P) if q['kind']!='short_tail_reservation']
            paths=[]
            for sh in head_shapes:
                b=sh.BoundingBox();paths.append(cube((b.xlen+.05,b.ylen+.05,b.zlen+20),((b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2,(b.zmin+b.zmax)/2+10)))
            check('PCB_axial_insertion_before_caps',h.union(paths),lambda q:q['name'].startswith(pre+'pcb_') or q['name'].startswith((pre+'board_cap_',pre+'board_M2x6_')),pre+'pcb_board')
            fpc=cube((3.6,25,.3),(0,13.95,P+.3)).rotate((0,0,0),(0,0,1),BOARD_ROTATION)
            check('FPC_insertion_on_bench',fpc,lambda q:q['name']==pre+'pcb_J1_dimension_envelope',pre+'pcb_J1_dimension_envelope')
            actuator=cube((5.2,3.2,1.9),(0,-.25,P+.95)).rotate((0,0,0),(0,0,1),BOARD_ROTATION)
            check('FPC_actuator_on_bench',actuator,lambda q:q['name']==pre+'pcb_J1_dimension_envelope',pre+'pcb_J1_dimension_envelope')
            for i,x in enumerate((-17.5,17.5)):
                check('cartridge_mount_M3_before_girdle_upstream_join',cyl(50.1,83,1.5).translate((x,0,0)),lambda q:q['owner'] not in (f'clavicle_{side}',f'upperarm_{side}.flex_frame',f'upperarm_{side}.abduct_frame',f'upperarm_{side}',f'elbow_{side}'),clutch+'mount_M3x10_'+str(i),True)
    h.save(R/'verification/revL_flex_tool_access.json',dict(scope='Nominal staged bench geometry, cup insertion samples and conservative component AABB board insertion paths; no grip, torque, tolerances or full cable routing verified',checks=results))
    bad=[q for q in results if q['unexpected_contacts']]
    print(json.dumps(dict(checks=len(results),unexpected=[{k:q[k] for k in ('character','side','stage','unexpected_contacts')} for q in bad])),flush=True)
    assert not bad
if __name__=='__main__':main()
