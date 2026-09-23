# Rev M 构建、分阶段验收与校准

现在无需你购买量具、接线或打印整机。以下是数字设计完成后的执行顺序；当前通过的检查都保存在 `verification`，没有把合成数据写成真实传感器校准。

## 本地重建

本文命令在独立 `design/` 仓库根目录运行；首次环境检查优先使用根目录 `scripts/Build-Design.ps1`。机械生成入口是 `Hardware/PoseDoll44/cad/revM/final_model.py`，整机导出是 `export_complete.py`。不能独立运行一个早期关节脚本，再把它的旧输出混入本次总装。

当前电脑的 CAD 运行器 `tools/run_cad.py` 借用正在打开的 CQ-editor 中的 CadQuery 运行环境；关闭或升级 CQ-editor 后可能需要重新定位环境。可长期复现的替代方式是安装 CadQuery 2.7.x、NumPy 与 VTK，直接执行同一生成脚本。当前导出已留 STEP，读模型不依赖原临时运行环境。

在仓库根执行的命令示例：

```powershell
python -X utf8 Hardware/PoseDoll44/tools/run_cad.py Hardware/PoseDoll44/cad/revM/final_model.py
python -X utf8 Hardware/PoseDoll44/tools/run_cad.py Hardware/PoseDoll44/cad/revM/export_complete.py
python -X utf8 Hardware/PoseDoll44/tools/run_cad.py Hardware/PoseDoll44/cad/revM/audit_complete.py
```

完整重建可使用 `tools/Build-RevM.ps1 -Stage All`；也可选择 CAD、Electronics、Firmware、OfflineTests、Reports。最后运行 `-Stage Delivery`，在本地 8874 服务开启时检查三维页面和零件下载，并核对全部来源后生成最终报告与哈希清单。默认阶段只运行 OfflineTests，不连接硬件。Delivery 遇到旧报告、失败结果或缺件会停止，不自动冒充通过。

审核报告记录所用 CAD 输入的 SHA-256；改过几何后，旧报告不再证明新模型通过。缓存只读取本地生成且输入哈希一致的文件。最终交付清单另外记录电子文件和固件，不把“CAD 没变”当作电路没变。

查看器要通过 HTTP 打开，不能双击 `file://` 后依赖浏览器跨文件读取。当前服务地址为 `http://127.0.0.1:8874/generated/revM/RevM_Full_Body_Review.html`。服务不在时，在 `Hardware/PoseDoll44` 目录运行 `python -m http.server 8874 --bind 127.0.0.1`，再打开上面的本地地址。

## 阶段 1：高负载关节首件

由加工/预装方做一套最终版本的腰部双摩擦面关节，使用实际碟簧、摩擦片、轴套、保持螺钉和磁铁托。你收到可直接转动的装配件，自己不压装 1,656 N 的弹簧堆。

| 项目 | 方法 | 原型目标 |
|---|---|---|
| 起动与运行扭矩 | 拉力计垂直拉动已知力臂，扭矩=力×力臂；正反向各 5 次 | 保持扭矩 ≥整机预算需求×1.5；运行阻力不高于名义值的 1.2 倍；起动/运行比 ≤1.5 |
| 保持 | 在预算重力扭矩下保持 30 分钟，记录开始/结束角度 | 漂移 ≤1°，无可见松动 |
| 回差 | 在同一参考角正反向靠近，卸去操作力后读角度 | 差值目标 ≤1°，不能靠滤波隐藏机械松动 |
| 预压件 | 加工方用轴向夹具检查金属力路及螺纹 | 名义预紧×1.5 的试验载荷后无永久变形、拉脱、滑牙；这不是要求用户手压测试 |
| 往复 | 首轮 500 次、中期 5,000 次缓慢往复 | 记录扭矩衰减、掉粉和松动；变化 >20% 或保持不合格即返工 |

阈值是本项目的候选验收标准，尚未测得通过。PEEK 摩擦系数 0.15 是计算假设，若实物不足，不应简单无限增加预紧；要一起复核材料、接触面与轴系应力。

## 阶段 2：单传感器、区域板和最长线束

建议由贴片方先完成限流上电、短路/焊接检查及基本读数，交付测试记录。将一块传感器板与一个区域板按本版线束连接，用完整设计中的最长传感器线验证，不以一根 10 cm 台架线代替。

- 磁铁/芯片间距、偏心、磁场强弱、AGC/错误标志和角度重复性逐项记录；传感器 14 位分辨率不等于人偶实际精度。
- 连续运行至少 30 分钟，记录供电电压、3.3 V、输入电流、板内温度和错误计数。六节点组合后复核总输入、最远板端电压、保险和 PTC 温升。
- 150 mA MCU 预算、80% 降压效率、接触电阻和实际线长均需核对。设计中 200 mA 的敏感性结果不是已满足全部电源余量的承诺。
- 250 kHz SPI 只是初始设置；示波器查看最远线的时钟、CS、MISO 振铃/建立时间。降时钟频率不能自动消除容性负载或边沿问题。
- 拔掉一个传感器应显示 `missing` / `invalid`；重新接线前先断电。故障不能变成“零度正常”。

## 固件与诊断

`generated/revM/firmware/node1…node6` 是对应 N1…N6 的独立镜像包，附各自 `manifest.json` 和原始 `flasher_args.json`。芯片 ESP32-S3，Flash 8 MB，DIO 80 MHz；映像地址来自构建输出：bootloader `0x0`，partition table `0x8000`，应用 `0x10000`。不得把 N1 的应用烧到六个节点，也不要复制设备身份。

