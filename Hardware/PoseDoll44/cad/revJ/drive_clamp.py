"""Rev J removable split metal D hub. All dimensions mm, unstrained CAD.
The split takes up shaft fit clearance; these solids are not a deformation model.
"""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'revI'))
import shoulder_integration as previous
from shoulder_clutch import *
HERE=Path(__file__).resolve().parent
COL=dict(COL,aluminum=(.62,.70,.75),magnet=(.75,.22,.20),pcb=(.12,.38,.23))
MOUNT_RADIUS=5.9
MOUNT_Y=-5.9
BORE_D=6.06
FLAT_X=2.53
SPLIT=.6
def cross_cyl(a,b,r,y,z):
 return h.rod((a,y,z),(b,y,z),r)
def hub(tip):
 # Compact axial band: flange 0..1.5, printed backing 1.5..4.0.
 # The rear half stays within a 9 mm radial envelope.
 metal=cyl(tip,tip+5.5,6)
 for x in (-MOUNT_RADIUS,MOUNT_RADIUS):
  metal=metal.fuse(cyl(tip,tip+1.5,2.6).translate((x,MOUNT_Y,0)))
  metal=metal.cut(cyl(tip-.1,tip+1.6,1.1).translate((x,MOUNT_Y,0)))
 ears=h.union([cube((6,5,4),(x,5.2,tip+3)) for x in (-3.3,3.3)]).intersect(cyl(tip,tip+6,9))
 metal=metal.fuse(ears)
 metal=metal.cut(dshape(tip-.1,tip+5.6,BORE_D,FLAT_X))
 metal=metal.cut(cube((SPLIT,20,7),(0,12.8,tip+3)))
 metal=metal.cut(cross_cyl(-7,0,.8,5.2,tip+3)).cut(cross_cyl(0,7,1.1,5.2,tip+3))
 metal=metal.cut(cross_cyl(4,8,2.1,5.2,tip+3))
 # M2 x10 cross clamp, head recessed into one ear; opposite ear tapped.
 screw=cross_cyl(-6,4,1,5.2,tip+3).fuse(cross_cyl(4,6,1.9,5.2,tip+3))
 socket=hexagon(1.5,0,1.1).rotate((0,0,0),(0,1,0),90).translate((5,5.2,tip+3))
 screw=screw.cut(socket)
 parts=[dict(name='split_hub',shape=metal,material='aluminum',note='Custom split metal D hub; M2 tapped clamp ear; preload/elastic closure not simulated'),
        dict(name='pinch_M2x10',shape=screw,material='fastener',note='M2 transverse pinch screw takes up shaft fit clearance; tightening torque not yet qualified')]
 for i,x in enumerate((-MOUNT_RADIUS,MOUNT_RADIUS)):
  # M2 x4: 1.5 mm metal flange plus 2.5 mm printed backing.
  bolt=cyl(tip,tip+4,1).fuse(cyl(tip-2,tip,1.9))
  bolt=bolt.cut(hexagon(1.5,tip-2.1,tip-.9))
  nut=hexagon(4,tip+2.3,tip+3.9).cut(cyl(tip+2,tip+4.1,.8))
  parts += [dict(name='mount_M2x4_'+str(i),shape=bolt.translate((x,MOUNT_Y,0)),material='fastener',note='Flange screw with trapped M2 nut; 1.6 mm nominal nut engagement'),
            dict(name='mount_M2_nut_'+str(i),shape=nut.translate((x,MOUNT_Y,0)),material='fastener',note='Captured nut inside output yoke; fit and creep require testing')]
 for q in parts:assert q['shape'].isValid() and len(q['shape'].Solids())==1,q['name']
 return parts

def backing_and_cuts(tip):
 # A lower semicircular bridge preserves continuity around the metal socket.
 # A straight bar would be removed by the shaft pocket and split the open U yoke.
 lower=ring(tip+1.5,tip+4,9.5,6.15).intersect(cube((30,15,5),(0,-7.5,tip+2.75)))
 backing=[lower]
 for x in (-MOUNT_RADIUS,MOUNT_RADIUS):
  backing.append(cyl(tip+1.5,tip+4,3).translate((x,MOUNT_Y,0)))
 support=h.union(backing).intersect(cyl(tip+1.4,tip+4.1,11.25))
 # Open pocket around the entire split hub, allowing elastic closure and disassembly.
 pocket=cyl(tip-.05,tip+6.2,6.15)
 for x in (-3.3,3.3):pocket=pocket.fuse(cube((6.4,5.4,4.4),(x,5.2,tip+3)))
 for x in (-MOUNT_RADIUS,MOUNT_RADIUS):
  pocket=pocket.fuse(cyl(tip-.1,tip+1.5,2.75).translate((x,MOUNT_Y,0)))
 cuts=[pocket,cyl(tip-6,tip,5.2)]
 for x in (-MOUNT_RADIUS,MOUNT_RADIUS):
  cuts += [cyl(tip-2.1,tip+4.2,1.15).translate((x,MOUNT_Y,0)),
   hexagon(4.3,tip+2.2,tip+4.1).translate((x,MOUNT_Y,0)),
   cyl(tip-2.2,tip,2.05).translate((x,MOUNT_Y,0)),
   cyl(tip-60,tip-2.1,1.1).translate((x,MOUNT_Y,0))]
 # Clearance for the recessed clamp screw and straight access to its socket.
 cuts.append(cross_cyl(3.9,12,2.15,5.2,tip+3))
 return support,cuts
