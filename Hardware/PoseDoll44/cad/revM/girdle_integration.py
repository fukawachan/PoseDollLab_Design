"""Four measured shoulder-girdle axes with retained shafts and preload cartridges.
Digital integration candidate; actual assembly, load and field qualification pending.
"""
from twist_completion import *
import twist_completion as shoulder
from girdle_cartridge import module4
from cad_cache import get_body

def world_part(A,name):
 q=next(q for q in A.parts if q['name']==name)
 return q,h.move(q['local_shape'],A.T0[q['owner']])

def replace_world(A,q,s,note,material='aluminum_7075'):
 if not s.isValid() or len(s.Solids())!=1:
  print('BAD CONNECTION',q['name'],s.isValid(),[(x.Volume(),x.Center().toTuple(),(x.BoundingBox().xlen,x.BoundingBox().ylen,x.BoundingBox().zlen)) for x in s.Solids()],flush=True)
  assert False,(q['name'],len(s.Solids()))
 q.update(local_shape=s.translate(tuple(-A.T0[q['owner']][:3,3])),material=material,note=note)

def cartridge(A,axis,origin,normal,xdir,end,clip_sign,middle_key=None):
 node=next(n for n in A.profile['nodes'] if n.get('axis_id')==axis)
 fixed=node['parent'];rotor=node['id'];loc=cq.Location(cq.Plane(origin=tuple(origin),xDir=xdir,normal=normal));prefix=axis.replace('.','_')+'_G4_'
 parts,meta=module4(end,clip_sign,middle_key)
 for q in parts:A.add(prefix+q['name'],q['shape'].moved(loc),q['material'],fixed if q['owner']=='fixed' else rotor,q['note'],q['role'])
 A.thread_pairs.extend([[prefix+n for n in pair] for pair in meta['intended_thread_pairs']])
 # Direct encoder is on the negative shaft end; report that outward normal explicitly.
 sn=-np.array(normal);ax=A.A0[axis];g=float(np.dot(ax['direction'],sn))
 A.channels.append(dict(axis_id=axis,kind='AS5048A_direct',fixed_owner=fixed,magnet_owner=rotor,origin_neutral_mm=list(origin),normal_neutral=sn.tolist(),xdir_neutral=list(xdir),geometric_sign=g,magnet_face_mm=18.3,package_face_mm=19.8,gap_mm=1.5,family='G4P2',calibrated=False))
 # Numerically integrate mean contact radius of the clipped annulus, not the full disc.
 xy=np.arange(-12,12.0001,.08);xx,yy=np.meshgrid(xy,xy);rr=np.sqrt(xx*xx+yy*yy);inside=(rr>=2.05)&(rr<=12)
 if clip_sign is not None:inside &= yy*clip_sign>=-5.5
 reff=float(rr[inside].mean());meta.update(nominal_torque_Nm=.15*1114*reff/1000,clutch_force_nominal_N=1114,contact_mean_radius_mm=reff)
 j=dict(axis=axis,prefix=prefix,origin=origin,loc=loc,rotor=rotor,fixed=fixed,size='G4P2',meta=meta)
 A.joints[axis]=j;return j

def pads(A,j,sy=1):
 pieces=[]
 for i,x in enumerate((-6,6)):
  sh=cube((8,10,4),(x,sy*9,-4.05)).cut(cyl(-7,-1,7)).cut(cyl(-6.2,-1.9,1.7).translate((x,sy*9,0)));pieces.append(sh)
  bolt=cyl(-6.05,-.05,1.5).fuse(cyl(-9.05,-6.05,2.75)).cut(hexagon(2.5,-9.15,-7.55))
  n=j['prefix']+'fixed_mount_M3x6_'+str(i);A.add(n,bolt.translate((x,sy*9,0)).moved(j['loc']),'metal',j['fixed'],'M3x6 into metal cartridge plate; nominal 1.95 mm engagement, spring preload closed inside cartridge')
  A.thread_pairs.append([n,j['prefix']+'fixed_reaction_plate'])
 return pieces

