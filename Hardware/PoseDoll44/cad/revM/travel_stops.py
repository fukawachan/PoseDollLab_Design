"""Positive travel guards on load-bearing cartridge flanges; never on magnetic cups.
Work-in-progress geometry. Not enabled in final assembly until full checks pass.
"""
from head_shells import *
import head_shells as covers
from collision_review import classify_all

def sector(ri,ro,z0,z1,a,b):
 assert 0<b-a<360
 return cq.Workplane('XZ').polyline([(ri,z0),(ro,z0),(ro,z1),(ri,z1)]).close().revolve(b-a,(0,0),(0,1)).val().rotate((0,0,0),(0,0,1),a)

def add_guards(A):
 rows=[]
 limits={x['id']:np.degrees(x['limits_rad']) for x in A.profile['axes']}
 signs={c['axis_id']:c['geometric_sign'] for c in A.channels}
 for axis,j in A.joints.items():
  if j['size'] not in SPECS:continue
  lo,hi=sorted(limits[axis]*signs[axis]);radius=j['meta']['clutch_outer_radius_mm'];half=8.;span=16.
  def near_posts(p):return min(abs((p+180)%360-180),abs(p%360-180))
  phase=next((p for p in (90,45,135,0,180,225,270,315) if min(near_posts(p+lo-half-span/2),near_posts(p+hi+half+span/2))>25),90)
  fixed,fw=world_part(A,j['prefix']+'fixed_metal_eye');rotor,rw=world_part(A,j['prefix']+'flanged_rotor_shaft')
  tab=sector(radius-.6,radius+4,-3,0,phase-half,phase+half).fuse(sector(radius+1.35,radius+4,0,.8,phase-half,phase+half))
  stop_shapes=[]
  for a,b in ((phase+lo-half-span,phase+lo-half),(phase+hi+half,phase+hi+half+span)):
   stop_shapes.extend([sector(radius-.6,radius+5,1,4,a,b),sector(radius+1.3,radius+5,.05,1.1,a,b)])
  for sh in stop_shapes:fw=fuse_checked(fw,sh.moved(j['loc']),axis+'_fixed_guard')
  rw=fuse_checked(rw,tab.moved(j['loc']),axis+'_rotor_guard')
  replace_world(A,fixed,fw,fixed['note']+'; integral angular travel guards reacting directly into bearing eye','aluminum_7075')
  replace_world(A,rotor,rw,rotor['note']+'; integral load-bearing flange stop tab; magnetic cup is not a stop','aluminum_7075')
  rows.append(dict(axis=axis,limits_deg=limits[axis].tolist(),geometric_sign=signs[axis],phase_deg=phase,tab_half_width_deg=half,stop_span_deg=span,tab_outer_radius_mm=radius+4,fixed_outer_radius_mm=radius+5,physical_tested=False))
 return rows

def endpoint_check(A,guards):
 result=[]
 for g in guards:
  axis=g['axis'];j=A.joints[axis];fixed,_=world_part(A,j['prefix']+'fixed_metal_eye');rotor,_=world_part(A,j['prefix']+'flanged_rotor_shaft');lo,hi=g['limits_deg'];values=[]
  for theta in [lo-1,lo,(3*lo+hi)/4,(lo+hi)/2,(lo+3*hi)/4,hi,hi+1]:
   T,_=h.fk(A.profile,{axis:theta});a=h.move(fixed['local_shape'],T[fixed['owner']]);b=h.move(rotor['local_shape'],T[rotor['owner']]);v=a.intersect(b).Volume();outside=theta<lo or theta>hi
   assert v>.02 if outside else v<.005,(axis,theta,v,outside)
   values.append(dict(angle_deg=theta,volume_mm3=v,outside_allowed_range=outside))
  result.append(dict(axis=axis,checks=values))
 return result

def build(name):
 A,meta=covers.build(name);guards=add_guards(A);return A,dict(meta,compact_travel_guards=guards)

def main():
 out={}
 for name in (['manny'] if '--manny' in sys.argv else ['quinn'] if '--quick' in sys.argv else ('manny','quinn')):
  A,meta=build(name);meta['endpoint_checks']=endpoint_check(A,meta['compact_travel_guards']);print('positive guard endpoint checks passed '+name,flush=True);aff={j['prefix']+s for j in A.joints.values() if j['size'] in SPECS for s in ('fixed_metal_eye','flanged_rotor_shaft')};checks=[]
  cases={'neutral':{}}
  for g in meta['compact_travel_guards']:
   for k,angle in zip(('min','max'),g['limits_deg']):cases[g['axis']+'_'+k]={g['axis']:angle}
  if '--probe' in sys.argv:cases={k:v for k,v in cases.items() if k in ('neutral','forearm_l.twist_min','forearm_l.twist_max','hand_l.deviate_max','waist.pitch_max')}
  for label,pose in cases.items():
   hits=fast_contacts(A.scene(pose),A.thread_pairs,aff,label!='neutral');review=classify_all(hits,A.parts);bad=[q for q in review if q['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,hits=hits,review=review));print(json.dumps(dict(character=name,pose=label,structural=bad[:10],structural_count=len(bad),pose_restrictions=len(review)-len(bad))),flush=True)
  out[name]=dict(meta=meta,checks=checks);h.save(ROOT/('verification/revM_travel_guards_'+name+'_work.json'),out)
if __name__=='__main__':main()
