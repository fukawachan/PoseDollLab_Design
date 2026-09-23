# Rev K · 紧凑测角与扭转安装检查

状态：CAD／电路候选，未制造放行、未实测。新增 12 × 10 mm 测角板，并完成两款各左右两套扭转测角几何安装。两路屈伸仍未集成。现在不用采购或打印。

## 总装结果

| 角色 | 实体与占位 | 无局部结构冲突 | 同时没有双臂互碰 | 测角安装候选 |
|---|---:|---:|---:|---:|
| Manny | 289 | 36/36 | 32/36 | 4 |
| Quinn | 289 | 36/36 | 30/36 | 4 |

两款共 72 个离散姿态。结构冲突阈值仍为相交体积 0.02 mm³；对独立左右手臂的接触保留橙色摆姿限制。没有缩小关节范围或把内部干涉改成摆姿限制。当前仍只有 12/44 轴参与局部总装，不包括完整躯干、头、手与下肢。

验证采用增量几何检查：先核对 Rev J 几何源文件、比例、传感器 STEP 与原始检查结果的 SHA256，并在构建中断言未改零件保持原 Shape 对象。未改零件之间复用 Rev J 结果；每个姿态中，所有涉及 Rev K 新增／修改零件的跨节段配对都重新做 BRep 相交。新增零件和固定框增量还单独进行同一运动节段的装配检查，未发现未解释重叠。记录的螺纹包络仅豁免具体螺钉／内螺纹对，不豁免轴、磁铁、盖或板子。

每款新增 40 个实体／占位，替换 2 根旧扭转轴，因此从 251 变为 289。PCB 器件、连接器尺寸包络和短排线分别计数，**289 不是采购件数量**。所有逻辑实体有效且为单一实体。

## 电路与传角

- ERC、DRC、未连接项、原理图一致性检查均为 0 项；与 Rev B 的器件引脚网络逐项等价，仍为 3.3 V 六线 SPI。
- 小板名义 12 × 10 × 1.0 mm，双层，0.15 mm 线宽／间距，0.25 mm 铜至板边，11 个 0.6/0.3 mm 过孔。
- AS5048A、四个无源器件和 FR4 来自 KiCad STEP；FH19C 连接器是厂家尺寸包络，短 FPC 是占位。完整线束没有被验证。
- 四处测角在两款各 36 姿态下共 288 条同轴／相对转角／名义气隙检查通过；扭转 1.5 mm，原外展 2.8 mm。
- 独立扭转组件另完成 -90° 至 90°、每 10° 取样的 19 项旋转检查。

这些是数字检查，不是电子实测。磁场、精度、供电噪声、SPI 时序、排线寿命、真实角度正方向及校准仍待验证。电路规则集及默认忽略类别已记录在 [小板接口](../electronics/sensor_revC_mini/mechanical_interface.json)；没有自定义 DRC 排除项。

## 装配与工具

64 条原有通道和 36 条新增工具／插入／连接器服务包络检查通过，共 100 条。新增过程明确检查了先在独立轴上装磁铁盖、再插入整轴、再装独立托座和板子的顺序。早期一体托边会阻挡轴插入，最终版已拆成独立托座。托座转到关节前后方向，避开中间外展角度的内侧螺钉。

这是明确分步的名义几何结果；没有验证手指抓握、公差极限、螺纹强度或原位维修。完整步骤见 [装配说明](../docs/SHOULDER_REVK.zh-CN.md)。

## 持姿预算

| 角色 | 最不利轴下游已建质量 / g | 加每腕 100 g 的最大取样力矩 / N·m | μ=0.15、名义 552 N 时余量 |
|---|---:|---:|---:|
| Manny | 182.4 | 0.372 | 2.01 |
| Quinn | 173.4 | 0.349 | 2.14 |

仅复核现有屈伸／外展持姿预算。打印件按实心 PLA、定制轴按铝、元器件按估算密度，并加每腕 100 g 点质量，在无相交姿态取任意重力方向上界。线束回弹、手部外力、动态、蠕变及完整身体未计入验收。余量不是额定负载，扭转与肩带预紧仍未完成。见 [预算假设与原始数据](revK_load_budget.json)。

## 摆姿限制

| 角色 | 样本 | 独立双臂相交对数 |
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

## 交付与未完成项

- [交互查看页](../generated/revK/RevK_Shoulder_Review.html)，可看左肩扭转细节。
- [Manny STEP](../generated/revK/manny/Manny_shoulder_assembly.step) · [Quinn STEP](../generated/revK/quinn/Quinn_shoulder_assembly.step)。
- [紧凑扭转组件](../generated/revK/components/compact_twist_encoder_assembly.step)；其中固定柱只是参考节选，真实连接在总装的外展框中。
- [KiCad 原生工程](../electronics/sensor_revC_mini/PoseDoll_AS5048A_revC_mini.kicad_pro) · [正面布线](../generated/revK/components/sensor_front.svg) · [背面布线](../generated/revK/components/sensor_back.svg)。
- [44 轴状态](../mechanical_manifest/dual_character_mechanics_revK.json) · [模型清单，非采购表](../mechanical_manifest/revK_assembly_inventory.json) · [源文件与结果快照](revK_design_audit.json)。

Quinn 的屈伸测角直排方案在后收＋下压时仍有胸部内部承力框干涉，两款屈伸安装都没有计入完成。肩带测角、肘传感转接、扭转／肩带预紧、完整轴向保持、线束与其转接、躯干和下肢等还需设计。旧试排失败结果保留为历史研究，与最终扭转方案分开标记。按用户最新要求，本体不依赖固定外部支架，外部支撑物暂不设计；完整站、坐、躺的全身检查尚未完成。骨盆三轴实体参考另行设计，不冒充已有测量。没有修改 UE 插件、Python 模拟器或原始下载方案包。
