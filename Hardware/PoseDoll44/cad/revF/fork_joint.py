"""Complete fork axis using the Rev F face clutch and separate encoder.
The axle line is local Z. Input anchors lie on the back of the fixed frame;
output leaves the rotating outer cap so the connecting link clears the frame.
"""
from pivot import *

def hexprism(af,z,h):return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).translate((0,0,z)).val()

def module(size='M6',span=10,angle=0,with_encoder_support=True):
 sp=SPECS[size];d=sp['shaft'];parts=[];fixed_shapes=[];q=matrix(rotation([0,0,1],angle));supports=[]
 def add(n,s,m,o,note=''):parts.append(shape_record(n,s,m,o,'fork_'+size,note))
 C=orient((0,0,1),(0,0,span));E=orient((0,0,-1),(0,0,-span))
 for tag,items,base in [('C',friction(size),C),('E',encoder(d),E)]:
  for p in items:
   T=base if p['owner']=='fixed' else q@base
   add(tag+'_'+p['name'],move(p['shape'],T),p['material'],p['owner'],p['note'])
  radius=max(19,sp['ro']+6) if tag=='C' else 20
  for side in (-1,1):
   y=side*radius
   block=cube((8,7,6),(0,y,8));block=hole(block,0,y,1.8)
   block=block.cut(hexprism(6,7.8,4).translate((0,y,0)))
   fixed_shapes.append(move(block,base));supports.append((base@np.array([0,y,8,1]))[:3])
   washer=ring(3.5,1.6,.5,.5).translate((0,y,0))
   screw=cyl(1.5,.5,10).fuse(cyl(2.75,-2.5,3)).translate((0,y,0))
   nut=hexprism(5.5,7.8,2.4).cut(cyl(1.3,7.7,2.7)).translate((0,y,0))
   add(tag+'_mount_washer_'+str(side),move(washer,base),'fastener','fixed')
   add(tag+'_mount_screw_'+str(side),move(screw,base),'fastener','fixed')
   add(tag+'_mount_nut_'+str(side),move(nut,base),'fastener','fixed')
 # Printed truss remains outside the metal spring loop. Back pads accept the next frame.
 rails=[]
 for side in (-1,1):
  a=np.array([-24.,side*16.,-span-8]);b=np.array([-24.,side*16.,span+8]);fixed_shapes.append(rod(a,b,3.3));rails.append((a,b))
 for pos in supports:
  dest=np.array([-24.,math.copysign(16,pos[1]),pos[2]])
  fixed_shapes.append(rod(pos,dest,3.3))
 fixed_shapes.append(rod(rails[0][0],rails[1][0],3.3))
 back=cube((6,40,9),(-24,0,-span-8))
 for y in (-12,12):back=back.cut(rod((-28,y,-span-8),(-20,y,-span-8),1.8))
 fixed_shapes.append(back)
 if with_encoder_support:
  # Side posts hold the adjustment bridge without entering the rotating magnet cup.
  for x in (-11,11):
   local=rod((x,22,8),(x,22,24.4),2.5).fuse(cube((5,16.5,3),(x,16.25,25.9)))
   # Flatten top member to remain within the 3mm bridge thickness and away from washers.
   local=local.cut(cube((40,50,10),(0,10,32.4)))
   fixed_shapes.append(move(local,E))
   pos=(E@np.array([x,22,8,1]))[:3];dest=np.array([-24,math.copysign(16,pos[1]),pos[2]])
   fixed_shapes.append(rod(pos,dest,2.5))
  # Unite bridge with the printed fixed fork; metal/PCB hardware stays separate.
  bridge=next(p for p in parts if p['name']=='E_PCB_alignment_bridge');fixed_shapes.append(bridge['shape']);parts.remove(bridge)
 frame=fixed_shapes[0]
 for shape in fixed_shapes[1:]:frame=frame.fuse(shape)
 # Final drilling follows all unions; bridge ribs must not refill the fastener holes.
 for tag,base in [('C',C),('E',E)]:
  radius=max(19,sp['ro']+6) if tag=='C' else 20
  frame=frame.cut(move(cyl(max(radius+5,26),-.05,5.05),base))
  for side in (-1,1):
   y=side*radius
   frame=frame.cut(move(cyl(1.8,-3,16).translate((0,y,0)),base))
   frame=frame.cut(move(hexprism(6,7.8,8).translate((0,y,0)),base))
 frame=frame.cut(cube((20,36,12),(-37,0,-span-8)))
 for yy in (-12,12):
  frame=frame.cut(rod((-40,yy,-span-8),(-12,yy,-span-8),1.8))
  frame=frame.cut(move(hexprism(6,0,5),orient((1,0,0),(-21,yy,-span-8))))
 add('printed_fixed_fork',frame,'printed','fixed','Metal bearing inserts bolt to four pads; two rear M3 ports; encoder side posts integrated')
 # Both trunnions engage one positive-drive split hub. No sensor PCB carries joint loads.
 hub=cyl(d/2+4,-span+3,2*(span-3))
 for base in (C,E):hub=hub.cut(move(Dshape(d+.4,d/2-.3,-9.1,6.2),base))
 for zz in (-span+6,span-6):
  hub=hub.fuse(cube((5,14,5),(d/2+1.8,0,zz))).cut(cube((8,.7,5.2),(d/2+3,0,zz)))
  hub=hub.cut(rod((d/2+1.8,-9,zz),(d/2+1.8,9,zz),1.3))
  pocket=hexprism(4.4,0,2).rotate((0,0,0),(1,0,0),90).translate((d/2+1.8,-4.8,zz))
  hub=hub.cut(pocket)
  hub=hub.cut(rod((d/2+1.8,6,zz),(d/2+1.8,10,zz),2.1))
  screw=rod((d/2+1.8,-8,zz),(d/2+1.8,6,zz),1).fuse(rod((d/2+1.8,6,zz),(d/2+1.8,8,zz),1.9))
  nut=hexprism(4,0,1.6).cut(cyl(.85,-1,4)).rotate((0,0,0),(1,0,0),90).translate((d/2+1.8,-4.9,zz))
  add('hub_clamp_screw_'+str(zz),move(screw,q),'fastener','rotor');add('hub_clamp_nut_'+str(zz),move(nut,q),'fastener','rotor')
 for base in (C,E):hub=hub.cut(move(Dshape(d+.4,d/2-.3,-9.1,6.2),base))
 add('split_rotor_hub',move(hub,q),'printed','rotor','Inner D sockets plus two M2 clamps; dimensions provisional for PLA')
 cap_bottom=SPRING_Z+2*(sp['test']+(sp['parallel']-1)*sp['t']);output_z=span+cap_bottom+5
 output=ring(16,4.2,output_z,4)
 for x in (-11,11):
  output=hole(output,x,0,1.3)
  add('output_spacer_'+str(x),move(ring(2.5,1.1,span+cap_bottom+3,2).translate((x,0,0)),q),'aluminum','rotor')
  screw=cyl(1,output_z+4-10,10).fuse(cyl(1.9,output_z+4,2)).translate((x,0,0))
  add('output_screw_'+str(x),move(screw,q),'fastener','rotor','M2x10; engages tapped metal cap; tip clearance explicitly checked')
 for y in (-11,11):output=hole(output,0,y,1.8)
 add('printed_output_flange',move(output,q),'printed','rotor','Two downstream M3 ports at (0,+/-11); central tool access to preload screw')
 return parts,{'input_mm':[-24,0,-span-8],'input_axis':[1,0,0],'input_hole_pitch_mm':24,'output_mm':[0,0,output_z+4],'output_axis':[0,0,1],'output_hole_pitch_mm':22,'bearing_span_mm':2*(span+3),'joint_axis':[0,0,1],'encoder_positive_angle_sign_wrt_joint':-1,'spring_force_N':sp['F']*sp['parallel']}

