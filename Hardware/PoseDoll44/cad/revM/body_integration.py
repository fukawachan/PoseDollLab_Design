"""Continuous pelvis-to-skull structure, no external stand. Work in progress."""
from trunk_integration import *
from neck_module import add_neck

def build(name):
 A,meta=limbs.build(name);trunk=add_trunk(A);neck=add_neck(A)
 W=A.A0['waist.yaw']['origin'];C=A.A0['chest.yaw']['origin'];P=A.T0['pelvis'][:3,3];N=A.A0['head.yaw']['origin']
 wy,wf,wr=trunk['waist'];cy,cf,cr=trunk['chest']
 root=A.plate(wy,'fixed').moved(wy['loc'])
 root=root.fuse(rails([W+[29,0,-68],W+[45,0,-68],P+[52,0,-65],P+[-78,0,-65]],4))
 for side,sy in [('l',1),('r',-1)]:
  hip=A.joints[f'thigh_{side}.flex'];H=A.A0[hip['axis']]['origin'];root=root.fuse(A.plate(hip,'fixed').moved(hip['loc']))
  root=root.fuse(rails([H+[0,sy*42,-31],H+[-78,sy*42,-31],[H[0]-78,H[1]+sy*42,P[2]-65],P+[-78,0,-65]],4))
 A.add('pelvis_M_body_frame',root,'aluminum_7075','pelvis','Permanent internal pelvis frame, no external stand; root forward is a fixed local reference')
 # Merge the existing chest bearing frame into one continuous output structure.
 old=next(q for q in A.parts if q['name']=='common_chest_bearing_frame');world=old['local_shape'].translate(tuple(A.T0['chest'][:3,3]));A.parts.remove(old)
 pieces=[world,A.plate(cr,'rotor').moved(cr['loc']),rails([C+[7,0,-20],C+[7,0,0],C+[-57,0,0],C+[-57,0,35]],3)]
 for sy in (-1,1):pieces.append(rails([C+[-57,0,35],C+[-57,sy*10,35]],3.5))
 pieces.append(A.plate(neck[0],'fixed').moved(neck[0]['loc']))
 # Extend the rising rail 3 mm below the crossbar; the former tangent junction
 # made OpenCascade discard the lower body despite returning a valid solid.
 pieces.append(rails([C+[-57,10,32],C+[-57,30,130],N+[27,20,-42],N+[27,0,-42]],3.5))
 sh=union_checked(pieces,'chest_body')
 A.add('chest_M_body_frame',sh,'aluminum_7075','chest','Existing paired clavicle bearings now connect to chest roll and fixed neck yaw mount; torso shell remains separate')
 return A,dict(meta,stage='continuous_body_frame',root_reference='pelvis_local_fixed',measured_axes=41,trunk_joints={s:[j['axis'] for j in js] for s,js in trunk.items()},head_joints=[j['axis'] for j in neck])

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if q['name'].startswith(('pelvis_','waist_','chest_','head_'))};checks=[]
  relaxed={'upperarm_l.abduct':15,'upperarm_r.abduct':15}
  cases={'neutral':{},'standing':relaxed,'sit':relaxed|{'thigh_l.flex':90,'thigh_r.flex':90,'calf_l.flex':90,'calf_r.flex':90},'trunk_bend':relaxed|{'waist.pitch':40,'chest.pitch':30},'trunk_extend':relaxed|{'waist.pitch':-20,'chest.pitch':-20},'trunk_lean':relaxed|{'waist.roll':25,'chest.roll':20},'head_nod':relaxed|{'head.pitch':55},'head_look_up':relaxed|{'head.pitch':-45},'hip_back':relaxed|{'thigh_l.flex':-30,'thigh_r.flex':-30},'hip_out':relaxed|{'thigh_l.abduct':65,'thigh_r.abduct':65}}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral');checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,count=len(hits),hits=hits[:12])),flush=True)
  out[name]=dict(meta=meta,checks=checks)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene(relaxed) if q['role']!='reservation'],folder/'body.png',name.title()+' | body integration work',camera=(1500,-2700,1100))
 h.save(ROOT/'verification/revM_body_work.json',out)
if __name__=='__main__':main()
