"""Rev N1: remove anterior facade; relieve one shoulder-tab interference.
Rear electronics remain installed. External architecture is a separate feasibility study.
"""
from pathlib import Path
import sys, json, hashlib, copy, csv, math, runpy, shutil
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'cad/revM'))
import final_model as M
from guard_relief import apply as apply_guard_relief
from collision_cache import CollisionCache
from full_body_audit import poses

REMOVE={'chest_M_front_shell','chest_shell_M2x20_0','chest_shell_M2x20_1','chest_shell_nut_M2_0','chest_shell_nut_M2_1'}

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def is_back(n):return n.startswith(tuple('N'+str(i)+'_' for i in range(1,7))) or n.startswith('POWER_') or '_electronics_' in n

def trim(A):
 assert REMOVE <= {q['name'] for q in A.parts}
 before={q['name']:(id(q['local_shape']),q['owner'],q['material']) for q in A.parts}
 A.parts=[q for q in A.parts if q['name'] not in REMOVE]
 A.thread_pairs=[p for p in A.thread_pairs if not set(p)&REMOVE]
 assert len(A.parts)==1994
 assert all(before[q['name']]==(id(q['local_shape']),q['owner'],q['material']) for q in A.parts)
 return A

def behind_pose(A):
 # Kinematic target only. It is subsequently evaluated with the real BReps.
 best=None;target=M.np.array([-100.,30.,A.T0['pelvis'][2,3]+55.])
 for f in (-10,-20,-30,-40,-50):
  for a in (0,10,20,30):
   for tw in (45,60,75,90):
    for e in (45,60,75,90,105,120):
     pose={'upperarm_l.flex':f,'upperarm_l.abduct':a,'upperarm_l.twist':tw,'elbow_l.flex':e}
     T,_=M.h.fk(A.profile,pose);point=T['hand_l'][:3,3];score=float(M.np.linalg.norm(point-target))
     if best is None or score<best[0]:best=(score,pose,point)
 pose=best[1];pose |= {k.replace('_l.','_r.'):v for k,v in list(pose.items())}
 return pose,dict(target_wrist_mm=target.tolist(),left_wrist_mm=best[2].tolist(),target_error_mm=best[0],label='Hands behind lower trunk: kinematic position candidate, no contact success implied')

