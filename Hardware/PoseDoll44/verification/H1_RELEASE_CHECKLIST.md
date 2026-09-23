# H1 放行检查表

| 项目 | 状态 | 证据/条件 |
|---|---|---|
| 44轴ID、顺序及分区 | 数字通过 | design_consistency.json |
| 13个打印实体与打印包络 | 数字通过 | cad_parts.json |
| 打印配合假设 | Rev B，未实测标定 | print_fit_sensitivity.json、../docs/DESIGN_BASIS.zh-CN.md |
| 导出 STEP 代表性孔径 | 数字检查 | fit_geometry_check.json；不代表实际孔径 |
| 单轴名义30姿态实体检查 | 数字通过（有限范围） | exact_geometry_screen.json |
| 传感器ERC/DRC/网表一致性 | 数字通过（记录规则集） | sensor_erc.json、sensor_parity_drc.json |
| 诊断协议与故障恢复 | 软件测试 | h1_protocol_tests.txt |
| 中文诊断窗口 | 构造通过，无串口连接 | diagnostic_gui_smoke.txt |
| 固件 | 编译通过，无烧录 | firmware_build.txt |
| 原模拟器 | 回归通过 | simulator_regression.txt |
| 三件尺寸试片文件 | Rev B，留作以后验证 | generated/stl_fit，仅H1-001/002/003；现在不要求打印 |
| 试片实际尺寸/配合 | deferred / not_run | 用户暂无工具；设计继续，实测安排在设计完成后 |
| 实际模块/磁铁/五金尺寸冻结 | 未完成 | 供应商修订与工单 |
| 承载关节制造放行 | 未放行 | 公差、材料、预紧、紧固件和工具空间待审查 |
| 自制PCB制造放行 | 未放行 | 元器件实物/装配/供电/信号完整性审查 |
| 单轴上电、绝对误差、重复性、静止噪声 | not_run | 独立基准与原始日志 |
| 持姿、摩擦力、1000次磨耗、磁串扰 | not_run | 负载和方法先审查 |
| 全身结构/线束冻结 | 未放行 | 完整三轴几何与碰撞限制仍在 |
| CAN/全44台架/60分钟运行 | not_run | 节点及网关尚未实现 |
| 实体UE预览/Capture/Undo/重开 | not_run | 实体配置与校准尚未实现 |

不得通过把缺失轴填零、修改旧golden vectors、忽略传感器故障或隐藏碰撞来改变这些结论。目标值见 physical_acceptance.json，实际值保持空值。

本轮未采购、下单、烧录或远程打印。用户已明确先继续设计，后做实物测试。试片文件存在不等于现在需要打印，工程假设不等于经过机器标定。
