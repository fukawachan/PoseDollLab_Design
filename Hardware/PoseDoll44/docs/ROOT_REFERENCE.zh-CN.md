# 骨盆固定参考与 UE 整体摆放

用户已于 2026-09-23 确认：实体人偶只用于设计相对关节姿势；整体位置、左右转向、前后倾斜和左右侧倾全部在 UE 中调整。

胯部外形的正前方定义人偶自身的 +X。硬件不安装 IMU，也不测量人偶相对地面的方向。各关节不动时，将整个人偶从竖直放成平躺，输入姿势不变；要让角色躺下，应调整 UE Placement 的整体旋转。弯腰、抬腿、屈膝等相对动作仍由人偶输入。

## 数据约定

- 保留原 44 个通道名称与顺序。
- `pelvis.yaw`、`pelvis.pitch`、`pelvis.roll` 是已声明的固定局部参考，值为 0 rad。样本中使用 `axis_status = fixed`、`raw_angles_rad = null`。
- 其余 41 路来自关节传感器。缺失或失效应报告 `missing` / `invalid`，不得改成固定零值。
- 两款能力文件位于 `mechanical_manifest/physical_manny_41_capabilities.json` 和 `physical_quinn_41_capabilities.json`。不修改之前已测试的虚拟 44 路 / 35 路能力文件。
- 当前 UE 核心和 Python 解码器均能按已声明能力处理固定通道。现有载入器使用固定文件名；实体配置包必须带正确的 profile、calibration 与 capability 三份配套文件，并以相同文件字节的 SHA-256 握手。仅保存能力文件不代表已完成实体固件接入。
- 尚未实物校准的传感器零点不能作为真实校准发布。工厂占位零点仅用于合成输入测试。

## UE 操作

Placement 已支持 `x_cm / y_cm / z_cm / yaw_deg / pitch_deg / roll_deg`，采集时会写入角色的整体 Transform 轨道。当前实现要求先解除手脚接触锁定，再改变 Placement；调整完成后可重新设置接触约束。整体位置和姿势关键帧仍保存在 UE 中。

本次只验证了接口语义，没有更改当前运行中的 UE 会话、角色 Placement 或现有动画。

## 已执行的验证

`Tools/PoseDollHardwareBridge/test_root_reference.py` 使用现有 Python 解码器验证了四种情况：41 路有效传感器与 3 路固定参考正常解码；实测关节不能被偷偷改成固定轴；实测关节缺失会被拒绝；骨盆固定参考不能冒充有效的零度测量。4 项通过。此测试不构成真实硬件精度验证。