def main():
 baseaudit=read(R/'verification/revM_complete_audit.json');oldloads=read(R/'verification/revM_load_work.json');guardproof=read(R/'verification/revN_guard_relief.json')
 guardpath=Path(__file__).with_name('guard_relief.py')
 report=dict(revision='N1',physical_tested=False,manufacturing_released=False,scope='Five deleted parts plus one subtractive shoulder-frame relief per character. Unchanged-pair contacts inherited from hash-matched Rev M; all pairs involving the modified part freshly recomputed in 164 old poses and one new behind-back pose. Rear electronics unchanged.',characters={})
 for name in ('manny','quinn'):
  print('LOAD',name,flush=True);base=R/'generated/revM'/name;out=R/'generated/revN'/name;out.mkdir(parents=True,exist_ok=True);(out/'parts').mkdir(exist_ok=True)
  mf=read(base/'manufacturing_manifest.json');view=read(base/'viewer.json');src=mf['source_sha256']
  for rel,h in src.items():assert sha(R/rel)==h,('changed Rev M geometry input',rel)
  assert baseaudit['characters'][name]['source_sha256']==src==view['source_sha256']
  assert guardproof[name]['source_sha256']==src and guardproof[name]['generator_sha256']==sha(guardpath)
  A,meta=M.build(name);assert meta['source_sha256']==src
  original_profile=copy.deepcopy(A.profile);trim(A);changes=apply_guard_relief(A);assert A.profile==original_profile
  assert changes==guardproof[name]['changes'];affected={q['part'] for q in changes};partindex={q['name']:i for i,q in enumerate(A.parts)}
  sources=src|{str(Path(__file__).relative_to(R)):sha(Path(__file__)),str(guardpath.relative_to(R)):sha(guardpath)}
  a=copy.deepcopy(baseaudit['characters'][name]);a.update(source_sha256=sources,parts=len(A.parts),independent_cache_checks=[],removed_parts=sorted(REMOVE),modified_parts=changes,affected_part_checks_count=0)
  changed=[];cache=CollisionCache(A)
  def merge_recheck(row):
   oldraw=[q for q in row['raw_contacts'] if not {q['a'],q['b']}&REMOVE]
   fresh=cache.contacts(row['angles_deg'],affected,skip_same_owner=row['pose']!='neutral')
   assert {frozenset((q['a'],q['b'])) for q in fresh}<={frozenset((q['a'],q['b'])) for q in oldraw},(name,row['pose'],'unexpected new contact after subtraction')
   raw=[q for q in oldraw if not {q['a'],q['b']}&affected]+fresh
   raw.sort(key=lambda q:(partindex[q['a']],partindex[q['b']]))
   row['raw_contacts']=raw;row['review']=M.classify_all(raw,A.parts);row['verification_method']='Fresh BRep check for every pair touching modified shoulder frame; exact source-matched inheritance for unchanged pairs'
   a['affected_part_checks_count']+=1
  for row in a['checks']:
   old=len(row['review']);deleted=sum(bool({q['a'],q['b']}&REMOVE) for q in row['review']);merge_recheck(row)
   if deleted:changed.append(dict(pose=row['pose'],removed_contact_pairs=deleted,remaining_contact_pairs=len(row['review'])))
   if a['affected_part_checks_count']%20==0:print(name,'modified frame checks',a['affected_part_checks_count'],'/ 165',flush=True)
  initial=read(R/f'verification/revN_behind_initial_{name}.json');assert initial['source_sha256']==src
  extra=initial['angles_deg'];extra_info=initial['target_info']
  extra_row=dict(pose='hands_behind_lower_back',angles_deg=extra,raw_contacts=initial['raw_contacts']);merge_recheck(extra_row);a['checks'].append(extra_row)
  a['hands_behind_info']=extra_info;a['structural_failed_poses']=sum(any(q['classification']=='structural' for q in row['review']) for row in a['checks'])
  assert not a['structural_failed_poses'],(name,'unresolved structural contact')
  a['chest_removed_pose_changes']=changed;a['inherited_readout_and_endpoints']='Sensor geometry/owners/profile unchanged; readout for original 164 cases inherited. Shoulder twist endpoint records replaced by the new 1-degree range test; other 39 endpoint records unchanged.'
  for ep in a['endpoints']:
   if ep['axis'] in ('upperarm_l.twist','upperarm_r.twist'):
    side=ep['axis'].split('_')[1].split('.')[0];ep['checks']=[dict(angle_deg=q['angle_deg'],volume_mm3=q['volume_mm3'],outside=q['outside']) for q in guardproof[name]['checks'] if q['side']==side];ep['verification_method']='New range scan in relative joint coordinates, 1 degree steps plus 1 degree outside both ends'
  a['baseline_audit_sha256']=sha(R/'verification/revM_complete_audit.json');a['initial_behind_check_sha256']=sha(R/f'verification/revN_behind_initial_{name}.json');a['guard_proof_sha256']=sha(R/'verification/revN_guard_relief.json')
  a['rear_equipment_baseline_pose_contacts']=[dict(pose=row['pose'],pairs=sum(is_back(q['a']) or is_back(q['b']) for q in row['review'])) for row in a['checks'] if any(is_back(q['a']) or is_back(q['b']) for q in row['review'])]
  removed_mass=sum(p['kg'] for p in oldloads[name]['parts'] if p['name'] in REMOVE);relief_mass=sum(q['removed_volume_mm3']*2.81/1e6 for q in changes)
  a['removed_mass_kg']=removed_mass+relief_mass;a['estimated_mass_kg']=oldloads[name]['model_mass_kg']+oldloads[name]['allowance_mass_kg']-a['removed_mass_kg'];a['rear_equipment_mass_kg']=sum(p['kg'] for p in oldloads[name]['parts'] if is_back(p['name']))
  report['characters'][name]=a;save(R/'verification/revN_chest_audit.json',report)
  # Retain the exact old meshes for unchanged parts, append the one revised part.
  view['parts']=[p for p in view['parts'] if p['name'] not in REMOVE];shutil.copyfile(base/'meshes.bin',out/'meshes.bin');cursor=(out/'meshes.bin').stat().st_size//24
  for p in view['parts']:p['STEP']='../../revM/'+name+'/'+p['STEP']
  newrecords={}
  with (out/'meshes.bin').open('ab') as binary:
   for q in A.parts:
    if q['name'] not in affected:continue
    sh=q['local_shape'];step='parts/'+q['name']+'.step';sh.exportStep(str(out/step),precision_mode=1);check=M.cq.importers.importStep(str(out/step)).val();assert check.isValid() and len(check.Solids())==1 and abs(check.Volume()-sh.Volume())<.001
    bb=sh.BoundingBox();bounds=[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax];vs,faces=sh.tessellate(.7,.4);vs=M.np.array([v.toTuple() for v in vs],dtype=M.np.float32);faces=M.np.array(faces,dtype=M.np.int32);pts=vs[faces];normal=M.np.cross(pts[:,1]-pts[:,0],pts[:,2]-pts[:,0]);normal/=M.np.maximum(M.np.linalg.norm(normal,axis=1)[:,None],1e-12);data=M.np.concatenate((pts,M.np.repeat(normal[:,None,:],3,axis=1)),axis=2).astype('<f4');binary.write(data.tobytes());count=len(faces)*3
    vp=next(p for p in view['parts'] if p['name']==q['name']);vp.update(first=cursor,count=count,bounds=bounds,STEP=step,note=q['note']);cursor+=count;newrecords[q['name']]=dict(STEP=step,local_bounds_mm=bounds,volume_mm3=sh.Volume(),note=q['note'])
  view.update(revision='N1',source_sha256=sources,mesh_asset='meshes.bin');T,_=M.h.fk(A.profile,extra);view['poses']['hands_behind_lower_back']=dict(angles_deg=extra,transforms={o:T[o].T.flatten().tolist() for o in T});save(out/'viewer.json',view)
  mf['parts']=[p for p in mf['parts'] if p['id'] not in REMOVE]
  for p in mf['parts']:
   p['STEP']='../../revM/'+name+'/'+p['STEP']
   if 'print' in p:p['print']['STL']='../../revM/'+name+'/'+p['print']['STL']
   if p['id'] in newrecords:p.update(newrecords[p['id']])
  mf.update(revision='N1',source_sha256=sources,removed_parts=sorted(REMOVE),modified_parts=changes,electronics_architecture='Rev M retained. Hybrid external architecture is not implemented by this file.',baseline_manifest_sha256=sha(base/'manufacturing_manifest.json'))
  mf['meta']=copy.deepcopy(mf['meta']);mf['meta']['rigid_chest_cover']=dict(installed=False,previous_revision='M',load_bearing_chest_frame_unchanged=True,unused_integral_mount_lugs_retained=True);mf['meta']['revision']='N1';mf['meta']['source_sha256']=sources;mf['meta']['guard_relief']=changes
  assert sum('print' in p for p in mf['parts'])==186;save(out/'manufacturing_manifest.json',mf)
  with (out/'parts_bom.csv').open('w',newline='',encoding='utf-8-sig') as f:
   fields=['id','owner','material','role','quantity','volume_mm3','STEP','note'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(mf['parts'])
  print(name,'EXPORT STEP',flush=True);assembly=M.cq.Assembly(name='PoseDoll_'+name+'_RevN1')
  for q in A.parts:assembly.add(M.h.move(q['local_shape'],A.T0[q['owner']]),name=q['name'],color=M.cq.Color(*M.COL[q['material']]))
  assembly.save(str(out/(name.title()+'_RevN1_assembly.step')))
  scene=A.scene({'upperarm_l.abduct':15,'upperarm_r.abduct':15});render=[(q['name'],q['shape'],M.COL[q['material']]) for q in scene if q['role']!='reservation'];M.h.render(render,out/'front.png',name.title()+' | Rev N1 | open chest, existing electronics',camera=(2800,-850,950))
  render=[(q['name'],q['shape'],M.COL[q['material']]) for q in A.scene(extra) if q['role']!='reservation'];M.h.render(render,out/'hands_behind.png',name.title()+' | hands behind | existing rear interference retained',camera=(-2800,850,950))
  print(name,'LOAD BUDGET',flush=True);budget=runpy.run_path(str(R/'cad/revM/load_budget.py'),run_name='revN_load_consumer')['budget'];b=budget(A,read(R/f'harness/{name}_revM.json'));b['source_cad_sha256']=sources;b['source_harness_sha256']=sha(R/f'harness/{name}_revM.json');save(out/'load_budget.json',b)
  a['minimum_nominal_clutch_margin']=min(p['clutch_margin'] for p in b['axes'] if p['clutch_margin'] is not None);assert a['minimum_nominal_clutch_margin']>=1.5
  a['revised_mesh_sha256']=sha(out/'meshes.bin');a['assembly_STEP_sha256']=sha(out/(name.title()+'_RevN1_assembly.step'));save(R/'verification/revN_chest_audit.json',report)
  print(name,'DONE',json.dumps(dict(parts=len(A.parts),prints=186,changed_poses=len(changed),removed_pairs=sum(c['removed_contact_pairs'] for c in changed),hands_behind_pairs=len(extra_row['review']),back_in_new_pose=sum(is_back(q['a']) or is_back(q['b']) for q in extra_row['review']),mass_kg=a['estimated_mass_kg'])),flush=True)
if __name__=='__main__':main()
