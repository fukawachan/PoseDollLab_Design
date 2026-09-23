from torso_shells import *
from full_body_audit import channels41
A,meta=build('quinn');changes=[]
for c in channels41(A,'quinn'):
 q=next((q for q in A.parts if q['name'].startswith(c['part_prefix']) and q['name'].endswith('J1_dimension_envelope')),None)
 if q is None:continue
 loc=cq.Location(cq.Plane(origin=tuple(c['origin_neutral_mm']),normal=tuple(c['normal_neutral']),xDir=tuple(c['xdir_neutral'])))
 sh=cube((9.4,9.6,3.3),(0,2.1,c['package_face_mm']+1.995+1.65)).rotate((0,0,0),(0,0,1),c.get('board_rotation_deg',0)).moved(loc)
 replace_world(A,q,sh,'Side-entry SH6 mated connector maximum + allowance','pcb_component');changes.append(q['name'])
for label,pose in [('neutral',{}),('back_down',h.cases()['back_down']),('side',h.cases()['arms_side']),('wrist',{'hand_l.flex':65})]:
 items=A.scene(pose);by={q['name']:q for q in items};raw=fast_contacts(items,A.thread_pairs,set(changes),label!='neutral');review=classify_all(raw,A.parts)
 for q in review:
  if q['classification']!='structural':continue
  a=by[q['a']]['shape'];b=by[q['b']]['shape'];hit=a.intersect(b);bb=hit.BoundingBox();print(json.dumps(dict(pose=label,**q,intersection_bounds=[bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax])),flush=True)
  if label=='neutral':
   c=next(c for c in channels41(A,'quinn') if q['a'].startswith(c['part_prefix']) or q['b'].startswith(c['part_prefix']));print('frame origin',c['axis_id'],c['origin_neutral_mm'],flush=True)
 h.render([(q['name'],q['shape'],COL[q['material']]) for q in items if q['name'] in set(x[k] for x in review if x['classification']=='structural' for k in ('a','b'))],ROOT/'generated/revM/quinn'/('jst_'+label+'_work.png'),'SH6 contact review '+label,camera=(1200,-1300,1000))
