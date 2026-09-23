from flex_encoder import *
import hashlib

def main():
    folder=OUT/'components';folder.mkdir(parents=True,exist_ok=True)
    assy=cq.Assembly(name='RevL_flex_encoder_candidate');rows=[];render=[];exploded=[]
    local=module()+[dict(name='aluminum_keyed_stop_cap',shape=stop_cap(),material='aluminum',owner='rotor',note='Same original stop datums, added external flat; not strength-qualified'),dict(name='titanium_M3x8_button',shape=button_screw(),material='titanium',owner='rotor',note='Accu SSB-M3-8-TI5 dimensional candidate, conservative cylindrical head')]
    for q in local:
        if q['owner']=='reservation':continue
        sh=q['shape'];n=q['name'];bb=sh.BoundingBox()
        assy.add(sh,name=n,color=cq.Color(*COL[q['material']]))
        rows.append(dict(name=n,material=q['material'],valid=sh.isValid(),solids=len(sh.Solids()),bbox_mm=[bb.xlen,bb.ylen,bb.zlen],note=q['note']))
        if not n.startswith('pcb_'):cq.exporters.export(sh,str(folder/(n+'.step')))
        render.append((n,sh,COL[q['material']]))
        dz=34 if n.startswith(('board_cap_','board_M2')) else 26 if n.startswith('pcb_') else 20 if n.startswith('board_saddle') else 12 if n=='magnet_keeper' or n.startswith('keeper_set_') else 8 if n.startswith('diametric') else 4 if n=='D_keyed_magnet_cup' or n.startswith('cap_set_') else 0
        exploded.append((n,sh.translate((0,0,dz)),COL[q['material']]))
    assy.save(str(folder/'flex_encoder_assembly.step'))
    h.render(render,folder/'flex_encoder.png','Rev L | keyed cup and removable sensor mount',camera=(400,-650,400))
    h.render(exploded,folder/'flex_exploded.png','Rev L | assembly layers | reaction plate omitted',camera=(400,-650,400))
    h.save(R/'verification/revL_components.json',dict(parts=rows,reference_note='Isolated module omits original reaction plate and clutch cartridge; actual connection is in character assembly',manufacturing_released=False,nominal=dict(board_datum_mm=P,magnet_bottom_mm=MAG_BOTTOM,magnet_face_mm=MAG_TOP,magnet_gap_mm=GAP,cap_stop_bottom_mm=CAP_BOTTOM,cap_stop_top_mm=CAP_TOP,custom_standoff_height_mm=POST_TOP-47,old_head_probe_board_datum_mm=63.995,board_datum_reduction_mm=63.995-P)))
    print(json.dumps(dict(component_entities=len(rows),board_datum=P,board_datum_reduction=63.995-P)),flush=True)
if __name__=='__main__':main()
