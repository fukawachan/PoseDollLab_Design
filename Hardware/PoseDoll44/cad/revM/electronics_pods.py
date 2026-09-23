"""Six removable regional-node pods; positive board capture without PCB holes.
Connector / cable spaces are separately identified envelopes, not measured wires.
"""
from trunk_dual_friction import *
import trunk_dual_friction as bearings
from functools import lru_cache
COL['silicone']=(.18,.20,.23)

def xcyl(a,b,r,y=0,z=0):return h.axis_cyl(0,a,b,r,(0,y,z))
def xhex(af,a,b,y,z):return hexagon(af,a,b).rotate((0,0,0),(0,1,0),90).translate((0,y,z))

@lru_cache(None)
def pod_parts():
 outer=cube((36,44,100));cavity=cube((32.4,40.4,96.4));wall=outer.cut(cavity)
 main=wall.intersect(cube((60,100,120),(18,0,0))) # X -12..18
 lid=wall.intersect(cube((60,100,120),(-42,0,0))) # X -18..-12
 bits=[];pairs=[]
 for sy in (-1,1):
  for sz in (-1,1):
   y,z=sy*17.,sz*46.;tag=f'{sy}_{sz}'
   main=fuse_checked(main,cube((28.2,6,6),(2.1,y,z)),'pod_main_boss')
   main=fuse_checked(main,cube((16.2,6,3),(8.1,y,sz*41.5)),'board_support')
   lid=fuse_checked(lid,cube((4.2,6,9),(-14.1,y,sz*44.5)),'lid_bolt_boss')
   lid=fuse_checked(lid,cube((14.2,6,3),(-9.1,y,sz*41.5)),'lid_board_clamp')
   main=main.cut(xcyl(-12.1,10,1.2,y,z)).cut(xhex(4.2,4.5,6.3,y,z))
   main=main.cut(cube((1.8,12,4.2),(5.4,y+sy*6,z)))
   lid=lid.cut(xcyl(-18.1,-11.9,1.2,y,z)).cut(xcyl(-18.1,-16,2.1,y,z))
   bolt=xcyl(-16,9,1,y,z).fuse(xcyl(-18,-16,1.9,y,z)).cut(xhex(1.5,-18.1,-16.7,y,z))
   nut=xhex(4,4.5,6.1,y,z).cut(xcyl(4.4,6.2,.8,y,z))
   bits += [(f'lid_M2x25_{tag}',bolt,'metal','M2x25 clamps case seam; polymer pads retain board without drilled holes'),(f'lid_nut_M2_{tag}',nut,'metal','M2 nut inserted radially from open side slot')]
   pairs.append([f'lid_M2x25_{tag}',f'lid_nut_M2_{tag}'])
   for face,x in [('front',-.2),('rear',-1.8)]:bits.append((f'board_pad_{face}_{tag}',cube((.4,5.8,2.4),(x,y,sz*41.5)),'silicone','0.5 mm free silicone sheet, nominal 0.4 mm installed; PCB corner support, no solder-pad contact'))
 for sign in (-1,1):
  y,z=sign*8.,sign*30.
  main=fuse_checked(main,xcyl(11.8,18,5,y,z),'pod_mount_boss').cut(xhex(5.7,11.7,14.4,y,z)).cut(xcyl(14.3,18.1,1.7,y,z))
  nut=xhex(5.5,12,14.4,y,z).cut(xcyl(11.9,14.5,1.25,y,z));bolt=xcyl(11.2,21.2,1.5,y,z).fuse(xcyl(21.2,24.2,2.75,y,z)).cut(xhex(2.5,22.7,24.3,y,z))
  bits += [(f'mount_nut_M3_{sign}',nut,'metal','M3 captive nut installed from inside before PCB'),(f'mount_M3x10_{sign}',bolt,'metal','M3x10 through separate carrier; serviceable from the open torso')]
  pairs.append([f'mount_nut_M3_{sign}',f'mount_M3x10_{sign}'])
  # The centre pod accepts the carrier/frame bolts; all six cases share this relief.
  main=main.cut(xcyl(12.5,18.1,2.1,0,sign*15))
 for z in (-50,50):
  opening=cube((24,22,10),(0,0,z));main=main.cut(opening);lid=lid.cut(opening)
 bits += [('case_front',main,'shell','36 x44 x100 mm printed pod; 1.8 mm walls; removable rear lid; top/bottom wire exits'),('case_rear',lid,'shell','Removable lid includes insulated board corner supports; requires all four M2x25 screws')]
 for n,s,m,t in bits:assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
 return bits,pairs

