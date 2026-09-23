"""Generate the Rev E review documents and machine-readable design registry."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def write(p,t):(ROOT/p).write_text(t.rstrip()+'\n',encoding='utf8')
def save(p,v):write(p,json.dumps(v,ensure_ascii=False,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 b=read('verification/revE_proportion_baselines.json')['characters'];k=read('verification/revE_kinematic_comparison.json')['characters'];g=read('verification/revE_layout_geometry.json')['characters']
 measurements={n:v['measurements_mm'] for n,v in b.items()}
 rows=[('中立脚底至头顶','neutral_surface_height'),('上臂：肩中心→肘中心','upperarm_l'),('前臂：肘中心→腕中心','forearm_l'),('手腕→指端参考点','hand_wrist_to_tip_l'),('肩→肘→腕→指端的分段长度之和','shoulder_to_fingertip_l'),('大腿：髋中心→膝中心','thigh_l'),('小腿：膝中心→踝中心','shin_l'),('左右肩中心间距','shoulder_span'),('左右髋中心间距','hip_span'),('骨盆→肩中心的竖直高度','pelvis_to_shoulder_height'),('头部参考宽度','head_width'),('头部参考高度','head_height'),('脚部参考长度','foot_length_l'),('脚部参考宽度','foot_width_l')]
 table='| 项目（mm） | Manny | Quinn |\n|---|---:|---:|\n'+'\n'.join(f'| {label} | {measurements["manny"][key]:.1f} | {measurements["quinn"][key]:.1f} |' for label,key in rows)
 cases={n:max(v['poses'],key=lambda x:x['max_error_mm']) for n,v in k.items()}
 wrists={n:max(v['worst_by_landmark'][a]['error_mm'] for a in ('hand_l','hand_r')) for n,v in k.items()}
 registry={'revision':'RevE_Manny_Quinn_proportions','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'NEUTRAL_PROPORTIONS_ALIGNED_MECHANICAL_INTEGRATION_PENDING','common_scale':1/3,'source_engine':'5.8.2','units':'mm except protocol translations in m','canonical_geometry_source':'each SkeletalMesh GetRefSkeleton plus its own skinned reference geometry','axis_count':44,'protocol_axis_order_changed':False,'manufacturing_release':False,'physical_validation':'not_run','user_testing_required_now':False,'existing_simulator_and_UE_plugin_modified':False,'characters':{}}
 for name in ('manny','quinn'):
  profile=ROOT/'mechanical_manifest'/f'physical_{name}_44_revE_proportion.json'
  asset=REPO/'Content/Characters/Mannequins/Meshes'/f'SKM_{name.title()}_Simple.uasset'
  registry['characters'][name]={'mesh':b[name]['mesh'],'source_uasset_sha256_at_packaging':sha(asset),'profile':str(profile.relative_to(ROOT)).replace('\\','/'),'profile_sha256':sha(profile),'neutral_proportion_gate_passed':k[name]['neutral_proportion_gate_passed'],'dynamic_position_gate_passed':k[name]['position_gate_passed'],'maximum_sampled_head_error_mm':k[name]['worst_by_landmark']['head']['error_mm'],'maximum_sampled_wrist_error_mm':wrists[name],'new_physical_profile_UE_validated':False,'target_adapter_preexisting_validation':name=='manny','reference_cad':g[name]['step'].replace('\\','/'),'measurements_mm':measurements[name]}
 registry['required_next_steps']=['Integrate bearings, friction, encoders and wiring around corrected joint centres; complete a collision-checked assembly for each variant.','Resolve distributed-neck positional mismatch without silently relaxing the 1% stature target.','Build and validate Quinn-specific mesh/reference/Control Rig adaptation separately from Manny.','Recalculate variant masses, centres of gravity and holding torque with real assembly parts.','Complete stand, regional electronics, wiring, limits, assembly drawings and physical acceptance.']
 save('mechanical_manifest/dual_character_design_revE.json',registry)
 constraints=read('mechanical_manifest/proportion_constraints_revD.json');constraints.update({'revision':'RevE_dual_character_requirement','status':'NEUTRAL_PROPORTION_PASS_DYNAMIC_AND_MECHANICAL_PENDING','target_meshes':{n:b[n]['mesh'] for n in b},'selected_scale':1/3,'body_height_mm_by_character':{n:measurements[n]['neutral_surface_height'] for n in b},'user_requirement':'Manny 和 Quinn 两款人偶分别保持与对应 UE 角色一致的体格比例，摆姿势尽量所见即所得。','supersedes':'proportion_constraints_revD.json'})
 for key in ('target_mesh','body_height_mm'):constraints.pop(key,None)
 constraints['policies'].append('Quinn must use her own mesh reference lengths, never Manny lengths copied from the shared Control Rig.')
 save('mechanical_manifest/proportion_constraints_revE.json',constraints)
 write('docs/MANNY_QUINN_DESIGN.zh-CN.md',f'''# Manny / Quinn 双角色比例设计 · Rev E

两款都以本地项目中的实际角色为依据，统一缩小至 **1:3**。当前交付是两套已纠正比例的 44 轴运动设计基准、STEP 参考布局和外形对照模型；承力、摩擦、传感器等机构仍需围绕这些基准完成集成。

[打开可旋转的 3D 比较页](../generated/revE/Manny_Quinn_3D_Review.html) · [当前工程入口](../START_HERE.zh-CN.md) · [验证报告](../verification/REVE_REPORT.zh-CN.md)

![Manny 与 Quinn 的比例对照](../generated/revE/images/Manny_Quinn_proportion_front.png)

## 尺寸以什么为准

Manny 使用 `/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple`，Quinn 使用同目录的 `SKM_Quinn_Simple`。提取对象是各自网格的参考骨架和蒙皮数据，避免共享 Skeleton / Control Rig 的默认尺寸覆盖角色实际差异。测量时转换到与既有姿势适配器一致的 N 中立姿势，保持每根骨骼长度，以实际参考表面最低点为地面，再应用统一缩放。

1:3 是当前设计选定值；两款中立高度均约 605 mm，不含支架和突出电子件。原来的约 500 mm 仅为探索目标。本次优先保留实际身体比例，后续机构尺寸不足时需重新设计机构或整体缩放，不能单独拉长手臂、撑宽肩膀。

{table}

表中四肢取左侧；源文件保留左右原始数值。头、手、脚区域由顶点的主要骨骼权重分组，指端使用参考手型下最末端的网格点。肩到指端一行是分段长度之和，不是所有姿势下的直线距离。手指不在 44 路输入内，实体握持件尚未设计。

Manny 的肩到腕分段长度/身高约 **{(measurements['manny']['upperarm_l']+measurements['manny']['forearm_l'])/measurements['manny']['neutral_surface_height']:.3f}**；Quinn 约 **{(measurements['quinn']['upperarm_l']+measurements['quinn']['forearm_l'])/measurements['quinn']['neutral_surface_height']:.3f}**。这些来自各自角色，不能用一套固定臂长替换。

## 机械设计如何服从比例

肩部三个轴以实际肩关节中心为交点，髋部同理；手腕、脚踝的两个轴也以对应中心为交点。旧 Rev C 肩部两个轴相隔 56 mm 的结构不能直接沿用。前臂旋转轴放在肘腕连线上，不额外增加前臂长度。

腰部、胸部和颈部目前使用等效转动中心表示 UE 的多骨骼运动。中立姿势标志点已对齐，但颈部动态位置仍有误差，详见验证报告。当前共心颈部方案没有获得动态设计放行；不得为了让检查通过而缩小已承诺的关节角度范围或放宽阈值。

下列原则已经落实到两份物理参数文件：44 个轴 ID、顺序、方向及协议保持一致；人物尺寸、关节位置、参考表面和独立 profile_id 分别保存。已有 `virtual_humanoid_44_v1`、模拟器和 UE 插件没有为了适应机械件而被修改。

| 组成部分 | 双版本处理方式 |
|---|---|
| 角度传感器板、电气接口、44 轴协议 | 共用已设计的接口，整机安装仍须验证 |
| 持姿关节的基本结构 | 尽量共用；规格需按每款最终质量与力臂选型 |
| 上臂、前臂、大腿、小腿的结构长度 | 分别取各自角色尺寸 |
| 肩带、骨盆和躯干连接结构 | 按不同肩宽、髋宽、躯干长度分别设计 |
| 头、手、脚及握持外壳 | 各自参考角色外形，后续转换为可装配结构 |
| 校准、实体设备配置、UE 目标角色配置 | 两款独立绑定，不能只依据“同为 44 轴”混用 |

## 文件与使用

- [Manny STEP 关节布局](../generated/revE/manny/Manny_44_proportion_layout.step) / [Manny 参数](../mechanical_manifest/physical_manny_44_revE_proportion.json)
- [Quinn STEP 关节布局](../generated/revE/quinn/Quinn_44_proportion_layout.step) / [Quinn 参数](../mechanical_manifest/physical_quinn_44_revE_proportion.json)
- [CQ-editor 入口](../cad/revE/open_in_cq_editor.py)：`CHARACTER` 选 `BOTH`、`MANNY` 或 `QUINN`，`POSE` 选已有样本。
- [两款设计登记表](../mechanical_manifest/dual_character_design_revE.json) / [比例约束](../mechanical_manifest/proportion_constraints_revE.json)
- [重建方法](BUILD_REVE.zh-CN.md) / [Quinn 适配待办](QUINN_ADAPTER_HANDOFF.zh-CN.md)

STEP 中的杆、点和轴线都是设计参考几何，不是实际轴、轴承或连接件。PLY/NPZ/网页中的身体表面是 UE 角色的比例参照，不是可打印外壳。Rev C / Rev D 的旧关节研究件继续保留，但不得直接作为新比例的全身总装。

后续继续按 A1 mini、0.4 mm 喷嘴、PLA 做分件设计。当前不用打印试片、测量或采购；各零件是否适合打印空间，要在实际零件完成后逐件检查。
''')
 report=f'''# Rev E 双角色比例与运动检查

## 当前结论

**Manny、Quinn 两款的中立比例基准已建立并通过数字检查；动态一致性与机械制造均未放行。**

| 检查 | Manny | Quinn |
|---|---:|---:|
| 44 轴 ID、顺序、轴定义、父子链保持不变 | 通过 | 通过 |
| 主要肢体长度、肩宽、髋宽，相对误差 ≤ 1% | 通过 | 通过 |
| 中立骨骼标志点误差 ≤ 身高 0.5% | 通过 | 通过 |
| 14 组多轴目标中心 | 组内间距为 0 | 组内间距为 0 |
| 参考 STEP 几何有效性 | {g['manny']['entity_count']} 个有效参考实体 | {g['quinn']['entity_count']} 个有效参考实体 |
| 独立运动比较 | {k['manny']['sample_count']} 个样本 | {k['quinn']['sample_count']} 个样本 |
| 最大手腕位置误差 | {wrists['manny']:.3f} mm | {wrists['quinn']:.3f} mm |
| 最大头部位置误差 | {cases['manny']['max_error_mm']:.3f} mm | {cases['quinn']['max_error_mm']:.3f} mm |
| 动态位置目标：身高的 1% | ≤ {k['manny']['digital_position_target_mm']:.3f} mm，未通过 | ≤ {k['quinn']['digital_position_target_mm']:.3f} mm，未通过 |
| 该角色既有 UE 适配 | 5 组已有引擎结果用于交叉核对 | 尚未完成 |
| 新实体配置在 UE 中验收 | 未运行 | 未运行 |
| 实际装配/持姿/测角/寿命测试 | 未运行 | 未运行 |

数字模型的长度误差接近浮点运算精度，只说明参数一致，不代表打印或装配能达到同样精度。

## 为什么颈部没有通过

最大误差发生在头部 yaw=75°、pitch=55°、roll=35° 同时达到上限时。当前人偶以一个共心三轴关节转动头部；UE 分别转动 neck_01、neck_02、head，头部的位置轨迹因此不同。Manny 偏差约 {cases['manny']['max_error_mm']:.2f} mm，Quinn 约 {cases['quinn']['max_error_mm']:.2f} mm。四肢比例已经纠正，颈部仍需机构和目标适配联合设计。

进行了两种枢轴调整研究：移动单个共心枢轴，以及分别移动颈部三轴。后一方案在拟合姿势中误差较小，但在未参与拟合的极端姿势中仍失败，因此**没有应用到正式参数**。不得把拟合样本通过当作全范围通过。

[单枢轴研究](revE_neck_pivot_study.json) · [分轴研究](revE_distributed_neck_pivot_study.json)

## 检查方法和适用范围

每款有 232 个设计样本（16 个命名姿势、88 个单轴端点、128 个随机组合），另有 855 个独立样本（不同随机种子的 512 个组合及 7×7×7 的颈部网格）。每个样本用物理参数做正向运动学，再与角色自己的中立骨长及 UE 的旋转分配规则比较，不是只从同一张 CAD 图上重复量尺寸。

Manny 的预测模型另与仓库保存的 5 组实际 UE 骨骼结果交叉核对，最大差异约 0.000012 mm。这证明当前坐标转换和骨链推导与那些已有样本一致；本轮没有重新执行真实 Control Rig 采集与关键帧写入验收。

Quinn 的预测使用她自己的网格骨长；当前导出的共享 Control Rig 初始骨架与她的网格参考骨架最大相差约 17.90 mm（1:3 尺度）。因此 Quinn 的离线比较不能代替她在 UE 中的验收。需要独立适配、指纹和 N 姿势校准。

双手靠拢与手到额头样本已经按参考表面的指定指端点求解到达；这只证明点可达，不证明整个手掌贴合、不穿插、能操作或站得稳。全身零件干涉、握持外形、地面接触及固定支架还要在实际机构模型中检查。随机角度组合也不等于全部可实现的动作范围。

## 提取与出处

参考数据来自当前本地 UE 5.8.2 项目：每款 89 根网格参考骨骼，Manny 46,098 个顶点 / 92,178 个三角形，Quinn 43,761 个顶点 / 87,280 个三角形。使用 GeometryScript 从临时 DynamicMesh 读取几何及权重，不保存或改写角色资产。网页仅使用减面后的显示数据；所有尺寸和运动计算使用完整源数据。

提取使用独立无界面 UE 进程；早期 FBX 导出在 NullRHI 下失败，正式结果来自后续 GeometryScript 路径。该进程完成两套 JSON 后，因项目已有的 GameFeatures AssetManager 错误返回 1；因此记录的是“提取文件完整且读取成功”，不是“命令行项目检查全部成功”。相关输出保留在 `reference_export_ue.log` 和 `reference_export_console.log`。

- [原始提取登记](../reference/ue58/extraction.json)
- [两款尺寸与来源哈希](revE_proportion_baselines.json)
- [全部角度和误差明细](revE_kinematic_comparison.json)
- [CAD 参考实体登记](revE_layout_geometry.json)
- [数字设计登记表](../mechanical_manifest/dual_character_design_revE.json)

## 下一阶段

围绕正确的肩、髋等中心重做承力叉架与共心结构，集成摩擦组件、传感器和走线；解决颈部运动差异；为 Quinn 做独立 UE 适配；用两款完整装配重新计算质量、保持扭矩和支架负荷，再生成最终装配与打印包。旧 Rev C 全身比例已经被替代，旧关节研究与电路成果仍可继续使用。
'''
 write('verification/REVE_REPORT.zh-CN.md',report)
 write('generated/revE/README.zh-CN.md','''# Rev E 输出目录

这里是 Manny / Quinn 两套等比例关节布局及角色参考表面。

[可旋转 3D 比较页](Manny_Quinn_3D_Review.html) · [设计说明](../../docs/MANNY_QUINN_DESIGN.zh-CN.md) · [检查报告](../../verification/REVE_REPORT.zh-CN.md)

STEP 是关节中心和连线参考模型；PLY、NPZ、图片与网页表面用于尺寸和姿势对照。制造零件、支架、摩擦与测角机构仍须集成，未提供整机打印放行。
''')
 write('START_HERE.zh-CN.md',f'''# PoseDoll 44 · Manny / Quinn 双角色设计

当前按项目内的实际 Manny、Quinn 建立了两套 **1:3 比例、约 60.5 cm 高**的人偶设计基准。四肢长度、肩宽、髋宽、躯干、头、手和脚分别取自对应角色，旧 Rev C 的全身比例已被替代。

**先打开 [可旋转的 3D 比较页](generated/revE/Manny_Quinn_3D_Review.html)**。可以并排查看、切换角色、旋转、缩放并点击关节中心。

![双角色比例与轴中心](generated/revE/images/Manny_Quinn_proportion_front.png)

[双角色设计说明和尺寸表](docs/MANNY_QUINN_DESIGN.zh-CN.md) · [完整检查报告](verification/REVE_REPORT.zh-CN.md)

| 当前尺寸（mm） | Manny | Quinn |
|---|---:|---:|
| 中立参考高度 | {measurements['manny']['neutral_surface_height']:.1f} | {measurements['quinn']['neutral_surface_height']:.1f} |
| 上臂 / 前臂 | {measurements['manny']['upperarm_l']:.1f} / {measurements['manny']['forearm_l']:.1f} | {measurements['quinn']['upperarm_l']:.1f} / {measurements['quinn']['forearm_l']:.1f} |
| 大腿 / 小腿 | {measurements['manny']['thigh_l']:.1f} / {measurements['manny']['shin_l']:.1f} | {measurements['quinn']['thigh_l']:.1f} / {measurements['quinn']['shin_l']:.1f} |
| 左右肩中心间距 | {measurements['manny']['shoulder_span']:.1f} | {measurements['quinn']['shoulder_span']:.1f} |
| 左右髋中心间距 | {measurements['manny']['hip_span']:.1f} | {measurements['quinn']['hip_span']:.1f} |

两款保持相同的 44 轴协议，但各有独立实体参数。当前中立比例检查通过；每款 1,087 个动态样本中，极端颈部组合仍产生 {cases['manny']['max_error_mm']:.2f} / {cases['quinn']['max_error_mm']:.2f} mm 的头部位置误差，超过设定目标。Quinn 还需要单独的 UE 适配与验收。

当前模型用于确定身体尺寸、关节中心和外形参考。整机承力、摩擦、传感器、线束及支架尚未按新比例完成集成，**还不能按这些参考 STEP 直接打印装配**。现在不用打印、测量或采购。

## 两款文件

- [Manny 关节布局 STEP](generated/revE/manny/Manny_44_proportion_layout.step) · [Manny 实体参数](mechanical_manifest/physical_manny_44_revE_proportion.json)
- [Quinn 关节布局 STEP](generated/revE/quinn/Quinn_44_proportion_layout.step) · [Quinn 实体参数](mechanical_manifest/physical_quinn_44_revE_proportion.json)
- [CQ-editor 入口](cad/revE/open_in_cq_editor.py) · [重建方法](docs/BUILD_REVE.zh-CN.md) · [版本登记表](mechanical_manifest/dual_character_design_revE.json)

## 继续使用的机构与电路研究

[H2 持姿关节说明](docs/H2_CLUTCH.zh-CN.md)、[M 规格研究夹具](generated/revC/H2/M/H2_M_assembly.step)、[Rev B 传感器板](electronics/sensor_revB/PoseDoll_AS5048A_revB.kicad_pro)仍保留。传感器 PCB 为 18×20 mm；之前的 ERC / DRC 检查结果仍是未通电板的数字检查。

[旧 Rev C 报告](verification/REVC_REPORT.zh-CN.md)与[比例问题审计](verification/PROPORTION_AUDIT.zh-CN.md)保留为历史记录。Rev D 减重关节研究尚有装配干涉，未放行；旧关节不能直接复制到新比例整机上。

后续继续按 A1 mini、0.4 mm 喷嘴、PLA 设计分件。已有 UE 插件、Python 模拟器及原始下载方案包保持不变。
''')
 print(json.dumps({'neutral_gates':{n:k[n]['neutral_proportion_gate_passed'] for n in k},'dynamic_gates':{n:k[n]['position_gate_passed'] for n in k},'report':'verification/REVE_REPORT.zh-CN.md'}))
if __name__=='__main__':main()
