"""Rev L verification: unchanged K pairs require source hashes and shape identity."""
from flex_encoder import *
from probe_flex import overlap
from collision_policy import classify_checks, classify_hit
import hashlib

def allowed(a,b):
    pair={a,b}
    for s in ('l','r'):
        c=s+'_flex_clutch_';p=s+'_flex_sensor_'
        if pair=={c+'flanged_shaft',c+'outer_M3x8'}:return True
        for i in (0,1):
            if pair in ({c+'reaction_plate',p+'threaded_standoff_'+str(i)},
                        {c+'keyed_stop_cap',p+'cap_set_M2x4_'+str(i)},
                        {p+'D_keyed_magnet_cup',p+'keeper_set_M2x3_'+str(i)},
                        {p+'threaded_standoff_'+str(i),p+'board_M2x6_'+str(i)}):return True
    return False

def intersect_affected(items,affected,same_owner=False):
    out=[];bbs={q['name']:q['shape'].BoundingBox() for q in items}
    for i,a in enumerate(items):
        if a['role']=='reservation':continue
        for b in items[i+1:]:
            if b['role']=='reservation' or not ({a['name'],b['name']}&affected):continue
            if (a['owner']==b['owner'])!=same_owner:continue
            v=overlap(a['shape'],b['shape'],bbs[a['name']],bbs[b['name']])
            if v>.02:out.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4),reservation_involved=False,intentional_thread=allowed(a['name'],b['name'])))
    return out

def main():
    for name in ('manny','quinn'):
        p,parts,meta=build(name);affected=set(meta['affected_parts']);folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
        snap=json.loads((R/'verification/revK_design_audit.json').read_text('utf8'))['source_and_output_snapshot_sha256']
        required=[key for key in snap if key.startswith('cad/') or key.startswith('mechanical_manifest/physical_') or key==f'verification/revK_{name}.json' or key=='generated/revK/components/sensor_revC_mini.step']
        # Also validate the older geometry transitively; it is used by k.build.
        j_snap=json.loads((R/'verification/revJ_design_audit.json').read_text('utf8'))['source_and_output_snapshot_sha256']
        for key,digest in [(key,snap[key]) for key in required]+[(key,value) for key,value in j_snap.items() if key.startswith('cad/') or key=='generated/revC/step/sensor_revB.step']:
            assert hashlib.sha256((R/key).read_bytes()).hexdigest()==digest,key
        baseline=json.loads((R/f'verification/revK_{name}.json').read_text('utf8'))
        prior={q['pose']:q for q in baseline['motion_checks']}
        neutral,T0,A0=h.scene(parts,p,{});rows=[];assy=cq.Assembly(name=name+'_RevL_shoulder_assembly')
        for item in neutral:
            sh=item['shape'];bb=sh.BoundingBox();assy.add(sh,name=item['name'],color=cq.Color(*COL[item['material']]))
            rows.append({key:value for key,value in item.items() if key not in ('shape','local_shape')}|dict(valid=sh.isValid(),solids=len(sh.Solids()),bbox_mm=[bb.xlen,bb.ylen,bb.zlen],volume_mm3=sh.Volume(),local_com_mm=list(item['local_shape'].Center().toTuple())))
            if item['name'] in affected:cq.exporters.export(sh,str(folder/(item['name']+'.step')))
        assy.save(str(folder/(name.title()+'_shoulder_assembly.step')))
        owners={q['name']:q['owner'] for q in parts};checks=[]
        for label,angles in poses_all().items():
            assert prior[label]['angles_deg']==angles
            items,T,A=h.scene(parts,p,angles)
            hits=[dict(q) for q in prior[label]['hits'] if not ({q['a'],q['b']}&affected)]
            hits+=intersect_affected(items,affected)
            checks.append(dict(pose=label,angles_deg=angles,hits=hits))
            print(json.dumps(dict(character=name,pose=label,structural=sum(classify_hit(x,owners)['classification']=='structural' for x in hits),pose_contacts=sum(classify_hit(x,owners)['classification']=='pose_restriction' for x in hits))),flush=True)
        contacts=intersect_affected(neutral,affected,True)
        assert not [q for q in contacts if not q['intentional_thread']],contacts
        focused=[];clearance=[]
        for girdle in ('back_down','forward_up'):
            for angle in (-50,90,160):
                pose=dict(h.cases()[girdle],**{f'upperarm_{s}.flex':angle for s in ('l','r')})
                items,T,A=h.scene(parts,p,pose);hits=intersect_affected(items,affected)
                focused.append(dict(pose=girdle+'_flex_'+str(angle),angles_deg=pose,hits=hits,scope='Only pairs involving new or modified Rev L components'))
                assert not [q for q in hits if classify_hit(q,owners)['classification']=='structural'],focused[-1]
        # Measure the closest new flex module feature to the chest in all base poses.
        for label,angles in poses_all().items():
            items,T,A=h.scene(parts,p,angles);chest=next(q for q in items if q['name']=='common_chest_bearing_frame')
            candidates=[q for q in items if '_flex_sensor_' in q['name'] and q['role']!='reservation']
            d,q=min(((q['shape'].distance(chest['shape']),q) for q in candidates),key=lambda pair:pair[0])
            clearance.append(dict(pose=label,nearest_part=q['name'],distance_mm=d))
        record=classify_checks(dict(meta=meta,parts=rows,motion_checks=checks,new_same_owner_assembly_contacts=contacts,unexpected_new_assembly_contacts=[q for q in contacts if not q['intentional_thread']],focused_combination_checks=focused,new_sensor_to_chest_clearance=clearance,collision_method='Source-hashed Rev K unchanged pairs reused with in-build object identity assertions; all pairs involving L changes re-intersected per sample. Same-owner affected pairs checked separately.',manufacturing_released=False,physical_tested=False))
        assert not any(q['structural_hits'] for q in record['motion_checks'])
        h.save(R/f'verification/revL_{name}.json',record)
        h.render([(q['name'],q['shape'],COL[q['material']]) for q in neutral if q['role']!='reservation'],folder/'neutral.png',name.title()+' | Rev L six shoulder sensor candidates',camera=(1000,-1500,600))
        print(json.dumps(dict(character=name,parts=len(parts),local_clear=len(checks),focused=len(focused),closest_to_chest=min(clearance,key=lambda q:q['distance_mm']))),flush=True)
if __name__=='__main__':main()
