"""Rev I shoulder face clutch. Millimetres; local +Z points out of the joint.
A positive shoulder sets nominal spring height; PLA is outside the preload loop.
Custom machined parts are design candidates, not purchased or released parts.
"""
from pathlib import Path
import sys, math, json
import numpy as np
import cadquery as cq
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revH'))
import shoulder_mechanism as h
COL=dict(h.COL,spring=(.35,.38,.42),fastener=(.37,.40,.43),thrust=(.60,.55,.36))
SPRING={'manufacturer':'SCHNORR','article':'002 200','outside_mm':12.0,'inside_mm':6.2,
 'thickness_mm':.6,'free_height_mm':.95,'catalog_test_height_mm':.688,'catalog_force_N':552,
 'count_series':2,'source':'https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf','pdf_page':11}
THRUST={'candidate':'SKF PCMW 102001.5 E','id_mm':10,'od_mm':20,'thickness_mm':1.5,
 'source':'https://cdn.skfmediahub.skf.com/api/public/0901d19680090e01/pdf_preview_medium/0901d19680090e01_pdf_preview_medium.pdf','pdf_page':37}
ring=lambda a,b,ro,ri:h.tube(2,a,b,ro,ri)
cyl=lambda a,b,r:h.axis_cyl(2,a,b,r)
cube=h.cube
PITCH=17.5
CAP_BOTTOM=6+2*SPRING['catalog_test_height_mm']
SHAFT_END=CAP_BOTTOM+2
TOP=CAP_BOTTOM+3

def dshape(a,b,diameter=6,flat=2.5):
 return cyl(a,b,diameter/2).cut(cube((12,16,b-a+2),(flat+6,0,(a+b)/2)))

def hexagon(af,a,b):
 return cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(b-a).translate((0,0,a)).val()

def spring(z,flip=False):
 height=SPRING['catalog_test_height_mm'];t=SPRING['thickness_mm']
 pts=[(3.1,height-t),(6,0),(6,t),(3.1,height)]
 if flip:pts=[(r,height-y) for r,y in pts]
 return cq.Workplane('XZ').polyline(pts).close().revolve(360,(0,0),(0,1)).translate((0,0,z)).val()

def cartridge(tip):
 parts=[]
 def add(n,s,m,o,note=''):
  assert s.isValid() and len(s.Solids())==1,n
  parts.append(dict(name=n,shape=s,material=m,owner=o,role='structural_concept',note=note))
 # Integral steel rotor, journal and two D drives; nominal thread pilot bores.
 shaft=cyl(tip+6,SHAFT_END,3).fuse(dshape(tip,tip+6)).fuse(cyl(-3,0,13.5))
 shaft=shaft.cut(cube((12,16,2.1),(8.5,0,SHAFT_END-1.05)))
 shaft=shaft.cut(cyl(SHAFT_END-8,SHAFT_END+1,1.25)).cut(cyl(tip-1,tip+9,1.25))
 add('flanged_shaft',shaft,'metal','rotor','Custom steel 6 mm journal; integral flange, inner D drive, outer D cap seat, two M3 blind threads')
 lining=ring(0,1,12.5,4.15)
 for x in (-12.3,12.3):lining=lining.fuse(cube((2.6,3,1),(x,0,.5)))
 add('keyed_lining',lining,'lining','fixed','1 mm replaceable lining; coefficient and wear unqualified')
 plate=ring(1,4,13.7,4.15)
 for x in (-PITCH,PITCH):
  plate=plate.fuse(cube((12,7,3),(math.copysign(15,x),0,2.5)))
  plate=plate.cut(cyl(0,5,1.7).translate((x,0,0)))
 # The lining has two tabs; this shallow metal rim provides positive torque engagement.
 keeper=ring(0,1,13.7,12.5).cut(lining)
 plate=plate.fuse(keeper)
 add('reaction_plate',plate,'metal','fixed','3 mm steel reaction plate with keyed lining recess and two M3 frame mounts; spring thrust closes through plate')
 add('radial_bush',ring(1.1,3.9,4,3.05),'bush','fixed','POM radial guide, clear of thrust faces; press fit/retention pending')
 add('thrust_washer',ring(4,5.5,10,5),'thrust','fixed','SKF dimension candidate; PTFE face towards rotating spring seat; washer retention pending')
 add('spring_seat',ring(5.5,6,10,3.1),'metal','rotor','Steel spring seat; thrust washer separates rotation from fixed reaction plate')
 add('disc_spring_a',spring(6),'spring','rotor','SCHNORR 002 200 dimensional candidate at catalog test height')
 add('disc_spring_b',spring(6+SPRING['catalog_test_height_mm'],True),'spring','rotor','Opposed pair in series: force is not doubled')
 cap=cyl(CAP_BOTTOM,TOP,7).cut(dshape(CAP_BOTTOM-.01,SHAFT_END+.01,6.1,2.55)).cut(cyl(CAP_BOTTOM-1,TOP+1,1.65))
 add('keyed_stop_cap',cap,'metal','rotor','D key follows shaft; cap seats on metal shaft end; shim selection/retention and backlash need physical validation')
 screw=cyl(TOP-8,TOP,1.5).fuse(cyl(TOP,TOP+3,2.75))
 screw=screw.cut(hexagon(2.5,TOP+1.5,TOP+3.1))
 add('outer_M3x8',screw,'fastener','rotor','Simplified thread envelope; axial cap retention, not hand tightness setting')
 washer=ring(tip-1,tip,5,1.65)
 add('drive_retainer_washer',washer,'metal','rotor','Separate washer retains D drive in printed output hub')
 inner=cyl(tip-1,tip+7,1.5).fuse(cyl(tip-4,tip-1,2.75))
 inner=inner.cut(hexagon(2.5,tip-4.1,tip-2.5))
 add('inner_M3x8',inner,'fastener','rotor','Independent output-hub retention; does not set clutch spring compression')
 for j,x in enumerate((-PITCH,PITCH)):
  bolt=cyl(-6,4,1.5).fuse(cyl(4,7,2.75));bolt=bolt.cut(hexagon(2.5,5.5,7.1))
  nut=hexagon(5.5,-6,-3.6).cut(cyl(-7,-2,1.25))
  add('mount_M3x10_'+str(j),bolt.translate((x,0,0)),'fastener','fixed','Reaction plate to printed support; simplified thread')
  add('mount_M3_nut_'+str(j),nut.translate((x,0,0)),'fastener','fixed','Captured hex nut, accessible from inside of support')
 return parts

def mounting_lugs():
 items=[]
 for x in (-PITCH,PITCH):
  lug=cube((7,8,7),(x,0,-2.5)).cut(cyl(-7,2,1.7).translate((x,0,0)))
  lug=lug.cut(hexagon(5.8,-6.1,-3.4).translate((x,0,0)))
  items.append(lug)
 return items

def intentional_threads(a,b):
 pair={a,b}
 return pair in ({'flanged_shaft','outer_M3x8'},{'flanged_shaft','inner_M3x8'},
                 {'mount_M3x10_0','mount_M3_nut_0'},{'mount_M3x10_1','mount_M3_nut_1'})

def exact_hits(parts,same_owner=True):
 out=[]
 for i,a in enumerate(parts):
  aa=a['shape'].BoundingBox()
  for b in parts[i+1:]:
   if not same_owner and a['owner']==b['owner']:continue
   bb=b['shape'].BoundingBox()
   if not all(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
   v=a['shape'].intersect(b['shape']).Volume()
   if v>.02:out.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4),intentional_thread=intentional_threads(a['name'],b['name'])))
 return out
