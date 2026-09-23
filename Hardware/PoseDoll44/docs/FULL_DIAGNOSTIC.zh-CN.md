# 全身诊断工具（PD41）

入口：`Tools/PoseDollHardwareBridge/Open_Full_Diagnostic.cmd`。这是全身六节点工具；旧的 `Open_Diagnostic.cmd` 仍用于 H1 单轴。

当前默认只打开窗口，不扫描端口、不打开串口、不向 UE 发数据。先使用“打开离线记录”查看已有 `.bin`；实物阶段确认设备身份后，再点击刷新、选择明确的串口、开始采集。一次默认 10 秒，可中途停止并保留结果。

界面列出全部 44 个协议位置。其中骨盆三轴为固定参考，原始读数显示横线；其余 41 轴区分有效、故障、缺失。缺失和故障不会填成零，也不会使用上一帧凑齐姿势。显示的角度是传感器原始计数换算，不是校准后的机械关节角度。

保存结果包括原始 `.bin`、逐帧 `.jsonl` 和 `.summary.json`。摘要包含完整有效帧数、六节点到齐数、丢帧、错误及连续有效段的原始角度波动。缺失、故障与序列间隔会分开统计段；跨越 0/360° 会按连续角度展开。只有保持人偶不动时，波动才可作为噪声参考，不能据此声称测角精度或装配通过。

`calibrated` 和 `physical_acceptance` 始终为 false。零点、正负方向、磁场与实际机械角度仍需后续实物验证。本工具不会发送 UE 姿势或烧录固件。

离线命令示例（在本目录）：

```powershell
python full_diagnose.py --input recording.bin
```

硬件阶段的采集命令必须显式给出已核实端口和新的输出名前缀：

```powershell
python full_diagnose.py --port COM7 --seconds 10 --out captures/session01
```

端口号仅是示例，不能照抄。已存在的记录不会覆盖。当前双击入口使用本机 Espressif Python；迁移机器时需安装 Python、Tkinter、pyserial 并调整入口路径。
