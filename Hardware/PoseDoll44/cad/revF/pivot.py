"""Compact face-friction trunnion and opposite encoder support for a fork.
The spring load closes in metal through the friction face. The POM radial bush
is not in this preload path; an explicit replaceable thrust washer is.
"""
from common import *
from functools import lru_cache
SPRING_SOURCE='https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf'
THRUST_SOURCE='https://cdn.skfmediahub.skf.com/api/public/0901d19680090e01/pdf_preview_medium/0901d19680090e01_pdf_preview_medium.pdf'
SPRING_Z=7.0
SPECS={
 'S6':dict(shaft=6,ro=11,spring='002050',de=12.5,di=6.2,t=.35,free=.80,s=.338,test=.463,F=151,parallel=1),
 'M6':dict(shaft=6,ro=13,spring='002100',de=12,di=6.2,t=.5,free=.85,s=.263,test=.588,F=326,parallel=1),
 'H6':dict(shaft=6,ro=16,spring='002200',de=12,di=6.2,t=.6,free=.95,s=.263,test=.688,F=552,parallel=1),
 'L8':dict(shaft=8,ro=20,spring='003800',de=15,di=8.2,t=.7,free=1.1,s=.300,test=.800,F=666,parallel=2)}

def disk_spring(spec,z,flip=False):
 ro=spec['de']/2;ri=spec['di']/2;t=spec['t'];h=spec['test']
 points=[(ri,h-t),(ro,0),(ro,t),(ri,h)]
 if flip:points=[(r,h-d) for r,d in points]
 return cq.Workplane('XZ').polyline(points).close().revolve(360,(0,0),(0,1)).translate((0,0,z)).val()

def bush(d,z=1.1,h=3.8):
 return ring(d/2+1,d/2+.03,z,h).fuse(cube((2,2,h),(d/2+1,0,z+h/2))).cut(cyl(d/2+.03,z-1,h+2))

def eye(d,ro,z=1,h=4,mount_radius=None):
 mount_radius=ro+2 if mount_radius is None else mount_radius
 outer=cyl(ro,z,h)
 for side in (-1,1):outer=outer.fuse(cube((8,mount_radius-ro+7,h),(0,side*(ro+(mount_radius-ro)/2),z+h/2)))
 outer=outer.cut(cyl(d/2+1.02,z-1,h+2).fuse(cube((2.08,2.08,h+2),(d/2+1,0,z+h/2))))
 for side in (-1,1):outer=hole(outer,0,side*mount_radius,1.7)
 return outer

