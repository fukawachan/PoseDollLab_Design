"""Two friction faces for six trunk axes, without moving any encoder datum.
Digital candidate. mu=.15 is an acceptance assumption, not a material guarantee.
"""
from retained_bushes import *
import retained_bushes as bearings
COL['peek']=(.78,.71,.52)
COL['steel_17_4']=(.48,.51,.54)

def dual_face(A):
 rows=[]
 for axis,j in A.joints.items():
  if not axis.startswith(('waist.','chest.')):continue
  pre=j['prefix'];loc=j['loc'];sp=j['meta']['spring'];parallel=3;F=3*sp['F']
  # Keep the captured radial bush and all original spring/encoder axial datums.
  # A steel reaction washer supports the thin PEEK ring; its two screws carry
  # torque into the fixed eye. It is removable for installing the flanged bush.
  liner=ring(5,5.5,11,5)
  for sy in (-1,1):liner=liner.fuse(cube((2,2,.5),(0,sy*10.8,5.25)))
  reaction=ring(4,5,12.5,5).fuse(ring(5,5.5,12.5,11).cut(liner))
  eye,ew=world_part(A,pre+'fixed_metal_eye');ew=ew.moved(loc.inverse)
  for i,sy in enumerate((-1,1)):
   y=sy*14.;reaction=fuse_checked(reaction,cube((6,6,1),(0,y,4.5)),'dual_reaction_ear')
   cone=cq.Solid.makeCone(1,2,1.2,cq.Vector(0,y,3.8))
   reaction=reaction.cut(cyl(3.9,5.1,1.1).translate((0,y,0))).cut(cone)
   ew=ew.cut(cyl(1.9,4.1,.8).translate((0,y,0))).cut(cone)
   screw=cyl(2,3.8,1).translate((0,y,0)).fuse(cone).cut(cube((.6,3.3,.55),(0,y,4.825)))
   bn=pre+'upper_face_M2x3_'+str(i);A.add(bn,screw.moved(loc),'metal',j['fixed'],'M2x3 countersunk screw, nominal 2 mm engagement in fixed eye; axial spring force seats reaction plate directly on metal, screw carries reaction torque')
   A.thread_pairs.append([bn,eye['name']])
  replace_world(A,eye,ew.moved(loc),eye['note']+'; two M2 tapped upper reaction mounts and shallow countersink runout',eye['material'])
  q,_=world_part(A,pre+'thrust_wear_washer');replace_world(A,q,reaction.moved(loc),'Custom removable ground 17-4PH H900 reaction washer, 1 mm web and keyed upper PEEK pocket; captures radial bush flange below Z4','steel_17_4')
  A.add(pre+'upper_PEEK_friction_ring',liner.moved(loc),'peek',j['fixed'],'Unfilled machined PEEK, 0.50 mm finished, R5..11 and two tabs; dry contact against ground steel pressure plate; torque/creep/wear acceptance required')
  # A deep D-hub transmits torque without loading a thin keyed sheet edge.
  plate=cyl(5.5,6,11).fuse(cyl(4.15,5.5,4.8)).cut(dshape(4.1,6.1,3.05,2.55))
  q,_=world_part(A,pre+'spring_seat');replace_world(A,q,plate.moved(loc),'Ground 17-4PH H900 pressure plate with 1.85 mm deep D6 hub; 0.2 mm radial gap to reaction washer, lower hub clear of POM flange','steel_17_4')
  q,sw=world_part(A,pre+'flanged_rotor_shaft');sw=sw.moved(loc.inverse);se=j['meta']['shaft_end_mm']
  sw=sw.cut(cube((20,30,se-4+.2),(12.5,0,(se+4)/2)))
  replace_world(A,q,sw.moved(loc),q['note']+'; extended D-flat above bearing Z4 drives upper pressure plate; journal below Z3.9 remains round',q['material'])
  if axis.startswith('waist.'):
   # Three nested springs each side, plus 1.2 mm solid spacer; same cap height
   # as the previous four-parallel package, 1656 N instead of 2208 N.
   for i in range(2):
    dead=pre+'disc_spring_'+str(i)+'_3';A.parts=[q for q in A.parts if q['name']!=dead]
    for k in range(3):
     q,sw=world_part(A,pre+'disc_spring_'+str(i)+'_'+str(k));delta=1.2 if i==0 else .6
     replace_world(A,q,sw.moved(loc.inverse).translate((0,0,delta)).moved(loc),'SCHNORR 002200, three nested in each of two opposed groups; nominal 1656 N at catalog test height','spring')
   A.add(pre+'three_parallel_height_spacer',ring(6,7.2,6,3.1).moved(loc),'steel_17_4',j['rotor'],'Ground steel spacer 1.20 mm, preserves cap and sensor position after reducing waist spring count from eight to six')
  reff2=2/3*(11**3-5**3)/(11**2-5**2);cr=j['meta']['clutch_outer_radius_mm'];reff1=2/3*(cr**3-4.1**3)/(cr**2-4.1**2)
  nominal=.15*F*(reff1+reff2)/1000
  j['meta'].update(nominal_torque_Nm=nominal,clutch_force_nominal_N=F,friction_faces=2,upper_contact_mean_radius_mm=reff2,friction_mu_assumed=.15,preload_validation_required=True)
  row=dict(axis=axis,lower_radius_mm=cr,upper_radius_mm=11,upper_ID_mm=10,upper_lining_thickness_mm=.5,force_nominal_N=F,upper_mean_pressure_MPa=F/(math.pi*(11**2-5**2)),nominal_torque_Nm=nominal,measured_torque_Nm=None,encoder_datum_changed=False)
  rows.append(row)
 return rows

