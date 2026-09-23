"""Check explicit new contacts, including same-owner parts and added cradle volume."""
from compact_twist import *
def allowed(a,b):
    for s in ('l','r'):
        p=s+'_twist_sensor_'
        for screw in ('keeper_set_M2x3_0','keeper_set_M2x3_1','arm_radial_M2x6'):
            if {a,b}=={p+screw,p+'integral_magnet_shaft'}:return True
        for i in (0,1):
            if {a,b}=={p+'board_cap_M2x6_'+str(i),s+'_abduct_ring_and_twist_seat'}:return True
    return False
def audit(items):
    hits=[]
    for i,a in enumerate(items):
        for b in items[i+1:]:
            if a['role']=='reservation' or b['role']=='reservation':continue
            if not ('_twist_sensor_' in a['name'] or '_twist_sensor_' in b['name']):continue
            if a['owner']!=b['owner']:continue
            aa=a['shape'].BoundingBox();bb=b['shape'].BoundingBox()
            if not all(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
            v=a['shape'].intersect(b['shape']).Volume()
            if v>.02:hits.append(dict(a=a['name'],b=b['name'],volume_mm3=round(v,4),intentional_thread=allowed(a['name'],b['name'])))
    return hits
def delta_audit(name,items):
    _,oldparts,_=j.build(name);p=h.profile(name);old,_,_=h.scene(oldparts,p,{})
    baseline={q['name']:q for q in old};out=[]
    changed=[q for q in items if q['name'].endswith(('_abduct_ring_and_twist_seat','_arm_coupling'))]
    for q in changed:
        delta=q['shape'].cut(baseline[q['name']]['shape'])
        if delta.Volume()<.02:continue
        db=delta.BoundingBox()
        for other in items:
            if other['name']==q['name'] or other['owner']!=q['owner'] or other['role']=='reservation':continue
            bb=other['shape'].BoundingBox()
            if not all(min(getattr(db,k+'max'),getattr(bb,k+'max'))-max(getattr(db,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
            v=delta.intersect(other['shape']).Volume()
            if v>.02:out.append(dict(a=q['name'],b=other['name'],volume_mm3=round(v,4),intentional_thread=allowed(q['name'],other['name'])))
    return out
def main():
    p,parts,_=build('quinn');items,_,_=h.scene(parts,p,{})
    contacts=audit(items)+delta_audit('quinn',items)
    print(json.dumps(dict(contacts=contacts,unexpected=[x for x in contacts if not x['intentional_thread']])),flush=True)
if __name__=='__main__':main()