@lru_cache(None)
def pcba():
 source=ROOT/'electronics/regional_revM/regional_assembly_work.step'
 model=cq.importers.importStep(str(source)).val()
 # Five models were absent from the local KiCad library. Add conservative package
 # bodies at verified footprint coordinates. These are explicitly not vendor STEP.
 missing=[('U4',(1.5,2,.7),(0,-27,1.55)),('J4',(9.2,7.6,3.4),(0,-39.2,2.9)),('J1',(7.95,6.6,6.6),(-14.6,-30.5,4.5)),('L1',(4.2,4.2,1.8),(-14.5,19.5,-.9)),('U2',(2,2,.8),(-10,19,-.4))]
 compound=cq.Compound.makeCompound([model]+[cube(size,pos) for _,size,pos in missing])
 loc=cq.Location(cq.Plane(origin=(-1.6,0,0),normal=(1,0,0),xDir=(0,1,0)))
 return compound.moved(loc),dict(source=str(source.relative_to(ROOT)),missing_vendor_models=[r[0] for r in missing],mass_budget_kg=.024)

def add_pod(A,node,owner,O):
 prefix=f'N{node}_';parts,pairs=pod_parts();O=np.asarray(O)
 for n,s,m,note in parts:A.add(prefix+n,s.translate(tuple(O)),m,owner,note)
 A.thread_pairs.extend([[prefix+n for n in pair] for pair in pairs])
 sh,info=pcba();sh=sh.translate(tuple(O));assert sh.isValid()
 # A bought PCBA is intentionally a compound of its board and soldered parts.
 A.parts.append(dict(name=prefix+'regional_PCBA',local_shape=sh.translate(tuple(-A.T0[owner][:3,3])),material='pcb_component',owner=owner,role='purchased_assembly',note='Native KiCad assembly plus five conservative body envelopes; no plug geometry included; no internal component-to-component collision inference',mass_kg_override=.024))
 # Loose service wiring and mated plug space are checked against the case geometry.
 # They are routing allocations, not collision-exempt claims about actual wires.
 plugs=[]
 for u in (-12,0,12):
  for v in (5,-6,-17):plugs.append(dict(connector='sensor_SH',shape=cube((10,9,6),(-6.6,u,v))))
 for u in (0,12):plugs.append(dict(connector='CAN_GH',shape=cube((11,7,8),(-7.1,u,14))))
 plugs.append(dict(connector='power_PH',shape=cube((12,10,8),(5.6,-14.6,-30.5))))
 for i,r in enumerate(plugs):
  # Package contact with its own receptacle is intended. Only rigid case/fasteners
  # and PCB edge supports are evaluated here, not the PCBA internals.
  obstruct=[]
  for n,s,_,_ in parts:
   bb1=r['shape'].BoundingBox();bb2=s.BoundingBox()
   if all(min(getattr(bb1,k+'max'),getattr(bb2,k+'max'))-max(getattr(bb1,k+'min'),getattr(bb2,k+'min'))>1e-5 for k in 'xyz'):
    vol=r['shape'].intersect(s).Volume()
    if vol>.02:obstruct.append([n,vol])
  assert not obstruct,(node,r['connector'],i,obstruct)
 return dict(node=node,owner=owner,origin_mm=O.tolist(),external_mm=[36,44,100],PCB=info,plug_allocation_checked=True,wire_exit_mm=[24,22],board_corner_pad_free_mm=.5,physical_tested=False)

