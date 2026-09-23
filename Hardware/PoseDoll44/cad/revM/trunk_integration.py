"""Waist/chest mechanisms on exact skeleton axis lines. Integration work."""
from assembly_core import *
import leg_integration as limbs
from mechanism_modules import yx_pair

def rails(points,r=3):return h.union([h.rod(a,b,r) for a,b in zip(points,points[1:])])

def upper_pair(A,stem,size):
 ro=SPECS[size]['ro'];rf=2*ro+4;rd=44 if stem=='waist' else ro+3
 f=A.joint(stem+'.pitch',size,(0,1,0),(0,0,1),rf,board_rotation=90)
 r=A.joint(stem+'.roll',size,(1,0,0),(0,0,-1),rd,board_rotation=90)
 O=A.A0[f['axis']]['origin']
 sh=A.plate(f,'rotor').moved(f['loc']).fuse(A.plate(r,'fixed').moved(r['loc']))
 pts=[O+v for v in np.array([(0,rf-11,-ro-4),(0,rf-11,-ro-14),(-ro-5,rf-11,-ro-16),(-ro-5,0,-ro-16),(rd+6,0,-ro-16)])]
 sh=sh.fuse(rails(pts,3))
 A.add(stem+'_M_pitch_roll_frame',sh,'aluminum_7075',f['rotor'],'Two concentric upper-body axes; naked moving region; bolted metal interfaces')
 return f,r

def add_trunk(A):
 joints={}
 for stem,size,zoff in [('waist','H6P4',-74),('chest','H6P3',-40)]:
  O=A.A0[stem+'.yaw']['origin'];normal=1 if stem=='waist' else -1;y=A.joint(stem+'.yaw',size,(0,0,normal),(1,0,0),zoff*normal,board_rotation=90)
  f,r=upper_pair(A,stem,size) if stem=='waist' else yx_pair(A,stem+'.pitch',stem+'.roll',-1,size);ro=SPECS[size]['ro'];rf=2*ro+4
  sh=A.plate(y,'rotor').moved(y['loc']).fuse(A.plate(f,'fixed').moved(f['loc']))
  sy=1 if stem=='waist' else -1;vertical=1 if stem=='waist' else -1
  zz=zoff-normal*11.55
  pts=[O+v for v in np.array([(-ro-4,0,zz),(-50,0,zz),(-50,sy*(rf+6),zz),(-50,sy*(rf+6),vertical*(ro+15)),(0,sy*(rf+6),vertical*(ro+15))])]
  sh=sh.fuse(rails(pts,3))
  A.add(stem+'_M_yaw_pitch_frame',sh,'aluminum_7075',y['rotor'],'Rigid yaw-to-pitch frame; yaw cartridge shifted only along the original vertical axis')
  joints[stem]=(y,f,r)
 # Connect waist output to chest input without moving either pivot.
 wy,wf,wr=joints['waist'];cy,cf,cr=joints['chest'];W=A.A0['waist.yaw']['origin'];C=A.A0['chest.yaw']['origin']
 sh=A.plate(wr,'rotor').moved(wr['loc']).fuse(A.plate(cy,'fixed').moved(cy['loc']))
 sh=sh.fuse(cube((7.5,8,4),(W[0]+31.75,0,C[2]-46)))
 for x,y,z in wr['meta']['rotor_mounts_mm']:sh=sh.cut(cyl(-22,-12.05,3.1).translate((x,y,0)).moved(wr['loc']))
 A.add('waist_M_chest_input_frame',sh,'aluminum_7075',wr['rotor'],'Continuous waist-to-chest member; posterior offset route between the compact waist and chest cartridges')
 return joints

def build(name,isolated=False):
 if isolated:A=Assembly(h.profile(name));meta={}
 else:A,meta=limbs.build(name)
 joints=add_trunk(A)
 return A,dict(meta,trunk_joints={s:[j['axis'] for j in js] for s,js in joints.items()},stage='trunk_integration')

def main():
 results={}
 for name in ['quinn'] if '--quick' in sys.argv else ['manny','quinn']:
  A,meta=build(name,isolated='--isolated' in sys.argv);affected={q['name'] for q in A.parts if q['name'].startswith(('waist_','chest_'))}
  cases={'neutral':{},'bend':{'waist.pitch':40,'chest.pitch':30},'extend':{'waist.pitch':-20,'chest.pitch':-20},'lean':{'waist.roll':25,'chest.roll':20},'twist':{'waist.yaw':35,'chest.yaw':35},'lean_other':{'waist.roll':-25,'chest.roll':-20},'opposed':{'waist.pitch':40,'chest.pitch':-20,'waist.roll':25,'chest.roll':-20},'reverse':{'waist.yaw':-35,'chest.yaw':-35,'waist.pitch':-20,'chest.pitch':30}}
  checks=[]
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral');checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hits=hits)),flush=True)
  results[name]=dict(meta=meta,checks=checks)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({}) if q['role']!='reservation'],folder/'trunk.png',name.title()+' | trunk integration work',camera=(1300,-2300,1000))
 h.save(ROOT/'verification/revM_trunk_work.json',results)
if __name__=='__main__':main()
