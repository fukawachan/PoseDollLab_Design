# Rev C 本地工具入口

在 `E:/UnrealProjects/DollSimulation` 下执行。保持已安装的 CQ-editor 开启，CAD 适配器使用其 CadQuery 2.7 环境；其他工具路径在 `tools/local_toolchain.json`。

只检查当前输出并更新审查报告：

```powershell
& ./Hardware/PoseDoll44/tools/Build-RevC.ps1
```

从原理图、PCB 和参数重新生成全部 Rev C 候选文件，再检查：

```powershell
& ./Hardware/PoseDoll44/tools/Build-RevC.ps1 -Regenerate
```

工具顺序是：生成传感器板 → ERC/DRC/原理图一致性 → 导出真实 PCB STEP 和机械接口 → 全身 CAD → H2 夹具 → 13 个全身姿势 → 重力情景 → 数字审查与闭合网格检查。命令遇到失败会返回错误；源文件指纹不一致也会拒绝把旧结果标成当前检查。

电路板生成脚本和接线结果是这版工程候选，尚未制造。CAD 中的螺纹采用名义圆柱/底孔表达，攻丝要求写在 H2 说明和零件记录中。不要把研究件文件名理解成制造放行。

- [CQ-editor 新版入口](../cad/revC/open_in_cq_editor.py)
- [整体运动模型](../cad/revC/design.py)
- [H2 摩擦机构](../cad/revC/clutch.py)
- [负载假设与计算](../cad/revC/loads.py)
- [传感器生成器](../tools/build_sensor_revB.py)
- [真实 PCB 安装接口](../electronics/sensor_revB/mechanical_interface.json)
- [审查报告](../verification/REVC_REPORT.zh-CN.md)

原来的 `Build-Hardware.ps1` 继续用于 H1 / 旧 Rev A 布局 / Rev B 配合检查。新版命令不会烧录固件、操作打印机、创建订单或改动 UE 项目设置。
