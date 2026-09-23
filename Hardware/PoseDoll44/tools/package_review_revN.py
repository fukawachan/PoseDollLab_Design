"""Publish chest-deletion artifacts and an explicitly unbuilt external-box study."""
from pathlib import Path
import json, hashlib, datetime, re
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 audit=read(R/'verification/revN_chest_audit.json');assert set(audit['characters'])=={'manny','quinn'}
 for name,a in audit['characters'].items():
  assert a['parts']==1994 and len(a['checks'])==165 and a['structural_failed_poses']==0
  assert a['affected_part_checks_count']==165 and a['minimum_nominal_clutch_margin']>=1.5
  assert sha(R/f'generated/revN/{name}/{name.title()}_RevN1_assembly.step')==a['assembly_STEP_sha256']
  for rel,h in a['source_sha256'].items():assert sha(R/rel)==h,rel
 html=(R/'generated/revM/RevM_Full_Body_Review.html').read_text(encoding='utf-8')
 html=html.replace('Rev M','Rev N1').replace('REV M','REV N1').replace('_RevM_assembly.step','_RevN1_assembly.step')
 html=html.replace('Manny 与 Quinn 完整人偶','取消胸壳 · Manny 与 Quinn')
 html=html.replace('1:2 人物比例 · 41 个测量轴 · 稳定躯段包壳，活动区域外露','胸部承重骨架保留 · 背部设备仍为原位 · 外置方案评估另列')
 html=html.replace('模型按机械设计尺寸显示；无外部支架。','胸口罩壳已取消；背部设备尚未外置。')
 html=html.replace("functional_hands_on_hips:'叉腰'","functional_hands_on_hips:'叉腰',hands_behind_lower_back:'双手背后（当前背包仍有干涉）'")
 old="let [j,b,h]=await Promise.all([fetch(`${name}/viewer.json`).then(r=>r.json()),fetch(`${name}/meshes.bin`).then(r=>r.arrayBuffer()),fetch(`../../harness/${name}_revM.json`).then(r=>r.json())]);"
 new="let j=await fetch(`${name}/viewer.json`).then(r=>r.json());let [b,h]=await Promise.all([fetch(`${name}/${j.mesh_asset}`).then(r=>r.arrayBuffer()),fetch(`../../harness/${name}_revM.json`).then(r=>r.json())]);"
 assert old in html;html=html.replace(old,new)
 html=html.replace("fetch('../../verification/revM_complete_audit.json'","fetch('../../verification/revN_chest_audit.json'")
 html=html.replace('<h3>设计文件</h3>','<h3>本次改动</h3><p><a href="../../docs/CHEST_AND_EXTERNAL_REVN.zh-CN.md">胸壳改动与外置方案权衡</a></p><p><a href="../revM/RevM_Full_Body_Review.html">对比原 Rev M</a></p><p class="small">原 164 姿态保留未改件证据，修改的左肩支座在全部样本重新求交；另有双手背后样本与肩轴逐度检查。外置架构尚无新 PCB、壳体或制造文件。</p><h3>设计文件</h3>')
 html=html.replace('../../START_HERE.zh-CN.md','../../START_HERE_REVN.zh-CN.md')
 (R/'generated/revN/RevN_Chest_Review.html').write_text(html,encoding='utf-8')
 rows=[]
 for name,a in audit['characters'].items():
  changes=a['chest_removed_pose_changes'];behind=next(c for c in a['checks'] if c['pose']=='hands_behind_lower_back');before=read(R/'verification/revM_complete_audit.json')['characters'][name]['checks']
  rows.append(dict(character=name,affected_poses=len(changes),removed_contact_pairs=sum(c['removed_contact_pairs'] for c in changes),contacts_before=sum(len(c['review']) for c in before),contacts_after=sum(len(c['review']) for c in a['checks'][:164]),clear_poses_before=sum(not c['review'] for c in before),clear_poses_after=sum(not c['review'] for c in a['checks'][:164]),removed_mass_g=a['removed_mass_kg']*1000,estimated_mass_kg=a['estimated_mass_kg'],minimum_clutch_margin=a['minimum_nominal_clutch_margin'],guard_relief_volume_mm3=sum(c['removed_volume_mm3'] for c in a['modified_parts']),behind_back_contacts=len(behind['review']),behind_equipment_pairs=next((c['pairs'] for c in a['rear_equipment_baseline_pose_contacts'] if c['pose']=='hands_behind_lower_back'),0)))
 template=(R/'docs/CHEST_AND_EXTERNAL_REVN.template.md').read_text(encoding='utf-8')
 table='| 复核项 | Manny | Quinn |\n|---|---:|---:|\n'
 fields=[('左肩支座局部去除体积（mm³）','guard_relief_volume_mm3',3),('原 164 姿态中接触减少的姿态数','affected_poses',0),('取消的接触对次数（跨姿态累计）','removed_contact_pairs',0),('原 164 姿态剩余接触对次数','contacts_after',0),('原版完全无接触姿态数','clear_poses_before',0),('新版完全无接触姿态数','clear_poses_after',0),('本次减重（g）','removed_mass_g',2),('含原线束预留估重（kg）','estimated_mass_kg',3),('重新计算的最小名义持姿比','minimum_clutch_margin',3),('新增背手姿态仍有的背部设备接触对','behind_equipment_pairs',0)]
 for title,key,n in fields:table+='| '+title+' | '+' | '.join(f'{r[key]:.{n}f}' for r in rows)+' |\n'
 assert '{{RESULT_TABLE}}' in template
 (R/'docs/CHEST_AND_EXTERNAL_REVN.zh-CN.md').write_text(template.replace('{{RESULT_TABLE}}',table),encoding='utf-8')
 entry='''# Rev N1 · 胸口取消罩壳与背部外置评估

**已实施：两款人偶取消胸口罩壳、两颗螺钉和两颗螺母。** 胸部承重骨架和所有关节中心保持 Rev M，另修正左肩支座与旋转限位拨片的局部刮碰；各有 186 个打印件。背部仍保留原六个电子仓，外置方案是待重新布局的架构建议。

- [打开新三维查看器](http://127.0.0.1:8874/generated/revN/RevN_Chest_Review.html) · [本地 HTML](generated/revN/RevN_Chest_Review.html)
- [胸壳改动、接触减少数据与外置方案利弊](docs/CHEST_AND_EXTERNAL_REVN.zh-CN.md)
- [Manny 修订总装 STEP](generated/revN/manny/Manny_RevN1_assembly.step) · [Quinn 修订总装 STEP](generated/revN/quinn/Quinn_RevN1_assembly.step)
- [Manny 当前制造清单](generated/revN/manny/manufacturing_manifest.json) · [Quinn 当前制造清单](generated/revN/quinn/manufacturing_manifest.json)
- [碰撞复核记录](verification/revN_chest_audit.json) · [本轮文件清单](generated/revN/delivery_manifest.json)
- [原完整装配、电路和校准资料](START_HERE.zh-CN.md)（剔除取消的 5 件，左肩支座使用 N1 图纸）

新查看器增加双手背后姿态，并保留仍存在的后背设备干涉。不要把该姿态或外置方案理解成已经制造验证。无需现在采购或打印。

本轮 CAD 入口为 [chest_clearance.py](cad/revN/chest_clearance.py)。原版完整交付清单是 Rev M 时点的快照；当前入口提示的文字更新不会改变其几何文件。
'''
 (R/'START_HERE_REVN.zh-CN.md').write_text(entry,encoding='utf-8')
 p=R/'START_HERE.zh-CN.md';text=p.read_text(encoding='utf-8');banner='> **最新增量：** [Rev N1](START_HERE_REVN.zh-CN.md) 已取消胸口罩壳及其四个紧固件、修正左肩支座局部刮碰，并完成背部外置架构评估。下文为原 Rev M 配套资料，制造时以 N1 清单剔除取消件并替换左肩支座图纸；背部外置尚未实施。\n\n'
 if banner not in text:
  at=text.find('\n\n')+2;text=text[:at]+banner+text[at:];p.write_text(text,encoding='utf-8')
 tradeoff=read(R/'verification/revN_external_tradeoff.json');assert tradeoff['source_load_sha256']==sha(R/'verification/revM_load_work.json')
 summary=dict(revision='N1',implemented='Chest facade and four fasteners removed; left shoulder tab clearance corrected; rear electronics retained',external_architecture_status='FEASIBILITY_RECOMMENDATION_NOT_IMPLEMENTED',unchanged_M_geometry_reused_except_left_shoulder_frame=True,per_character=rows)
 save(R/'verification/revN_review_summary.json',summary)
 required=[R/'START_HERE_REVN.zh-CN.md',R/'START_HERE.zh-CN.md',R/'docs/CHEST_AND_EXTERNAL_REVN.zh-CN.md',R/'docs/CHEST_AND_EXTERNAL_REVN.template.md',R/'cad/revN/chest_clearance.py',R/'cad/revN/guard_relief.py',R/'cad/revN/screen_behind.py',R/'cad/revN/check_contact_precision.py',R/'verification/revN_guard_relief.json',R/'verification/revN_external_tradeoff.json',R/'verification/revN_twist_contact_precision.json',R/'verification/revN_behind_initial_manny.json',R/'verification/revN_behind_initial_quinn.json',R/'tools/check_viewer_revN.cjs',R/'tools/run_cad.py',R/'cad/revM/load_budget.py',R/'verification/revM_complete_audit.json',R/'verification/revM_load_work.json',R/'verification/revM_print_mesh_export.json',R/'verification/revM_print_exports.json',R/'verification/revM_print_process_clearance.json',Path(__file__),R/'verification/revN_review_summary.json',R/'verification/revN_chest_audit.json',R/'generated/revN/RevN_Chest_Review.html']
 for name in ('manny','quinn'):
  folder=R/'generated/revN'/name;required.extend(p for p in folder.iterdir() if p.is_file());required.append(R/f'generated/revM/{name}/meshes.bin');mf=read(folder/'manufacturing_manifest.json')
  for p in mf['parts']:
   required.append((folder/p['STEP']).resolve())
   if 'print' in p:required.append((folder/p['print']['STL']).resolve())
  for rel in mf['source_sha256']:required.append(R/rel)
  required.append(R/f'harness/{name}_revM.json')
  for row in read(R/'verification/revM_print_mesh_export.json')[name]['prints']:
   if row['print_process_STEP']:required.append(R/f'generated/revM/{name}'/row['print_process_STEP'])
 for p in [R/'START_HERE_REVN.zh-CN.md',R/'docs/CHEST_AND_EXTERNAL_REVN.zh-CN.md']:
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   if '://' in link or 'delivery_manifest.json' in link:continue
   assert (p.parent/link).exists(),(p,link)
 browser=R/'verification/browser_revN/checks.json'
 if browser.exists():
  for rel,h in read(browser)['source_sha256'].items():assert sha(R/rel)==h,('stale browser result',rel)
  required.extend(p for p in browser.parent.iterdir() if p.is_file())
 files=[dict(path=str(p.resolve().relative_to(R)).replace('\\','/'),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(set(p.resolve() for p in required))]
 save(R/'generated/revN/delivery_manifest.json',dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='CHEST_AND_SHOULDER_CLEARANCE_DIGITAL_CANDIDATE',external_architecture_implemented=False,paths_relative_to='Hardware/PoseDoll44',source_baseline='Rev M retained assets',summary=summary,files_count=len(files),files=files))
 print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
