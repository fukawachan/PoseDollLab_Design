from shoulder_revision import *
from build_and_verify import poses_all
import importlib.util
spec=importlib.util.spec_from_file_location('revh_labels',h.HERE/'build_review.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
LABELS=dict(old.LABELS)
for key in poses_all():
 if key.startswith('scan_'):
  _,axis,deg=key.split('_')
  LABELS[key]={'flex':'肩部屈伸','abduct':'肩部外展','twist':'上臂扭转'}[axis]+' '+deg+'°（单轴取样）'
def main():
 data={'labels':LABELS,'models':{}};counts={}
 for name in ('manny','quinn'):
  p,parts,meta=build(name);record=json.loads((ROOT/f'verification/revJ_{name}.json').read_text('utf8'))
  mesh=[];verified={q['name']:q for q in record['parts']}
  assert record['meta']['preload_nominal_force_N']==meta['preload_nominal_force_N']
  for item in parts:
   assert abs(item['local_shape'].Volume()-verified[item['name']]['volume_mm3'])<1e-5,item['name']
   vertices,tris=item['local_shape'].tessellate(.6,.45)
   mesh.append({k:v for k,v in item.items() if k!='local_shape'}|
    {'color':COL[item['material']],'vertices':[[round(c,4) for c in v.toTuple()] for v in vertices],'triangles':[list(t) for t in tris]})
  poses={};owners={q['owner'] for q in parts}
  for check in record['motion_checks']:
   T,A=h.fk(p,check['angles_deg'])
   poses[check['pose']]={'transforms':{owner:T[owner].round(9).tolist() for owner in owners},'hits':check['hits'],'angles':check['angles_deg']}
  assert set(poses)==set(LABELS)
  data['models'][name]=dict(parts=mesh,poses=poses,meta=meta,pass_count=sum(not q['hits'] for q in record['motion_checks']),
   local_clear_count=sum(q['structural_hits']==0 for q in record['motion_checks']))
  counts[name]=dict(parts=len(mesh),triangles=sum(len(q['triangles']) for q in mesh),poses=len(poses),
   collision_free_samples=data['models'][name]['pass_count'],local_clear_samples=data['models'][name]['local_clear_count'])
  items,_,_=h.scene(parts,p,{})
  detail=[q for q in items if q['name'].startswith('l_') and '_arm_' not in q['name'] and q['role']!='reservation' and not any(v in q['name'] for v in ('_yaw_','_elev_'))]
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in detail],OUT/name/'shoulder_detail.png',
   name.title()+' | Rev J actual CAD | left shoulder',camera=(1000,-1500,600))
  items,_,_=h.scene(parts,p,h.cases()['crossed_clearance_candidate'])
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in items if q['role']!='reservation'],OUT/name/'crossed_clearance_candidate.png',
   name.title()+' | Rev J staggered arm pose | sampled clearance',camera=(1800,-600,200))
 (OUT/'RevJ_Shoulder_Review.html').write_text((HERE/'review.template.html').read_text('utf8').replace('__DATA__',json.dumps(data,separators=(',',':'))),encoding='utf8')
 h.save(ROOT/'verification/revJ_viewer_geometry.json',counts)
 print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
