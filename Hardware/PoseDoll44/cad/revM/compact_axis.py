"""Rev M compact direct-readout joint. Millimetres; candidate, no physical rating.
The closed clutch preload path is metal. Printed carriers do not clamp the spring.
"""
from pathlib import Path
from functools import lru_cache
import sys, json, math
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revL'))
import flex_encoder as previous
h=previous.h; cq=h.cq; ROOT=previous.ROOT
COL=dict(previous.COL,pom=(.86,.85,.73),lining=(.60,.35,.20),spring=(.43,.45,.47),ptfe_composite=(.48,.5,.52),aluminum_7075=(.55,.63,.68))
cube=h.cube; cyl=previous.cyl; ring=previous.ring; hexagon=previous.hexagon
SPECS={
 'S6':dict(ro=11,spring='002050',de=12.5,di=6.2,t=.35,free=.80,test=.463,F=151),
 'M6':dict(ro=13,spring='002100',de=12,di=6.2,t=.5,free=.85,test=.588,F=326),
 'H6':dict(ro=16,spring='002200',de=12,di=6.2,t=.6,free=.95,test=.688,F=552),
}
SPECS['H6P2']=dict(SPECS['H6'],parallel=2)
SPECS['H6P3']=dict(SPECS['H6'],parallel=3)
SPECS['H6P4']=dict(SPECS['H6'],parallel=4,clutch_ro=18,rotor_mount_offset_mm=22)

def dshape(z0,z1,r=3,flat=2.5):
 return cyl(z0,z1,r).cut(cube((20,30,z1-z0+2),(flat+10,0,(z0+z1)/2)))

def spring(sp,z,flip=False):
 ro,ri=sp['de']/2,sp['di']/2;t=sp['t'];hh=sp['test']
 pts=[(ri,hh-t),(ro,0),(ro,t),(ri,hh)]
 if flip:pts=[(r,hh-v) for r,v in pts]
 return cq.Workplane('XZ').polyline(pts).close().revolve(360,(0,0),(0,1)).translate((0,0,z)).val()

def screw(z,length,diam=3,head_h=3,head_r=2.75,af=2.5):
 return cyl(z-length,z,diam/2).fuse(cyl(z,z+head_h,head_r)).cut(hexagon(af,z+head_h-(1.04 if head_h==1.65 else 1.4),z+head_h+.1))

