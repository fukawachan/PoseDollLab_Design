"""Unified SH6 sensor cables on all 41 axes; two shoulder boards keep large mounting pattern."""
from power_case import *
import power_case as body
from assembly_cache import get_assembly

def build(name):
 A,meta=get_assembly(name,body.build,ROOT,'powerbody')
 records=[];affected=[]
 for c in channels41(A,name):
  if not(c['axis_id'].startswith('upperarm_') and c['axis_id'].endswith('.abduct')):continue
  loc=cq.Location(cq.Plane(origin=tuple(c['origin_neutral_mm']),normal=tuple(c['normal_neutral']),xDir=tuple(c['xdir_neutral'])));datum=c['package_face_mm']+2.595;pre=c['part_prefix']
  q,_=world_part(A,pre+'pcb_J1_back_connector');plug=cube((9.4,9.6,3.3),(0,-4.5,datum+1.65)).moved(loc)
  replace_world(A,q,plug,'JST SH6 SM06B-SRSS-TB with conservative mated allocation; actual 18 x20 x1.6 PCB keeps chip, holes and native pin order; wire exit toward local +Y','pcb_component');affected.append(q['name'])
  q,_=world_part(A,pre+'pcb_passive_3');cap=cube((2.3,1.45,1.45),(5.7,2.3,datum-1.595-.725)).moved(loc)
  replace_world(A,q,cap,'CL21A106KAYNNNE maximum body envelope, 10 uF 25 V X5R','pcb_component');affected.append(q['name'])
  A.parts=[q for q in A.parts if q['name'] not in (pre+'plug_service_envelope',pre+'wire_service_envelope')]
  records.append(dict(axis_id=c['axis_id'],connector_part=pre+'pcb_J1_back_connector',board_rotation_deg=0,PCB='electronics/sensor_revM_large_sh/PoseDoll_AS5048A_revM_large_sh.kicad_pcb',socket='SM06B-SRSS-TB(LF)(SN)',mated_envelope_mm=[9.4,9.6,3.3],datum_mm=datum,wire_exit_local_mm=[0,.3,datum+1.65],wire_direction_local=[0,1,0]))
 assert len(records)==2
 # Direct view of the power LED through a 3 mm hole in the separate rear cover.
 O=np.array(meta['power_compartment']['origin_mm']);q,w=world_part(A,'POWER_case_rear');w=w.cut(xcyl(-40.1,-33.9,1.5,-12,-46).translate(tuple(O)));replace_world(A,q,w,q['note']+'; 3 mm direct-view opening for the green power indicator',q['material']);affected.append(q['name'])
 return A,dict(meta,sensor_heads=meta['sensor_heads']+records,affected_large_sensor_parts=affected,all_sensor_connector_family='JST SH6')

def main():
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name);cases,_=poses(A);cache=CollisionCache(A);checks=[];read=readout(A,channels41(A,name),cases)
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,set(meta['affected_large_sensor_parts']),label!='neutral'),A.parts);bad=[r for r in review if r['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,review=review))
   if bad:print(json.dumps(dict(character=name,pose=label,structural=bad)),flush=True)
  out[name]=dict(heads=meta['sensor_heads'],checks=checks,readout=read);h.save(ROOT/'verification/revM_large_SH_heads_work.json',out);print(name,'finished',len(checks),'failed',sum(any(r['classification']=='structural' for r in x['review']) for x in checks),flush=True)
if __name__=='__main__':main()