def add_carrier(A,owner,centre):
 O=np.asarray(centre);base=A.T0[owner][:3,3];offset=O-base;prefix=owner+'_electronics_'
 # Case fronts are X=-87 relative to body origin. Carrier is deliberately separate.
 sh=union_checked([cube((3,136,8),tuple(base+[-85.3,0,offset[2]+z])) for z in (-30,30)]+[cube((3,8,68),tuple(base+[-85.3,y,offset[2]])) for y in (-12,12)],'electronics_carrier')
 for y in (-46,0,46):
  for sg in (-1,1):sh=sh.cut(h.axis_cyl(0,-87,-83.7,1.7,base+[0,y+sg*8,offset[2]+sg*30]))
 # Extend the fixed body frame with a rear central rail; no rail crosses a joint.
 frame,fw=world_part(A,owner+'_M_body_frame')
 if owner=='chest':path=[base+[-57,0,0],base+[-78,0,0],base+[-78,0,75]]
 else:path=[base+[-78,0,-65],base+[-78,0,0]]
 fw=fuse_checked(fw,rails(path,4),'fixed_electronics_spine')
 for i,zz in enumerate((-15,15)):
  z=offset[2]+zz;P=base+[-78,0,z]
  fw=fuse_checked(fw,cube((8,10,10),tuple(P)),'carrier_frame_lug');fw=fw.cut(h.axis_cyl(0,-83,-73.9,1.7,base+[0,0,z]))
  sh=fuse_checked(sh,cube((4.8,12,10),tuple(base+[-84.4,0,z])),'carrier_boss')
  # Connect both lugs to the carrier uprights rather than relying on contact.
  sh=fuse_checked(sh,cube((3,24,8),tuple(base+[-85.3,0,z])),'carrier_crossbar')
  sh=sh.cut(h.axis_cyl(0,-87,-81.9,1.7,base+[0,0,z])).cut(xhex(5.7,-86.8,-84.4,0,z).translate(tuple(base)))
  bolt=xcyl(-90,-74,1.5,0,z).fuse(xcyl(-74,-71,2.75,0,z)).cut(xhex(2.5,-72.5,-70.9,0,z));nut=xhex(5.5,-86.8,-84.4,0,z).cut(xcyl(-86.9,-84.3,1.25,0,z))
  bn=prefix+f'frame_M3x16_{i}';nn=prefix+f'frame_nut_M3_{i}';A.add(bn,bolt.translate(tuple(base)),'metal',owner,'M3x16 from open torso into captured carrier nut; two spaced joints');A.add(nn,nut.translate(tuple(base)),'metal',owner,'Insert M3 nut from rear before fitting centre node case');A.thread_pairs.append([bn,nn])
 replace_world(A,frame,fw,frame['note']+'; fixed rear electronics spine and two flat bolt lugs',frame['material'])
 A.add(prefix+'carrier',sh,'frame',owner,'Three removable regional nodes on rigid ladder carrier; four PCB clamping screws per pod; all printed below A1 mini envelope')

def build(name):
 A,meta=bearings.build(name);rows=[]
 for owner,ids,z in [('chest',(4,2,3),45),('pelvis',(6,1,5),-20)]:
  base=A.T0[owner][:3,3];add_carrier(A,owner,base+[0,0,z])
  for node,y in zip(ids,(-46,0,46)):rows.append(add_pod(A,node,owner,base+[-105,y,z]))
 return A,dict(meta,electronics_pods=rows)

def main():
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name);aff={q['name'] for q in A.parts if q['name'].startswith('N') or '_electronics_' in q['name'] or q['name'] in ('chest_M_body_frame','pelvis_M_body_frame')};cache=CollisionCache(A);checks=[]
  cases=dict(h.cases());cases.update(sit={'thigh_l.flex':90,'thigh_r.flex':90,'calf_l.flex':90,'calf_r.flex':90},trunk_bend={'waist.pitch':40,'chest.pitch':30},trunk_extend={'waist.pitch':-20,'chest.pitch':-20},trunk_roll={'waist.roll':25,'chest.roll':20})
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,aff,label!='neutral'),A.parts);bad=[r for r in review if r['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,review=review));print(json.dumps(dict(character=name,pose=label,structural_count=len(bad),first=bad[:8])),flush=True)
  out[name]=dict(pods=meta['electronics_pods'],checks=checks);h.save(ROOT/'verification/revM_electronics_mounts_work.json',out)
if __name__=='__main__':main()
