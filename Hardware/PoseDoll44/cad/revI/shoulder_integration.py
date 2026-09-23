"""Add four actual spring face-clutch candidates to the Rev H assembly."""
from shoulder_clutch import *
from collision_policy import classify_checks
ROOT=h.ROOT;OUT=ROOT/'generated/revI'
BRIDGE_RISE_MM=30.0
def frame_transform(normal,xdir,origin):
 return cq.Location(cq.Plane(origin=tuple(origin),xDir=tuple(xdir),normal=tuple(normal)))
def build(name):
 p,parts,meta=h.build(name);T0,A0=h.fk(p,{})
 new=[];changed=[]
 for side,sy in [('l',1),('r',-1)]:
  S=A0[f'upperarm_{side}.flex']['origin']
  F=f'upperarm_{side}.flex_frame';B=f'upperarm_{side}.abduct_frame';E=f'clavicle_{side}'
  # Dogleg approach stays outside the new flex clutch disc, then reaches the
  # bearing from its inner side; original shoulder and elevation axes unchanged.
  R=A0[f'clavicle_{side}.elevate']['origin'];sd=S-R
  endpoint=sd+[0,-sy*31.5,0]
  fixed=[h.tube(0,min(sy*31,sy*37),max(sy*31,sy*37),6.5,2.1),
   h.rod((sy*34,0,0),(sy*34,endpoint[1],endpoint[2]+BRIDGE_RISE_MM),3.5),
   h.rod((sy*34,endpoint[1],endpoint[2]+BRIDGE_RISE_MM),endpoint+[0,0,BRIDGE_RISE_MM],3.5),
   h.rod(endpoint+[0,0,BRIDGE_RISE_MM],endpoint,3.5)]
  for y in (-36.5,-27.5):
   lo,hi=sorted((sy*(y-2.5),sy*(y+2.5)))
   fixed.append(h.tube(1,lo,hi,6.5,4.15,sd))
  fixed.append(h.rod(sd+[0,-sy*36.5,-5],sd+[0,-sy*27.5,-5],3))
  frame=h.union(fixed).cut(h.axis_cyl(1,min(-sy*42,-sy*23),max(-sy*42,-sy*23),4.15,sd))
  item=next(q for q in parts if q['name']==side+'_clavicle_output_frame')
  item['local_shape']=frame.translate(tuple(R-T0[E][:3,3]))
  item['note']='Rev I dogleg clavicle frame clears medial clutch; both kinematic axes unchanged'
  for label,normal,xd,base,tip,fixed_owner,rotor_owner in [
    ('flex',(0,-sy,0),(1,0,0),43,-24,E,F),
    ('abduct',(1,0,0),(0,0,1),26,-16,F,B)]:
   direction=np.array(normal);origin=S+direction*base;loc=frame_transform(normal,xd,origin)
   module=cartridge(tip)
   def add(n,sh,mat,owner,note):
    world=sh.moved(loc);local=world.translate(tuple(-T0[owner][:3,3]))
    assert local.isValid() and len(local.Solids())==1,n
    new.append(dict(name=side+'_'+label+'_clutch_'+n,local_shape=local,material=mat,owner=owner,role='structural_concept',note=note))
   for q in module:add(q['name'],q['shape'],q['material'],fixed_owner if q['owner']=='fixed' else rotor_owner,q['note'])
   # Fuse explicit mounting lugs and ribs into existing printed support.
   fixed_name=side+('_clavicle_output_frame' if label=='flex' else '_flex_ring')
   item=next(x for x in parts if x['name']==fixed_name)
   supports=mounting_lugs()
   for x in (-PITCH,PITCH):
    zroot=-11.5 if label=='flex' else -8
    supports.append(h.rod((x,0,zroot),(x,0,-5),3))
    if label=='flex':
     supports.append(h.rod((math.copysign(5,x),0,zroot),(x,0,zroot),3))
    else:
     supports.append(h.rod((math.copysign(5,x),0,-5.5),(x,0,zroot),2.5))
   for sh in supports:
    item['local_shape']=item['local_shape'].fuse(sh.moved(loc).translate(tuple(-T0[fixed_owner][:3,3])))
   # Recut holes after ribs, including the captured nut access.
   for x in (-PITCH,PITCH):
    for cut in (cyl(-7,5,1.7).translate((x,0,0)),hexagon(5.8,-6.1,-3.4).translate((x,0,0))):
     item['local_shape']=item['local_shape'].cut(cut.moved(loc).translate(tuple(-T0[fixed_owner][:3,3])))
   item['note']+='; Rev I integral clutch support and captive M3 mounting nuts'
   changed.append(fixed_name)
   # Positive D output instead of a smooth shaft glued into a print.
   target=side+('_flex_ring' if label=='flex' else '_abduct_ring_and_twist_seat')
   output=next(x for x in parts if x['name']==target)
   hub=cyl(tip,tip+(5.5 if label=='flex' else 6),6)
   socket=dshape(tip-.2,tip+6.2,6.2,2.6)
   local_move=lambda sh:sh.moved(loc).translate(tuple(-T0[rotor_owner][:3,3]))
   output['local_shape']=output['local_shape'].fuse(local_move(hub)).cut(local_move(socket))
   output['local_shape']=output['local_shape'].cut(local_move(cyl(tip-6,tip,5.2)))
   if label=='abduct':
    # Rear stub and vertical twist bush are installed AFTER the inner M3.
    # Through-tool passage is 3.3 mm; rear 4 mm support gets an actual socket.
    output['local_shape']=output['local_shape'].cut(local_move(cyl(-44,tip,1.65)))
    output['local_shape']=output['local_shape'].cut(local_move(cyl(-42,-35,2.1)))
   output['note']+='; Rev I 6 mm D drive, separate axial retention'
   changed.append(target)
   if label=='abduct':
    # Front bearing becomes OD8/ID6; rear 4mm stub is retained.
    ringpart=next(x for x in parts if x['name']==side+'_flex_ring')
    ringpart['local_shape']=ringpart['local_shape'].fuse(h.tube(0,18,23,6.5,4.15)).cut(h.axis_cyl(0,17,24,4.15))
    bushpart=next(x for x in parts if x['name']==side+'_abduct_bush_20.5')
    bushpart['local_shape']=h.tube(0,18,23,4,3.05)
  parts=[q for q in parts if q['name'] not in (side+'_flex_stub',side+'_abduct_stub_1')]
 parts+=new
 for q in parts:assert q['local_shape'].isValid() and len(q['local_shape'].Solids())==1,(q['name'],len(q['local_shape'].Solids()))
 meta=dict(meta,revision='I',new_shoulder_clutches=4,new_clutch_parts=len(new),
  changed_frames=sorted(set(changed)),bridge_rise_mm=BRIDGE_RISE_MM,scope='Four shoulder flex/abduct spring clutch candidates; inherited axes/encoder/whole-body gaps remain',
  preload_nominal_force_N=SPRING["catalog_force_N"],preload_loop_excludes_print=True,spring=SPRING,thrust=THRUST)
 return p,parts,meta

def quick():
 for name in (['quinn'] if '--quinn' in sys.argv else ['manny','quinn']):
  p,parts,meta=build(name)
  sample_names=['neutral','arms_forward','arms_side','arms_overhead','hands_on_hips','forehead','forward_up','asymmetric','crossed_clearance_candidate']
  checks=[]
  for label in sample_names:
   items,_,_=h.scene(parts,p,h.cases()[label]);hits=h.collisions(items)
   checks.append(dict(pose=label,angles_deg=h.cases()[label],hits=hits))
   print(json.dumps(dict(name=name,pose=label,hits=hits)),flush=True)
  r=classify_checks({'parts':[{k:v for k,v in q.items() if k!='local_shape'} for q in parts],'motion_checks':checks})
  h.save(ROOT/f'verification/revI_trial_{name}.json',r)
  items,_,_=h.scene(parts,p,{})
  OUT.joinpath(name).mkdir(parents=True,exist_ok=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in items if q['role']!='reservation'],OUT/name/'neutral.png',name.title()+' | Rev I shoulder holding candidate',camera=(1000,-1500,600))
if __name__=='__main__':quick()
