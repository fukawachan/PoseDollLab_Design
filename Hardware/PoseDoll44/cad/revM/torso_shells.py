"""Rigid anterior lower thorax only; shoulder belt, abdomen and hips stay exposed."""
from electronics_pods import *
import electronics_pods as pods
from character_reference import reference_character

def add_chest_shell(A,name):
 C=A.T0['chest'][:3,3];ref=reference_character(name);dominant=[ref['names'][max(w,key=lambda q:q[1])[0]] for w in ref['geometry']['skin_weights']];v=ref['vertices_mm']*1.5-C;body=v[np.array([n.startswith('spine_') for n in dominant])];rows=[]
 for z in (20.,40.,65.,85.):
  band=body[np.abs(body[:,2]-z)<6.];assert len(band)>3,(name,z,len(band));lo=band.min(0);hi=band.max(0);front=80.;back=float(lo[0]-2);ry=float(max(abs(lo[1]),abs(hi[1]))+2)
  rows.append((z,(front+back)/2,(front-back)/2,max(45.,ry)))
 outer=head_loft(rows);inner=head_loft([(z+(-.5 if i==0 else .5 if i==len(rows)-1 else 0),cx,rx-1.8,ry-1.8) for i,(z,cx,rx,ry) in enumerate(rows)])
 for z in (50,75):inner=inner.cut(xcyl(69.05,90,4,0,z))
 shell=outer.cut(inner).intersect(cube((200,250,180),(130,0,50)))
 frame,w=world_part(A,'chest_M_body_frame');w=w.translate(tuple(-C))
 for i,z in enumerate((50,75)):
  w=fuse_checked(w,cube((8,8,6),(65,0,z)),'chest_skin_mount').cut(xcyl(60.9,69.1,1.2,0,z))
  shell=shell.cut(xcyl(60,90,1.2,0,z)).cut(xcyl(79,90,2.1,0,z))
  bolt=xcyl(59,79,1,0,z).fuse(xcyl(79,81,1.9,0,z)).cut(xhex(1.5,79.7,81.1,0,z));nut=xhex(4,59.4,61,0,z).cut(xcyl(59.3,61.1,.8,0,z))
  bn=f'chest_shell_M2x20_{i}';nn=f'chest_shell_nut_M2_{i}';A.add(bn,bolt.translate(tuple(C)),'metal','chest','M2x20 from front into M2 nut behind integral flat mount');A.add(nn,nut.translate(tuple(C)),'metal','chest','M2 nut accessible from open lateral torso; fit shell before rear electronics service cover');A.thread_pairs.append([bn,nn])
 replace_world(A,frame,w.translate(tuple(C)),frame['note']+'; two flat thorax shell attachment lugs',frame['material'])
 A.add('chest_M_front_shell',shell.translate(tuple(C)),'shell','chest','1.8 mm lower thorax facade; character-derived section widths; depth expanded to clear front neck-support beam; no shell over shoulder girdle, abdomen or hip folds')
 return dict(section_rows_mm=rows,wall_mm=1.8,covered_z_from_chest_pivot_mm=[20,85],front_depth_mm=80,reason='stable ribcage region only, expanded over internal support',physical_tested=False)

def build(name):
 A,meta=pods.build(name);chest=add_chest_shell(A,name);return A,dict(meta,rigid_chest_cover=chest)

def main():
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name);aff={q['name'] for q in A.parts if q['name'].startswith(('N','chest_shell_')) or '_electronics_' in q['name'] or q['name'] in ('chest_M_front_shell','chest_M_body_frame','pelvis_M_body_frame')};cache=CollisionCache(A);checks=[]
  cases=dict(h.cases());cases.update(sit={'thigh_l.flex':90,'thigh_r.flex':90,'calf_l.flex':90,'calf_r.flex':90},trunk_bend={'waist.pitch':40,'chest.pitch':30},trunk_extend={'waist.pitch':-20,'chest.pitch':-20},trunk_roll={'waist.roll':25,'chest.roll':20})
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,aff,label!='neutral'),A.parts);bad=[r for r in review if r['classification']=='structural'];checks.append(dict(pose=label,angles_deg=pose,review=review));print(json.dumps(dict(character=name,pose=label,structural_count=len(bad),first=bad[:8])),flush=True)
  out[name]=dict(chest=meta['rigid_chest_cover'],pods=meta['electronics_pods'],checks=checks);h.save(ROOT/'verification/revM_torso_covers_work.json',out)
  h.render([(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation'],ROOT/'generated/revM'/name/'torso_packaging_work.png',name.title()+' | rigid covers and electronics | candidate',camera=(1700,-2800,1100))
if __name__=='__main__':main()
