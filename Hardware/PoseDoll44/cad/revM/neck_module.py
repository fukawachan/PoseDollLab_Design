"""Neck module: yaw cartridge below the equivalent neck pivot, rigid head above."""
from assembly_core import *
from mechanism_modules import yx_pair
from trunk_integration import rails

def add_neck(A):
 O=A.A0['head.yaw']['origin'];tip=A.T0['head_tip'][:3,3]
 y=A.joint('head.yaw','S6',(0,0,-1),(1,0,0),36)
 f,r=yx_pair(A,'head.pitch','head.roll',1,'S6')
 frame=A.plate(y,'rotor').moved(y['loc']).fuse(A.plate(f,'fixed').moved(f['loc']))
 pts=[O+v for v in np.array([(-15,0,-24.45),(-40,0,-24.45),(-40,32,-24.45),(-40,32,-26),(0,32,-26)])]
 frame=frame.fuse(rails(pts,3))
 A.add('head_M_yaw_pitch_frame',frame,'frame',y['rotor'],'Yaw below the neck pivot; all offsets lie on existing axis lines')
 frame=A.plate(r,'rotor').moved(r['loc'])
 pts=[O+[1.5,0,-15],O+[1.5,0,10],O+[1.5,-24,10],O+[1.5,-24,48],O+[1.5,0,58],tip+[0,0,-20]]
 frame=frame.fuse(rails(pts,3))
 A.add('head_M_skull_frame',frame,'frame','head','Centre skull rail returns above the open neck; shell attachment pending')
 return y,f,r

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A=Assembly(h.profile(name));add_neck(A);checks=[]
  cases={'neutral':{},'turn':{'head.yaw':75},'nod':{'head.pitch':55},'look_up':{'head.pitch':-45},'tilt_l':{'head.roll':35},'tilt_r':{'head.roll':-35},'up_tilt':{'head.pitch':-45,'head.roll':35},'down_tilt':{'head.pitch':55,'head.roll':-35},'combo':{'head.yaw':-75,'head.pitch':55,'head.roll':35}}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,None,label!='neutral');checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,hits=hits)),flush=True)
  out[name]=checks
 h.save(ROOT/'verification/revM_neck_work.json',out)
if __name__=='__main__':main()
