"""Removable pelvis power compartment; external regulated 5 V only.
PCB/plug models are bought assemblies, with explicit conservative missing bodies.
"""
from sensor_cable_heads import *
import sensor_cable_heads as body
from functools import lru_cache
COL['nylon']=(.80,.81,.77)

@lru_cache(None)
def power_pcba():
 model=cq.importers.importStep(str(ROOT/'electronics/power_revM/power_assembly_work.step')).val()
 # Native export: origin (50,65), KiCad Y inverted, board top = 1.6 mm.
 # PJ-002AH drawing: 14.4 x9 x11 mm; conservative envelope includes tolerance.
 extra=[cube((9.6,15.,11.5),(0,-27.8,7.35)),cube((6.3,2.94,2.94),(10,-21.3,3.07))]
 pads=json.loads((ROOT/'electronics/power_revM/pad_map.json').read_text(encoding='utf8'))
 for n,(x,y,_) in pads['J1'].items():
  sx,sy=(.5,3.0) if n in ('1','2') else (2.5,.5)
  extra.append(cube((sx,sy,3.7),(x-50,65-y,-.25)))
 sh=cq.Compound.makeCompound([model]+extra)
 loc=cq.Location(cq.Plane(origin=(-22,0,-15),normal=(-1,0,0),xDir=(0,-1,0)))
 return sh.moved(loc),loc

