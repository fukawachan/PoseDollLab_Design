"""Opposite-side AS5048A encoder candidate; actual sensor_revB STEP solids.
Module +Z points behind the shoulder (-world X). No magnetic performance claim.
"""
from drive_clamp import *
COL=dict(COL,nylon=(.90,.88,.76),brass=(.71,.57,.23),pcb_component=(.20,.23,.25))
PCB_DATUM=41.895
MAGNET_BOTTOM=34.0
MAGNET_TOP=36.5
PACKAGE_GAP=2.8

def screw_z(a,length,head_h=1.4,head_r=1.75,reverse=False):
 # a is the head seating plane. Reverse: head is below a, shaft extends +Z.
 if reverse:return cyl(a,a+length,1).fuse(cyl(a-head_h,a,head_r))
 return cyl(a-length,a,1).fuse(cyl(a,a+head_h,head_r))

def make_encoder():
 parts=[]
 def add(n,sh,m,o,note):
  assert sh.isValid() and len(sh.Solids())==1,(n,len(sh.Solids()))
  parts.append(dict(name=n,shape=sh,material=m,owner=o,note=note))
 # D drive inside rotating yoke, a smooth 4 mm journal, outer D for magnet carrier.
 shaft=dshape(12,17,4,1.5).fuse(cyl(17,24,2)).fuse(dshape(24,30,4,1.5))
 shaft=shaft.cut(cyl(24.5,30.1,.8)).cut(cross_cyl(0,2.1,.8,0,15))
 add('rear_journal',shaft,'aluminum','rotor','Custom nonferromagnetic 4 mm journal; inner radial M2 and outer axial M2 retention')
 radial=cross_cyl(0,4,1,0,15).fuse(cross_cyl(4,6,1.9,0,15))
 radial=radial.cut(hexagon(1.5,0,1.1).rotate((0,0,0),(0,1,0),90).translate((5,0,15)))
 add('journal_radial_M2x4',radial,'brass','rotor','Candidate nonferromagnetic M2x4; keyed shaft is installed after front clutch screw, before twist shaft')
 carrier=cyl(24,36.5,5.3)
 for x in (-5,5):carrier=carrier.fuse(cyl(31,36.5,2.4).translate((x,0,0)))
 carrier=carrier.cut(dshape(23.9,30,4.1,1.55))
 carrier=carrier.cut(cyl(29.9,31.1,1.1)).cut(cyl(31,34,2.0))
 carrier=carrier.cut(cyl(34,36.6,3.1))
 for x in (-5,5):carrier=carrier.cut(cyl(30.9,36.6,.8).translate((x,0,0)))
 add('magnet_carrier',carrier,'frame','rotor','D driven magnet cup with separate axial screw; 0.1 mm radial adhesive bed prevents magnet rotation; adhesive selection and rotational slip test pending')
 add('carrier_axial_M2x6',screw_z(31,6),'nylon','rotor','Insert before magnet; nonmagnetic M2 screw into rear journal')
 add('diametric_magnet_6x2p5',cyl(MAGNET_BOTTOM,MAGNET_TOP,3),'magnet','rotor','6 x 2.5 mm diametrically magnetized candidate, never axially magnetized; grade and diagnostics require testing')
 bridge=cube((14.8,4.8,.8),(0,0,36.9))
 for x in (-5,5):bridge=bridge.cut(cyl(36.4,37.4,1.1).translate((x,0,0)))
 add('magnet_retaining_bridge',bridge,'frame','rotor','Positive removable cover; magnet face seats at 36.5 mm, no adhesive-only axial retention')
 for i,x in enumerate((-5,5)):
  add('magnet_cover_M2x6_'+str(i),screw_z(37.3,6).translate((x,0,0)),'nylon','rotor','Nominal M2 nylon screw into cup; printed threads not qualified')
 pcb=cq.importers.importStep(str(h.ROOT/'generated/revC/step/sensor_revB.step')).val()
 solids=pcb.Solids()
 assert len(solids)==7,len(solids)
 labels=['AS5048A','passive_1','passive_2','passive_3','passive_4','J1_back_connector','board']
 for name,sh in zip(labels,solids):
  add('pcb_'+name,sh.rotate((0,0,0),(1,0,0),180).translate((0,0,PCB_DATUM)),
   'pcb' if name=='board' else 'pcb_component','fixed','Actual sensor_revB STEP; model holes/parts preserved; 1.51 mm STEP board versus 1.6 mm nominal fabrication')
 for i,x in enumerate((-6.5,6.5)):
  spacer=ring(PCB_DATUM,PCB_DATUM+6,2.3,.8).translate((x,6.5,0))
  add('nylon_spacer_'+str(i),spacer,'nylon','fixed','M2 female 6 mm spacer; electrical insulation and spreaders required')
  add('nylon_spreader_'+str(i),ring(PCB_DATUM-2.01,PCB_DATUM-1.51,2.2,1.1).translate((x,6.5,0)),'nylon','fixed','0.5 mm insulating spreader, OD4.4/ID2.2')
  add('board_M2x4_'+str(i),screw_z(PCB_DATUM-2.01,4,reverse=True).translate((x,6.5,0)),'nylon','fixed','Front board screw; 1.99 mm nominal engagement')
  add('support_M2x6_'+str(i),screw_z(PCB_DATUM+9,6).translate((x,6.5,0)),'nylon','fixed','Rear support screw; 3 mm nominal engagement; 1.01 mm gap to opposing screw')
 # Placeholder includes mated plug and service bend; this is NOT a vendor plug model.
 add('plug_service_envelope',cube((13,8,7),(0,-6.6,PCB_DATUM+7.83)),'sensor_space','reservation','Unverified mated plug insertion envelope beyond actual connector')
 add('wire_service_envelope',cube((12,10,12),(0,-10,PCB_DATUM+17.33)),'sensor_space','reservation','Initial cable bend allowance only; no routed harness')
 return parts

