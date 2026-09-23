"""Summarize Rev G evidence; preserve the original Rev E profiles."""
from pathlib import Path
from copy import deepcopy
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def read(p): return json.loads((ROOT/p).read_text(encoding='utf8'))
def write_json(p,data): (ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 arm=read('verification/revG_centreline_arm.json')
 shoulder=read('verification/revG_shoulder_motion.json')
 env=read('verification/revG_surface_envelopes.json')
 dimensions=[]; motions=[]; shell_rows=[]; invariants={}; failed=[]
 for name in ('manny','quinn'):
  old=read(f'mechanical_manifest/physical_{name}_44_revE_proportion.json')
  new=deepcopy(old);new['profile_id']=f'physical_{name}_44_revG_humanform_trial'
  new['status']='HUMAN_FORM_HALF_SCALE_TRIAL_NOT_MANUFACTURING_RELEASE'
  new['notes_zh']=['沿用对应角色比例及44轴定义，按1:2试算。','约90.8cm为人形封装候选，不是已经冻结的整机高度。','稳定节段包壳，活动与形变区裸露；肩带及全身机构尚未完成。']
  for n in new['nodes']:
   for f in ('parent_to_axis','axis_to_child'):
    n[f]['translation_m']=[x*1.5 for x in n[f]['translation_m']]
  d=new['design_reference'];d['scale']=.5
  d['mesh_N_pose_surface_height_mm']*=1.5
  d['neutral_floor_shift_mm']=[x*1.5 for x in d['neutral_floor_shift_mm']]
  axis_old=[n['axis_id'] for n in old['nodes'] if n['kind']=='revolute']
  axis_new=[n['axis_id'] for n in new['nodes'] if n['kind']=='revolute']
  assert axis_old==axis_new and len(axis_new)==44
  for a,b in zip(old['nodes'],new['nodes']):
   expected=deepcopy(a)
   for f in ('parent_to_axis','axis_to_child'):
    expected[f]['translation_m']=[x*1.5 for x in a[f]['translation_m']]
   assert b==expected
  invariants[name]={'axis_count':44,'axis_ids_order_unchanged':True,'node_changes_only_uniform_translation_scale':True,'translation_factor':1.5}
  write_json(f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json',new)
  e=env['characters'][name]
  for section in ('elbow_section','wrist_section'): assert e[section]['centre_inside_all_ray_parities']
  for scale in env['candidates']:
   f=scale/(1/3)
   dimensions.append(f"| {name.title()} | {scale:.3f} | {old['design_reference']['mesh_N_pose_surface_height_mm']*f/10:.1f} | {e['elbow_section']['width_y_mm']*f:.1f} × {e['elbow_section']['depth_x_mm']*f:.1f} | {e['wrist_section']['width_y_mm']*f:.1f} × {e['wrist_section']['depth_x_mm']*f:.1f} |")
  for row in shoulder['characters'][name]['poses']:
   if row['pose'] in ('forward','shrug','forward_up'):
    s=row['shoulders']['l'];x,y,z=s['delta_mm']
    motions.append(f"| {name.title()} | {row['label']} | {x:.1f} | {y:.1f} | {z:.1f} | {s['travel_mm']:.1f} |")
  a=arm['characters'][name]
  assert all(p['valid'] for p in a['parts'])
  assert all(s['one_solid'] for s in a['meta']['shells'])
  assert not a['neutral_shell_intersections_including_reservations']
  for s in a['meta']['shells']:
   shell_rows.append(f"| {name.title()} | {s['name']} | {' × '.join(f'{v:.1f}' for v in s['bbox_mm'])} | 单实体 |")
  for row in a['motion_samples']:
   if row['hits']:
    for h in row['hits']:failed.append(f"| {name.title()} | {row['elbow_deg']} | {h['a']} / {h['b']} | {h['intersection_mm3']:.1f} |")
 passed=sum(not row['hits'] for ch in arm['characters'].values() for row in ch['motion_samples'])
 inputs=list((ROOT/'cad/revG').glob('*'))
 inputs += [ROOT/p for p in ('verification/revG_surface_envelopes.json','verification/revG_centreline_arm.json','verification/revG_shoulder_motion.json','tools/report_revG.py','mechanical_manifest/shell_coverage_revG.json')]
 hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs if p.is_file()}
 write_json('verification/revG_profile_and_source_audit.json',{'manufacturing_released':False,'physical_tested':False,'profile_checks':invariants,'source_sha256':hashes})
 failure_section=('| 角色 | 弯肘 / ° | 相交壳片 | 交叠体积 / mm³ |\n|---|---:|---|---:|\n'+'\n'.join(failed)) if failed else '这些指定样本均未发现超过检查阈值的跨节段实体交叠。'
 report="""# Rev G · 分段硬壳与裸露活动区检查

状态：可行性研究。没有制造放行，没有实物测试。按用户最新决定，稳定节段包壳，活动与形变区保持裸露，不把软皮或关节护套作为后续必做项。

本轮采用“稳定节段分段硬壳、运动与形变区直接裸露”的外形规则，保留握持主体与人形比例。分区约束见 [壳体覆盖规则](../mechanical_manifest/shell_coverage_revG.json)。约 90.8 cm、1:2 是空间研究候选，原 Rev E 的 1:3 参数保留；尚未决定最终整机尺寸。

## 肩带是否支持造成体表变化的动作

44 轴运动树的每侧肩带包含前伸／后收、抬高／下压两轴，后续肩部与整条手臂随之运动。旧 Rev C 有概念框架；当前尺寸下的实体肩带未完成。下面验证的是运动树的肩中心位置，不是已完成实体机构的动作能力。

1:2 试算，左肩相对自然姿态；+X 向前，+Y 向左，+Z 向上。前伸为 30°、耸肩为 30°。

| 角色 | 姿态 | ΔX / mm | ΔY / mm | ΔZ / mm | 两姿态直线距离 / mm |
|---|---|---:|---:|---:|---:|
"""+'\n'.join(motions)+"""

前伸／后收和抬降各自还计算了 −20°、−15° 的反向边界，以及左右不对称的组合；共两款各 7 个姿态。数据在 [肩带运动 JSON](revG_shoulder_motion.json)。

[交互查看页](../generated/revG/Human_Form_and_Shoulder_Review.html) 的形变来自 UE 参考网格蒙皮，不能当成 TPU／硅胶的物理仿真。页面中的参考点仅说明肩带相对胸部的运动，不能视为实际外壳固定点。当前肩带、肩胛活动区和腋下保持裸露，不设置软连接或浮动肩盖。完整体表只是比例与动作参考，不是覆盖方案。

## 截面与尺寸选择

从本地项目的 Manny / Quinn Simple 网格和骨架读取，保持各自的比例。表中是自然姿态人体表面的左右宽 × 前后厚，尚未扣掉壳厚、装配间隙和线束空间。

| 角色 | 相对 UE 尺度 | 身高 / cm | 肘截面 / mm | 腕截面 / mm |
|---|---:|---:|---:|---:|
"""+'\n'.join(dimensions)+"""

肘和腕截面的 72 条径向射线均通过本轮中心内外奇偶检查。肩根、髋根和部分上臂截面因按蒙皮权重切分而不闭合，不能据此宣称整个机构已装进角色体表。较大尺寸改善空间，但手腕、肩带根部仍是难点。

## 已生成的局部 CAD

两款各有中线臂架、肘轴系概念和 4 片开放式臂壳。传感器沿上臂安排，减少在肘轴侧面的堆叠。绿色电路板、琥珀色传动件和弹簧等部分只是空间预留：没有完成 PCB 布线、齿形、啮合公差、间隙校准、预紧导向或完整固定方式。

壳片由人体截面包围框拟合的椭圆放样生成，截面半轴额外增加 0.8 mm；名义半轴壁差为 1.8 mm，不代表各处法向厚度已经核实。Manny 靠近肩的一个截面不闭合，仅用于轮廓近似。当前壳形不等于精准贴合 UE 表面，不具备全表面包络证明。

- [Manny 臂架与壳片 STEP](../generated/revG/step/manny/Manny_centreline_shell_study.step)
- [Quinn 臂架与壳片 STEP](../generated/revG/step/quinn/Quinn_centreline_shell_study.step)
- [Quinn 局部剖视图](../generated/revG/images/quinn_cutaway_arm.png)
- [空间与穿插明细](revG_centreline_arm.json)

八片臂壳均为有效单实体。这里只核对 CAD 包围盒是否具备 A1 mini 分件空间，尚未做切片、支撑、搭接装配和打印检验。整机长肢段需要另行分件。

| 角色 | 壳片 | 包围盒 / mm | 实体 |
|---|---|---|---|
"""+'\n'.join(shell_rows)+"""

## 运动采样结果与未通过项

两款各采样 0、30、60、90、110、120、130、145° 弯肘。共 16 个样本，其中 """+str(passed)+""" 个在规定检查范围内未发现超过 0.02 mm³ 阈值的交叠。

"""+failure_section+"""

此前版本在 145° 有硬壳干涉。本轮继续收退肘窝两侧壳边，让活动区裸露：两侧让位面的局部斜率为 2.5，轴向截距为 24 mm，具体定义见 CAD 源码。没有缩小原 145° 动作目标，也不需要添加软皮填补开口。当前只有肘轴参与运动，不能把结果写成完整手臂或全身通过。

检查范围：运动时比较属于上臂、前臂两组的非预留实体；自然姿态额外比较壳片与全部内部件／预留空间。两款自然姿态均未发现超过阈值的壳片交叠。未覆盖同组内部装配、预留传动件的实际运动、连续扫掠、制造公差、装配间隙、受力变形及尚未完成的走线。无体积交叠不等于有足够的实际间隙。

## 参数与复现

新增两款 Rev G 试算配置：只把 Rev E 运动树的长度统一乘以 1.5，44 个轴的 ID、顺序、轴向、连接关系与旋转参数均不变。检查记录见 [参数与源文件审计](revG_profile_and_source_audit.json)。这些配置没有替换已使用的 UE／模拟器配置。

依次运行 tools/Build-RevG.ps1 可重建截面分析、局部臂壳、肩带查看页及本报告；依赖已安装的 CQ-editor 运行时。原始网格数据来自 reference/ue58，比例来源是 Rev E。此前极端颈部位置误差和 Quinn 的独立 UE 适配尚未解决。

实体肩带及其他 43 轴集成、全身壳体、完整传动与电路、限位、线束、质量、持姿、操作力、支架及裸露区域的边缘处理均未完成。当前无需打印、测量或采购。

[分段硬壳与裸露活动区设计说明](../docs/HUMAN_FORM_REVG.zh-CN.md)记录当前覆盖边界与结构决策。不能把本报告当作整机可制造或材料已验证的证明。
"""
 (ROOT/'verification/REVG_REPORT.zh-CN.md').write_text(report,encoding='utf8')
 print(json.dumps({'profiles':invariants,'sampled_passes_in_limited_scope':passed,'reported_collision_pairs':len(failed),'manufacturing_released':False},ensure_ascii=False))
if __name__=='__main__':main()