def exception_pairs(parts):
 result=set();names={p['name'] for p in parts}
 for tag,items in [('C',friction('M6')),('E',encoder(6))]:
  for pair in allowed(items):result.add(frozenset(tag+'_'+n for n in pair))
 for tag in ('C','E'):
  for side in (-1,1):result.add(frozenset((tag+'_mount_screw_'+str(side),tag+'_mount_nut_'+str(side))))
 for zz in (-4,4,-4.0,4.0):result.add(frozenset(('hub_clamp_screw_'+str(zz),'hub_clamp_nut_'+str(zz))))
 for x in (-11,11):result.add(frozenset(('output_screw_'+str(x),'C_keyed_stop_cap')))
 return {pair for pair in result if pair<=names}

def main():
 report={'status':'FORK_AXIS_DEVELOPMENT_NOT_MANUFACTURING_RELEASE','physical_tested':False,'families':{}}
 for size in ('S6','M6','H6','L8'):
  parts,ports=module(size);folder=OUT/'joints'/('J_'+size);folder.mkdir(exist_ok=True)
  assembly=cq.Assembly(name='J_'+size);manifest=[]
  for p in parts:
   s=p['shape'];assembly.add(s,name=p['name'],color=cq.Color(*COL[p['material']]))
   b=s.BoundingBox();manifest.append({k:v for k,v in p.items() if k!='shape'}|{'mass_g':mass(p),'valid':s.isValid(),'solid_count':len(s.Solids()),'bbox_mm':[b.xlen,b.ylen,b.zlen]})
   if p['material']=='printed':cq.exporters.export(s,str(folder/(p['name']+'.step')))
  assembly.save(str(folder/('RevF_J_'+size+'.step')))
  allowed_set=exception_pairs(parts);hits=pair_hits(parts);bad=[h for h in hits if frozenset((h['a'],h['b'])) not in allowed_set]
  rows=[]
  for angle in range(0,360,30):
   posed=[dict(p,shape=p['shape'].rotate((0,0,0),(0,0,1),angle)) if p['owner']=='rotor' else p for p in parts]
   rows.append({'angle_deg':angle,'hits':pair_hits(posed,skip_same_owner=True)})
  report['families'][size]={'parts':manifest,'ports':ports,'mass_g':sum(mass(p) for p in parts),'unplanned_assembly_hits':bad,'rotation_samples':rows,'intentional_thread_intersections':[h for h in hits if h not in bad]}
  print(json.dumps({'size':size,'parts':len(parts),'mass_g':report['families'][size]['mass_g'],'assembly_hits':bad,'rotating_hits':sum(len(x['hits']) for x in rows)}),flush=True)
  if size=='M6':render([(p['name'],p['shape'],COL[p['material']]) for p in parts],OUT/'images/RevF_J_M6.png','Rev F | double-bearing fork + single-face clutch + separate encoder | development')
 save(ROOT/'verification/revF_fork_joints.json',report)
if __name__=='__main__':main()
