"""Data audit and engineering record for the current shoulder clutch milestone."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads((ROOT/path).read_text('utf8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 load=read('verification/revI_load_budget.json');component=read('verification/revI_clutch_component_check.json')
 for key in ('flex','abduct'):
  assert not component[key]['unexpected_assembly_contacts']
  assert all(not q['hits'] for q in component[key]['rotation_checks'])
 tool_access=read('verification/revI_tool_access.json');assert all(not q['unexpected_contacts'] for q in tool_access['checks'])
 variants={};table=[];poses=[];budget=[]
 for name in ('manny','quinn'):
  record=read(f'verification/revI_{name}.json')
  p=read(f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json')
  old=read(f'mechanical_manifest/physical_{name}_44_revE_proportion.json')
  assert p['axis_order']==old['axis_order'] and len(p['axis_order'])==44
  limits={a['id']:a['limits_rad'] for a in p['axes']}
  assert all(q['valid'] and q['solids']==1 for q in record['parts'])
  assert not record['unexpected_new_assembly_contacts']
  assert record['meta']['preload_nominal_force_N']==load['force_catalog_N']==552
  for c in record['motion_checks']:
   assert c['structural_hits']==0,c
   assert c['bearing_axis_alignment_max_mm']<1e-5
   for aid,deg in c['angles_deg'].items():
    lo,hi=limits[aid];assert lo-1e-8<=math.radians(deg)<=hi+1e-8
   assert len(c['hits'])==c['structural_hits']+c['pose_restriction_hits']
   if c['hits']:poses.append(f"| {name.title()} | {c['pose']} | {len(c['hits'])} |")
  free=sum(not c['hits'] for c in record['motion_checks'])
  total=len(record['motion_checks'])
  maxprint=max(max(q['bbox_mm']) for q in record['parts'] if q['material'] in ('frame','shell'))
  table.append(f"| {name.title()} | {len(record['parts'])} | {total}/{total} | {free}/{total} | {maxprint:.1f} |")
  peak=load['variants'][name]['peak'];torque=peak['modeled_plus_100g_wrist_any_gravity_Nm']
  need=load['variants'][name]['force_required_N_at_mu_0p15_margin_1p5']
  margin=load['friction_torque_estimate_Nm_by_assumed_mu']['0.15']/torque
  assert margin>=1.5
  minmu=1.5*torque/(load['force_catalog_N']*load['friction_effective_radius_mm']*.001)
  budget.append(f"| {name.title()} | {peak['moving_model_mass_g']:.1f} | {torque:.3f} | {need:.1f} | {margin:.2f} | {minmu:.3f} |")
  axes=[]
  for aid in p['axis_order']:
   prefix,key=aid.split('.')
   active=prefix.startswith(('clavicle_','upperarm_','elbow_'))
   holding='new_spring_face_clutch_candidate' if prefix.startswith('upperarm_') and key in ('flex','abduct') else 'inherited_incomplete_candidate' if active else 'not_integrated'
   sensor='girdle_envelope_only' if prefix.startswith('clavicle_') else 'elbow_transfer_envelope_only' if prefix.startswith('elbow_') else 'not_integrated'
   axes.append(dict(axis_id=aid,articulated=active,holding_status=holding,readout_status=sensor,manufacturing_released=False))
  assert sum(q['articulated'] for q in axes)==12
  assert sum(q['holding_status']=='new_spring_face_clutch_candidate' for q in axes)==4
  variants[name]=dict(source_profile=f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json',
   height_mm=p['design_reference']['mesh_N_pose_surface_height_mm'],parts=len(record['parts']),samples=total,
   no_local_structural_conflict_samples=total,collision_free_samples=free,pose_restriction_samples=total-free,
   unexpected_new_assembly_contacts=0,axes=axes,assumed_holding_margin_mu_0p15=margin,
   bearing_axis_error_mm=max(c['bearing_axis_alignment_max_mm'] for c in record['motion_checks']))
 save('mechanical_manifest/dual_character_mechanics_revI.json',dict(status='FOUR_SHOULDER_CLUTCHES_INTEGRATED_CANDIDATE',
  manufacturing_released=False,physical_tested=False,coverage_rule='Rigid segment shells; deforming regions exposed',
  collision_policy='Cross-arm contacts constrain poses; local, adjacent or unresolved contacts remain structural findings',
  variants=variants))
 files=['cad/collision_policy.py','cad/revH/shoulder_mechanism.py','cad/revG/centerline_study.py','tools/report_revI.py','tools/check_shoulder_browser.cjs']
 files += [str(p.relative_to(ROOT)).replace('\\','/') for p in (ROOT/'cad/revI').glob('*.py')]
 files += ['cad/revI/review.template.html']
 for name in ('manny','quinn'):files += [f'verification/revI_{name}.json',f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json',f'generated/revI/{name}/{name.title()}_shoulder_assembly.step']
 files+=['generated/revI/RevI_Shoulder_Review.html','verification/revI_viewer_geometry.json','tools/Build-RevI.ps1','docs/SHOULDER_REVI.zh-CN.md','verification/revI_clutch_component_check.json','verification/revI_tool_access.json','verification/revI_load_budget.json']
 browser=None
 browser_path=ROOT/'verification/revI_browser_check.json'
 if browser_path.exists():
  candidate=read('verification/revI_browser_check.json')
  if candidate.get('htmlSha256')==hashlib.sha256((ROOT/'generated/revI/RevI_Shoulder_Review.html').read_bytes()).hexdigest():
   browser=dict(path='verification/revI_browser_check.json',checked_cases=candidate['checked_cases'],runtime_errors=len(candidate['errors']))
 save('verification/revI_design_audit.json',dict(browser_verification=browser,source_and_output_snapshot_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files},
  all_original_axis_ids_preserved=True,all_registered_angles_within_original_limits=True,
  local_geometry_samples_clear=True,new_same_owner_assembly_checks_clear=True,
  assumptions_required_for_holding_margin=True,manufacturing_released=False,physical_tested=False))
 report="""# Rev I · 肩部持姿组件检查报告

