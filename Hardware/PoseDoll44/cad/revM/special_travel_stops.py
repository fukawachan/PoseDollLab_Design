"""Load-side angular guards for girdle, neck and axial shoulder joints."""
from travel_stops import *
import travel_stops as compact

def descriptors(A):
 chs={c['axis_id']:c for c in A.channels};out=[]
 for axis,j in A.joints.items():
  if j['size']=='G4P2':out.append(dict(axis=axis,loc=j['loc'],fixed=j['prefix']+'fixed_reaction_plate',rotor=j['prefix']+'D4_friction_rotor',family='G4',sign=-chs[axis]['geometric_sign']))
  elif j['size']=='T4_light':
   fixed={'head.yaw':'chest_M_body_frame','head.pitch':'head_T4_yaw_pitch_frame','head.roll':'head_T4_pitch_roll_frame'}[axis]
   out.append(dict(axis=axis,loc=j['loc'],fixed=fixed,rotor=j['prefix']+'rotor_face',family='T4',sign=chs[axis]['geometric_sign']))
 for side,sy in [('l',1),('r',-1)]:
  axis=f'upperarm_{side}.twist';O=A.A0[axis]['origin'];loc=cq.Location(cq.Plane(origin=tuple(O),normal=(0,0,1),xDir=(sy,0,0)))
  out.append(dict(axis=axis,loc=loc,fixed=side+'_abduct_ring_and_twist_seat',rotor=side+'_twist_rotor_face',family='T4',support_ri=8.5,sign=float(np.dot(A.A0[axis]['direction'],[0,0,1]))))
 for side,sy in [('l',1),('r',-1)]:
  for lab,normal,xd,off in [('flex',(0,-sy,0),(1,0,0),43),('abduct',(1,0,0),(0,0,1),26)]:
   axis=f'upperarm_{side}.{lab}';O=A.A0[axis]['origin']+np.array(normal)*off
   out.append(dict(axis=axis,loc=cq.Location(cq.Plane(origin=tuple(O),normal=normal,xDir=xd)),fixed=side+'_'+lab+'_clutch_reaction_plate',rotor=side+'_'+lab+'_clutch_flanged_shaft',lining=side+'_'+lab+'_clutch_keyed_lining',family='L6',sign=float(np.dot(A.A0[axis]['direction'],normal))))
 return out

def geometry(d,lo,hi,phase):
 half=8;span=16;fixed=[]
 if d['family']=='G4':
  tab=sector(11.5,17,2,4.5,phase-half,phase+half)
  for a,b in ((phase+lo-half-span,phase+lo-half),(phase+hi+half,phase+hi+half+span)):fixed.append(sector(13.6,18,.1,5.5,a,b))
 elif d['family']=='L6':
  tab=sector(4.5,6.5,-.2,.85,phase-half,phase+half)
  for a,b in ((phase+lo-half-span,phase+lo-half),(phase+hi+half,phase+hi+half+span)):
   fixed.append(sector(4.5,6.5,.05,1.1,a,b))
 else:
  tab=sector(8.5,12,-12,-10,phase-half,phase+half).fuse(sector(10.35,12,-10,-9.2,phase-half,phase+half))
  for a,b in ((phase+lo-half-span,phase+lo-half),(phase+hi+half,phase+hi+half+span)):
   fixed.extend([sector(d.get('support_ri',9.5),13,-9,-6,a,b),sector(10.3,13,-9.95,-8.8,a,b)])
 return tab,[s for s in fixed]

def apply_one(A,d,phase):
 lim=next(q['limits_rad'] for q in A.profile['axes'] if q['id']==d['axis']);limits=np.degrees(lim);lo,hi=sorted(limits*d['sign']);tab,stops=geometry(d,lo,hi,phase)
 fixed,fw=world_part(A,d['fixed']);rotor,rw=world_part(A,d['rotor']);newf=fw
 if d['family']=='L6':
  liner,lw=world_part(A,d['lining']);replace_world(A,liner,lw.cut(cyl(-.1,1.1,6.8).moved(d['loc'])),liner['note']+'; inner radius 6.8 mm leaves a 0.3 mm radial clearance to protected inner travel tabs','lining')
 for sh in stops:newf=fuse_checked(newf,sh.moved(d['loc']),d['axis']+'_stop')
 newr=fuse_checked(rw,tab.moved(d['loc']),d['axis']+'_tab')
 if len(newf.Solids())!=1 or len(newr.Solids())!=1:raise ValueError('disconnected guard')
 replace_world(A,fixed,newf,fixed['note']+'; integral positive travel stops','aluminum_7075');replace_world(A,rotor,newr,rotor['note']+'; integral travel tab reacts directly into bearing frame','aluminum_7075')
 return dict(axis=d['axis'],fixed=d['fixed'],rotor=d['rotor'],family=d['family'],sign=d['sign'],phase_deg=phase,limits_deg=limits.tolist(),physical_tested=False),[(fixed,fw),(rotor,rw)]