固件源码在 `Firmware/PoseDollFullBody`，按 `tools/build.ps1 -Node 1` 到 `-Node 6` 构建。现有六组镜像已在 ESP-IDF 6.1 编译成功；没有执行任何烧录。首次烧录、BOOT/RESET 操作和首次通电由熟悉板卡的装配方完成，实际端口确定后再给出该设备的命令，不在文档里硬编码一个可能指向其他设备的 COM 口。

`Tools/PoseDollHardwareBridge/Open_Full_Diagnostic.cmd` 打开诊断窗口。窗口需要你明确选择设备和连接；当前设计流程没有自动打开串口。其作用是查看 44 个协议槽位、节点到齐、磁场故障并记录原始数据。前三槽始终是骨盆固定参考，其余 41 槽才是测量。

离线检查已有记录：

```powershell
python Tools/PoseDollHardwareBridge/full_diagnose.py --help
```

本轮新增校准工具只处理记录文件，不会连接串口或 UE。它也不烧写 AS5048A 的 OTP 零点。

## 阶段 3：单肢与完整结构

先做一条手臂、一条腿及它们的实际外壳、线夹和导线。分别从各运动轴下游抓握稳定骨段，检查轴的正反方向、限位、保持、梁弯曲和层间裂纹；不要用传感器板或磁铁盖作把手。安装顺序见 [装配说明](ASSEMBLY_REVM.zh-CN.md)。

PLA 受力梁在最终切片姿态下做静载及缓慢往复；把最不利操作扭矩传到梁上，记录弹性挠曲和卸载后的残余变形。先由装配方做预算静载的 1.5 倍样件证明试验，不把未经验证的完整人偶举起来承重。薄壳只提供抓握外形，不代替内部承力梁。

随后制作一款完整人偶，验证站、坐、躺的相对姿势和外部支撑安排。先用额外支撑物承住重量，不能期待人偶自由站稳。相邻机构/线束被夹属于返工项；左右手臂、腿等非相邻部位的接触可改变姿势避让，查看器会保留这类提示。

## 41 轴零点与方向校准

让预装方使用可溯源量角工具或按金属键面制作的夹具，对每轴建立至少三个已知参考角。固定其余轴，参考角是**该机械轴相对固定侧的角度**，不是在屏幕上目测手臂方向。量角不确定度目标 ≤0.5°。推荐参考值见各角色 `calibration_reference_plan.csv`；并未给它们填入传感器实测值。

每个角度保持不动，诊断窗口记录至少 30 个连续有效样本。下面以左肘 0° 的一个记录为例（其他角度/轴都须单独采集）：

```powershell
python Tools/PoseDollHardwareBridge/calibrate_pd41.py observe --character manny --axis elbow_l.flex --angle-deg 0 --input elbow_l_0.bin --out elbow_l_0.json
```

程序拒绝丢帧/坏帧、少于 30 个样本、故障轴或原始波动大于 0.4° 的记录。三个参考角至少跨 20°、不超过 160°，拟合仅求零点和正负方向，增益固定为 1；参考残差必须 ≤1°，不会用增益或曲线拟合掩盖装配问题。

收集全部 41 轴的观察 JSON 后，保存成一个数组文件 `observations_all.json`，生成新目录：

```powershell
python Tools/PoseDollHardwareBridge/calibrate_pd41.py build --character manny --observations observations_all.json --assembly-id Manny-001 --out Hardware/Calibration/Manny-001
python Tools/PoseDollHardwareBridge/calibrated_pd41.py --bundle Hardware/Calibration/Manny-001 --input full_body.bin --out calibrated_recording.jsonl
```

第二条命令只做离线转换。新配置包包含机械 profile、校准、能力文件和实测记录，绑定角色、设备 ID、装配编号与 profile 字节哈希；已有输出目录不会被覆盖。设备重启、旧序号、不同设备、被修改的 profile、缺失轴都会被拒绝或显式标成无效姿势。不会沿用上一帧假装当前有效。

校准中前三个骨盆通道明确固定为零，原始值为空，不参与零点拟合。现实中将整个人偶平躺，输出不变；场景内所有整体平移和旋转都用 UE Placement 调整。

## UE 接入的验收边界

本轮没有修改当前运行的 UE 项目、正在使用的 Shared 配置或已经测试通过的模拟器。当前插件按固定路径/文件名读取配置；实体校准包必须与 UE 端一起选择并用相同字节哈希握手，不能把一个硬件零点文件随意覆盖进旧虚拟配置。

新增工具完成的是原始 PD41 → 经过校准的现有姿势协议的**离线转换**。串口到 UE 的正式实时桥接、设备选择界面、Quinn 专属 Control Rig/资产绑定和真实硬件 Capture 持久化仍需接入测试，不能声称已经实机通过。Quinn 的机械比例已经使用 Quinn 参考骨架；这不等于软件中的 Manny 绑定文件自动变成 Quinn 绑定。

实物接入后复做原项目验收：不同动作捕获到 Sequencer，关闭输入程序并重启 UE 后仍有可编辑 Control Rig 关键帧；手指/面部保持原控制。测角误差、手感与硬件总延迟另记，不由“能连上”代替。
