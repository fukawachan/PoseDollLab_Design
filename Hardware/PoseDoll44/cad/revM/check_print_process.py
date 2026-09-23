"""Check printable process variants against the complete assembly and update mass."""
from final_model import *
from collision_cache import CollisionCache
from full_body_audit import poses
import runpy
budget=runpy.run_path(str(ROOT/'cad/revM/load_budget.py'),run_name='revM_budget_consumer')['budget']

def main():
 path=ROOT/'verification/revM_print_mesh_export.json';variants=json.loads(path.read_text());digest=hashlib.sha256(path.read_bytes()).hexdigest();out={};loads={}
 for name in ('manny','quinn'):
  A,m=build(name);folder=ROOT/f'generated/revM/{name}';manifest=json.loads((folder/'manufacturing_manifest.json').read_text());records={p['id']:p for p in manifest['parts']};parts={p['name']:p for p in A.parts};affected=set();changes=[]
  assert variants[name]['source_cad_sha256']==m['source_sha256']
  for row in variants[name]['prints']:
   if not row['print_process_STEP']:continue
   q=parts[row['id']];record=records[row['id']]['print'];f=folder/row['print_process_STEP'];s=cq.importers.importStep(str(f)).val();assert s.isValid() and len(s.Solids())==1
   s=s.translate(tuple(-np.array(record['translation_mm'])))
   if record['diagonal']:s=s.moved(cq.Location(cq.Plane(origin=(0,0,0),normal=record['final_plane']['normal'],xDir=record['final_plane']['xdir'])).inverse)
   for axis,angle in reversed(list(zip(((1,0,0),(0,1,0),(0,0,1)),record['euler_xyz_deg']))):
    if angle:s=s.rotate((0,0,0),axis,-angle)
   delta=s.Volume()-q['local_shape'].Volume();assert abs(s.Volume()-row['print_process_volume_mm3'])<max(.001,1e-6*row['print_process_volume_mm3']),(row['id'],delta)
   q['local_shape']=s;affected.add(q['name']);changes.append(dict(part=q['name'],added_volume_mm3=delta,STEP_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),STL_sha256=row['STL_sha256']))
  cache=CollisionCache(A);cases,_=poses(A);rows=[]
  for label,pose in cases.items():
   review=classify_all(cache.contacts(pose,affected=affected,skip_same_owner=label!='neutral'),A.parts);bad=[r for r in review if r['classification']=='structural'];rows.append(dict(pose=label,review=review));assert not bad,(name,label,bad[:5])
   if len(rows)%40==0:print(name,'print-process clearance',len(rows),'/',len(cases),flush=True)
  out[name]=dict(source_cad_sha256=m['source_sha256'],source_print_export_sha256=digest,changed_parts=changes,checks=rows,passed=True,scope='R0.10 mm printable variant beads checked at the same 164 complete-body poses, only affected pairs; base complete audit covers every unchanged pair. No physical printing claim.')
  h.save(ROOT/'verification/revM_print_process_clearance.json',out)
  harness=json.loads((ROOT/f'harness/{name}_revM.json').read_text());b=budget(A,harness);b.update(source_cad_sha256=m['source_sha256'],source_harness_sha256=hashlib.sha256((ROOT/f'harness/{name}_revM.json').read_bytes()).hexdigest(),source_print_export_sha256=digest);loads[name]=b;print(name,len(changes),'process variants PASS; mass',b['model_mass_kg']+b['allowance_mass_kg'],flush=True)
 h.save(ROOT/'verification/revM_load_work.json',loads)
if __name__=='__main__':main()
