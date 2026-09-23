"""Strap-mounted wire saddles on rigid limb rails. No screw into a thin printed wall."""
from completed_body import *
import completed_body as body

def add_saddles(A):
 rows=[];changed=[]
 targets=[]
 for side in ('l','r'):
  targets += [(f'upperarm_{side}',f'elbow_{side}_flex_M_upperarm_carrier'),(f'forearm_{side}',f'forearm_{side}_twist_M_distal_forearm_carrier'),(f'thigh_{side}',f'thigh_{side}_M_centreline_frame'),(f'calf_{side}',f'calf_{side}_M_centreline_frame')]
 scene=A.scene({})
 for owner,key in targets:
  frame,shape=world_part(A,key);bb=shape.BoundingBox();done=False
  for fraction in (.50,.40,.60,.30,.70):
   z=bb.zmin+(bb.zmax-bb.zmin)*fraction
   section=shape.intersect(cube((2000,2000,.1),(0,0,z)))
   if not section.Solids():continue
   sec=max(section.Solids(),key=lambda s:s.Volume()).BoundingBox()
   if max(sec.xlen,sec.ylen)>30 or min(sec.xlen,sec.ylen)<5:continue
   for axis,sg in ((1,1 if owner.endswith('_l') else -1),(0,-1),(0,1),(1,-1 if owner.endswith('_l') else 1)):
    lo=np.array([sec.xmin,sec.ymin]);hi=np.array([sec.xmax,sec.ymax]);centre=(lo+hi)/2
    plane=hi[axis] if sg>0 else lo[axis];centre[axis]=plane+sg*(.4+3.4)
    O=np.array([*centre,z]);angle={(0,1):0,(0,-1):180,(1,1):90,(1,-1):270}[(axis,sg)]
    saddle=ring(-3,3,3.4,2.4).cut(cube((10,3.0,8),(5,0,0)))
    saddle=fuse_checked(saddle,cube((1.2,6,6),(-2.8,0,0)),'wire_saddle_flat')
    # Mounting flat x=-3.4 touches a .4 mm compressed silicone pad.
    pad=cube((.4,6,6),(-3.6,0,0))
    saddle=saddle.rotate((0,0,0),(0,0,1),angle).translate(tuple(O));pad=pad.rotate((0,0,0),(0,0,1),angle).translate(tuple(O))
    sb=saddle.BoundingBox();mn=np.minimum(lo,[sb.xmin,sb.ymin])-.15;mx=np.maximum(hi,[sb.xmax,sb.ymax])+.15;mid=(mn+mx)/2
    strap=cube((mx[0]-mn[0]+1.3,mx[1]-mn[1]+1.3,2.5),(*mid,z)).cut(cube((mx[0]-mn[0],mx[1]-mn[1],2.7),(*mid,z)))
    bits=[('saddle',saddle,'frame'),('pad',pad,'silicone'),('strap',strap,'nylon')]
    trial=[dict(name='WIRE_'+owner+'_'+n,shape=s,owner=owner,role='candidate_solid') for n,s,m in bits]
    hits=fast_contacts(scene+trial,(),{q['name'] for q in trial})
    if hits:continue
    for n,s,m in bits:
     label='WIRE_'+owner+'_'+n;A.add(label,s,m,owner,'4.8 mm open wire saddle, .4 mm installed silicone pad, 2.5 mm PA66 cable tie; no rotating shaft contact');changed.append(label)
    scene=A.scene({});rows.append(dict(id='A_'+owner,owner=owner,mount_part=key,origin_neutral_mm=O.tolist(),direction=[0,0,1],inner_diameter_mm=4.8,pad_free_thickness_mm=.5,strap_width_mm=2.5,strap_length_mm=int(math.ceil((2*(mx-mn).sum()+25)/10)*10),wire_centre_local_mm=(O-A.T0[owner][:3,3]).tolist()))
    done=True;break
   if done:break
  if not done:raise ValueError(('no_clear_wire_saddle',owner))
 return rows,changed

def build(name):
 A,meta=body.build(name);anchors,changed=add_saddles(A)
 return A,dict(meta,wire_anchors=anchors,affected_wire_saddles=changed)

def main():
 out={}
 for name in ('quinn','manny'):
  A,meta=build(name);h.save(ROOT/f'mechanical_manifest/wire_anchors_revM_{name}.json',meta['wire_anchors']);cache=CollisionCache(A);cases,_=poses(A);checks=[]
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,set(meta['affected_wire_saddles']),label!='neutral'),A.parts);checks.append(dict(pose=label,angles_deg=pose,review=review));bad=[r for r in review if r['classification']=='structural']
   if bad:print(json.dumps(dict(character=name,pose=label,structural=bad)),flush=True)
  out[name]=dict(anchors=meta['wire_anchors'],checks=checks);h.save(ROOT/'verification/revM_wire_saddles_work.json',out)
  print(name,'wire saddles',len(checks),'failed',sum(any(r['classification']=='structural' for r in q['review']) for q in checks),flush=True)
if __name__=='__main__':main()