@lru_cache(None)
def friction(size='M6'):
 sp=SPECS[size];d=sp['shaft'];ro=sp['ro'];parts=[]
 def add(n,s,m,o,note=''):parts.append(shape_record(n,s,m,o,'friction_'+size,note))
 add('bearing_eye',eye(d,ro+1,mount_radius=max(19,ro+6)),'aluminum','fixed','Metal fork insert; two M3 mounts; non-round bush pocket')
 add('radial_bush',bush(d),'pom','fixed','Finished bore shaft+0.06; shaped OD prevents bush rotation; no axial preload')
 lining=ring(ro,d/2+1.1,0,1)
 for side in (-1,1):lining=lining.fuse(cube((3,2,1),(side*(ro-.5),0,.5)))
 # Printed material does not carry the spring clamp force. Lining tabs engage metal recesses.
 retaining=cyl(ro+1,0,1).cut(lining).cut(cyl(ro, -1,3))
 parts[0]['shape']=parts[0]['shape'].fuse(retaining)
 add('friction_lining',lining,'lining','fixed','1mm unqualified friction lining; two tabs prevent slipping in housing')
 total_pack=2*(sp['test']+(sp['parallel']-1)*sp['t']);cap_bottom=SPRING_Z+total_pack;end=cap_bottom+2
 shaft=cyl(d/2,-9,end+9).fuse(cyl(ro+1,-3,3))
 shaft=shaft.cut(cube((12,18,6),(d/2-.5+6,0,-6)))
 shaft=shaft.cut(cube((12,18,2.1),(d/2-.5+6,0,end-1.05)))
 bolt=3 if d==6 else 4;pilot=1.25 if d==6 else 1.65
 shaft=hole(shaft,0,0,pilot,end-9,end+1)
 add('flanged_trunnion',shaft,'aluminum','rotor','Smooth shaft; inner D drive; outer D key; blind thread; one active friction face')
 add('thrust_wear_washer',ring(10,5,5,1.5),'ptfe_composite','fixed','SKF PCMW102001.5 E dimensional candidate; steel-backed PTFE facing spring seat; counterface finish and availability require review')
 add('spring_seat',ring(10,d/2+.1,6.5,.5),'spring','rotor','Axially loaded steel spring seat; nominally follows spring stack')
 pack=sp['test']+(sp['parallel']-1)*sp['t']
 for j in range(sp['parallel']):
  add('spring_a_'+str(j),disk_spring(sp,SPRING_Z+j*sp['t']),'spring','rotor')
  add('spring_b_'+str(j),disk_spring(sp,SPRING_Z+pack+j*sp['t'],True),'spring','rotor')
 cap=cyl(d/2+4.5,cap_bottom,3).cut(Dshape(d+.1,d/2-.45,cap_bottom-.01,2.01))
 for x in (-11,11):
  cap=cap.fuse(cube((abs(x),6,3),(x/2,0,cap_bottom+1.5))).fuse(cyl(3,cap_bottom,3).translate((x,0,0)))
  cap=hole(cap,x,0,.8)
 clamp_y=d/2+2.4;clamp_z=cap_bottom+1.5
 for x in (-5.5,5.5):cap=cap.fuse(cube((5,5,3),(x,clamp_y,clamp_z)))
 cap=cap.cut(Dshape(d+.1,d/2-.45,cap_bottom-.01,2.01))
 cap=hole(cap,0,0,bolt/2+.15)
 cap=cap.cut(cube((.7,14,3.2),(0,8.6,clamp_z)))
 cap=cap.cut(rod((-12,clamp_y,clamp_z),(12,clamp_y,clamp_z),1.3))
 cap=cap.cut(rod((7,clamp_y,clamp_z),(12,clamp_y,clamp_z),2.1))
 hexnut=lambda af,z,h:cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).translate((0,0,z)).val()
 cap=cap.cut(move(hexnut(4.4,0,1.8),orient((1,0,0),(-8,clamp_y,clamp_z))))
 clamp_screw=rod((-9,clamp_y,clamp_z),(7,clamp_y,clamp_z),1).fuse(rod((7,clamp_y,clamp_z),(9,clamp_y,clamp_z),1.9))
 clamp_nut=hexnut(4,0,1.6).cut(cyl(.85,-1,4));clamp_nut=move(clamp_nut,orient((1,0,0),(-7.9,clamp_y,clamp_z)))
 add('key_clamp_screw',clamp_screw,'fastener','rotor','M2x16 closes split D key cap; shaft retention uses separate axial screw')
 add('key_clamp_nut',clamp_nut,'fastener','rotor')
 add('keyed_stop_cap',cap,'aluminum','rotor','Split D key with M2 clamp reduces assembly clearance; cap shoulder seats on shaft end; preload tolerance/shims and reversal backlash require testing')
 top=cap_bottom+3
 add('axial_retainer_screw',cyl(bolt/2,top-8,8).fuse(cyl(2.75 if bolt==3 else 3.5,top,3 if bolt==3 else 4)),'fastener','rotor','M3x8 or M4x8; simplified thread envelope; removable thread retention method pending')
 return parts

@lru_cache(None)
def encoder(d=6):
 # Reuse the magnet, retaining bridge and real PCB geometry already checked in H2.
 import clutch as h2
 parts=[]
 def add(n,s,m,o,note=''):parts.append(shape_record(n,s,m,o,'encoder_'+str(d),note))
 add('encoder_bearing_eye',eye(d,8,mount_radius=20),'aluminum','fixed','Same metal/POM bearing interface; two M3 mount ears')
 add('encoder_radial_bush',bush(d),'pom','fixed')
 shaft=Dshape(d,d/2-.5,-9,6).fuse(cyl(d/2,-3,9.2)).fuse(Dshape(8,3.5,6.2,3.8)).fuse(cyl(d/2+1.5,-2,2))
 add('encoder_trunnion',shaft,'aluminum','rotor','Inner D drive; outer 8mm D head matches existing magnetic coupling')
 add('encoder_thrust_washer',ring(d/2+1.8,d/2+.1,5.6,.5),'pom','fixed','Nominal end-float .6mm before adjustment; no clutch spring load')
 selected=('D_magnet_carrier','magnet_retaining_bridge','diametric_magnet_6x2p5','AS5048A_sensor_revB','nylon_M2_female_spacer','nylon_M2x6_top_screw','nylon_M2x4_board_screw','nylon_spreader','nylon_M2x8_cap_screw','nylon_M2_cap_nut','M2_magnet_set_screw','M2_magnet_set_nut')
 for p in h2.cartridge('S'):
  n=p['name'].split('_',1)[1]
  if any(n.startswith(v) for v in selected):add(n,p['shape'].translate((0,0,-24)),p['material'],p['owner'],p['note'])
 carrier=cube((22,12,3),(0,6.5,25.9))
 # Flat ribs stay between washer contact planes; fixes the Rev D protruding round-rib problem.
 for x in (-11,11):carrier=carrier.fuse(cube((3,11,3),(x,4,25.9)))
 for x in (-6.5,6.5):carrier=hole(carrier,x,6.5,2.1)
 add('PCB_alignment_bridge',carrier,'printed','fixed','Separate adjustment bridge; final fork supports use two side mounting pads')
 return parts

