# Rev F 机械设计重建

在 `E:/UnrealProjects/DollSimulation` 运行：

```powershell
& ./Hardware/PoseDoll44/tools/Build-RevF.ps1
```

当前本机使用 Python 3.13 与已经安装的 CQ-editor 2.7 运行库。保持 CQ-editor 打开即可；脚本不安装依赖，也不写入 Python 模拟器环境。可用 `-Python` 指定兼容的 Python 3.13 路径。

构建按顺序执行：记录源码与依赖哈希 → 摩擦 / 测角组件 → 四套叉架 → 两款部分手臂 → 离线查看页及图像 → 汇总与负载检查 → 中文报告。请勿并行执行这些写入相同目录的脚本。

输出会覆盖 `generated/revF` 中同名文件、`verification/revF_*` 记录、中文 Rev F 报告和 `mechanical_manifest/dual_character_mechanics_revF.json`。Rev E 角色配置、原始 UE 参考网格、旧版 CAD、现有 UE 插件与模拟器不被改写。

当前源数据仍是上一轮从本地 Manny、Quinn 网格提取的尺寸，不需要重新打开 UE 导出。若角色资产或 Rev E 基准改变，应先重新完成 Rev E 比例验证，再重建 Rev F。

## 查看

- 双击 [离线三维页](../generated/revF/RevF_Mechanical_Review.html)：选 Manny / Quinn / 独立关节，拖动旋转、缩放、点击零件，或使用肘、腕滑块。
- CQ-editor 打开 [入口](../cad/revF/open_in_cq_editor.py)，设置 `VIEW='BOTH' / 'MANNY' / 'QUINN' / 'JOINT'`，再 Render。可修改 `ELBOW_DEG`、`WRIST_DEG` 看两个已装入转轴的姿态。
- STEP 总装及独立零件位于 [文件目录](../generated/revF/README.zh-CN.md)。本轮没有整机 STL 放行包。

独立关节脚本会检查 0° 至 330° 每 30° 的几何姿态，用来查找结构穿插。这不表示实际人偶允许整圈转动：线束、机械限位和多轴总装会限制范围。

汇总检查对无效几何、未解释的零件穿插、断开的打印实体、超过名义打印空间、改变的前臂长度和构建期间改变的源码返回失败。摩擦计算使用尚未验证的系数，报告只针对已装入部件；构建成功也不会将制造放行设为 true。