def endpoint(A,g):
 fq,_=world_part(A,g['fixed']);rq,_=world_part(A,g['rotor']);lo,hi=g['limits_deg'];out=[]
 for v in (lo-1,lo,(lo+hi)/2,hi,hi+1):
  T,_=h.fk(A.profile,{g['axis']:v});vol=h.move(fq['local_shape'],T[fq['owner']]).intersect(h.move(rq['local_shape'],T[rq['owner']])).Volume();outside=v<lo or v>hi
  assert vol>.02 if outside else vol<.005,(g['axis'],v,vol)
  out.append(dict(angle_deg=v,volume_mm3=vol,outside=outside))
 return out

def search(name):
 A,meta=compact.build(name);rows=[]
 for d in descriptors(A):
  if '--girdle' in sys.argv and d['family']!='G4':continue
  if '--rest' in sys.argv and d['family']!='L6' and not d['axis'].endswith('.protract'):continue
  chosen=None;trials=[]
  # Build each phase independently; then combine the successful guards.
  original=[(q,dict(q)) for q in A.parts if q['name'] in (d['fixed'],d['rotor'],d.get('lining'))]
  for phase in (90,270,0,180,45,135,225,315,30,60,120,150,210,240,300,330):
   for q,old in original:q.update(old)
   try:
    g,old=apply_one(A,d,phase);ep=endpoint(A,g);hits=[]
    cases=[{d['axis']:float(v)} for v in np.linspace(*g['limits_deg'],9)]+[{}]+list(h.cases().values())
    for pose in cases:
     raw=fast_contacts(A.scene(pose),A.thread_pairs,{d['fixed'],d['rotor']},bool(pose))
     hits.extend(q for q in classify_all(raw,A.parts) if q['classification']=='structural')
    trials.append(dict(phase=phase,structural=len(hits),first=hits[:5]))
    print(json.dumps(dict(character=name,axis=d['axis'],phase=phase,structural=len(hits),first=hits[:3])),flush=True)
    if not hits:chosen=dict(g,endpoint_checks=ep);break
   except (AssertionError,ValueError) as e:
    trials.append(dict(phase=phase,error=str(e)));print(d['axis'],phase,str(e),flush=True)
  if chosen is None:
   for q,old in original:q.update(old)
  rows.append(dict(axis=d['axis'],selected=chosen,trials=trials));h.save(ROOT/f'verification/revM_special_guards_search_{name}.json',rows)
 return A,dict(meta,special_guard_search=rows)

PHASES={'clavicle_l.protract':45,'clavicle_l.elevate':270,'clavicle_r.protract':270,'clavicle_r.elevate':270,'head.yaw':45,'head.pitch':90,'head.roll':90,'upperarm_l.twist':45,'upperarm_r.twist':45,'upperarm_l.flex':90,'upperarm_l.abduct':90,'upperarm_r.flex':90,'upperarm_r.abduct':90}

def build(name):
 A,meta=compact.build(name);rows=[]
 for d in descriptors(A):
  g,_=apply_one(A,d,PHASES[d['axis']]);rows.append(g)
  if d['family']=='L6':
   fq,_=world_part(A,d['fixed']);rq,_=world_part(A,d['rotor']);reff=2/3*(12.5**3-6.8**3)/(12.5**2-6.8**2)
   A.joints[d['axis']]=dict(axis=d['axis'],fixed=fq['owner'],rotor=rq['owner'],size='L6_inner_stop',loc=d['loc'],meta=dict(clutch_force_nominal_N=552,nominal_torque_Nm=.15*552*reff/1000,friction_inner_radius_mm=6.8,friction_outer_radius_mm=12.5,physical_tested=False))
 assert len(rows)==13 and len(meta['compact_travel_guards'])==28
 return A,dict(meta,special_travel_guards=rows)

if __name__=='__main__':search('manny' if '--manny' in sys.argv else 'quinn')
