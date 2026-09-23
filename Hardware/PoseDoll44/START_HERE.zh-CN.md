# PoseDoll · Manny / Quinn 完整硬件设计

> **最新增量：** [Rev N1](START_HERE_REVN.zh-CN.md) 已取消胸口罩壳及其四个紧固件、修正左肩支座局部刮碰，并完成背部外置架构评估。下文为原 Rev M 配套资料，制造时以 N1 清单剔除取消件并替换左肩支座图纸；背部外置尚未实施。

当前交付是 **Rev M 完整数字原型候选**：两款角色各自的 1:2 关节比例、41 个相对测量轴、被动持姿机构、局部可拆外壳、电子仓、四种电路板、六节点固件及线束/校准文件。

**先打开 [完整人偶三维查看页](generated/revM/RevM_Full_Body_Review.html)**。若在浏览器查看，使用 [当前本地服务](http://127.0.0.1:8874/generated/revM/RevM_Full_Body_Review.html)。页面可切换 Manny / Quinn、站/坐与检查姿态、外壳、电子仓、线束固定点，并点击具体零件下载 STEP。


如果本地服务链接打不开，双击 [Open-Viewer.cmd](Open-Viewer.cmd)。它会在后台启动仅本机可访问的服务并打开页面；重启电脑后再次双击即可。不要直接双击 HTML，模型数据需要通过本地 HTTP 服务读取。

目前不需要你打印、采购、量尺寸或接线。完整设计先供复核；实物按“一个高负载关节 → 单传感器/区域板 → 单肢 → 一款整机 → 另一款”的顺序验证。数字检查与尚需补齐的证据集中在 [最终验证报告](verification/REVM_REPORT.zh-CN.md)。

## 确定的使用方式

- 两款都来自项目中的 Manny / Quinn 参考骨架与网格比例。参考高度分别约 907.93 / 907.70 mm；这是 1:2 人物参考高度，机械外壳包络不宣称逐点复制人体表面。
- 稳定躯段包壳，肩带、腰髋、肘膝、腕颈等活动区域裸露。大腿后侧、小腿后上段等压缩区留空；外壳不跨越这些运动区。
- 人偶不含固定外部支架；摆好姿势后使用外部承托，支撑物本轮不设计。
- 骨盆前方定义人偶前方。UE 中调整全部整体位置和转动；整个人偶平躺不会自动让 UE 角色平躺。相对弯腰、抬腿等动作仍由关节测量。
- 协议保留 44 个槽位，骨盆三轴明确 `fixed`、原始值为空；其余 41 轴测量。没有 IMU，不把缺失传感器伪装成零度。
- 非相邻部位接触保留为摆姿限制；同体或相邻结构穿插仍作为设计问题检查。

## 交付文件

| 内容 | Manny | Quinn |
|---|---|---|
| 整机总装 | [STEP](generated/revM/manny/Manny_RevM_assembly.step) | [STEP](generated/revM/quinn/Quinn_RevM_assembly.step) |
| 逐件 CAD / 工艺清单 | [清单 JSON](generated/revM/manny/manufacturing_manifest.json) | [清单 JSON](generated/revM/quinn/manufacturing_manifest.json) |
| 打印候选 | [187 件 STL](generated/revM/manny/print_candidates) | [187 件 STL](generated/revM/quinn/print_candidates) |
| 加工与采购分类 | [CSV](generated/revM/manny/procurement_routes.csv) | [CSV](generated/revM/quinn/procurement_routes.csv) |
| 线束裁线 / 端子表 | [CSV](harness/manny_cut_list_revM.csv) | [CSV](harness/quinn_cut_list_revM.csv) |
| 41 轴校准参考工单 | [CSV，未测](generated/revM/manny/calibration_reference_plan.csv) | [CSV，未测](generated/revM/quinn/calibration_reference_plan.csv) |

打印 STL 已做闭合性检查；每款 6 个零件另附小圆筋修正后的 `_print_process.step`，与名义总装的区别见制造说明，打印直接使用交付 STL。

两款各 1,999 个 CAD 实体，包含电子元件和重复螺丝，不代表 1,999 种采购件。每款电子部分为 **39 块小传感器板 + 2 块肩外展板 + 6 块区域板 + 1 块电源板**。加工/采购分类表把焊接元件归入 PCBA，不重复采购。

- [39 块小传感器板 KiCad](generated/revM/electronics/sensor_revM_side/PoseDoll_AS5048A_revM_side.kicad_pro)
- [2 块肩外展传感器板 KiCad](generated/revM/electronics/sensor_revM_large_sh/PoseDoll_AS5048A_revM_large_sh.kicad_pro)
- [区域板 KiCad](generated/revM/electronics/regional_revM/PoseDoll_PD41_Regional_revM.kicad_pro)
- [电源板 KiCad](generated/revM/electronics/power_revM/PoseDoll_PD41_Power_revM.kicad_pro)
- [六节点固件镜像](generated/revM/firmware) · [固件源码](../../Firmware/PoseDollFullBody)
- [腰关节 STEP](generated/revM/assembly_details/waist_pitch_assembly.step) · [拆解分组图](generated/revM/assembly_details/waist_pitch_exploded.png)
- [肘关节 STEP](generated/revM/assembly_details/elbow_l_flex_assembly.step) · [拆解分组图](generated/revM/assembly_details/elbow_l_flex_exploded.png)

## 按什么顺序阅读

1. [装配说明](docs/ASSEMBLY_REVM.zh-CN.md)：哪些交给加工方预装、你如何连接全身。
2. [制造、公差与打印](docs/FABRICATION_REVM.zh-CN.md)：0.4 mm + PLA、A1 mini 长梁斜放、金属关节与电路板工艺。
3. [线束与电源](docs/WIRING_REVM.zh-CN.md)：41 条传感器线、5 条 CAN 线、6 条电源线，插头与针序。
4. [受力与操作阻力](docs/LOAD_AND_HANDLING_REVM.zh-CN.md)：约 3.2 kg 量级，纸面保持能力与真实手感的区别。
5. [构建、测试和校准](docs/BUILD_AND_CALIBRATE_REVM.zh-CN.md)：离线工具、实物阶段和 UE 接入边界。

## 当前边界

这是完整整机范围的数字设计候选，**没有制造放行或实物鉴定**。精密轴系、摩擦片、弹簧预装和 PCBA 需要加工/贴片方完成，不能只靠打印机做出全部部件。制造 DFM、材料/螺纹强度、实际磁场、持姿/手感、线束耐久和电源/信号波形仍需要首件确认。

颈部与躯干采用等效转轴，运动轨迹不是逐点复刻 UE 的多骨骼脊柱/颈椎。最终离线样本的头部最大位置差异约 14.3 / 16.5 mm（Manny / Quinn）；四肢骨长比例一致，精确贴合身体的接触姿势仍需适配/IK 评估。详见 [轨迹差异记录](verification/revM_kinematic_mapping.json)。

UE 插件和模拟器原先已由用户测试通过。本轮新增的是硬件固件、诊断与离线校准转换；未连接当前 UE 会话或真实设备，未验证 Quinn 独立 Control Rig 绑定及真实硬件实时捕获。不存在已经测好的实体零点文件。

当前 CAD 入口为 [final_model.py](cad/revM/final_model.py)，重建脚本为 [Build-RevM.ps1](tools/Build-RevM.ps1)。最终文件哈希与检查匹配关系见 [交付清单](generated/revM/delivery_manifest.json)。Rev A～L 和其他 `*_work` 文件保留为历史，不作为当前打印或采购入口。
