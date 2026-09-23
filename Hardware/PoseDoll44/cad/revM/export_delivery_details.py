"""Delivery interfaces and two representative assemblies from the canonical body."""
from final_model import *
from full_body_audit import channels41

def stage(n):
 if any(x in n for x in ('pcb_','board_post','PCB_edge','PCB_M')):return 7
 if any(x in n for x in ('magnet','keeper','cup_M')):return 6
 if any(x in n for x in ('D_stop_cap','M3x8_button')):return 5
 if any(x in n for x in ('disc_spring','spring_seat','height_spacer')):return 4
 if any(x in n for x in ('fixed_metal_eye','radial_bush','thrust_wear','upper_face','upper_PEEK')):return 3
 if 'friction_lining' in n:return 2
 if 'flanged_rotor_shaft' in n:return 1
 return 0

def module_export(A,axis,folder):
 j=A.joints[axis];pre=j['prefix'];loc=j['loc'];selected=[p for p in A.parts if p['name'].startswith(pre) and not any(k in p['name'] for k in ('intermediate_frame','upperarm_carrier','proximal_forearm'))];ass=cq.Assembly(name=axis.replace('.','_'));regular=[];exploded=[];table=[]
 for q in selected:
  w=h.move(q['local_shape'],A.T0[q['owner']]).moved(loc.inverse);g=stage(q['name']);c=COL[q['material']];ass.add(w,name=q['name'],color=cq.Color(*c));regular.append((q['name'],w,c));exploded.append((q['name'],w.translate((0,0,g*20)),c));table.append(dict(name=q['name'],stage=g,material=q['material'],note=q['note']))
 stem=axis.replace('.','_');ass.save(str(folder/(stem+'_assembly.step')));h.render(regular,folder/(stem+'_assembled.png'),axis+' | actual final cartridge',camera=(150,-220,110));h.render(exploded,folder/(stem+'_exploded.png'),axis+' | assembly groups / not physical spacing',camera=(190,-280,140));h.save(folder/(stem+'_parts.json'),dict(axis=axis,parts=table,groups=['output cleat / retention','integral rotor shaft','lower PEEK lining','fixed eye / bush / reaction / upper lining','pressure plate / spring stack','keyed stop and axial retainer','magnet cup / magnet / retaining cover','sensor board and its mounting'],meta=j['meta']))

def main():
 for name in ('manny','quinn'):
  A,m=build(name);channels=channels41(A,name);parts=[]
  for q in A.parts:
   w=h.move(q['local_shape'],A.T0[q['owner']]);b=w.BoundingBox();parts.append(dict(name=q['name'],owner=q['owner'],material=q['material'],role=q['role'],bounds_mm=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]))
  h.save(ROOT/f'mechanical_manifest/interfaces_revM_{name}.json',dict(character=name,profile=A.profile,source_sha256=m['source_sha256'],nodes_neutral={o:T.tolist() for o,T in A.T0.items()},channels=channels,heads=m['sensor_heads'],pods=m['electronics_pods'],power=m['power_compartment'],parts=parts))
  h.save(ROOT/f'mechanical_manifest/physical_{name}_41_capabilities.json',dict(schema_version='1.0',capability_id=f'physical_{name}_41_pelvis_fixed_revM',profile_id=A.profile['profile_id'],measured_axis_ids=A.profile['axis_order'][3:],fixed_axis_values_rad={a:0 for a in A.profile['axis_order'][:3]}))
  h.save(ROOT/f'generated/revM/{name}/joints.json',[dict(axis_id=c['axis_id'],family=c['family'],fixed_owner=c['fixed_owner'],rotor_owner=c['magnet_owner'],geometry=c,cartridge=A.joints[c['axis_id']]['meta'] if c['axis_id'] in A.joints else None) for c in channels])
  if name=='manny':
   folder=ROOT/'generated/revM/assembly_details';folder.mkdir(exist_ok=True)
   for axis in ('waist.pitch','elbow_l.flex'):module_export(A,axis,folder)
  print(name,'interfaces and assembly details exported',flush=True)
if __name__=='__main__':main()
