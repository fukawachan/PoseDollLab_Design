from compact_twist import *
import hashlib
def main():
    folder=R/'generated/revK/components';folder.mkdir(parents=True,exist_ok=True)
    assy=cq.Assembly(name='RevK_twist_encoder_candidate');rows=[];renders=[]
    for q in module():
        if q['owner']=='reservation':continue
        sh=q['shape'];assy.add(sh,name=q['name'],color=cq.Color(*COL[q['material']]))
        bb=sh.BoundingBox();rows.append(dict(name=q['name'],valid=sh.isValid(),solids=len(sh.Solids()),bbox_mm=[bb.xlen,bb.ylen,bb.zlen],material=q['material'],note=q['note']))
        if not q['name'].startswith('pcb_'):cq.exporters.export(sh,str(folder/(q['name']+'.step')))
        renders.append((q['name'],sh,COL[q['material']]))
    for i,sh in enumerate(fixed_cradle()):
        assy.add(sh,name='fixed_cradle_reference_'+str(i),color=cq.Color(*COL['frame']))
        renders.append(('cradle_'+str(i),sh,COL['frame']))
    assy.save(str(folder/'compact_twist_encoder_assembly.step'))
    h.render(renders,folder/'compact_twist_encoder.png','Rev K | compact twist sensor | fixed cradle excerpt',camera=(400,-600,350))
    h.render([(q['name'],q['shape'],COL['pcb'] if q['name']=='board' else COL['pcb_component']) for q in head(0) if q['kind']!='short_tail_reservation'],folder/'sensor_head.png','12 x 10 mm sensing head | connector dimensional envelope',camera=(400,-600,-350))
    exploded=[]
    for q in module():
        if q['owner']=='reservation':continue
        n=q['name'];dz=26 if n.startswith(('board_edge_cap','board_cap_')) else 18 if n.startswith('pcb_') else 12 if n.startswith('board_seat_') else 10 if n=='magnet_keeper' or n.startswith('keeper_set_') else 5 if n.startswith('diametric_magnet') else 0
        exploded.append((n,q['shape'].translate((0,0,dz)),COL[q['material']]))
    h.render(exploded,folder/'twist_exploded.png','Rev K | assembly sequence: shaft, removable seats, PCB, caps',camera=(400,-600,350))
    h.save(R/'verification/revK_components.json',dict(parts=rows,cradle_note='Reference posts only; production shape is fused to the revised abduction frame in character assembly',sensor_source_sha256=hashlib.sha256((folder/'sensor_revC_mini.step').read_bytes()).hexdigest(),nominal_board_size_mm=[12,10,1],model_FR4_body_mm=.91,connector_model='Dimension envelope from Hirose drawing, not supplier STEP',manufacturing_released=False))
    print(json.dumps(dict(parts=len(rows))),flush=True)
if __name__=='__main__':main()
