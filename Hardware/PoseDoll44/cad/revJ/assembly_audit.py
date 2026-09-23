from shoulder_revision import *
def allowed_contact(a,b):
 for marker in ('_clutch_','_drive_','_abduct_sensor_'):
  pa=a.split(marker);pb=b.split(marker)
  if len(pa)!=2 or len(pb)!=2 or pa[0]!=pb[0]:continue
  aa,bb=pa[1],pb[1]
  if marker=='_clutch_':return intentional_threads(aa,bb)
  if marker=='_abduct_sensor_':return allowed_thread(aa,bb)
  if {aa,bb}=={'split_hub','pinch_M2x10'}:return True
  for i in (0,1):
   if {aa,bb}=={'mount_M2x4_'+str(i),'mount_M2_nut_'+str(i)}:return True
 return False

def pairs(items,only_new=True,same_owner=True):
 out=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if a['role']=='reservation' or b['role']=='reservation':continue
   if same_owner and a['owner']!=b['owner']:continue
   if only_new and not any(s in a['name'] or s in b['name'] for s in ('_clutch_','_drive_','_abduct_sensor_')):continue
   aa=a['shape'].BoundingBox();bb=b['shape'].BoundingBox()
   if not all(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
   v=a['shape'].intersect(b['shape']).Volume()
   if v<=.02:continue
   out.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4),intentional_thread=allowed_contact(a['name'],b['name'])))
 return out

def main():
 p,parts,meta=build('quinn');items,_,_=h.scene(parts,p,{})
 hits=pairs(items)
 print(json.dumps({'unexpected':[q for q in hits if not q['intentional_thread']],'expected':sum(q['intentional_thread'] for q in hits)}),flush=True)
 h.save(ROOT/'verification/revJ_assembly_trial.json',hits)
 h.render([(q['name'],q['shape'],COL[q['material']]) for q in items if q['name'].startswith('l_') and q['role']!='reservation' and '_arm_' not in q['name'] and not any(v in q['name'] for v in ('_yaw_','_elev_'))],OUT/'quinn_shoulder_trial.png','Rev J | clamp + rear abduction sensor',camera=(1000,-1500,600))
if __name__=='__main__':main()