def shoulder_faces(A):
 rows=[]
 for side,sy in [('l',1),('r',-1)]:
  S=A.A0['upperarm_'+side+'.twist']['origin'];loc=cq.Location(cq.Plane(origin=tuple(S),normal=(0,0,1),xDir=(sy,0,0)))
  fq,fw=world_part(A,side+'_abduct_ring_and_twist_seat');rq,rw=world_part(A,side+'_twist_rotor_face')
  replace_world(A,fq,fuse_checked(fw,ring(-9,-8,10,8.5).moved(loc),'twist_fixed_contact'),fq['note']+'; outer friction contact radius increased to 10 mm',fq['material'])
  replace_world(A,rq,fuse_checked(rw,ring(-12,-10,10,8.5).moved(loc),'twist_rotor_contact'),rq['note']+'; outer friction contact radius increased to 10 mm',rq['material'])
  candidates=[q for q in A.parts if q['owner']==fq['owner'] and q['material']=='lining' and q['name'].startswith(side+'_twist')]
  assert len(candidates)==1,[q['name'] for q in candidates]
  q=candidates[0];w=h.move(q['local_shape'],A.T0[q['owner']]);replace_world(A,q,fuse_checked(w,ring(-10,-9,10,8.5).moved(loc),'twist_lining_contact'),q['note']+'; unfilled PEEK ring R3.15..10, dry contact candidate','peek')
  j=A.joints['upperarm_'+side+'.twist'];reff=2/3*(10**3-3.15**3)/(10**2-3.15**2);j['meta']['nominal_torque_Nm']=.15*294*reff/1000
  rows.append(dict(axis=j['axis'],force_N=294,outer_radius_mm=10,nominal_torque_Nm=j['meta']['nominal_torque_Nm']))
 return rows

def strong_output_keys(A):
 rows=[]
 for axis,j in A.joints.items():
  if j['size'] not in ('H6','H6P2','H6P3','H6P4'):continue
  pre=j['prefix'];loc=j['loc'];q,w=world_part(A,pre+'flanged_rotor_shaft');w=w.moved(loc.inverse)
  w=fuse_checked(w,dshape(-9,-3,4,3.5),'D8_output_key').cut(h.axis_cyl(0,0,4.1,.8,(0,0,-5.5)))
  replace_world(A,q,w.moved(loc),q['note']+'; D8/flat3.5 output below flange, D6 journal preserved; 7075-T6 material candidate; radial M2 pilot retained','aluminum_7075')
  q,w=world_part(A,pre+'D_output_cleat');w=w.moved(loc.inverse).cut(dshape(-8.1,-2.95,4.05,3.55))
  replace_world(A,q,w.moved(loc),q['note']+'; enlarged D8 output bore matches strengthened high-load shaft','aluminum_7075')
  rows.append(dict(axis=axis,journal_mm=6,output_D_mm=8,output_flat_mm=3.5,physical_tested=False))
 return rows

def build(name):
 A,meta=bearings.build(name);rows=dual_face(A);arms=shoulder_faces(A);keys=strong_output_keys(A)
 for q in A.parts:
  if q['material']=='lining':q['material']='peek';q['note']+='; unfilled machined PEEK candidate, dry contact; actual torque and creep must be qualified'
 return A,dict(meta,trunk_dual_friction=rows,shoulder_twist_contact=arms,high_load_D8_outputs=keys)


def main():
 from trunk_integration import build as trunk_build
 results={}
 for name in ('manny','quinn'):
  A,_=trunk_build(name,isolated=True)
  # Install the same captured bush before checking the changed upper thrust path.
  for j in A.joints.values():captured8(A,j['prefix'],j['prefix']+'fixed_metal_eye',j['loc'])
  rows=dual_face(A);cache=CollisionCache(A);checks=[]
  cases={'neutral':{},'bend':{'waist.pitch':40,'chest.pitch':30},'extend':{'waist.pitch':-20,'chest.pitch':-20},'roll':{'waist.roll':25,'chest.roll':20},'yaw':{'waist.yaw':35,'chest.yaw':35}}
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,skip_same_owner=label!='neutral'),A.parts);checks.append(dict(pose=label,review=review));print(json.dumps(dict(character=name,pose=label,contacts=review)),flush=True)
  results[name]=dict(modules=rows,checks=checks);h.save(ROOT/'verification/revM_dual_trunk_component_work.json',results)
if __name__=='__main__':main()
