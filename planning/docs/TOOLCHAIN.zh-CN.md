# 面向 Codex 的设计工具链

## 1. 默认工具选择

机械主源使用 CadQuery + Python。零件尺寸、安装界面、关节轴、连杆与电子件占位体都由参数化源生成，输出 STEP、STL、装配图和机械 profile。CadQuery 的官方文档明确支持脚本式参数化 CAD 和多种交换格式。[S2] FreeCAD 可作为人工查看/测量工具，但不同时维护一份与代码不同步的主模型。

CadQuery 环境单独安装，与已工作的模拟器 Python 3.13 环境分离。H0 探测可用解释器和二进制依赖，锁定实际验证的版本；不要为满足 CAD 的依赖而升级或降级现有 UE/Python 环境。

电子设计使用 KiCad 原生 `.kicad_sch` / `.kicad_pcb`，以 `kicad-cli` 运行 ERC、DRC、BOM 与制造文件导出。[S3] CLI 擅长检查和导出，不是自动电路设计师。原理图/板子通过版本支持的编程接口、可靠生成器或审查过的模板构建；必须可以在 KiCad 正常打开、编辑并继续迭代。

KiCad IPC 是操控正在运行的 KiCad 实例的编程接口，不是“无需 GUI 的官方 MCP”。本地版本支持什么能力要先探测。需要 MCP 时，只包装已经能复现的固定动作，例如打开工程、导出 STEP、运行规则检查、读取结果；不要依赖来源不明的 MCP 插件才能恢复设计。[S7]

固件使用 ESP-IDF 与 `idf.py`，统一构建 node/gateway 角色。官方 CLI 支持构建、烧录和监视等动作。[S8] 使用本地真实开发板、芯片和引脚；不能把某篇示例代码的 GPIO 当作量产针脚表。记录 USB、flash/PSRAM、启动配置脚、SPI 和 CAN 所需引脚的占用与限制。

打印采用 Bambu Studio 的真实 A1 mini/耗材配置，人确认切片预览后开始。机械模型和检查流程自动化已经满足 CLI-first；不要求第一阶段实现自动切片/远程打印。未经本地探测，不假定 Bambu Studio 的所有 GUI 功能都有稳定 CLI。

## 2. 建议代码与文件结构（待 Codex 创建）

```text
Hardware/PoseDoll44/
  cad/                       # CadQuery 源、装配、关节结构族、打印试片
  mechanical_manifest/       # 轴/坐标/材料/紧固件/负载和制造版本
  electronics/
    sensor/                  # 传感器板的 KiCad 工程
    acquisition_node/        # 可复用区域采集板
    gateway_power/           # 网关、配电、防反灌与保护
  harness/                   # 线束 ID、长度、接头、针脚视图
  fixtures/                  # 校准、持姿力、磁场串扰试验夹具
  tests/                     # CAD/协议/配置一致性与负例
  manufacturing/             # 仅放已批准某轮试制的文件
  assembly/                  # 面向用户的中文分步说明
  verification/              # 保留工程证据，不与运行缓存混淆
Firmware/PoseDollHardware/
Tools/PoseDollHardwareBridge/
Shared/Profiles/physical_... # 新增，保留原虚拟配置
```

现仓库忽略了根目录 `/reports/`，硬件验收证据应放在明确追踪的目录或单独发布包，避免“本地做过但交接时全丢了”。较大的照片/视频可以独立附件保留，但报告须记录关联文件名、内容哈希、测试对象版本和条件。

## 3. 命令行复现约束

以下是已存在工具的命令类型，实际参数以本机 `--help` 为准：

```text
kicad-cli sch erc --exit-code-violations <schematic.kicad_sch>
kicad-cli pcb drc --exit-code-violations <board.kicad_pcb>
kicad-cli pcb export step <board.kicad_pcb>
idf.py build
idf.py -p <confirmed_port> flash monitor
```

不要对未经确认的串口运行烧录。重写校准和固件前备份设备身份与配置；禁止自动烧 OTP/熔丝或随意擦除全闪存。

Codex 还需开发项目自己的“一键生成机械件、一键导出 profile、一键跑检查、一键形成试制包”命令。不能把这些尚未实现的命令伪装成 CadQuery 或 KiCad 自带功能。所有命令返回可读报告与非零失败退出码，不能只写“导出成功”而遗漏坏几何体或未连线错误。

## 4. 自动检查范围

机械检查：实体有效性、零件包络、孔位与供应商模型配合、螺丝/工具通道、真实轴变换、指定姿势集的碰撞、线束最小余量、BOM 数量与 CAD 一致性。打印方向和支撑清除依然要人工看切片。

电子检查：原理图规则、PCB 规则、原理图/PCB 一致性、连接器对照表、芯片额定值与电压、驱动/负载、稳压器热预算、CAN 终端、电源反灌、短路保护和调试点。ERC/DRC 通过不代表后面这些都正确。

固件/桥接检查：包边界、CRC、片段重组、epoch 回绕、重启、身份/哈希不符、丢包/延迟、错误角度和磁场状态、串口误选、旧会话拒绝、完整采集与 UE 回归。

首版密集 PCB 在下单前应进行一次与原设计相独立的原理图/针脚复核，优先让具备经验的工程师或代工技术人员复核关键电源与连接器，不把判断转嫁给用户。自动检查和供应商 DFM 也不能替代功能实测。
