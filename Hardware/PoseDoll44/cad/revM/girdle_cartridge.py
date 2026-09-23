"""Small D4 girdle cartridge, clipped inward face and negative-side encoder.
Local Z=0 is the inherited clutch plane. Shaft end is set by each bearing span.
"""
from assembly_core import *
COL['bronze']=(.72,.53,.30)
GSPRING=dict(article='001800',de=12,di=4.2,t=.6,free=1.0,test=.7,F=557)

@lru_cache(None)
def module4(end=42,clip_sign=1,middle_key=None):
 out=[];allowed=[]
 def add(n,s,m,o,note='',role='candidate_solid'):
  assert s.isValid() and len(s.Solids())==1,(n,len(s.Solids()))
  out.append(dict(name=n,shape=s,material=m,owner=o,note=note,role=role))
 def clipped(s):return s if clip_sign is None else s.cut(cube((80,60,150),(0,-clip_sign*35.5,20)))
 mount_sign=clip_sign or 1
 # Entire M3 thread reaches the bottom tip; the tip flat is only a magnet key.
 shaft=dshape(-15,-9.95,1.5,1.0).fuse(cyl(-9.95,-5.1,1.5)).fuse(cyl(-5.1,1.5,2)).fuse(dshape(1.5,4.5,2,1.5)).fuse(cyl(4.5,end-4,2)).fuse(dshape(end-4,end,2,1.5)).fuse(cyl(4.5,6.5,4.5))
 shaft=shaft.cut(cyl(end-4.5,end+.1,.8))
 if middle_key is not None:
  a,b=middle_key;shaft=shaft.cut(cube((8,8,b-a),(5.5,0,(a+b)/2)))
  shaft=shaft.cut(h.axis_cyl(0,0,2.1,.8,(0,0,(a+b)/2)))
 for sg in (-1,1):shaft=shaft.cut(h.axis_cyl(1,*sorted((0,sg*1.6)),.8,(0,0,-12)))
 add('stepped_D4_shaft',shaft,'aluminum_7075','rotor','M3x0.5 external thread continuously to Z-15 including magnet-key flat; fully round loaded thread above Z-9.95. Upper D4 key for carriage, M2 end-retention pilot.')
 plate=clipped(ring(-2,1,14,2.05));lining=clipped(ring(1,1.5,12,2.05))
 for x in (-11.4,11.4):lining=lining.fuse(cube((2,2,.5),(x,0,1.25)))
 plate=plate.fuse(clipped(ring(1,1.5,14,12)).cut(lining))
 for x in (-10,10):plate=plate.cut(cyl(-2.1,1.1,.8).translate((x,0,0)))
 for x in (-6,6):plate=plate.cut(cyl(-2.1,1.1,1.25).translate((x,mount_sign*9,0)))
 add('fixed_reaction_plate',plate,'aluminum_7075','fixed','M3 tapped attachment pair at X+/-6,Y outward9; two independent M2 sensor posts; clipped inward boundary Y=-/+5.5')
 add('keyed_friction_lining',lining,'lining','fixed','Positive lining tabs; 0.5 mm candidate, friction coefficient untested')
 rotor=clipped(cyl(1.5,4.5,12)).cut(dshape(1.4,4.6,2.05,1.55))
 add('D4_friction_rotor',rotor,'aluminum_7075','rotor','3 mm metal drive face; upper shaft flange carries the axial spring load')
 add('lower_thrust_washer',ring(-2.5,-2,6.5,2.1),'bronze','fixed','0.5 mm CuSn8 plain thrust washer; surface and wear require qualification')
 for i in range(2):
  for layer in range(2):add('disc_'+str(i)+'_'+str(layer),spring(GSPRING,-5.1+i*1.3+layer*.6,bool(i)),'spring','rotor','Two nested discs per group; two opposed groups. Nominal 1114 N at catalog height.')
 add('spring_lower_washer',ring(-5.6,-5.1,6.5,1.6),'spring','rotor')
 for name,z in [('preload_nut',-7.4),('jam_nut',-9.2)]:
  add(name,hexagon(5.5,z,z+1.8).cut(cyl(z-.1,z+1.9,1.25)),'metal','rotor','M3 thin nut, nominal AF5.5 x1.8; threads onto the continuous threaded tip before magnet cup installation')
  allowed.append(['stepped_D4_shaft',name])
 # Mechanically keyed removable magnet cup, installed after the two M3 nuts.
 cup=cyl(-18.3,-10,5.5).cut(dshape(-15.05,-9.9,1.55,1.05)).cut(cyl(-18.4,-15.8,3.1))
 for sg in (-1,1):
  cup=cup.cut(h.axis_cyl(1,*sorted((sg*1.0,sg*5.6)),1.1,(0,0,-12)))
  cup=cup.cut(h.axis_cyl(1,*sorted((sg*3.1,sg*5.6)),.8,(0,0,-17.3)))
 add('removable_D3_magnet_cup',cup,'aluminum','rotor','D3 threaded-tip flat transmits only encoder torque; 0.75 mm floor separates shaft and magnet')
 for i,sg in enumerate((-1,1)):
  add('cup_M2x5_'+str(i),h.axis_cyl(1,*sorted((sg*.5,sg*5.5)),1,(0,0,-12)),'brass','rotor','Slotted brass M2x5, 1 mm nominal shaft thread engagement, unloaded magnet extension')
  allowed.append(['stepped_D4_shaft','cup_M2x5_'+str(i)])
 add('magnet_6x2p5',cyl(-18.3,-15.8,3),'magnet','rotor')
 keeper=ring(-18.3,-16.3,6.8,5.7).fuse(ring(-19.1,-18.3,6.8,2.5))
 for sg in (-1,1):keeper=keeper.cut(h.axis_cyl(1,*sorted((sg*5.5,sg*6.9)),1.1,(0,0,-17.3)))
 add('magnet_keeper',keeper,'frame','rotor','1.1 mm radial wall; 0.20 mm radial clearance; 0.8 mm retention face')
 for i,sg in enumerate((-1,1)):
  add('keeper_M2x3_'+str(i),h.axis_cyl(1,*sorted((sg*3.8,sg*6.8)),1,(0,0,-17.3)),'brass','rotor')
  allowed.append(['removable_D3_magnet_cup','keeper_M2x3_'+str(i)])
 p=18.3+3.495;px=10
 def flip(s):return s.rotate((0,0,0),(1,0,0),180)
 for i,sg in enumerate((-1,1)):
  x=sg*px
  post=hexagon(3.5,2,p-2).fuse(cyl(-.5,2,1)).cut(cyl(p-7,p-1.9,.8))
  add('post_'+str(i),flip(post.translate((x,0,0))),'brass','fixed','Custom M2 male/female spacer; 2.5 mm into reaction plate; clamping does not load PCB')
  saddle=cube((px-5.6,4,1),(sg*(px+5.6)/2,0,p-1.5)).fuse(cube((px-6.1,4,1),(sg*(px+6.1)/2,0,p-.5))).fuse(cube((4,4,2),(x,0,p-1))).cut(cyl(p-2.1,p+.1,1.1).translate((x,0,0)))
  cap=cube((px-5.6+2,4,.8),(sg*(px+7.6)/2,0,p+.4)).cut(cyl(p-.1,p+.9,1.1).translate((x,0,0)))
  add('board_saddle_'+str(i),flip(saddle),'frame','fixed')
  add('board_cap_'+str(i),flip(cap),'nylon','fixed')
  add('board_M2x6_'+str(i),flip(screw(p+.8,6,2,2,1.9,1.5).translate((x,0,0))),'nylon','fixed')
  allowed.extend([['fixed_reaction_plate','post_'+str(i)],['post_'+str(i),'board_M2x6_'+str(i)]])
 for q in previous.k.head(p):add('pcb_'+q['name'],flip(q['shape']),'pcb' if q['name']=='board' else 'sensor_space' if 'tail' in q['kind'] else 'pcb_component','fixed',q['kind'],'reservation' if 'tail' in q['kind'] else 'candidate_solid')
 return out,dict(shaft_end=end,clip_sign=clip_sign,middle_key=middle_key,nominal_force_N=1114,gap_mm=1.5,magnet_face_mm=-18.3,board_back_mm=-p,intended_thread_pairs=allowed,manufacturing_released=False)

def main():
 out={}
 for sy in (-1,1):
  parts,meta=module4(42,sy);allow={frozenset(x) for x in meta['intended_thread_pairs']}
  static=[x for x in collision_pairs(parts) if frozenset((x['a'],x['b'])) not in allow];motion=[]
  for angle in (-20,0,15,30):
   posed=[dict(q,shape=q['shape'].rotate((0,0,0),(0,0,1),angle)) if q['owner']=='rotor' else q for q in parts]
   hits=collision_pairs(posed,True);motion.append(dict(angle=angle,hits=hits))
  print(json.dumps(dict(side=sy,static=static,motion=motion)),flush=True);out[str(sy)]=dict(meta=meta,static=static,motion=motion)
 h.save(ROOT/'verification/revM_girdle_cartridge_work.json',out)
if __name__=='__main__':main()
