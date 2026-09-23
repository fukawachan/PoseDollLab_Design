from shoulder_revision import *
import hashlib
def main():
 folder=OUT/'components';folder.mkdir(parents=True,exist_ok=True)
 rows=[]
 modules={'D6_split_drive':hub(0),'abduction_encoder':make_encoder()}
 for name,parts in modules.items():
  assembly=cq.Assembly(name='RevJ_'+name)
  for q in parts:
   sh=q['shape'];assembly.add(sh,name=q['name'],color=cq.Color(*COL[q['material']]))
   bb=sh.BoundingBox()
   rows.append(dict(module=name,name=q['name'],material=q['material'],note=q['note'],solid_count=len(sh.Solids()),
    valid=sh.isValid(),bbox_mm=[bb.xlen,bb.ylen,bb.zlen],volume_mm3=sh.Volume()))
   if q['material'] in ('aluminum','frame'):cq.exporters.export(sh,str(folder/(name+'_'+q['name']+'.step')))
  assembly.save(str(folder/(name+'_assembly.step')))
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in parts if q['material']!='sensor_space'],folder/(name+'.png'),'Rev J | '+name+' | nominal CAD, not released',camera=(300,-500,240))
 source=ROOT/'generated/revC/step/sensor_revB.step'
 record=dict(status='COMPONENT_DESIGN_CANDIDATE_NOT_MANUFACTURING_RELEASE',parts=rows,physical_tested=False,
  qty_per_character={'D6_split_drive':4,'abduction_encoder':2},sensor_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
  drive_interface_mm=dict(shaft_d=6,shaft_flat_x=2.5,socket_d=BORE_D,socket_flat_x=FLAT_X,open_split=SPLIT,
    flange_thickness=1.5,mount_centres=[[x,MOUNT_Y] for x in (-MOUNT_RADIUS,MOUNT_RADIUS)],print_backing_start=1.5,print_backing_end=4,
    print_support_radial_limit=11.25),
  encoder_mm=dict(shaft_d=4,shaft_flat_x=1.5,shaft_start=12,shaft_end=30,board_datum=PCB_DATUM,
    magnet_diameter=6,magnet_height=2.5,magnet_front=MAGNET_TOP,package_surface_gap=PACKAGE_GAP,
    pcb_mount_xy=[[-6.5,6.5],[6.5,6.5]],spacer_height=6,nominal_board_thickness=1.6,step_board_thickness=1.51),
  sources={'magnet_guide':'https://ams-osram.com/documents/20143/80162/AnglePositionOnAxis_AN000271_2-00.pdf/bd13692b-b589-af7f-560c-4d62bf25d9dd?t=1519844940990',
   'M2_nominal_socket_head':'https://uk.misumi-ec.com/files/images/products/docs/hexsocketheadcapscrews.pdf'},
  manufacturing_gaps=['No final dimensions/tolerance/finish drawing or purchased fastener qualification','No elastic clamp FEA or tightening torque rating',
   'Printed flange creep and minimum web strength not qualified','Magnet adhesive selection, field and rotational slip untested',
   'Nylon pan head envelope 3.5 mm diameter x 1.4 mm high is a purchasing constraint, not a confirmed product'])
 h.save(ROOT/'verification/revJ_components.json',record)
 print(json.dumps({'logical_component_rows':len(rows),'valid':all(q['valid'] and q['solid_count']==1 for q in rows)}),flush=True)
if __name__=='__main__':main()