状态：新增四套摩擦持姿机构的 CAD 集成候选，未制造放行、未实测。Manny / Quinn 保持 1:2 候选比例、各自关节中心和原 44 轴接口。

## 几何和装配

| 角色 | 实体与占位件 | 未发现局部结构冲突 | 同时无双臂相交 | 打印候选最大包围盒边 / mm |
|---|---:|---:|---:|---:|
"""+'\n'.join(table)+"""

两款共 72 个不同姿态：原 42 个组合动作，加上 30 个不重复的肩部单轴取样；包含屈伸 −50° / 160°、外展 −30° / 150°、扭转 ±90° 的端点。跨运动节段精确 BRep 相交体积阈值为 0.02 mm³。72 个均未发现局部结构冲突，其中 62 个没有任何登记的跨节段穿插，10 个有左右独立手臂的相交。

轴套实际 CAD 质心到 FK 轴线的偏差均小于 0.00001 mm，只验证坐标一致性，不能理解为加工精度。每款新增 64 个持姿零件，并替换 4 根旧轴；每款共 179 个有效单实体（包含历史占位件）。

本轮另逐对检查了新持姿零件与同一刚性节段的装配，未发现未解释的重叠。只豁免明确登记的 M3 螺钉与内螺纹简化包络，不豁免垫片、支架或轴套相交。两种独立组件还各检查了 24 个转角，全部无跨固定／转动件的超阈值交叠。两款的四套组件共 8 条内侧紧固件工具路径，在明确的分步装配状态下均无超阈值阻挡；详见 [工具通道检查](revI_tool_access.json)。

## 保留的摆姿限制

| 角色 | 姿态标识 | 左右手臂相交对数 |
|---|---|---:|
"""+'\n'.join(poses)+"""

