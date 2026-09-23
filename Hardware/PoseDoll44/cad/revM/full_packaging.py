"""Torso and neck packaging after all girdle readout cartridges are present."""
from girdle_integration import *
import girdle_integration as girdle
import legacy_threads

def apply_packaging(A):
 # Move the chest pitch/roll connecting arch to the front, away from right yaw readout.
 f=A.joints['chest.pitch'];r=A.joints['chest.roll'];O=A.A0['chest.pitch']['origin'];dry=Assembly(A.profile)
 ps=[dry.plate(f,'rotor').moved(f['loc']),dry.plate(r,'fixed').moved(r['loc']),rails([O+v for v in np.array([(0,-25,19),(0,-25,29),(21,-25,31),(21,0,31),(25,0,31)])],2.5)]
 q,_=world_part(A,'chest_pitch_M_intermediate_frame');replace_world(A,q,union_checked(ps,'chest_front_arch'),'Metal anterior chest pitch/roll arch, clears the shoulder-girdle readout behind it')
 # Replace the bulky neck with three T4 cartridges, preserving anatomical centres.
 removed={q['name'] for q in A.parts if q['name'].startswith('head_')};A.parts=[q for q in A.parts if q['name'] not in removed]
 A.thread_pairs=[x for x in A.thread_pairs if not set(x)&removed];A.channels=[x for x in A.channels if not x['axis_id'].startswith('head.')]
 for k in list(A.joints):
  if k.startswith('head.'):del A.joints[k]
 from neck_light import add_light_neck,merge_links
 y,f,r=add_light_neck(A)
 C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin']
 support=rails([C+[-57,10,35],C+[-57,35,35],C+[65,35,35],C+[65,0,35],[C[0]+65,0,N[2]-36],N+[35,0,-28],N+[15,0,-28],N+[15,0,-30],N+[6.3,0,-30]],3)
 merge_links(A,['chest_M_body_frame',y['prefix']+'fixed_housing'],[support],'chest_M_body_frame','chest','Continuous metal chest frame with integrated T4 neck bearing, four girdle cartridges and centre-line anterior support; machining split pending')
 return A

def build(name):
 A,meta=girdle.build(name,neck_support=False);apply_packaging(A);legacy_threads.apply(A);return A,dict(meta,neck_packaging='T4_integral_housings_yaw34_pitch38_roll38_posterior_roll')

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);aff={q['name'] for q in A.parts if '_G4_' in q['name'] or q['name'].startswith('head_') or q['name'] in ('chest_M_body_frame','chest_pitch_M_intermediate_frame','l_yaw_carriage','r_yaw_carriage','l_clavicle_output_frame','r_clavicle_output_frame')};rows=[]
  cases={k:v for k,v in h.cases().items() if k in ('neutral','forward','backward','shrug','down','forward_up','back_down','asymmetric')}
  cases.update(head_turn={'head.yaw':75},head_other={'head.yaw':-75},head_nod={'head.pitch':55},head_up={'head.pitch':-45},head_tilt={'head.roll':35},head_tilt_other={'head.roll':-35},chest_bend={'chest.pitch':30},chest_roll={'chest.roll':20})
  if '--combined' in sys.argv:
   cases.update({f'head_combo_{y}_{p}_{r}':{'head.yaw':y,'head.pitch':p,'head.roll':r} for y in (-75,0,75) for p in (-45,55) for r in (-35,35)})
   for label,pose in list(cases.items()):
    if label in ('forward_up','back_down','asymmetric'):
     for y,p in ((-75,-45),(75,55)):
      cases[f'{label}_head_{y}_{p}']=dict(pose,**{'head.yaw':y,'head.pitch':p})
  if '--probe' in sys.argv:cases={k:v for k,v in cases.items() if k in ('neutral','shrug','head_turn','head_nod')}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,aff,label!='neutral');rows.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,count=len(hits),hits=hits[:16])),flush=True)
  out[name]=dict(meta=meta,checks=rows)
 h.save(ROOT/'verification/revM_upper_body_packaging_work.json',out)
if __name__=='__main__':main()
