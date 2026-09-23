"""Rev M arm continuation: real direct encoder elbows and forearm rotation.
Still a work in progress until integration and full body checks close.
"""
from assembly_core import *

def build(name):
 p,old,oldmeta=previous.build(name)
 # Only replace the original Rev G arm group; retain the K shaft's radial retainer.
 kept=[q for q in old if not q['name'].startswith(('l_arm_','r_arm_')) or '_shell_' in q['name']]
 A=Assembly(p,kept);new=[];removed=[q['name'] for q in old if q not in kept]
 for side,sy in [('l',1),('r',-1)]:
  e=A.joint(f'elbow_{side}.flex','M6',(0,sy,0),(0,0,1),5.525)
  f=A.joint(f'forearm_{side}.twist','S6',(0,0,1),(-1,0,0),0)
  E=A.A0[e['axis']]['origin'];F=A.A0[f['axis']]['origin'];S=A.A0[f'upperarm_{side}.flex']['origin'];W=A.A0[f'hand_{side}.flex']['origin']
  # Upper arm remains a centreline beam outside the exposed elbow region.
  ep=A.plate(e,'fixed');xp=e['meta']['fixed_mounts_mm'][0][0]
  U=float(S[2]-E[2]);ep=ep.fuse(cube((16,12,18),(xp+12,0,-1)))
  ep=ep.fuse(cube((U-25-xp-6,12,10),((U-25+xp+6)/2,0,-5.525)))
  ep=ep.cut(cube((max(1,U-25-xp-10),8,6),((U-25+xp+10)/2,0,-5.525)))
  coupling=next(q for q in old if q['name']==side+'_arm_coupling')
  ep_world=ep.moved(e['loc']).fuse(h.move(coupling['local_shape'],A.T0[coupling['owner']]))
  A.add(e['prefix']+'upperarm_carrier',ep_world,'frame',e['fixed'],'One printed carrier includes the existing Rev K keyed shoulder coupling and its radial retainer interface')
  # Proximal forearm has a short central section, then forks around the encoder.
  er=A.plate(e,'rotor');rx=e['meta']['rotor_mounts_mm'][0][0]
  # Radius 3 on the two far mounting-pad corners clears deep elbow flexion.
  for sg in (-1,1):
   corner=cube((3,3,6),(rx-6.5,sg*8.5,-10.05)).cut(cyl(-13.1,-7.9,3).translate((rx-5,sg*7,0)))
   er=er.cut(corner)
  er=er.fuse(cube((11,12,10),(rx-11,0,-7.05)))
  er=er.fuse(cube((12,12,10),(rx-16,0,-5.525)))
  fw=A.plate(f,'fixed').moved(f['loc']);ew=er.moved(e['loc'])
  # Branches stay clear of the 12 x 10 PCB; any violations are checked, not masked.
  for y in (-6,6):
   a=F+np.array([-25,y,6]);b=F+np.array([-30,y,6]);c=F+np.array([-30,y,30]);d=E+np.array([0,0,-32])
   fw=fw.fuse(h.rod(a,b,3)).fuse(h.rod(b,c,3)).fuse(h.rod(c,d,3))
  proximal=ew.fuse(fw)
  A.add(e['prefix']+'proximal_forearm',proximal,'frame',e['rotor'],'Direct elbow and axial forearm rotation share a single printed proximal carrier')
  fr=A.plate(f,'rotor');rx=f['meta']['rotor_mounts_mm'][0][0]
  fr=fr.fuse(cube((abs(rx)+6,12,8),(rx/2,0,-15.5))).fuse(cube((12,10,22),(0,0,-25)))
  for _,y,_ in f['meta']['rotor_mounts_mm']:
   fr=fr.cut(cyl(-30,-8,3).translate((rx,y,0)))
  A.add_local(f,'rotor','distal_forearm_carrier',fr)
  # Move only the distal half of the old forearm shell with pronation.
  for sh in list(A.parts):
   if not sh['name'].startswith(side+'_arm_forearm_shell_'):continue
   A.parts.remove(sh);world=h.move(sh['local_shape'],A.T0[sh['owner']])
   z=F[2]
   prox=world.intersect(cube((200,200,200),(E[0],E[1],z+100.5)))
   dist=world.intersect(cube((200,200,200),(E[0],E[1],z-124)))
   # Proximal shell leaves disconnected fins after two joint reliefs; keep this short motion zone exposed.
   for suffix,shape,owner in [('distal',dist,f['rotor'])]:
    if len(shape.Solids()):A.add(sh['name']+'_'+suffix,shape,'shell',owner,'Split at forearm twist station; attachment and swept clearance still under evaluation')
 # Rounded clearance openings for the elbow mounting screw heads.
  for sh in A.parts:
   if sh['name'].startswith(side+'_arm_upperarm_shell_'):
    world=h.move(sh['local_shape'],A.T0[sh['owner']]).cut(cyl(-80,80,42).moved(e['loc']))
    for xx,yy,_ in e['meta']['fixed_mounts_mm']:
     world=world.cut(cyl(8,35,3.2).translate((xx,yy,0)).moved(e['loc']))
    sh['local_shape']=world.translate(tuple(-A.T0[sh['owner']][:3,3]))
 return A,dict(character=name,revision='M-work',inherited_revision='L',removed=removed,channels=A.channels,stage='elbow_forearm_integration')

def main():
 result={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);oldnames={q['name'] for q in previous.build(name)[1]};affected={q['name'] for q in A.parts if q['name'] not in oldnames}
  cases={'neutral':{},'elbow90':{'elbow_l.flex':90,'elbow_r.flex':90},'elbow145':{'elbow_l.flex':145,'elbow_r.flex':145},'pronate':{'elbow_l.flex':90,'forearm_l.twist':90},'supinate':{'elbow_l.flex':90,'forearm_l.twist':-90}}
  rows=[]
  for label,pose in cases.items():
   scene=A.scene(pose);hits=fast_contacts(scene,A.thread_pairs,affected,skip_same_owner=label!='neutral')
   rows.append(dict(pose=label,hits=hits));print(json.dumps(dict(name=name,pose=label,hits=hits)),flush=True)
  result[name]=dict(meta=meta,checks=rows)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  assy=cq.Assembly(name=name+'_RevM_arm_integration')
  for q in A.scene({}):assy.add(q['shape'],name=q['name'],color=cq.Color(*COL[q['material']]))
  assy.save(str(folder/(name+'_arm_integration.step')))
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({}) if q['role']!='reservation'],folder/'arm_integration.png',name.title()+' | direct elbow and forearm twist | integration in progress',camera=(1000,-1500,600))
 h.save(ROOT/'verification/revM_arm_work.json',result)
if __name__=='__main__':main()