这些姿态在查看页中为橙色。实际使用时需要避让；它们没有被删除、压小体积或更改为物理可达。关节内部、同侧相邻肢段及归属不明的相交仍按红色结构问题处理。原始姿态不会被自动改写到硬件输入或 UE。

## 持姿预算

假设已建打印实体全部为实心 PLA；金属按钢密度；轴套按 POM；未知摩擦片密度暂定。详细密度与遗漏项记录在 [预算 JSON](revI_load_budget.json)。每只手另外在腕位置保留 100 g 点质量；这不是实测手部重量。取各无相交样本在任意重力方向下的单轴上界，因此不局限于躯干竖直。

| 角色 | 最不利肩轴下游已建质量 / g | 加 100 g 腕载荷后的力矩 / N·m | μ=0.15、1.5 倍余量所需预紧 / N | 552 N、μ=0.15 的计算余量 | 达到 1.5 倍余量所需最低 μ |
|---|---:|---:|---:|---:|---:|
"""+'\n'.join(budget)+"""

当前碟簧候选为 SCHNORR 002 200，外径 12 mm、内径 6.2 mm、厚 0.6 mm；目录测试高度 0.688 mm 对应 552 N。两片反向串联，力不翻倍。来源：[厂家目录，第 11 页](https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf)。这个数值不保证装配后恰好产生 552 N。

单工作摩擦面的内／外半径 4.15 / 12.5 mm，采用均匀压力模型。μ 分别假设为 0.08、0.15、0.25 时的力矩见预算 JSON。μ=0.15 下约 0.747 N·m；μ 较低时不能满足这里的 1.5 倍余量。摩擦材料、启动和滑动阻力、预紧公差、磨损与手感必须由后续选材与实测确认。因此计算余量不是额定负载。

止推垫片采用 [SKF 目录第 37 页](https://cdn.skfmediahub.skf.com/api/public/0901d19680090e01/pdf_preview_medium/0901d19680090e01_pdf_preview_medium.pdf) PCMW 102001.5 E 的 10 × 20 × 1.5 mm 尺寸候选，需继续核对安装固定、表面和可获得性。

## 检查边界

- 只有肩带、肩部、双肘共 12 轴在当前局部总装中运动，其余 32 轴未在本总装集成。
- 未做连续扫掠、公差极限、打印收缩、变形、载荷强度或线束回弹验证；未包括完整头、胸廓表面、手腕、手和支架。
- 肩带／上臂扭转轴的预紧和轴端固定仍未完成；六路肩部测角尚未集成，四路肩带电路仍为占位。
- 新 D 形连接已有几何传力与轴向固定，但间隙、回差、打印接口长期压溃与防松方式尚待验证；不能据此宣称姿势保持精度。
- 预留件不计入结构通过统计。中立姿态仍有左右肘部两对名义齿轮外廓交叠，实际齿形与传动未完成。
- 包围盒尺寸仅说明有机会放入 A1 mini，未生成本轮打印放行包。

## 文件

- [Rev I 交互查看页](../generated/revI/RevI_Shoulder_Review.html)
- [Manny STEP](../generated/revI/manny/Manny_shoulder_assembly.step) · [Quinn STEP](../generated/revI/quinn/Quinn_shoulder_assembly.step)
- [Manny 检查 JSON](revI_manny.json) · [Quinn 检查 JSON](revI_quinn.json)
- [组件检查](revI_clutch_component_check.json) · [44 轴状态](../mechanical_manifest/dual_character_mechanics_revI.json)
- [结构说明](../docs/SHOULDER_REVI.zh-CN.md) · [源文件与输出快照](revI_design_audit.json)

运行 tools/Build-RevI.ps1 可重建本轮 CAD、检查、力矩预算、查看页及报告。现在不用打印、测量或采购。
"""
 (ROOT/'verification/REVI_REPORT.zh-CN.md').write_text(report,encoding='utf8')
 print(json.dumps({k:{x:v for x,v in q.items() if x!='axes'} for k,q in variants.items()}))
if __name__=='__main__':main()
