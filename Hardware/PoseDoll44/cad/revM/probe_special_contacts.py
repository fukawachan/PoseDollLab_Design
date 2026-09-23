from special_travel_stops import *
A,_=build('manny')
for label,pose,a,b in [('forward_up',h.cases()['forward_up'],'l_clavicle_output_frame','chest_M_body_frame'),('back_down',h.cases()['back_down'],'l_flex_sensor_board_M2x6_0','clavicle_l_protract_G4_fixed_reaction_plate')]:
 items={q['name']:q for q in A.scene(pose)};s=items[a]['shape'].intersect(items[b]['shape']);bb=s.BoundingBox();print(label,'contact',s.Volume(),s.Center().toTuple(),[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax],flush=True)
print('neck',A.A0['head.yaw']['origin'].tolist(),'chest',A.A0['chest.yaw']['origin'].tolist(),flush=True)