def revised_chest(A,left_c=-35,right_c=-76,neck_support=True):
 roots={side:A.A0[f'clavicle_{side}.protract']['origin'] for side in ('l','r')};mid=(roots['l']+roots['r'])/2
 fixed=[cube((14,float(abs(roots['l'][1]-roots['r'][1])+10),10),(0,0,-13))]
 fixed += [h.rod((-28,y,-110),(-28,y,-27),3.5) for y in (-10,10)]
 fixed += [h.rod((-6,y,-13),(-28,y,-27),3.5) for y in (-6,6)]
 fixed += [h.rod((-28,-10,-100),(-28,10,-100),3.5)]
 for side,sy,c in [('l',1,left_c),('r',-1,right_c)]:
  off=roots[side]-mid;fixed.append(h.tube(2,c+8,c+16,4.8 if side=='l' else 5.5,3.15,off));fixed.append(h.rod(off+[-4.2 if side=='l' else -5,0,c+(14 if side=='l' else 12)],[-28,sy*10,c+(14 if side=='l' else 12)],3.5))
 base=union_checked(fixed,'girdle_bearing_frame')
 for R in roots.values():base=base.cut(h.axis_cyl(2,-100,0,3.15,R-mid))
 base=base.translate(tuple(mid));C=A.A0['chest.yaw']['origin'];N=A.A0['head.yaw']['origin'];dry=Assembly(A.profile)
 ny=dict(A.joints['head.yaw']);ny['loc']=cq.Location(cq.Vector(*N),cq.Vector(0,0,1),180)*cq.Location(cq.Vector(*(-N)))*ny['loc']
 pieces=[base,dry.plate(A.joints['chest.roll'],'rotor').moved(A.joints['chest.roll']['loc']),rails([C+[7,0,-20],C+[7,0,0],C+[-57,0,0],C+[-57,0,35]],3)]
 for sy in (-1,1):pieces.append(rails([C+[-57,0,35],C+[-57,sy*10,35]],3.5))
 if neck_support:pieces += [dry.plate(ny,'fixed').moved(ny['loc']),rails([C+[-57,10,32],C+[-65,10,32],[C[0]-65,30,N[2]-46],[C[0]-65,-12.5,N[2]-46],N+[-27,-12.5,-46],N+[-27,-12.5,-42],N+[-27,0,-42]],3)]
 return union_checked(pieces,'revised_chest')

