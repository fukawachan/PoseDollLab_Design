# Rev J · 夹紧与测角安装检查报告

状态：CAD 候选，未制造放行、未实测。四处肩屈伸／外展 D 形接口增加金属夹头；左右肩外展增加两套实际 PCB 与磁铁安装结构。Manny / Quinn 沿用 Rev I 的同一份比例模型，关节中心与原 44 轴定义保持。

## 当前总装结果

| 角色 | 实体与占位件 | 未发现局部结构冲突 | 同时没有双臂互碰 | 打印候选最长包围盒边 / mm |
|---|---:|---:|---:|---:|
| Manny | 251 | 36/36 | 32/36 | 125.9 |
| Quinn | 251 | 36/36 | 30/36 | 122.5 |

两款共 72 个离散姿态，其中 62 个没有登记的跨运动节段相交；其余 10 个只有独立双臂的摆姿限制。相交体积判断阈值为 0.02 mm³。原组合动作与肩轴极限均保留，没有缩小范围、删除动作或把内部干涉改称摆姿限制。

每款新增 24 个夹头零件和 50 个测角实体／占位，替换两根旧后端轴，因此由 179 变为 251 个逻辑实体。其中 PCB 被拆为七个真实实体计数，不能把总数当采购件数量。全部实体有效且各为单一实体。仍只有 12 个轴在这份局部总装中运动，另外 32 个尚未集成。

检查同时覆盖新增组件与同一运动节段上的装配关系；未发现未解释的重叠。只登记了具体的螺钉／内螺纹简化包络，不豁免磁铁、支架、摩擦片、垫片或 PCB 穿插。名义轴套中心到 FK 轴线的误差小于 0.00001 mm，是坐标一致性检查，不是加工精度。

64 条分步装配工具通道全部无超阈值阻挡。外展内侧 M3 必须先装，再加入后端测角轴；磁铁与保护桥先装，PCB 后装。详见 [工具检查](revJ_tool_access.json) 和 [装配顺序](../docs/SHOULDER_REVJ.zh-CN.md)。

## 测角检查

两路外展在两款各 36 个姿态下，共完成 144 条同轴／间隙／相对转角检查。名义磁铁表面至芯片封装表面间隙保持 2.8 mm，相对几何角度与原外展轴一致；独立测角组件另完成 −30° 到 150°、每 15° 一个样本，共 13 个旋转检查，无跨固定／转动件相交。

这不代表电子读数已验证。板厚公差、磁铁偏心、磁场强度、磁铁防转粘接、杯体间隙、原始读数方向与校准仍待验证。附近铁磁件的影响不能由几何检查排除。真实 PCB 的来源哈希记在 [组件尺寸与来源](revJ_components.json)。

## 剩余肩部测角试排

下表仅检查同一块实际 PCB 沿现有轴端直排的位置，还没有固定件。失败意味着这个位置不能直接采用，不代表该轴无法测量。

| 角色 | 轴 | 结论 | 首个有碰撞的样本 | 示例相交零件 |
|---|---|---|---|---|
| Manny | upperarm_l.flex | 样本无碰撞，未设计固定件 | — | — |
| Manny | upperarm_l.twist | 此直排位置不通过 | arms_side | l_clavicle_output_frame、l_flex_ring、l_flex_clutch_flanged_shaft |
| Manny | upperarm_r.flex | 样本无碰撞，未设计固定件 | — | — |
| Manny | upperarm_r.twist | 此直排位置不通过 | arms_side | r_clavicle_output_frame、r_flex_ring、r_flex_clutch_flanged_shaft |
| Quinn | upperarm_l.flex | 此直排位置不通过 | neutral | l_yaw_bush_top、l_yaw_shaft、common_chest_bearing_frame |
| Quinn | upperarm_l.twist | 此直排位置不通过 | arms_side | l_clavicle_output_frame、l_flex_ring、l_flex_clutch_flanged_shaft |
| Quinn | upperarm_r.flex | 此直排位置不通过 | neutral | r_yaw_shaft、r_yaw_carriage |
| Quinn | upperarm_r.twist | 此直排位置不通过 | arms_side | r_clavicle_output_frame、r_flex_ring、r_flex_clutch_flanged_shaft |

