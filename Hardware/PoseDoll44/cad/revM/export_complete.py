"""Export complete, input-hashed assemblies, all parts and printer candidates."""
from final_model import *
import csv,struct
from collision_review import region
from full_body_audit import poses

PRINT={'frame','shell'}

def orientation(shape):
 candidates=[]
 for xyz in ((0,0,0),(90,0,0),(-90,0,0),(0,90,0),(0,-90,0),(180,0,0)):
  sh=shape
  for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),xyz):
   if angle:sh=sh.rotate((0,0,0),axis,angle)
  bb=sh.BoundingBox();candidates.append((sh,dict(euler_xyz_deg=list(xyz),diagonal=False),bb))
 # A long slender beam can fit in the volume diagonal without shortening a bone.
 longest=max((shape.BoundingBox().xlen,shape.BoundingBox().ylen,shape.BoundingBox().zlen))
 if longest>174:
  for xyz in ((0,0,0),(90,0,0),(0,90,0)):
   sh=shape
   for axis,angle in zip(((1,0,0),(0,1,0),(0,0,1)),xyz):
    if angle:sh=sh.rotate((0,0,0),axis,angle)
   for nx,ny in ((1,1),(1,-1),(-1,1),(-1,-1)):
    loc=cq.Location(cq.Plane(origin=(0,0,0),normal=(nx,ny,1),xDir=(ny,-nx,0)))
    diagonal=sh.moved(loc);candidates.append((diagonal,dict(euler_xyz_deg=list(xyz),diagonal=True,final_plane=dict(normal=[nx,ny,1],xdir=[ny,-nx,0])),diagonal.BoundingBox()))
 def score(r):
  b=r[2];fit=max(b.xlen+6,b.ylen+6,b.zlen)<=180
  return (not fit, max(b.xlen+6,b.ylen+6,b.zlen) if longest>174 or not fit else b.zlen)
 sh,record,bb=min(candidates,key=score);shift=(-bb.xmin,-bb.ymin,-bb.zmin)
 record.update(translation_mm=list(shift),bounds_mm=[bb.xlen,bb.ylen,bb.zlen],a1_mini_180_with_3mm_brim=max(bb.xlen+6,bb.ylen+6,bb.zlen)<=180,slicer_support_review_required=True)
 return sh.translate(shift),record

def export(name):
 A,meta=build(name);folder=ROOT/'generated/revM'/name;partsdir=folder/'parts';printdir=folder/'print_candidates'
 partsdir.mkdir(parents=True,exist_ok=True);printdir.mkdir(exist_ok=True);assembly=cq.Assembly(name='PoseDoll_'+name+'_RevM');rows=[];meshes=[];cursor=0
 with (folder/'meshes.bin').open('wb') as binary:
  for index,q in enumerate(A.parts):
   if q['role']=='reservation':continue
   sh=q['local_shape'];world=h.move(sh,A.T0[q['owner']]);color=COL[q['material']]
   assembly.add(world,name=q['name'],color=cq.Color(*color));bb=sh.BoundingBox()
   record=dict(id=q['name'],owner=q['owner'],material=q['material'],role=q['role'],note=q['note'],quantity=1,volume_mm3=sh.Volume(),local_bounds_mm=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax],assembly_transform=A.T0[q['owner']].tolist(),region=region(q['owner']))
   filename=q['name']+'.step';cq.exporters.export(sh,str(partsdir/filename));record['STEP']='parts/'+filename
   if q['material'] in PRINT:
    ps,setting=orientation(sh);cq.exporters.export(ps,str(printdir/(q['name']+'.stl')),tolerance=.05,angularTolerance=.1);record['print']=dict(setting,STL='print_candidates/'+q['name']+'.stl',material='PLA, prototype only',nozzle_mm=.4,layer_mm=.2,walls=6,infill_percent=40 if q['material']=='frame' else 15)
   vs,faces=sh.tessellate(.7,.4);vs=np.array([v.toTuple() for v in vs],dtype=np.float32);faces=np.array(faces,dtype=np.int32);pts=vs[faces];n=np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
   data=np.concatenate((pts,np.repeat(n[:,None,:],3,axis=1)),axis=2).astype('<f4');binary.write(data.tobytes());count=len(faces)*3
   meshes.append(dict(name=q['name'],owner=q['owner'],material=q['material'],role=q['role'],note=q['note'],region=region(q['owner']),color=list(color),first=cursor,count=count,bounds=record['local_bounds_mm'],STEP=record['STEP']));cursor+=count;rows.append(record)
   if index%250==0:print(name,'exported',index,'/',len(A.parts),flush=True)
 assembly.save(str(folder/(name.title()+'_RevM_assembly.step')))
 cases,_=poses(A);states={}
 for label,pose in cases.items():
  T,_=h.fk(A.profile,pose);states[label]=dict(angles_deg=pose,transforms={o:T[o].T.flatten().tolist() for o in T})
 manifest=dict(character=name,revision='M',profile=A.profile,source_sha256=meta['source_sha256'],parts=rows,meta=meta,manufacturing_released=False,physical_tested=False)
 h.save(folder/'manufacturing_manifest.json',manifest);h.save(folder/'viewer.json',dict(character=name,revision='M',source_sha256=meta['source_sha256'],parts=meshes,poses=states))
 h.save(ROOT/f'mechanical_manifest/wire_anchors_revM_{name}.json',meta['wire_anchors'])
 with (folder/'parts_bom.csv').open('w',newline='',encoding='utf-8-sig') as f:
  fields=['id','owner','material','role','quantity','volume_mm3','STEP','note'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
 failures=[r['id'] for r in rows if 'print' in r and not r['print']['a1_mini_180_with_3mm_brim']]
 print(name,'export finished',len(rows),'parts',sum('print' in r for r in rows),'print candidates','oversize',failures,flush=True)
 render=[(q['name'],q['shape'],COL[q['material']]) for q in A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15}) if q['role']!='reservation']
 h.render(render,folder/'full_front.png',name.title()+' | complete 41-axis design candidate',camera=(2800,-850,950));h.render(render,folder/'full_back.png',name.title()+' | electronics and service access',camera=(-2800,850,950))
 return dict(character=name,parts=len(rows),print_parts=sum('print' in r for r in rows),oversize_parts=failures)
if __name__=='__main__':
 out=[]
 for name in ('manny','quinn'):out.append(export(name));h.save(ROOT/'verification/revM_export_summary.json',out)