@lru_cache(None)
def module(size='M6',board_rotation=0):
 sp=SPECS[size];ro=sp['ro'];cr=sp.get('clutch_ro',ro);rx=-sp.get('rotor_mount_offset_mm',ro+4);cleat_len=-rx+5;parallel=sp.get('parallel',1);pack=sp['test']+(parallel-1)*sp['t'];cb=6+2*pack;top=cb+3;se=cb+2
 mb=top+1.65+.6;mt=mb+2.5;pcb=mt+1.5+1.995;out=[];allow=[]
 def add(n,sh,mat,owner,note='',role='candidate_solid'):
  assert sh.isValid() and len(sh.Solids())==1,(size,n,len(sh.Solids()))
  out.append(dict(name=n,shape=sh,material=mat,owner=owner,note=note,role=role))
 # Bearing eye and its two mounting tabs point proximally (+X).
 eye=cyl(1,4,cr+1)
 for y in (-6,6):
  eye=eye.fuse(cube((13,7,3),(ro+5,y,2.5))).cut(cyl(.9,4.1,1.25).translate((ro+8,y,0)))
 eye=eye.cut(cyl(.9,4.1,4.03))
 lining=ring(0,1,cr,4.1)
 for sy in (-1,1):lining=lining.fuse(cube((2,2,1),(0,sy*(cr-.3),.5)))
 # Rim recesses lock the lining rotationally without pressing on the POM bush.
 rim=ring(0,1,cr+1,cr).cut(lining)
 eye=eye.fuse(rim)
 add('fixed_metal_eye',eye,'aluminum','fixed','Machined 6061-T6 eye; 2 x M3 tapped mounting holes; friction lining reacts into this eye')
 add('radial_bush',ring(1.1,3.9,4,3.03),'pom','fixed','D6 journal +0.06 mm nominal diametral clearance; not part of axial preload loop')
 add('friction_lining',lining,'lining','fixed','1 mm replaceable lining with positive edge tabs; friction coefficient is an untested assumption')
 shaft=dshape(-9,-3).fuse(cyl(-3,se,3)).fuse(cyl(-3,0,cr+1))
 # Shaft end D-key retains orientation of the stop cap. Axial M3 blind pilot.
 shaft=shaft.cut(cube((20,30,2.05),(12.5,0,se-1.025)))
 shaft=shaft.cut(cyl(se-9,se+.1,1.25))
 shaft=shaft.cut(h.axis_cyl(0,0,3.1,.8,(0,0,-5.5)))
 add('flanged_rotor_shaft',shaft,'aluminum_7075' if parallel>=3 else 'aluminum','rotor','Integral D6 drive, journal and friction flange; blind M3 end thread and M2 radial retention; no threaded running surface')
 add('thrust_wear_washer',ring(4,5.5,10,5),'ptfe_composite','fixed','SKF PCMW102001.5 E envelope; radial bush is unloaded axially')
 add('spring_seat',ring(5.5,6,10,3.1),'spring','rotor')
 for i in range(2):
  for layer in range(parallel):add('disc_spring_'+str(i)+'_'+str(layer),spring(sp,6+i*pack+layer*sp['t'],bool(i)),'spring','rotor','SCHNORR '+sp['spring']+'; '+str(parallel)+' nested parallel per group, two groups opposed in series')
 cap=cyl(cb,top,6.8).cut(dshape(cb-.1,se+.05,3.05,2.55)).cut(cyl(cb-.1,top+.1,1.65))
 cap=cap.cut(cube((20,30,5),(15.6,0,cb+1.5)))
 for sy in (-1,1):cap=cap.cut(h.axis_cyl(1,*sorted((sy*3.1,sy*6.9)),.8,(0,0,top-1.3)))
 add('D_stop_cap',cap,'aluminum','rotor','Metal shoulder fixes nominal spring height; actual preload requires selected shims and a physical torque test')
 add('M3x8_button_retainer',screw(top,8,3,1.65,2.85,2),'titanium','rotor','Accu SSB-M3-8-TI5 nominal head envelope; thread and bearing stress unqualified')
 allow.append(['flanged_rotor_shaft','M3x8_button_retainer'])
 cup=cyl(cb+.2,mt,8.2)
 slot=cyl(cb+.1,top+.1,6.85).cut(cube((20,30,5),(15.65,0,cb+1.5)))
 cup=cup.cut(slot).cut(cyl(top-.05,mb-.6,3)).cut(cyl(mb,mt+.1,3.1))
 for sy in (-1,1):
  cup=cup.cut(h.axis_cyl(1,*sorted((sy*6.6,sy*8.3)),1.1,(0,0,top-1.3)))
  cup=cup.cut(h.axis_cyl(1,*sorted((sy*5.8,sy*8.3)),.8,(0,0,mt-1)))
 add('keyed_magnet_cup',cup,'aluminum','rotor','External D key transmits angle; 0.05 mm nominal fit and two radial brass retainers')
 for i,sy in enumerate((-1,1)):
  add('cup_M2x4_'+str(i),h.axis_cyl(1,*sorted((sy*4.2,sy*8.2)),1,(0,0,top-1.3)),'brass','rotor','Thread envelope; slotted brass M2x4')
  allow.append(['D_stop_cap','cup_M2x4_'+str(i)])
 add('diametric_magnet_6x2p5',cyl(mb,mt,3),'magnet','rotor','Diametric magnet; magnetic field and interference require bench qualification')
 keeper=ring(mt-1.9,mt,9.6,8.4).fuse(ring(mt,mt+.8,9.6,2.5))
 for sy in (-1,1):keeper=keeper.cut(h.axis_cyl(1,*sorted((sy*8.2,sy*9.7)),1.1,(0,0,mt-1)))
 add('magnet_keeper',keeper,'frame','rotor','1.2 mm radial wall, 0.20 mm nominal radial fit allowance, 0.8 mm face; mechanical retention outside sensor air gap')
 for i,sy in enumerate((-1,1)):
  add('keeper_M2x3_'+str(i),h.axis_cyl(1,*sorted((sy*6.6,sy*9.6)),1,(0,0,mt-1)),'brass','rotor','Slotted brass M2x3 thread envelope')
  allow.append(['keyed_magnet_cup','keeper_M2x3_'+str(i)])
 # Rotor output cleat lies on the opposite side of the flange.
 cleat=cyl(-8,-3.05,6)
 for y in (-6,6):cleat=cleat.fuse(cube((cleat_len,7,4.95),(-cleat_len/2,y,-5.525)))
 cleat=cleat.cut(dshape(-8.1,-2.95,3.05,2.55))
 for y in (-6,6):cleat=cleat.cut(cyl(-8.1,-2.95,1.7).translate((rx,y,0)))
 cleat=cleat.cut(h.axis_cyl(0,2.4,6.1,1.1,(0,0,-5.5)))
 add('D_output_cleat',cleat,'aluminum','rotor','Two M3 attachment bores; drive on D-flat, axial retention by radial M2 into shaft')
 add('output_M2x6',h.axis_cyl(0,0,6,1,(0,0,-5.5)).fuse(h.axis_cyl(0,6,8,1.9,(0,0,-5.5))),'brass','rotor','Nominal M2x6 radial retainer; install before connecting distal segment')
 allow.append(['flanged_rotor_shaft','output_M2x6'])
 # Separate M2 brass posts and insulating edge clamps permit assembly over the magnet.
 px=ro+3
 def board_turn(sh):return sh.rotate((0,0,0),(0,0,1),board_rotation)
 for i,sg in enumerate((-1,1)):
  x=sg*px;foot=hexagon(3.5,4,pcb-2).fuse(cyl(1.5,4,1)).cut(cyl(pcb-7,pcb-1.9,.8))
  add('board_post_'+str(i),board_turn(foot.translate((x,0,0))),'brass','fixed','Custom AF3.5 male/female M2 spacer; 2.5 mm nominal engagement in metal eye')
  # Fixed eye gains a narrow supported ear at each post.
  ear=cube((max(4,px-ro+4),4,3),(sg*(ro+(px-ro)/2),0,2.5))
  out[0]['shape']=out[0]['shape'].fuse(board_turn(ear)).cut(board_turn(cyl(1,4.1,.8).translate((x,0,0))))
  saddle=cube((px-5.6,4,1),(sg*(px+5.6)/2,0,pcb-1.5)).fuse(cube((px-6.1,4,1),(sg*(px+6.1)/2,0,pcb-.5)))
  saddle=saddle.fuse(cube((4,4,2),(x,0,pcb-1)))
  saddle=saddle.cut(cyl(pcb-2.1,pcb+.1,1.1).translate((x,0,0)))
  add('PCB_edge_saddle_'+str(i),board_turn(saddle),'frame','fixed')
  cover=cube((px-5.6+2,4,.8),(sg*(px+7.6)/2,0,pcb+.4)).cut(cyl(pcb-.1,pcb+.9,1.1).translate((x,0,0)))
  add('PCB_edge_cap_'+str(i),board_turn(cover),'nylon','fixed')
  add('PCB_M2x6_'+str(i),board_turn(screw(pcb+.8,6,2,2,1.9,1.5).translate((x,0,0))),'nylon','fixed')
  allow.extend([['fixed_metal_eye','board_post_'+str(i)],['board_post_'+str(i),'PCB_M2x6_'+str(i)]])
 for q in previous.k.head(pcb):add('pcb_'+q['name'],board_turn(q['shape']),'pcb' if q['name']=='board' else 'sensor_space' if 'tail' in q['kind'] else 'pcb_component','fixed',q['kind'],'reservation' if 'tail' in q['kind'] else 'candidate_solid')
 for p in out:assert p['shape'].isValid() and len(p['shape'].Solids())==1,(p['name'],len(p['shape'].Solids()))
 reff=2/3*(cr**3-4.1**3)/(cr**2-4.1**2)
 meta=dict(family=size,clutch_outer_radius_mm=cr,mount_reference_radius_mm=ro,board_rotation_deg=board_rotation,shaft_mm=6,clutch_force_nominal_N=sp['F']*parallel,spring=sp,friction_mu_assumed=.15,nominal_torque_Nm=.15*sp['F']*parallel*reff/1000,
   cap_bottom_mm=cb,shaft_end_mm=se,board_back_mm=pcb,magnet_face_mm=mt,package_face_mm=pcb-1.995,gap_mm=1.5,
   fixed_mounts_mm=[[ro+8,y,2.5] for y in (-6,6)],rotor_mounts_mm=[[rx,y,-5.525] for y in (-6,6)],
   intended_thread_pairs=allow,physical_tested=False,manufacturing_released=False)
 return out,meta