Manny 的屈伸板在这些试排样本中能避开已建零件，但尚无支座、完整走线和装配方案；Quinn 的内侧空间更紧。两款扭转板都不能直接放在当前顶部位置。四路仍列为未集成，应继续设计布局，不计入本轮已完成的两路外展安装。

## 持姿预算与回差

| 角色 | 最不利轴下游已建质量 / g | 加每腕 100 g 后的最大取样力矩 / N·m | μ=0.15、名义 552 N 时的计算余量 |
|---|---:|---:|---:|
| Manny | 182.4 | 0.372 | 2.01 |
| Quinn | 173.5 | 0.349 | 2.14 |

新夹头和后端轴按铝，径向紧固件按黄铜，PCB 与元器件采用估算密度；旧金属件按钢，打印件仍按实心 PLA。每腕另加 100 g 点质量，在无相交姿态下计算任意重力方向上界。线束回弹、外力、动态载荷、材料变形和完整手部均未验收。密度、遗漏项与全部样本见 [预算](revJ_load_budget.json)。

摩擦片与碟簧沿用 [Rev I 的选型和来源](REVI_REPORT.zh-CN.md)。名义预紧不是实测预紧，计算余量不是额定负载。

D 形孔的中心固定、未夹紧截面计算见 [测角检查 JSON 的 unclamped_D_fit](revJ_readout_check.json)。这个数字忽略轴的横移、法兰相对滑移、夹头弹性和打印蠕变，不能当作整机回差。当前只实现了可夹紧、可维护的几何结构，真实回差仍未验收。

## 双臂摆姿限制

| 角色 | 样本 | 相交对数 |
|---|---|---:|
| Manny | arms_crossed | 9 |
| Manny | forward_shrug_reach | 13 |
| Manny | crossed_staggered | 4 |
| Manny | scan_abduct_-30 | 9 |
| Quinn | down | 1 |
| Quinn | back_down | 4 |
| Quinn | arms_crossed | 9 |
| Quinn | forward_shrug_reach | 52 |
| Quinn | crossed_staggered | 3 |
| Quinn | scan_abduct_-30 | 19 |

以上在查看页中显示为橙色。它们需要调整摆姿来避让，不会自动修改硬件输入或 UE 姿势。

预留件另行记录，不计入结构通过统计。中立姿态的跨节段占位相交如下；旧肘部齿轮外廓尚无完成的齿形，新配对插头与线束也尚无真实型号。

| 角色 | 中立占位相交对数 |
|---|---:|
| Manny | 2 |
| Quinn | 2 |

## 交付与未完成项

- [Rev J 交互查看页](../generated/revJ/RevJ_Shoulder_Review.html)：人物、姿态、臂壳、占位件、肩部及左肩测角细节。
- [Manny STEP](../generated/revJ/manny/Manny_shoulder_assembly.step) · [Quinn STEP](../generated/revJ/quinn/Quinn_shoulder_assembly.step)。
- [共用夹头 STEP](../generated/revJ/components/D6_split_drive_assembly.step) · [外展测角零件组 STEP](../generated/revJ/components/abduction_encoder_assembly.step)，不含与肩框一体的支撑桥。
- [44 轴状态](../mechanical_manifest/dual_character_mechanics_revJ.json) · [模型清单，非采购表](../mechanical_manifest/revJ_assembly_inventory.json)。
- [Manny 原始检查](revJ_manny.json) · [Quinn 原始检查](revJ_quinn.json) · [源文件与输出哈希](revJ_design_audit.json)。

下一步继续剩余肩部测角、线束、肩带／扭转轴的轴向固定和预紧，再推进躯干、下肢与整机。当前几何不包括完整头、颈、胸廓表面、手和支架，已有颈部位置与 Quinn 适配问题仍保留。未做连续扫掠、公差极限、强度、夹紧变形、疲劳、磨损或打印试验。

复建入口：tools/Build-RevJ.ps1。当前不用打印、测量或采购。
