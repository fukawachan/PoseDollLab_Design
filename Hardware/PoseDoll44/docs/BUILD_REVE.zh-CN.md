# Rev E 双角色重建

在仓库 `E:/UnrealProjects/DollSimulation` 运行：

```powershell
& ./Hardware/PoseDoll44/tools/Build-RevE.ps1
```

当前本机使用 Python 3.13 和已经安装的 CQ-editor 2.7 包，保持 CQ-editor 打开即可。脚本不安装依赖，不写入模拟器虚拟环境。已有正常 CadQuery / NumPy / VTK 环境时，也可以依次运行 `cad/revE/character_reference.py`、`check_proportions.py`、`build_layout.py`、`build_review.py` 和 `tools/report_revE.py`。

重建使用已经导出的 `reference/ue58` 只读参考数据：生成两份独立实体配置、完整中立尺寸、每款 1,087 个运动样本、两套 STEP 参考布局、PLY/NPZ 表面、预览图和无需联网的 HTML 三维查看器，最后更新设计说明和验证报告。`generated/revE` 与相应 Rev E 报告会重建覆盖。

正常完成不等于所有设计指标通过。当前中立比例通过，颈部动态指标失败，脚本会明确输出 warning 并保留失败详情。制造放行仍为 false。不会沿用旧 Rev C 碰撞检查作为新结构的检查结果。

## 数据来源更新

只有目标角色资产改变、需要更新参考数据时，才重新执行 [UE 提取脚本](../tools/export_character_reference_ue.py)。它读取每个 SkeletalMesh 的网格参考骨架、GeometryScript 网格与蒙皮权重，并创建临时 rig 检查实例；不保存网格、骨架或 Control Rig 资产。

当前本机命令如下，使用独立的无界面进程，不操作已打开的 UE 编辑器：

```powershell
& 'E:/UnrealEngine/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe' `
  'E:/UnrealProjects/DollSimulation/DollSimulation.uproject' `
  -run=pythonscript `
  -script='E:/UnrealProjects/DollSimulation/Hardware/PoseDoll44/tools/export_character_reference_ue.py' `
  -unattended -NullRHI -nosplash -nosound -nop4 -ModelContextProtocolPort=8011 `
  -abslog='E:/UnrealProjects/DollSimulation/Hardware/PoseDoll44/verification/reference_export_ue.log'
```

提取可能较慢。先核对日志、`reference/ue58/extraction.json` 中新时间及两款 JSON 是否齐全，再重建。当前项目已有 GameFeatures AssetManager 配置错误，提取结果完成后进程仍可能以 1 退出；不能仅凭此退出码判断几何数据成功或失败，也不能忽略其他错误。之前失败的无界面 FBX 导出路径已经不再使用。

## 查阅与打开

- 双击 `generated/revE/Manny_Quinn_3D_Review.html`，可离线旋转查看、选择角色、显示关节中心。网页减面只用于显示，完整几何和原始数据参与尺寸计算。
- CQ-editor 打开 `cad/revE/open_in_cq_editor.py`，Render。可设置 `CHARACTER='BOTH' / 'MANNY' / 'QUINN'` 与 `POSE`。
- 如需查看完整参考表面，使用各自的 PLY；STEP 仅含目标关节中心、轴线和连线。
- `study_neck_pivot.py` / `study_distributed_neck.py` 是独立的枢轴调整研究，不会修改正式实体参数，也不属于日常重建步骤。

与实际制造有关的孔径、公差、持姿材料、采购件和装配要求，须待机构完成后另行生成；本目录没有整机 STL 打印放行包。
