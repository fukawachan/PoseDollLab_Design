"""Nominal straight 2.5 mm hex key access in explicit assembly states."""
from shoulder_integration import *
def main():
 results=[]
 for name in ('manny','quinn'):
  p,parts,meta=build(name);items,T,A=h.scene(parts,p,{})
  for side,sy in [('l',1),('r',-1)]:
   S=A[f'upperarm_{side}.flex']['origin']
   for label,normal,xd,tip in [('flex',(0,-sy,0),(1,0,0),19),('abduct',(1,0,0),(0,0,1),10)]:
    loc=frame_transform(normal,xd,S)
    tool=cyl(-60,tip-4.5,1.5).fuse(hexagon(2.5,tip-4.5,tip-2.55)).moved(loc)
    keep=[];removed=[]
    for q in items:
     if q['role']=='reservation':continue
     omit=False
     if label=='flex':
      omit=q['owner'] in (f'upperarm_{side}.abduct_frame',f'upperarm_{side}',f'elbow_{side}') or q['name'].startswith(side+'_abduct_clutch_')
     else:
      omit=q['name'] in (side+'_abduct_stub_-1',side+'_twist_bush',side+'_twist_shaft')
     (removed if omit else keep).append(q)
    findings=[]
    tb=tool.BoundingBox()
    for q in keep:
     bb=q['shape'].BoundingBox()
     if not all(min(getattr(tb,k+'max'),getattr(bb,k+'max'))-max(getattr(tb,k+'min'),getattr(bb,k+'min'))>1e-4 for k in 'xyz'):continue
     vol=tool.intersect(q['shape']).Volume()
     if vol>.02:findings.append({'part':q['name'],'volume_mm3':round(vol,4)})
    results.append(dict(character=name,side=side,clutch=label,tool='3mm shaft envelope with nominal 2.5mm hex tip',
     not_installed=[q['name'] for q in removed],unexpected_contacts=findings))
    print(json.dumps(dict(character=name,side=side,clutch=label,contacts=findings)),flush=True)
 h.save(ROOT/'verification/revI_tool_access.json',{'scope':'Straight insertion geometry at staged neutral assembly; not a real tool/hand accessibility test','checks':results})
 if any(q['unexpected_contacts'] for q in results):raise RuntimeError('Tool path obstructed')
if __name__=='__main__':main()
