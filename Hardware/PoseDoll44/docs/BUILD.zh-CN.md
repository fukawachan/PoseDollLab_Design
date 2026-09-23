# 构建与复现

工具路径在 tools/local_toolchain.json。本轮没有安装新工具或修改模拟器 Python 环境。

CadQuery 复用已运行的 CQ-editor 2.7 包。run_cad.py 是本机 PyInstaller 包兼容加载器，**不是官方 CQ-editor CLI**。CQ-editor 关闭后临时目录可能消失，需重新打开；也可用独立 CadQuery 2.7 环境直接运行 cad/build.py。

仓库根目录 PowerShell 执行：

~~~
powershell -NoProfile -File Hardware\PoseDoll44\tools\Build-Hardware.ps1 -Regenerate -Firmware
~~~

-Regenerate 从 Python 源覆盖本包生成的 CAD/PCB，手动修改原生 KiCad 文件后需同步生成器；日常检查可去掉此选项。-Firmware 只编译不烧录。脚本不会打印、采购、修改现有 UE 或模拟器。

检查包含 CAD 导出、名义干涉、KiCad ERC/DRC/原理图一致性、渲染、诊断故障测试、GUI 构造、模拟器回归、固件编译和跨文件检查。退出码/日志写入 verification。-SkipGeometry 只用于快速复查，修改 CAD 后不能省略完整检查。

主要源码：
- cad/model.py：运动树、偏移、关节包络和节点位置。
- cad/parts.py：13 个编号打印件与五金/PCB参考。
- cad/build.py：导出、姿势、质量/扭矩/电源/CAN预算。
- cad/inspect_geometry.py：OCC 实体交集采样。
- tools/build_electronics.py、route_sensor.py：原生 KiCad 生成和本板路由，最后由官方检查工具判定。
- 仓库 Firmware/PoseDollHardware：单轴固件。
- 仓库 Tools/PoseDollHardwareBridge：解码、日志、中文界面和测试。

CAD 用 mm，实体 profile 导出为 m，44轴顺序不变。当前自动检查不会把实物状态改为通过。无有限元或认证承载结论、无上电和精度实测、无本轮实体 UE Capture/Undo/重开验收；区域节点与网关尚未实现。

## 仅更新机械设计

本轮新增 -MechanicalOnly 开关。配合参数为 mechanical_manifest/print_fit_profile_revB.json；由 CAD、后续试片、图纸和敏感性报告共用。

在仓库根目录执行 Hardware/PoseDoll44/tools/Build-Hardware.ps1 -Regenerate -MechanicalOnly，会重新生成 CAD，检查运动干涉、导出 STEP 的代表性孔径、参数情景和跨文件一致性，并更新报告。不会重建未改变的 PCB、固件或运行无关软件测试；既有报告仍保留。

不带 -Regenerate 则检查已有导出文件；输入哈希和 STEP/STL/ZIP 一致性用于发现过期产物。输出 fit_geometry_check.json 是名义几何检查，print_fit_sensitivity.json 是工程情景计算，均不能代替实物测试。

当前用户实测明确后置，脚本完成不再提示立即打印。