def collision_pairs(items,skip_same_owner=False):
 hits=[];bbs=[x['shape'].BoundingBox() for x in items]
 for i,a in enumerate(items):
  if a.get('role')=='reservation':continue
  for j in range(i+1,len(items)):
   b=items[j]
   if b.get('role')=='reservation' or (skip_same_owner and a['owner']==b['owner']):continue
   if not all(min(getattr(bbs[i],s+'max'),getattr(bbs[j],s+'max'))-max(getattr(bbs[i],s+'min'),getattr(bbs[j],s+'min'))>1e-5 for s in 'xyz'):continue
   v=a['shape'].intersect(b['shape']).Volume()
   if v>.02:hits.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,5)))
 return hits

def main():
 out={'status':'COMPONENT_GEOMETRY_CHECK','physical_tested':False,'families':{}}
 for size in SPECS:
  parts,meta=module(size);allow={frozenset(pair) for pair in meta['intended_thread_pairs']}
  assembly_hits=collision_pairs(parts);bad=[x for x in assembly_hits if frozenset((x['a'],x['b'])) not in allow]
  motion=[]
  for q in range(0,360,15):
   posed=[dict(p,shape=p['shape'].rotate((0,0,0),(0,0,1),q)) if p['owner']=='rotor' else p for p in parts]
   motion.append(dict(degrees=q,hits=collision_pairs(posed,True)))
  row=dict(meta=meta,parts=len(parts),unplanned_assembly_hits=bad,motion=motion)
  out['families'][size]=row
  print(json.dumps(dict(size=size,parts=len(parts),assembly_hits=bad,motion_failed=[x for x in motion if x['hits']])),flush=True)
  folder=ROOT/'generated/revM/components'/size;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name='RevM_'+size)
  for p in parts:
   assy.add(p['shape'],name=p['name'],color=cq.Color(*COL[p['material']]))
   if p['role']!='reservation':cq.exporters.export(p['shape'],str(folder/(p['name']+'.step')))
  assy.save(str(folder/('RevM_'+size+'.step')))
 h.save(ROOT/'verification/revM_compact_components.json',out)
if __name__=='__main__':main()
