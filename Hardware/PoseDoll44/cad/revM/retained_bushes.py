"""Radial sleeve retention and installed fits. Free-state press fits are explicit.
No friction spring force is intentionally applied through a polymer sleeve.
"""
from toe_caps import *
import toe_caps as skin

def captured8(A,prefix,eye_name,loc):
 eye,ew=world_part(A,eye_name);bush,bw=world_part(A,prefix+'radial_bush')
 # Upper flange is enclosed by a housing shoulder and the separate thrust washer.
 pocket=cyl(3.15,4.10,7.25).moved(loc)
 replace_world(A,eye,ew.cut(pocket),eye['note']+'; D14.50 x0.85 upper retaining counterbore, flat Z3.15',eye['material'])
 b=ring(1.1,3.9,4,3.03).fuse(ring(3.2,3.9,7.2,3.03)).moved(loc)
 replace_world(A,bush,b,bush['note']+'; D14.40 x0.70 flange at Z3.20..3.90, captured below thrust washer Z4.00; 0.15 total nominal axial float','pom')
 return dict(bush=bush['name'],kind='captured_flange',nominal_axial_float_mm=.15,installed_OD_mm=8.,running_ID_mm=6.06,flange_OD_mm=14.4,flange_thickness_mm=.7,preload_path='metal eye -> thrust washer; flange has axial clearance')

def install_press_fit(A,bname,fname,axis):
 q,b=world_part(A,bname);f,w=world_part(A,fname);assert f['material'] in ('aluminum_7075','aluminum','metal','titanium'),(fname,f['material'],'press fit requires metal housing');bb=b.BoundingBox();mins=np.array([bb.xmin,bb.ymin,bb.zmin]);maxs=np.array([bb.xmax,bb.ymax,bb.zmax]);mid=(mins+maxs)/2;a=float(mins[axis]);z=float(maxs[axis]);ro=float((maxs-mins)[(axis+1)%3]/2);ri=3.02 if ro>3.5 else 2.02
 off=mid.copy();off[axis]=0
 # Installed-state bush equals the finished metal bore; free OD is larger.
 sleeve=h.tube(axis,a,z,ro+.16,ro,off)
 replace_world(A,f,fuse_checked(w,sleeve,'bearing_fit_'+bname),f['note']+'; reamed press-fit sleeve seat, see retained_bushes manifest',f['material'])
 b=h.tube(axis,a,z,ro,ri,off)
 replace_world(A,q,b,'Machined POM-C plain sleeve. CAD is installed/compressed state; free OD is +0.030 +/-0.005 mm above nominal, housing bore +0.000..+0.010. Finish running bore after installation. No clutch axial preload. Pull-out and thermal qualification required.','pom')
 return dict(bush=bname,housing=fname,kind='interference_fit_installed_state',nominal_OD_mm=2*ro,housing_bore_deviation_mm=[0,.010],free_bush_OD_deviation_mm=[.025,.035],free_diametral_interference_mm=[.015,.035],finished_running_ID_mm=2*ri,running_bore_tolerance_mm=[0,.02],axial_pullout_acceptance_N=10,physical_tested=False)

def apply(A):
 rows=[]
 for j in A.joints.values():
  if j['size'] in SPECS:rows.append(captured8(A,j['prefix'],j['prefix']+'fixed_metal_eye',j['loc']))
 for d in descriptors(A):
  if d['family']=='L6':
   prefix=d['fixed'].replace('reaction_plate','');rows.append(captured8(A,prefix,d['fixed'],d['loc']))
 for side,sy in [('l',1),('r',-1)]:
  S=A.A0['upperarm_'+side+'.twist']['origin'];loc=cq.Location(cq.Plane(origin=tuple(S),normal=(0,0,1),xDir=(sy,0,0)))
  q,b=world_part(A,side+'_twist_bush');f,w=world_part(A,side+'_abduct_ring_and_twist_seat')
  w=fuse_checked(w,ring(-8,5.5,3.16,3.02).moved(loc),'twist_bore_fit').cut(cyl(-9.01,-8,3.75).moved(loc))
  hub=world_part(A,side+'_abduct_drive_split_hub')[1]
  for delta in ([.2,0,0],[-.2,0,0],[0,.2,0],[0,-.2,0],[0,0,.2],[0,0,-.2]):w=w.cut(hub.translate(tuple(delta)))
  replace_world(A,f,w,f['note']+'; D6.04 nominal sleeve seat and captured D7.4 lower flange',f['material'])
  b=ring(-8,5,3,2.03).fuse(ring(-8.8,-8,3.7,2.03)).moved(loc)
  replace_world(A,q,b,'Flanged POM-C D6 sleeve, D4.06 running bore; D7.4 x0.8 flange trapped between lining top -9 and housing shoulder -8. Nominal axial float .2 mm.','pom')
  rows.append(dict(bush=q['name'],kind='captured_flange',installed_OD_mm=6.,running_ID_mm=4.06,flange_OD_mm=7.4,flange_thickness_mm=.8,nominal_axial_float_mm=.2))
  ringpart,_=world_part(A,side+'_flex_ring');ringpart['material']='aluminum_7075';ringpart['note']+='; 7075-T6 metal candidate required for reamed interference-fit radial bush seats; no PLA press-fit claim'
  for suf,frame,axis in [('yaw_bush_top','chest_M_body_frame',2),('yaw_bush_lower','chest_M_body_frame',2),('elev_bush_27',side+'_yaw_carriage',0),('elev_bush_43',side+'_yaw_carriage',0),('flex_bush_-36.5',side+'_clavicle_output_frame',1),('flex_bush_-27.5',side+'_clavicle_output_frame',1),('abduct_bush_-20.5',side+'_flex_ring',0),('abduct_bush_20.5',side+'_flex_ring',0)]:
   rows.append(install_press_fit(A,side+'_'+suf,frame,axis))
 return rows

def build(name):
 A,meta=skin.build(name);rows=apply(A);return A,dict(meta,retained_bushes=rows)

def main():
 out={}
 for name in ('manny','quinn'):
  A,meta=build(name);affected={r['bush'] for r in meta['retained_bushes']}|{r['housing'] for r in meta['retained_bushes'] if 'housing' in r}|{q['name'] for q in A.parts if q['name'].endswith(('fixed_metal_eye','reaction_plate','abduct_ring_and_twist_seat'))}
  cache=CollisionCache(A);cases={'neutral':{},**h.cases()};rows=[]
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,affected,label!='neutral'),A.parts);bad=[q for q in review if q['classification']=='structural'];rows.append(dict(pose=label,review=review));print(json.dumps(dict(character=name,pose=label,structural_count=len(bad),first=bad[:4])),flush=True)
  out[name]=dict(fits=meta['retained_bushes'],checks=rows);h.save(ROOT/'verification/revM_bush_retention_work.json',out)
if __name__=='__main__':main()
