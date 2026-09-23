from abduct_encoder import *
from collision_policy import classify_checks
ROOT=h.ROOT;OUT=ROOT/'generated/revJ'
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
def build(name):
 p,parts,meta=previous.build(name);T0,A0=h.fk(p,{})
 created=[];changed=[]
 for side,sy in [('l',1),('r',-1)]:
  S=A0[f'upperarm_{side}.flex']['origin']
  for label,normal,xd,base,tip,target in [
   ('flex',(0,-sy,0),(1,0,0),43,-24,side+'_flex_ring'),
   ('abduct',(1,0,0),(0,0,1),26,-16,side+'_abduct_ring_and_twist_seat')]:
   q=next(q for q in parts if q['name']==target);owner=q['owner']
   loc=previous.frame_transform(normal,xd,S+np.array(normal)*base)
   to_local=lambda sh:sh.moved(loc).translate(tuple(-T0[owner][:3,3]))
   support,cuts=backing_and_cuts(tip)
   q['local_shape']=q['local_shape'].fuse(to_local(support))
   for cut in cuts:q['local_shape']=q['local_shape'].cut(to_local(cut))
   q['note']='Rev J removable split metal drive hub; flange fixed with two M2 screws, nut pockets and tool relief; strain/creep not verified'
   changed.append(q['name'])
   for x in hub(tip):
    created.append(dict(name=side+'_'+label+'_drive_'+x['name'],local_shape=to_local(x['shape']),material=x['material'],owner=owner,role='structural_concept',note=x['note']))
 parts+=created
 sensor_added=[];sensor_map=[]
 for side,sy in [('l',1),('r',-1)]:
  S=A0[f'upperarm_{side}.flex']['origin']
  loc=previous.frame_transform((-1,0,0),(0,0,sy),S)
  F=f'upperarm_{side}.flex_frame';B=f'upperarm_{side}.abduct_frame'
  to_owner=lambda sh,owner:sh.moved(loc).translate(tuple(-T0[owner][:3,3]))
  fixed=next(q for q in parts if q['name']==side+'_flex_ring')
  fixed['local_shape']=fixed['local_shape'].fuse(to_owner(fixed_support(),F))
  output=next(q for q in parts if q['name']==side+'_abduct_ring_and_twist_seat')
  support,cuts=rotating_socket()
  output['local_shape']=output['local_shape'].fuse(to_owner(support,B))
  for cut in cuts:output['local_shape']=output['local_shape'].cut(to_owner(cut,B))
  parts=[q for q in parts if q['name']!=side+'_abduct_stub_-1']
  for q in make_encoder():
   owner=B if q['owner']=='rotor' else F
   sensor_added.append(dict(name=side+'_abduct_sensor_'+q['name'],local_shape=to_owner(q['shape'],owner),
    material=q['material'],owner=owner,role='reservation' if q['owner']=='reservation' else 'sensor_candidate',note=q['note']))
  sensor_map.append(dict(axis_id=f'upperarm_{side}.abduct',fixed_owner=F,magnet_owner=B,
   module_origin_neutral_mm=S.tolist(),module_normal_neutral=[-1,0,0],module_xdir_neutral=[0,0,sy],
   geometric_angle_sign=-sy,raw_sensor_sign_calibrated=False,package_to_magnet_gap_mm=PACKAGE_GAP,
   board_datum_mm=PCB_DATUM,magnetic_field_verified=False))
 parts+=sensor_added
 for side in ('l','r'):
  meta['datums'][side]['pending_shoulder_axes_readout']=[f'upperarm_{side}.{key}' for key in ('flex','twist')]
 for q in parts:assert q['local_shape'].isValid() and len(q['local_shape'].Solids())==1,(q['name'],len(q['local_shape'].Solids()))
 meta=dict(meta,revision='J',new_drive_hubs=4,new_drive_parts=len(created),changed_frames=sorted(set(meta['changed_frames']+changed)),
  sensor_channels=sensor_map,new_sensor_parts=len(sensor_added),scope='Rev J four removable split drive hubs and two actual abduction sensor installation candidates')
 return p,parts,meta

def quick():
 p,parts,meta=build('quinn')
 selected=['neutral','arms_forward','arms_side','arms_overhead','forehead','crossed_clearance_candidate']
 records=[]
 for key in selected:
  items,_,_=h.scene(parts,p,h.cases()[key]);hits=h.collisions(items)
  print(json.dumps(dict(pose=key,hits=hits)),flush=True)
  records.append(dict(pose=key,angles_deg=h.cases()[key],hits=hits))
 record=classify_checks(dict(parts=[{k:v for k,v in q.items() if k!='local_shape'} for q in parts],motion_checks=records))
 h.save(ROOT/'verification/revJ_clamp_trial.json',record)
if __name__=='__main__':quick()
