"""Full-body collision review policy reflecting the user's pose-adjustment rule.
Never deletes a raw contact. Internal, neighbouring mechanism and unknown-owner
contacts stay structural; only separated body segments become pose restrictions.
"""

def region(owner):
 if owner in ('world','pelvis'):return 'pelvis'
 base=owner.split('.')[0]
 if base in ('waist','chest','head','head_tip'):return 'head' if base=='head_tip' else base
 for s in ('l','r'):
  for prefix,r in [('clavicle','girdle'),('upperarm','upperarm'),('elbow','forearm'),('forearm','forearm'),('hand','hand'),('hand_tip','hand'),('thigh','thigh'),('calf','calf'),('foot','foot'),('ball','toe'),('toe_tip','toe'),('sole','foot')]:
   if base==prefix+'_'+s:return r+'_'+s
 return None

ADJACENT={frozenset(e) for e in [('pelvis','waist'),('waist','chest'),('chest','head'),('girdle_l','girdle_r')]}
for s in ('l','r'):
 ADJACENT.update(frozenset(e) for e in [('chest','girdle_'+s),('head','girdle_'+s),('girdle_'+s,'upperarm_'+s),('upperarm_'+s,'forearm_'+s),('forearm_'+s,'hand_'+s),('pelvis','thigh_'+s),('thigh_'+s,'calf_'+s),('calf_'+s,'foot_'+s),('foot_'+s,'toe_'+s)])

def classify(hit,owners):
 a=owners.get(hit['a']);b=owners.get(hit['b']);ra=region(a) if a else None;rb=region(b) if b else None
 if not ra or not rb:kind='structural';reason='unknown_owner_requires_review'
 elif a==b:kind='structural';reason='unplanned_same_rigid_body_overlap'
 elif ra==rb or frozenset((ra,rb)) in ADJACENT:kind='structural';reason='internal_or_neighbouring_mechanisms'
 else:kind='pose_restriction';reason='separated_body_segments_adjust_pose'
 return dict(hit,owner_a=a,owner_b=b,region_a=ra,region_b=rb,classification=kind,reason=reason)

def classify_all(hits,parts):
 owners={q['name']:q['owner'] for q in parts};return [classify(h,owners) for h in hits]
