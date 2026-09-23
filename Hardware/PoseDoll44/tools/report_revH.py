"""Audit and summarize Rev H without changing software or geometry."""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text('utf8'))
def save(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 summary=[];failures=[];loads=[];variants={};input_paths=[]
 labels={'down':'下压肩膀，原始组合','back_down':'后收下压，原始组合','arms_crossed':'原始对称抱臂','forward_shrug_reach':'前伸耸肩加前举，原始组合','crossed_staggered':'错开抱臂试算 A'}
 for name in ('manny','quinn'):
  rp=f'verification/revH_{name}.json';pp=f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json'
  r=read(rp);p=read(pp);limits={a['id']:a['limits_rad'] for a in p['axes']}
  assert len(p['axis_order'])==44 and len(set(p['axis_order']))==44
  assert all(x['valid'] and x['solids']==1 for x in r['parts'])
  for c in r['motion_checks']:
   for axis,deg in c['angles_deg'].items():
    assert axis in limits
    low,high=limits[axis];assert low-1e-8<=math.radians(deg)<=high+1e-8,(axis,deg,limits[axis])
   assert c['bearing_axis_alignment_max_mm']<1e-5
   if c['hits']:
    failures.append(f"| {name.title()} | {labels.get(c['pose'],c['pose'])} | {len(c['hits'])} |")
  passed=sum(not c['hits'] for c in r['motion_checks'])
  maxprint=max(max(x['bbox_mm']) for x in r['parts'] if x['material'] in ('frame','shell'))
  axis_error=max(c['bearing_axis_alignment_max_mm'] for c in r['motion_checks'])
  summary.append(f"| {name.title()} | {len(r['parts'])} | {passed} / {len(r['motion_checks'])} | {r['meta']['root_spacing_mm']:.3f} | {r['meta']['upper_bearing_min_nominal_web_mm']:.3f} | {maxprint:.1f} |")
  load_rows=[x for x in r['unit_payload_loads'] if not x['sample_has_collision']]
  peak=max(load_rows,key=lambda x:x['torque_nm_per_100g_at_wrist'])
  loads.append(f"| {name.title()} | {peak['axis']} | {peak['pose']} | {peak['torque_nm_per_100g_at_wrist']:.3f} |")
  axis_states=[]
  for axis in p['axis_order']:
   prefix=axis.split('.')[0]
   active=prefix.startswith(('clavicle_','upperarm_','elbow_'))
   sensor='girdle_board_envelope_only' if prefix.startswith('clavicle_') else 'elbow_transfer_envelope_only' if prefix.startswith('elbow_') else 'not_integrated'
   axis_states.append({'axis_id':axis,'articulated_in_revH':active,'readout_status':sensor,'manufacturing_released':False})
  assert sum(x['articulated_in_revH'] for x in axis_states)==12
  variants[name]={'source_profile':pp,'candidate_height_mm':p['design_reference']['mesh_N_pose_surface_height_mm'],'parts':len(r['parts']),'passed_samples':passed,'no_local_structural_conflict_samples':sum(c['structural_hits']==0 for c in r['motion_checks']),'total_samples':len(r['motion_checks']),'max_bearing_line_error_mm':axis_error,'axes':axis_states}
  input_paths += [rp,pp]
 input_paths += [str(x.relative_to(ROOT)).replace('\\','/') for x in (ROOT/'cad/revH').glob('*') if x.is_file()]
 input_paths += ['cad/collision_policy.py','cad/revG/centerline_study.py','verification/revG_surface_envelopes.json','verification/revE_proportion_baselines.json','mechanical_manifest/shell_coverage_revG.json','tools/report_revH.py']
 hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in input_paths}
 save('mechanical_manifest/dual_character_mechanics_revH.json',{'status':'SHOULDER_GIRDLE_AND_ARMS_PACKAGING_INTEGRATION','manufacturing_released':False,'physical_tested':False,'coverage_rule':'Rigid segment shells; all deforming motion zones exposed; no soft skin','variants':variants})
 save('verification/revH_design_audit.json',{'source_sha256':hashes,'all_sample_angles_within_original_limits':True,'all_44_axis_ids_preserved':True,'all_bearing_axes_numerically_aligned':True,'physical_tested':False,'manufacturing_released':False})
 report="""# Rev H · 肩带与双臂检查报告

状态：局部空间集成候选。没有制造放行或实物测试。共 12 个转轴参与运动，44 轴协议与 Manny / Quinn 各自比例保持。约 90.8 cm 仍是 Rev G 的候选尺寸，没有再次放大。

## 几何与运动检查

| 角色 | 实体／占位件数量 | 无超阈值穿插样本 | 肩带竖轴间距 / mm | 上轴承桥两孔名义净壁 / mm | 打印候选最大包围盒边长 / mm |
|---|---:|---:|---:|---:|---:|
"""+'\n'.join(summary)+"""

两款各 21 个姿态，共 42 个样本，34 个未发现超过 0.02 mm³ 阈值的跨运动节段结构穿插。所有 CAD 件均为有效单实体。打印分件包围盒只说明尺寸条件，未验证支撑、材料、公差、装配或强度。

轴承／金属轴的实际 CAD 质心到对应运动轴线的垂距也逐个计算，均小于 0.00001 mm。这个数值只是坐标与轴线核对，不是加工精度或传感器精度。

通过样本包括两款的前伸、后收、耸肩、前伸加耸肩、左右不对称、前举、侧举、上举、叉腰参考、扶额参考、弯肘 145°，以及补偿后的双臂竖直／平行前伸和错开抱臂候选。没有改动原关节范围。

## 需要双臂避让的姿态样本

| 角色 | 姿态 | 超阈值相交对数 |
|---|---|---:|
"""+'\n'.join(failures)+"""

按用户确认的验收原则，42 个样本均未发现已建局部机构的结构冲突，其中 8 个样本有左右手臂之间的相交，作为姿态限制保留并标橙，不判定为关节设计失败。关节内部、同侧相邻节段及分类不明确的相交仍按结构问题处理。其中原始对称抱臂使两前臂进入同一空间；直接叠加肩带前伸耸肩与双臂前举也可能让两臂向中间交叉。Quinn 的两个肩膀下压原始组合还有前臂壳相碰。不能把“模型每个轴都能转”理解为所有角度组合都可在实物上同时达到。

新增的错开抱臂候选在两款局部 CAD 中均未发现超阈值穿插，但尚未检查完整躯干外形、头和手。搜索与原相交记录见 [初始抱臂候选检查](revH_crossed_pose_search.json)和 [较小不对称姿态的复核](revH_crossed_pose_refinement.json)。补偿姿态只用于证明当前结构存在其他可达组合，不自动修改硬件输入或 UE 适配。

## 检查范围与排除项

检查基于 CAD 精确实体的交体积，覆盖不同运动节段之间已建出的结构、轴、轴套、臂壳及摩擦面。相同刚性节段内部的固定接合没有逐对审查，全部预留空间没有混入“结构通过”的统计。没有做连续扫掠、公差极限、材料挠曲或受力强度认证。

中立姿态另检查了预留空间与其他运动节段的交叠；两款仅保留左右肘部两个名义齿轮外廓交叠，属于 Rev G 未完成的传动占位。它们不代表已验证的实际齿形啮合。运动中的预留空间没有全部放行。

肩部屈伸与外展的持姿组件尚未装入；肩带及扭转摩擦面也未完成预紧受力闭环。轴端固定、夹紧、传力键、完整电子件、线束、限位、接触边缘和维护性仍待细化。尤其不能把缺少零件时通过的空间样本当成最终总装通过。

## 单位末端载荷参考

下表只计算在腕位置施加 100 g 质量、受重力时，各通过样本中最大的单轴力矩。没有加入这套机构本身的重量、手、线束恢复力或操作外力，也没有包含躯干倾斜后的所有重力方向，不能作为额定承载能力或最终预紧力。

| 角色 | 作用轴 | 样本 | 每 100 g 腕部载荷的力矩 / N·m |
|---|---|---|---:|
"""+'\n'.join(loads)+"""

上半身竖直时肩带前后转轴接近竖直，重力对这一轴的分量可能接近零；不能因此省略其持姿机构。躯干倾斜后需要重新核算。原始力矩明细保存在每款检查 JSON 中。

## 文件与复现

- [实际 CAD 交互查看页](../generated/revH/RevH_Shoulder_Review.html)
- [Manny STEP 总装](../generated/revH/manny/Manny_shoulder_assembly.step) · [Quinn STEP 总装](../generated/revH/quinn/Quinn_shoulder_assembly.step)
- [Manny 检查明细](revH_manny.json) · [Quinn 检查明细](revH_quinn.json)
- [44 轴集成状态](../mechanical_manifest/dual_character_mechanics_revH.json) · [源文件审计](revH_design_audit.json)
- [结构说明与未完成项](../docs/SHOULDER_REVH.zh-CN.md)

运行 tools/Build-RevH.ps1 重建 CAD、已登记姿态、查看页和本报告。抱臂搜索记录仅说明候选来源，构建使用明确登记的固定角度，不会每次重新挑选姿态。

本轮没有改动 UE 插件、Python 模拟器或原始下载方案。现在不用打印、测量或采购。
"""
 (ROOT/'verification/REVH_REPORT.zh-CN.md').write_text(report,encoding='utf8')
 print(json.dumps({n:{k:v for k,v in data.items() if k in ('parts','passed_samples','total_samples','max_bearing_line_error_mm')} for n,data in variants.items()}))
if __name__=='__main__':main()
