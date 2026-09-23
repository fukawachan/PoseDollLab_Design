"""Full leg mechanisms on both exact character skeletons; integration work."""
from hand_shells import *
import hand_shells as upper
from mechanism_modules import yx_pair,distal_twist,distal_stem,hinge_upper,hinge_lower,proximal_yx

def build(name):
 A,meta=upper.build(name);legs=[]
 for side,sy in [('l',1),('r',-1)]:
  hf,ha=yx_pair(A,f'thigh_{side}.flex',f'thigh_{side}.abduct',sy,'H6P2')
  ht=distal_twist(A,ha,f'thigh_{side}.twist','H6P2')
  knee=A.joint(f'calf_{side}.flex','H6',(0,sy,0),(0,0,1),5.525)
  af,ai=yx_pair(A,f'foot_{side}.dorsiflex',f'foot_{side}.invert',sy,'M6')
  toe=A.joint(f'ball_{side}.flex','S6',(0,sy,0),(-1,0,0),5.525)
  H=A.A0[hf['axis']]['origin'];K=A.A0[knee['axis']]['origin'];F=A.A0[af['axis']]['origin'];B=A.A0[toe['axis']]['origin'];T=A.T0[f'toe_tip_{side}'][:3,3]
  thigh=distal_stem(A,ht).fuse(hinge_upper(A,knee,float(H[2]-K[2])-105))
  A.add(f'thigh_{side}_M_centreline_frame',thigh,'frame',ht['rotor'],'Hollow centreline thigh between the measured hip twist and metal knee eye')
  calf=hinge_lower(A,knee,float(K[2]-F[2])-38)
  ankle,branches=proximal_yx(A,af,F+[0,0,45],45);calf=calf.fuse(ankle)
  A.add(f'calf_{side}_M_centreline_frame',calf,'frame',knee['rotor'],'Centreline calf with external ankle yoke; hollow section, explicit M3 joint mounts')
  foot=A.plate(ai,'rotor').moved(ai['loc']).fuse(A.plate(toe,'fixed').moved(toe['loc']))
  # Foot tray stays above the reference sole; heel/toe clearances are checked separately.
  sole=A.T0[f'sole_{side}'][:3,3];zfloor=float(sole[2]+5)
  tray=cube((float(B[0]-F[0])+25,30,4),((F[0]+B[0])/2-8,F[1],zfloor))
  foot=foot.fuse(tray)
  foot=foot.fuse(h.rod(F+[4.8,0,-19],F+[4.8,0,-27],3))
  for y in (-8,8):foot=foot.fuse(h.rod(F+[4.8,0,-27],F+[-2,y,zfloor-F[2]+1],3))
  for z in (-6,6):foot=foot.fuse(h.rod(B+[-26,sy*11.525,z],B+[-30,sy*11.525,zfloor-B[2]+1],3))
  A.add(f'foot_{side}_M_tray',foot,'frame',ai['rotor'],'Foot tray with measured toe hinge; 5 mm nominal stand-off above reference sole, exterior foot shell pending')
  fore=A.plate(toe,'rotor').moved(toe['loc'])
  start=B+[14,-sy*4.525,0];bend=B+[26,-sy*4.525,0];end=B+.90*(T-B)
  fore=fore.fuse(h.rod(start,bend,2)).fuse(h.rod(bend,end,4))
  A.add(f'ball_{side}_M_forefoot_frame',fore,'frame',toe['rotor'],'Rigid forefoot rail towards the character-specific toe tip; no toe-finger channels')
  legs.append(dict(side=side,hip_twist_offset_mm=float(ht['origin'][2]-H[2]),hip_pivot=H.tolist(),knee_pivot=K.tolist(),ankle_pivot=F.tolist(),toe_pivot=B.tolist()))
 return A,dict(meta,stage='full_leg_integration',legs=legs,channels=A.channels)

def main():
 result={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if q['name'].startswith(('thigh_','calf_','foot_','ball_'))}
  cases={'neutral':{},'relaxed_standing':{'upperarm_l.abduct':15,'upperarm_r.abduct':15},'sitting':{f'{p}_{s}.flex':90 for p in ('thigh','calf') for s in ('l','r')},'knee_deep':{f'calf_{s}.flex':155 for s in ('l','r')},'hip_out':{f'thigh_{s}.abduct':65 for s in ('l','r')},'hip_twist':{'thigh_l.twist':50,'thigh_r.twist':-50},'ankle_toe':{f'foot_{s}.dorsiflex':-45 for s in ('l','r')}|{f'ball_{s}.flex':60 for s in ('l','r')}}
  checks=[]
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral')
   checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hit_count=len(hits),leg_internal=[v for v in hits if all(v[k].startswith(('thigh_','calf_','foot_','ball_')) for k in ('a','b'))])),flush=True)
  result[name]=dict(meta=meta,checks=checks)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name=name+'_RevM_legs')
  for q in A.scene({}):assy.add(q['shape'],name=q['name'],color=cq.Color(*COL[q['material']]))
  assy.save(str(folder/(name+'_legs.step')))
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({}) if q['role']!='reservation'],folder/'legs.png',name.title()+' | full limb mechanisms | integration work',camera=(1300,-2300,1000))
 h.save(ROOT/'verification/revM_leg_work.json',result)
if __name__=='__main__':main()
