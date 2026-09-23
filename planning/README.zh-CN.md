# PoseDoll HW-44：硬件设计与 Codex 交接方案

版本：v0.1 / 2026-09-19。范围：完整 44 轴手动姿势人偶；分阶段制造、测试。

这是**工程设计任务书、接口约束和验收计划**，不是已经完成的 CAD、电路板、生产 BOM 或实测认证。文件中的尺寸、性能阈值、总线频率为待验证的设计目标。没有附上可直接投产的 STL、接线针脚图或 Gerber，避免把未经设计审查的文件误当成成品。

项目基线：`fukawachan/DollSimulation`，检查到的提交为 `7c22e075fe0efe295ce2935a8bb2a92cff0b6def`。本地继续开发前，必须检查用户当前分支与未提交修改，不能重置到这个提交。

## 阅读入口

先读 `CODEX_START_HERE.md`，然后读 `docs/HARDWARE_DESIGN.zh-CN.md`。具体软件衔接见 `docs/INTEGRATION_AND_PROTOCOL.zh-CN.md`；测试与每轮交付见 `docs/TEST_AND_RELEASE.zh-CN.md`；工具见 `docs/TOOLCHAIN.zh-CN.md`。

`contracts/axis_allocation.json` 已按照实际仓库的轴顺序分配完整 44 轴到六个区域节点。它**不是接线引脚表**；未定的针脚和实际关节限位明确为 null。

`tools/check_plan.py` 仅检查计划文件的内部一致性，也可以对本地仓库进行只读的轴顺序与基线哈希检查。其成功不代表机械强度、电路安全、传感器精度或 UE 新增硬件功能已经通过。

```powershell
python .\tools\check_plan.py
python .\tools\check_plan.py --repo "D:\YourProject\DollSimulation"
```

所有物理测试初始均为 `not_run`。先交付全身结构布局与第一轮少量试件，不直接采购全身电子元件，不自动提交 PCB 订单或启动打印机。