def apply_girdle(A,neck_support=True):
 chest,_=world_part(A,'chest_M_body_frame');replace_world(A,chest,revised_chest(A,neck_support=neck_support),'Metal chest frame, left lower yaw bearing raised 10 mm to clear the opposite bearing from the encoder')
 q,sh=world_part(A,'l_yaw_bush_lower');replace_world(A,q,sh.translate((0,0,10)),'Left lower yaw radial bushing, shifted with cartridge; same axis line','bush')
 for side,sy in [('l',1),('r',-1)]:
  R=A.A0[f'clavicle_{side}.protract']['origin'];c=-35 if sy==1 else -76
  oldnames={side+'_'+lab+'_'+tail for lab in ('yaw','elev') for tail in ('shaft','fixed_face','friction','rotor_face','preload_space','magnet_space','pcb_space','chip_space')}
  A.parts=[q for q in A.parts if q['name'] not in oldnames]
  j=cartridge(A,f'clavicle_{side}.protract',R+[0,0,c],(0,0,1),(1,0,0),-3-c,sy)
  q,carrier=world_part(A,side+'_yaw_carriage')
  carrier=carrier.fuse(cyl(-7,-3,2.1).translate(tuple(R))).cut(dshape(-7.1,-2.9,2.05,1.55).translate(tuple(R)))
  # Shoulder elevation is carried by the same retained yaw carriage.
  elev=cartridge(A,f'clavicle_{side}.elevate',R+[sy*58,0,0],(-sy,0,0),(0,0,1),38,None,(21,27))
  addpieces=pads(A,elev)
  for x in (-6,6):
   addpieces.append(rails([[x,16,-4.05],[x,16,15],[math.copysign(8,x),0,15]],3.5))
  carrier=carrier.fuse(h.union(addpieces).moved(elev['loc']))
  carrier=carrier.cut(cyl(-3,-2.5,4.2).translate(tuple(R))).cut(cyl(-2.5,.5,2.2).translate(tuple(R)))
  plate=next(x for x in A.parts if x['name']==elev['prefix']+'fixed_reaction_plate');carrier=carrier.cut(h.move(plate['local_shape'],A.T0[plate['owner']]))
  replace_world(A,q,carrier,'Machined yaw carriage, keyed D4 end and two original elevation bearings; bolt-on G4 reaction plate support')
  washer=ring(-3,-2.7,4,1.1).translate(tuple(R));A.add(j['prefix']+'carriage_retention_washer',washer,'brass',j['rotor'],'0.30 mm metal end washer; retains carriage, not spring preload')
  bolt=screw(-2.7,4,2,2,1.9,1.5).translate(tuple(R));bn=j['prefix']+'carriage_M2x4';A.add(bn,bolt,'brass',j['rotor'],'M2x4 into shaft end; nominal 3.7 mm engagement; accessible from above before adjacent carriage')
  A.thread_pairs.append([bn,j['prefix']+'stepped_D4_shaft'])
  # Fixed yaw mounts join the common chest frame outside both rotation shafts.
  addpieces=[p.moved(j['loc']) for p in pads(A,j,sy)]
  for x in (-6,6):addpieces.append(rails([R+[x,sy*16,c-4.05],[R[0]-28,sy*10,R[2]+c-4.05]],3.5))
  chest,cs=world_part(A,'chest_M_body_frame');replace_world(A,chest,fuse_checked(cs,h.union(addpieces),'girdle_chest_support'),'Continuous metal chest frame with bolted four-axis girdle and neck supports; machining split pending')
  # Positive elevation drive at the mid-shaft hub, separately retained radially.
  q,link=world_part(A,side+'_clavicle_output_frame')
  hub=cyl(21,27,2.1).moved(elev['loc']);key=dshape(20.9,27.1,2.05,1.55).moved(elev['loc'])
  link=link.fuse(hub).cut(key).cut(h.axis_cyl(0,0,6.6,1.1,(0,0,24)).moved(elev['loc']))
  link=link.cut(cyl(19,21,2.05).moved(elev['loc'])).cut(cyl(27,29,2.05).moved(elev['loc']))
  replace_world(A,q,link,'Machined clavicle link, D4 middle key transfers elevation torque, M2 radial retainer; original shoulder centre preserved')
  bn=elev['prefix']+'hub_M2x6';bolt=h.axis_cyl(0,.5,6.5,1,(0,0,24));A.add(bn,bolt.moved(elev['loc']),'brass',elev['rotor'],'Slotted M2x6 from top of hub into shaft, nominal 1.5 mm engagement')
  A.thread_pairs.append([bn,elev['prefix']+'stepped_D4_shaft'])
 for j in [j for k,j in A.joints.items() if k.startswith('clavicle_') and k.endswith('.protract')]:
  chest,cs=world_part(A,'chest_M_body_frame');plate=next(x for x in A.parts if x['name']==j['prefix']+'fixed_reaction_plate');cs=cs.cut(h.move(plate['local_shape'],A.T0[plate['owner']]))
  sy=1 if '_l.' in j['axis'] else -1
  for xx in (-6,6):cs=cs.cut(cyl(-9.3,-6.05,3.05).translate((xx,sy*9,0)).moved(j['loc'])).cut(cyl(-6.05,2,1.7).translate((xx,sy*9,0)).moved(j['loc']))
  replace_world(A,chest,cs,chest['note'])
 return A

def build(name,neck_support=True):
 A,meta=get_body(name,shoulder.build);apply_girdle(A,neck_support);return A,dict(meta,shoulder_girdle='four_direct_encoders_preloaded',measured_encoder_installations=41)

def main():
 out={}
 for name in ['quinn'] if '--quick' in sys.argv else ('manny','quinn'):
  A,meta=build(name);affected={q['name'] for q in A.parts if '_G4_' in q['name'] or q['name'] in ('chest_M_body_frame','l_yaw_carriage','r_yaw_carriage','l_clavicle_output_frame','r_clavicle_output_frame')};checks=[]
  cases={k:v for k,v in h.cases().items() if k in ('neutral','forward','backward','shrug','down','forward_up','back_down','asymmetric','arms_overhead','forward_shrug_reach')}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,affected,label!='neutral');checks.append(dict(pose=label,angles_deg=pose,hits=hits));print(json.dumps(dict(character=name,pose=label,count=len(hits),hits=hits[:18])),flush=True)
  out[name]=dict(meta=meta,checks=checks,channels=A.channels)
  folder=ROOT/'generated/revM'/name;folder.mkdir(parents=True,exist_ok=True)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],folder/'girdle_integration.png',name.title()+' | all 41 encoders installed | verification in progress',camera=(1300,-2000,1100))
 h.save(ROOT/'verification/revM_girdle_work.json',out)
if __name__=='__main__':main()
