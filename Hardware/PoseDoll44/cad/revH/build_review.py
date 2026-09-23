"""Offline viewer and renderings from the exact same Rev H CAD."""
from shoulder_mechanism import *
LABELS={'neutral':'自然姿态','forward':'双肩前伸','backward':'双肩后收','shrug':'耸肩','down':'下压肩膀（原始组合）','forward_up':'前伸加耸肩','back_down':'后收下压（原始组合）','asymmetric':'左右肩不对称','arms_forward':'双臂前举','arms_overhead':'双臂上举','arms_side':'双臂侧举','hands_on_hips':'叉腰参考','arms_crossed':'原始对称抱臂（双臂需避让）','forehead':'扶额参考','forward_shrug_reach':'前伸耸肩加前举（原始组合）','elbows_closed':'弯肘 145°','down_arms_vertical':'下压肩膀、保持双臂竖直','back_down_arms_clear':'后收下压、双臂让位','shrug_reach_parallel':'前伸耸肩、双臂平行前伸','crossed_staggered':'抱臂错开试算 A（双臂需避让）','crossed_clearance_candidate':'错开抱臂可达候选'}
def main():
 data={'labels':LABELS,'models':{}};counts={}
 for name in ('manny','quinn'):
  p,parts,meta=build(name);record=json.loads((ROOT/f'verification/revH_{name}.json').read_text('utf8'))
  mesh=[]
  for item in parts:
   vertices,tris=item['local_shape'].tessellate(.6,.45)
   mesh.append({k:v for k,v in item.items() if k!='local_shape'}|{'color':COL[item['material']],'vertices':[[round(c,4) for c in v.toTuple()] for v in vertices],'triangles':[list(t) for t in tris]})
  poses={}
  owners={x['owner'] for x in parts}
  for check in record['motion_checks']:
   T,A=fk(p,check['angles_deg'])
   poses[check['pose']]={'transforms':{owner:T[owner].round(9).tolist() for owner in owners},'hits':check['hits'],'angles':check['angles_deg']}
  assert set(poses)==set(LABELS)
  passed=sum(not x['hits'] for x in record['motion_checks'])
  data['models'][name]={'parts':mesh,'poses':poses,'meta':meta,'pass_count':passed,'local_clear_count':sum(c.get('structural_hits',len(c['hits']))==0 for c in record['motion_checks']),'max_axis_error_mm':max(x['bearing_axis_alignment_max_mm'] for x in record['motion_checks'])}
  counts[name]={'parts':len(mesh),'triangles':sum(len(x['triangles']) for x in mesh),'poses':len(poses),'passes':passed,'local_clear_samples':data['models'][name]['local_clear_count']}
  for case in ('shrug_reach_parallel','crossed_clearance_candidate'):
   items,_,_=scene(parts,p,cases()[case]);render([(x['name'],x['shape'],COL[x['material']]) for x in items if x['role']!='reservation'],OUT/name/(case+'.png'),name.title()+' | '+case.replace('_',' ')+' | local packaging only',camera=(1800,-600,200))
 (OUT/'RevH_Shoulder_Review.html').write_text((HERE/'review.template.html').read_text('utf8').replace('__DATA__',json.dumps(data,separators=(',',':'))),encoding='utf8')
 save(ROOT/'verification/revH_viewer_geometry.json',counts)
 print(json.dumps(counts),flush=True)
if __name__=='__main__':main()