def compartment(A,O):
 O=np.array(O);q,lid=world_part(A,'N1_case_rear');lid=lid.translate(tuple(-O));before=lid.Volume()
 outer=cube((22,44,100),(-29,0,0));inner=cube((20.3,40.4,96.4),(-28.05,0,0));wall=outer.cut(inner)
 extension=wall.intersect(cube((100,80,120),(16,0,0))) # x >= -34
 rear=wall.intersect(cube((100,80,120),(-84,0,0))) # x <= -34
 lid=fuse_checked(lid,extension,'power_extension')
 bits=[];pairs=[]
 # Four threaded board supports, accessed after removing the rear cover.
 for yy in (-17.,17.):
  for zz in (-38.,17.):
   tag=f'{yy}_{zz}';post=xcyl(-22,-17.8,3.3,yy,zz)
   lid=fuse_checked(lid,post,'power_board_post').cut(xcyl(-24,-16.1,1.2,yy,zz)).cut(xhex(4.2,-20.4,-18.6,yy,zz))
   # Radial captive-nut insertion, at the side facing the open centre.
   lid=lid.cut(cube((1.8,9,4.2),(-19.5,yy-(4.5 if yy>0 else -4.5),zz)))
   washer=xcyl(-24.1,-23.6,2.5,yy,zz).cut(xcyl(-24.2,-23.5,1.1,yy,zz))
   bolt=xcyl(-24.1,-16.1,1,yy,zz).fuse(xcyl(-26.1,-24.1,1.9,yy,zz)).cut(xhex(1.5,-26.2,-24.8,yy,zz))
   nut=xhex(4,-20.3,-18.7,yy,zz).cut(xcyl(-20.4,-18.6,.8,yy,zz))
   bits += [('PCB_washer_'+tag,washer,'nylon','M2 nylon flat washer, 5 OD x2.2 ID x0.5; isolates screw head from board'),('PCB_M2x8_'+tag,bolt,'metal','M2x8 into captive nut; remove power before servicing'),('PCB_nut_'+tag,nut,'metal','M2 captive nut inserted from inner radial opening before fitting PCB')]
   pairs.append(['PCB_M2x8_'+tag,'PCB_nut_'+tag])
 # Rear cover fasteners do not share the regional board or its service screws.
 for sy in (-1,1):
  for sz in (-1,1):
   yy,zz=18*sy,45*sz;tag=f'{sy}_{sz}'
   lid=fuse_checked(lid,xcyl(-34,-26,3.2,yy,zz),'power_main_boss').cut(xcyl(-34.1,-25.9,1.2,yy,zz)).cut(xhex(4.2,-30,-28.2,yy,zz))
   lid=lid.cut(cube((1.8,10,4.2),(-29.1,yy+sy*5,zz)))
   rear=fuse_checked(rear,xcyl(-38.3,-34,3.2,yy,zz),'power_cover_boss').cut(xcyl(-40.1,-33.9,1.2,yy,zz)).cut(xcyl(-40.1,-38,2.1,yy,zz))
   bolt=xcyl(-38,-28,1,yy,zz).fuse(xcyl(-40,-38,1.9,yy,zz)).cut(xhex(1.5,-40.1,-38.7,yy,zz));nut=xhex(4,-29.9,-28.3,yy,zz).cut(xcyl(-30,-28.2,.8,yy,zz))
   bits += [('cover_M2x10_'+tag,bolt,'metal','M2x10 removable power cover screw'),('cover_nut_'+tag,nut,'metal','M2 captive nut inserted from outside before fitting rear cover')];pairs.append(['cover_M2x10_'+tag,'cover_nut_'+tag])
 # Housing loads from DC-plug insertion transfer to the printed seat behind jack.
 # 0.3 mm nominal end float; do not use solder joints as the mechanical stop.
 stop=union_checked([cube((11.9,13,1.8),(-29.95,0,-34.1)),cube((1.7,44,1.8),(-33.05,0,-34.1))],'jack_backstop');lid=fuse_checked(lid,stop,'jack_backstop')
 # An insertion opening, not a chamfer hiding interference. Leave jack front flush.
 opening=cube((15,12,5),(-29.4,0,-50));lid=lid.cut(opening);rear=rear.cut(opening)
 # PCB ends at the jack-facing lower edge; provide a real protected edge slot.
 lid=lid.cut(cube((2.2,40.6,3),(-22.8,0,-49.5)))
 # Top exit for all six insulated 5 V pairs. Internal clear volume is checked below.
 exit_tool=cube((10,16,8),(-28,0,50));lid=lid.cut(exit_tool);rear=rear.cut(exit_tool)
 # Recessed zip-tie bridge holds the stationary branch bundle, away from the PCB.
 anchor=cube((3.6,20,6),(-19.8,0,38));lid=fuse_checked(lid,anchor,'power_strain_relief').cut(cube((1.8,14,3),(-20.0,0,38)))
 replace_world(A,q,lid.translate(tuple(O)),q['note']+'; integrated protected rear power compartment, four PCB posts and supported downward DC jack',q['material'])
 A.add('POWER_case_rear',rear.translate(tuple(O)),'shell','pelvis','Removable 1.8 mm wall rear cover; four M2x10 fasteners; top branch-cable exit; DC plug enters from below')
 for n,s,m,t in bits:A.add('POWER_'+n,s.translate(tuple(O)),m,'pelvis',t)
 A.thread_pairs.extend([['POWER_'+n for n in pair] for pair in pairs])
 sh,loc=power_pcba();sh=sh.translate(tuple(O))
 A.parts.append(dict(name='POWER_PCBA',local_shape=sh.translate(tuple(-A.T0['pelvis'][:3,3])),material='pcb_component',owner='pelvis',role='purchased_assembly',note='Native KiCad power board plus jack, terminal and F0 maximum-body allocations; bought assembly, internal overlaps intentional',mass_kg_override=.026))
 # Check purchased assembly against every rigid case component, including old lid.
 rigid=[('N1_case_rear',lid),('POWER_case_rear',rear)]+[(n,s) for n,s,_,_ in bits];native=sh.translate(tuple(-O));contacts=[]
 for n,s in rigid:
  v=native.intersect(s).Volume()
  if v>.02:contacts.append([n,v])
 # PH housings mate on the front/component side of this rear-facing PCB.
 plugs=[]
 for i,(x,y) in enumerate([(36,40),(62,40),(36,55),(62,55),(36,70),(62,70)],1):
  env=cube((8,7.5,10),(x-49,65-y,6.6)).moved(loc)
  for n,s in rigid:
   v=env.intersect(s).Volume()
   if v>.02:contacts.append([f'N{i}_plug / '+n,v])
  plugs.append(dict(node=i,centre_local_mm=[(env.BoundingBox().xmin+env.BoundingBox().xmax)/2,(env.BoundingBox().ymin+env.BoundingBox().ymax)/2,(env.BoundingBox().zmin+env.BoundingBox().zmax)/2],allocated_mm=[8,7.5,10]))
 if contacts:
  for n,s in rigid:
   for i,solid in enumerate(native.Solids()):
    hit=s.intersect(solid)
    if hit.Volume()>.02:print('POWER_OBSTRUCTION',n,i,hit.Volume(),hit.Center().toTuple(),flush=True)
 assert not contacts,contacts
 return dict(origin_mm=O.tolist(),PCB_mass_allowance_kg=.026,case_added_volume_mm3=lid.Volume()-before,board_holes_yz_mm=[[-17,-38],[-17,17],[17,-38],[17,17]],PCB_plug_allocations=plugs,power_input='regulated 5 V / center positive / 5.5 OD plug / PJ-002AH socket',physical_tested=False)

