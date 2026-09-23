"""Mesh-section study for anthropomorphic packaging; not collision certification."""
from pathlib import Path
import sys,json,math
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE.parent/'revE'))
from character_reference import reference_character
SCALES=[1/3,1/2.5,1/2]

def cross2(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
def section(verts,faces,mask,z,centre):
 tri=verts[faces];near=(tri[:,:,2].min(axis=1)<z)&(tri[:,:,2].max(axis=1)>z)&mask;tri=tri[near];segs=[]
 for points in tri:
  hits=[]
  for i,j in ((0,1),(1,2),(2,0)):
   a,b=points[i],points[j]
   if (a[2]-z)*(b[2]-z)<0:hits.append(a[:2]+(b[:2]-a[:2])*((z-a[2])/(b[2]-a[2])))
  if len(hits)==2:segs.append(hits)
 if not segs:return None
 segs=np.array(segs);radii=[];counts=[]
 for angle in np.arange(0,360,5):
  d=np.array([math.cos(math.radians(angle)),math.sin(math.radians(angle))]);a=segs[:,0]-centre;edge=segs[:,1]-segs[:,0];den=cross2(d,edge);valid=np.abs(den)>1e-9
  t=cross2(a,edge)[valid]/den[valid];u=cross2(a,d)[valid]/den[valid];ts=t[(t>1e-8)&(u>=-1e-8)&(u<1-1e-8)]
  ts=np.unique(np.round(ts,6));counts.append(len(ts));radii.append(float(min(ts)) if len(ts) else None)
 flat=segs.reshape(-1,2);valid=all(x is not None for x in radii) and all(n%2==1 for n in counts)
 return {'z_mm_at_one_third':z,'centre_xy_mm_at_one_third':centre.tolist(),'depth_x_mm':float(np.ptp(flat[:,0])),'width_y_mm':float(np.ptp(flat[:,1])),'offset_bbox_centre_mm':((flat.max(axis=0)+flat.min(axis=0))/2-centre).tolist(),'radial_angles_deg':list(range(0,360,5)),'radial_distances_mm':radii,'ray_counts':counts,'centre_inside_all_ray_parities':valid,'minimum_central_radius_mm':min(x for x in radii if x is not None)}

def main():
 result={'status':'ANTHROPOMORPHIC_ENVELOPE_STUDY_NOT_MANUFACTURING_RELEASE','wall_mm':1.8,'internal_gap_mm':1.2,'baseline_scale':1/3,'candidates':SCALES,'characters':{}}
 for name in ('manny','quinn'):
  c=reference_character(name);verts=c['vertices_mm'];faces=np.array(c['geometry']['triangles']);dom=np.array([max(w,key=lambda p:p[1])[0] for w in c['geometry']['skin_weights']]);names=c['names'];parents=c['parents'];out={}
  def desc(prefix):
   ids=[];wanted=c['index'][prefix]
   for i in range(len(names)):
    j=i
    while j>=0:
     if j==wanted:ids.append(i);break
     j=parents[j]
   return ids
  groups=[('upperarm','upperarm_l','lowerarm_l','upperarm_l'),('forearm','lowerarm_l','hand_l','upperarm_l'),('thigh','thigh_l','calf_l','thigh_l'),('shin','calf_l','foot_l','thigh_l')]
  for label,prox,dist,root in groups:
   mask=np.any(np.isin(dom[faces],desc(root)),axis=1);a,b=c['points'][prox],c['points'][dist];rows=[]
   for f in (.03,.10,.25,.50,.75,.90,.97):
    point=a+(b-a)*f;s=section(verts,faces,mask,float(point[2]),point[:2]);rows.append({'fraction':f,**s})
   out[label]={'length_mm_at_one_third':float(np.linalg.norm(b-a)),'sections':rows}
  elbows=section(verts,faces,np.any(np.isin(dom[faces],desc('upperarm_l')),axis=1),float(c['points']['lowerarm_l'][2]+.001),c['points']['lowerarm_l'][:2])
  wrist=section(verts,faces,np.any(np.isin(dom[faces],desc('upperarm_l')),axis=1),float(c['points']['hand_l'][2]+.001),c['points']['hand_l'][:2])
  out['elbow_section']=elbows;out['wrist_section']=wrist
  heights=[{'scale':scale,'height_mm':c['height_mm']*scale/(1/3),'elbow_outer_width_mm':elbows['width_y_mm']*scale/(1/3),'elbow_outer_depth_mm':elbows['depth_x_mm']*scale/(1/3),'wrist_outer_width_mm':wrist['width_y_mm']*scale/(1/3),'wrist_outer_depth_mm':wrist['depth_x_mm']*scale/(1/3)} for scale in SCALES]
  out['scale_comparison']=heights;result['characters'][name]=out
  print(json.dumps({'name':name,'elbow':elbows,'wrist':wrist,'scales':heights},ensure_ascii=False),flush=True)
 (ROOT/'verification/revG_surface_envelopes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