def fixed_support():
 P=PCB_DATUM
 support=cube((26,5,3),(0,6.5,P+7.5))
 for sign in (-1,1):
  support=support.fuse(h.rod((sign*4,0,20.5),(sign*11.5,6.5,24),1.5))
  support=support.fuse(h.rod((sign*11.5,6.5,24),(sign*11.5,6.5,P+7.5),1.5))
 for x in (-6.5,6.5):support=support.cut(cyl(P+5.9,P+9.1,1.1).translate((x,6.5,0)))
 return support

def rotating_socket():
 support=cyl(12,17,4)
 cuts=[dshape(11.9,17.1,4.1,1.55),cross_cyl(1.4,6.1,1.1,0,15)]
 return support,cuts

def allowed_thread(a,b):
 a,b=sorted((a,b))
 if {a,b}=={'journal_radial_M2x4','rear_journal'}:return True
 if {a,b}=={'carrier_axial_M2x6','rear_journal'}:return True
 if (a=='magnet_carrier' and b.startswith('magnet_cover_M2x6_')) or (b=='magnet_carrier' and a.startswith('magnet_cover_M2x6_')):return True
 for i in (0,1):
  if {a,b} in ({'board_M2x4_'+str(i),'nylon_spacer_'+str(i)},{'support_M2x6_'+str(i),'nylon_spacer_'+str(i)}):return True
 return False

def quick():
 parts=make_encoder();support=fixed_support();pocket,cuts=rotating_socket()
 print(json.dumps({'encoder_parts':len(parts),'support_valid':support.isValid(),'support_solids':len(support.Solids())}),flush=True)
 folder=h.ROOT/'generated/revJ';folder.mkdir(exist_ok=True)
 h.render([(q['name'],q['shape'],COL[q['material']]) for q in parts if q['owner']!='reservation']+[('support',support,COL['frame'])],folder/'encoder_module.png','Rev J | actual PCB + magnet installation')
if __name__=='__main__':quick()
