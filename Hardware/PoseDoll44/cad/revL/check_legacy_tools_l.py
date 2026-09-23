"""Straight driver envelopes at explicitly staged neutral assembly; hand reach untested."""
from flex_encoder import *
from compact_twist import previous, MOUNT_RADIUS, MOUNT_Y, cross_cyl, PCB_DATUM

def main():
 results=[]
 for name in ('manny','quinn'):
  p,parts,meta=build(name);items,T,A=h.scene(parts,p,{})
  def check(stage,tool,omit,target):
   findings=[];removed=[];tb=tool.BoundingBox()
   for q in items:
    if q['role']=='reservation':continue
    if omit(q):removed.append(q['name']);continue
    bb=q['shape'].BoundingBox()
    if not all(min(getattr(tb,k+'max'),getattr(bb,k+'max'))-max(getattr(tb,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
    v=tool.intersect(q['shape']).Volume()
    if v>.02:findings.append(dict(part=q['name'],volume_mm3=round(v,4)))
   results.append(dict(character=name,stage=stage,target=target,not_installed=removed,unexpected_contacts=findings))
   if findings:print(json.dumps(results[-1]),flush=True)
  for side,sy in [('l',1),('r',-1)]:
   S=A[f'upperarm_{side}.flex']['origin']
   for label,normal,xd,base,tip in [('flex',(0,-sy,0),(1,0,0),43,-24),('abduct',(1,0,0),(0,0,1),26,-16)]:
    loc=previous.frame_transform(normal,xd,S+np.array(normal)*base)
    def omit(q):
     if label=='flex':
      return q['owner'] in (f'upperarm_{side}.abduct_frame',f'upperarm_{side}',f'elbow_{side}') or q['name'].startswith(side+'_abduct_clutch_')
     return q['name'].startswith((side+'_abduct_sensor_',side+'_twist_sensor_')) or q['name'] in (side+'_twist_bush',side+'_twist_shaft')
    tool=cyl(tip-60,tip-4.5,1.5).fuse(hexagon(2.5,tip-4.5,tip-2.55)).moved(loc)
    check(label+'_inner_M3_before_inner_parts',tool,omit,side+'_'+label+'_clutch_inner_M3x8')
    for i,x in enumerate((-MOUNT_RADIUS,MOUNT_RADIUS)):
     tool=cyl(tip-50,tip-2.1,1).fuse(hexagon(1.48,tip-2.1,tip-.95)).translate((x,MOUNT_Y,0)).moved(loc)
     check(label+'_flange_M2_before_inner_parts',tool,omit,side+'_'+label+'_drive_mount_M2x4_'+str(i))
    tool=cross_cyl(6.1,55,1,5.2,tip+3).fuse(hexagon(1.48,0,1.08).rotate((0,0,0),(0,1,0),90).translate((5.02,5.2,tip+3))).moved(loc)
    check(label+'_pinch_M2_before_inner_parts',tool,omit,side+'_'+label+'_drive_pinch_M2x10')
   loc=previous.frame_transform((-1,0,0),(0,0,sy),S)
   prefix=side+'_abduct_sensor_'
   # M2 journal screw is reached radially, preserving the earlier front M3 assembly order.
   tool=cross_cyl(6.1,45,1,0,15).fuse(hexagon(1.48,0,1.08).rotate((0,0,0),(0,1,0),90).translate((5.02,0,15))).moved(loc)
   check('rear_journal_radial_M2_before_twist',tool,lambda q:q['name'].startswith(side+'_twist_sensor_'),prefix+'journal_radial_M2x4')
   def board_removed(q):
    return q['name'].startswith(prefix+'pcb_') or q['name'].startswith(prefix+'board_M2x4_') or q['name'].startswith(prefix+'nylon_spreader_')
   # Nylon driver tips are not modeled. Envelope ends 0.1 mm outside each head.
   def carrier_omit(q):
    return board_removed(q) or q['name']==prefix+'diametric_magnet_6x2p5' or q['name']==prefix+'magnet_retaining_bridge' or q['name'].startswith(prefix+'magnet_cover_M2x6_')
   check('carrier_axial_M2_before_magnet_and_board',cyl(32.5,70,1).moved(loc),carrier_omit,prefix+'carrier_axial_M2x6')
   for i,x in enumerate((-5,5)):
    check('magnet_cover_M2_before_board',cyl(38.8,70,1).translate((x,0,0)).moved(loc),board_removed,prefix+'magnet_cover_M2x6_'+str(i))
   for i,x in enumerate((-6.5,6.5)):
    check('board_front_M2',cyl(12,PCB_DATUM-3.51,1).translate((x,6.5,0)).moved(loc),lambda q:False,prefix+'board_M2x4_'+str(i))
    check('board_support_rear_M2',cyl(PCB_DATUM+10.5,PCB_DATUM+40,1).translate((x,6.5,0)).moved(loc),lambda q:False,prefix+'support_M2x6_'+str(i))
 h.save(ROOT/'verification/revL_legacy_tool_access.json',dict(scope='Neutral staged geometry, 2 mm M2 driver shaft / 3 mm M3 shaft; no grip, torque or insertion sweep test',checks=results))
 print(json.dumps({'checks':len(results),'unexpected':sum(bool(q['unexpected_contacts']) for q in results)}),flush=True)
 if any(q['unexpected_contacts'] for q in results):raise RuntimeError('Tool path obstructed')
if __name__=='__main__':main()
