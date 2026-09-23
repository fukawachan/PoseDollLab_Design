"""Two measured wrist axes, direct drive and bolt-on intermediate frame."""
from arm_integration import *
import arm_integration as arms

def build(name):
 A,meta=arms.build(name)
 for side,sy in [('l',1),('r',-1)]:
  flex=A.joint(f'hand_{side}.flex','S6',(0,sy,0),(0,0,-1),26)
  dev=A.joint(f'hand_{side}.deviate','S6',(1,0,0),(0,0,1),14,board_rotation=90)
  W=A.A0[flex['axis']]['origin']
  wp=A.plate(flex,'fixed').moved(flex['loc'])
  branches=[]
  for x in (-6,6):
   path=[W+np.array(v) for v in [(x,sy*32,-26),(-20,sy*32,-26),(-20,sy*32,40),(0,0,45)]]
   for a,b in zip(path,path[1:]):
    wp=wp.fuse(h.rod(a,b,3));branches.append((a,b))
  distal=next(q for q in A.parts if q['name']==f'forearm_{side}_twist_M_distal_forearm_carrier')
  whole=h.move(distal['local_shape'],A.T0[distal['owner']]).fuse(wp)
  assert len(whole.Solids())==1
  distal['local_shape']=whole.translate(tuple(-A.T0[distal['owner']][:3,3]));distal['note']+='; integrated wrist flex mounting pad and two 6 mm branches'
  rp=A.plate(flex,'rotor').moved(flex['loc']);dp=A.plate(dev,'fixed').moved(dev['loc'])
  path=[W+np.array(v) for v in [(0,sy*15,14),(0,sy*15,24),(-16,sy*15,26),(-16,0,26),(20,0,26)]]
  frame=rp.fuse(dp)
  for a,b in zip(path,path[1:]):frame=frame.fuse(h.rod(a,b,2.5))
  A.add(f'hand_{side}_flex_M_intermediate_frame',frame,'frame',flex['rotor'],'Exposed wrist frame; concentric flex/deviation axes, 5 mm round members, fastener access reviewed separately')
  hand=A.plate(dev,'rotor')
  hand=hand.fuse(cube((12,12,4),(-23,0,-10.05)))
  # A centreline hand rail reaches the actual target hand-tip position.
  T=A.T0[f'hand_tip_{side}'][:3,3];start=W+np.array([4,0,-25]);end=W+.86*(T-W)
  mid=W+.40*(T-W)
  hand=hand.moved(dev['loc']).fuse(h.rod(start,mid,5)).fuse(h.rod(mid,end,5))
  # Openings let the fixed carrier exit the stable shell without compressing it.
  for sh in A.parts:
   if sh['name'].startswith(side+'_arm_forearm_shell_'):
    world=h.move(sh['local_shape'],A.T0[sh['owner']])
    for a,b in branches:world=world.cut(h.rod(a,b,3.4))
    assert world.isValid() and len(world.Solids())==1
    sh['local_shape']=world.translate(tuple(-A.T0[sh['owner']][:3,3]))
  A.add(f'hand_{side}_M_palm_rail',hand,'frame',dev['rotor'],'Hand rail points to the character-specific hand tip; palm shell and finger silhouette will be added around it')
 return A,dict(meta,stage='wrist_and_palm_rail_integration',channels=A.channels)

def main():
 result={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if '_M_' in q['name']}
  cases={'neutral':{},'closed_elbows':{'elbow_l.flex':145,'elbow_r.flex':145},'palm_up':{'elbow_l.flex':90,'forearm_l.twist':90},'wrist_flex':{'hand_l.flex':70,'hand_r.flex':70},'wrist_extend':{'hand_l.flex':-70,'hand_r.flex':-70},'deviate_in':{'hand_l.deviate':30,'hand_r.deviate':30},'deviate_out':{'hand_l.deviate':-30,'hand_r.deviate':-30}}
  checks=[]
  for label,pose in cases.items():
   scene=A.scene(pose);hits=fast_contacts(scene,A.thread_pairs,affected,label!='neutral')
   checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hits=hits)),flush=True)
  result[name]=dict(meta=meta,checks=checks)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name=name+'_RevM_wrists')
  for q in A.scene({}):assy.add(q['shape'],name=q['name'],color=cq.Color(*COL[q['material']]))
  assy.save(str(folder/(name+'_wrists.step')))
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({}) if q['role']!='reservation'],folder/'wrists.png',name.title()+' | measured wrist integration | work in progress',camera=(1000,-1500,600))
 h.save(ROOT/'verification/revM_wrist_work.json',result)
if __name__=='__main__':main()