def allowed(parts):
 names={p['name'] for p in parts};out={frozenset(('flanged_trunnion','axial_retainer_screw')),frozenset(('key_clamp_screw','key_clamp_nut'))}
 for j in range(2):
  out.add(frozenset(('nylon_M2_female_spacer'+str(j),'nylon_M2x6_top_screw'+str(j))))
  out.add(frozenset(('nylon_M2_female_spacer'+str(j),'nylon_M2x4_board_screw'+str(j))))
  out.add(frozenset(('nylon_M2x8_cap_screw'+str(j),'nylon_M2_cap_nut'+str(j))))
 out.add(frozenset(('M2_magnet_set_screw','M2_magnet_set_nut')))
 return {x for x in out if x<=names}

def main():
 report={'status':'FORK_COMPONENT_DEVELOPMENT_NOT_MANUFACTURING_RELEASE','physical_tested':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'spring_source':SPRING_SOURCE,'thrust_washer_source':THRUST_SOURCE,'thrust_washer_candidate':'PCMW 102001.5 E','material_density_note':'Composite washer mass conservatively approximates solid steel density; not a supplier weight.','units':'mm','families':{}}
 for name,parts in [(s,friction(s)) for s in SPECS]+[('E6',encoder(6)),('E8',encoder(8))]:
  folder=OUT/'joints'/name;folder.mkdir(exist_ok=True);assembly=cq.Assembly(name='RevF_'+name);manifest=[]
  for p in parts:
   s=p['shape'];assembly.add(s,name=p['name'],color=cq.Color(*COL[p['material']]))
   bb=s.BoundingBox();manifest.append({k:v for k,v in p.items() if k!='shape'}|{'mass_g':mass(p),'solid_count':len(s.Solids()),'valid':s.isValid(),'bbox_mm':[bb.xlen,bb.ylen,bb.zlen]})
   if p['material'] in ('printed','aluminum','pom','lining','ptfe_composite'):cq.exporters.export(s,str(folder/(p['name']+'.step')))
  assembly.save(str(folder/('RevF_'+name+'.step')))
  exceptions=allowed(parts);allhits=pair_hits(parts);bad=[h for h in allhits if frozenset((h['a'],h['b'])) not in exceptions]
  rows=[]
  for angle in range(0,360,30):
   transformed=[dict(p,shape=p['shape'].rotate((0,0,0),(0,0,1),angle)) if p['owner']=='rotor' else p for p in parts]
   rows.append({'angle_deg':angle,'hits':pair_hits(transformed,skip_same_owner=True)})
  row={'parts':manifest,'mass_g':sum(mass(p) for p in parts),'unplanned_assembly_hits':bad,'thread_envelope_hits':[h for h in allhits if h not in bad],'rotation_samples':rows}
  if name in SPECS:
   sp=SPECS[name];ri=sp['shaft']/2+1.1;reff=(2/3)*(sp['ro']**3-ri**3)/(sp['ro']**2-ri**2)
   row['spec']=sp;row['spring_count']=2*sp['parallel'];row['nominal_force_N']=sp['F']*sp['parallel'];row['active_friction_faces']=1
   row['friction_estimate_Nm_mu_0p15']=.15*row['nominal_force_N']*reff/1000
   row['thrust_washer_pressure_MPa']=row['nominal_force_N']/(math.pi*(10**2-5**2))
  report['families'][name]=row
  print(json.dumps({'name':name,'parts':len(parts),'mass_g':row['mass_g'],'assembly_hits':bad,'sweep_hits':sum(len(r['hits']) for r in rows)}),flush=True)
  if name in ('M6','E6'):render([(p['name'],p['shape'],COL[p['material']]) for p in parts],OUT/'images'/('RevF_'+name+'.png'),'Rev F '+name+' | integrated fork bearing component | development')
 save(ROOT/'verification/revF_pivot_components.json',report)
if __name__=='__main__':main()