def build(name):
 A,meta=body.build(name);info=compartment(A,A.T0['pelvis'][:3,3]+[-105,0,-20]);return A,dict(meta,power_compartment=info)

def main():
 if '--component' in sys.argv:
  from types import SimpleNamespace
  A=SimpleNamespace(T0={'pelvis':np.eye(4)},thread_pairs=[],parts=[])
  def add(n,s,m,o,t):
   assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
   A.parts.append(dict(name=n,local_shape=s,material=m,owner=o,role='part',note=t))
  A.add=add
  for n,s,m,t in pod_parts()[0]:
   if n=='case_rear':add('N1_'+n,s,m,'pelvis',t)
  info=compartment(A,np.zeros(3));print(json.dumps(info),flush=True)
  rows=[dict(q,shape=q['local_shape']) for q in A.parts]
  bad=fast_contacts(rows,A.thread_pairs,None,False);assert not bad,bad
  print('Power component: valid solids, no rigid contacts',flush=True)
  h.render([(q['name'],q['local_shape'],COL[q['material']]) for q in A.parts],ROOT/'generated/revM/power_compartment_component.png','Power compartment | candidate',camera=(-130,-190,80))
  return
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name)
  interfaces=dict(character=name,profile=A.profile,nodes_neutral={k:v.tolist() for k,v in A.T0.items()},channels=channels41(A,name),pods=meta['electronics_pods'],power=meta['power_compartment'],parts=[])
  for q in A.scene({}):
   b=q['shape'].BoundingBox();interfaces['parts'].append(dict(name=q['name'],owner=q['owner'],material=q['material'],role=q['role'],bounds_mm=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]))
  h.save(ROOT/f'mechanical_manifest/interfaces_revM_{name}.json',interfaces)
  aff={q['name'] for q in A.parts if q['name'].startswith('POWER_') or q['name']=='N1_case_rear'};cases,_=poses(A);cache=CollisionCache(A);checks=[]
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,aff,label!='neutral'),A.parts);bad=[r for r in review if r['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,review=review))
   if bad:print(json.dumps(dict(character=name,pose=label,structural=bad)),flush=True)
  out[name]=dict(power=meta['power_compartment'],checks=checks);h.save(ROOT/'verification/revM_power_compartment_work.json',out);print(name,'finished',len(checks),'failed',sum(any(r['classification']=='structural' for r in x['review']) for x in checks),flush=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],ROOT/'generated/revM'/name/'power_compartment_work.png',name.title()+' | body and protected power compartment | candidate',camera=(-1700,-2800,1100))
if __name__=='__main__':main()
