# Quinn 目标适配待办

本轮已经建立 Quinn 自己的物理人偶比例基准，但没有修改或宣称完成 UE 插件的 Quinn 支持。现有 Manny 测试通过的功能继续保留。

## 已知输入

- 角色：`/Game/Characters/Mannequins/Meshes/SKM_Quinn_Simple`。
- 现有共享 rig：`/Game/Characters/Mannequins/Rigs/CR_Mannequin_Body`。
- 实体参数：`physical_quinn_44_revE_proportion`，44 轴名称/顺序与既有协议一致，尺寸和校准独立。
- 骨骼及网格来源：`reference/ue58/quinn_mesh_probe.json`、`quinn_geometry.json`，采集时使用各自 SkeletalMesh 的 GetRefSkeleton。
- 当前提取的共享 rig 初始骨架仍为 Manny 尺寸，与 Quinn 网格参考骨架最大相差约 17.90 mm（1:3），不能把原 Manny 角色配置直接更名为 Quinn。

## 后续实现要求

1. 为 Quinn 建立独立的角色 profile、网格/骨架指纹及 N 姿势校准。先调查共享 rig 在实际绑定、初始化和评估阶段如何取得骨长，确保输出使用 Quinn 的真实参考尺寸；需要时创建独立 rig 资产，保留原 Manny 资产。
2. 把目标网格的参考骨架与 rig 默认骨架区分开。检查肩宽、髋宽、上臂、前臂、大腿、小腿、躯干、手和脚；不能只核对骨骼名称相同。
3. 实体设备需要独立 device/calibration/profile 绑定。新参数不冒充 `virtual_humanoid_44_v1`；不要绕过当前对未识别配置的拒绝逻辑。
4. 检查中立、单肘 90°、单膝 90°、肩前举 90°、左右不对称姿势，再比较双手接触、扶额、叉腰、蹲坐等任务姿势。输出实际骨骼位置和控制器姿态，与 Rev E 参考数据比较。
5. 解决颈部多骨骼与实体 3 轴的轨迹差异，记录目标位置与方向误差。不要通过随意改变骨长掩盖误差。
6. 再验收 Control Rig 可编辑关键帧：Capture、Capture & Advance、Undo/Redo、保存、关闭输入源、重启 UE 后回读；手指/面部未测量部分不被覆盖。给 Quinn 建立独立的验收证据。
7. 回归已有 Manny 功能，确认两款角色能正确选择配置且不会互相覆盖校准。

离线数学预测与 CAD 参考不能代替上述引擎验收。这份待办明确后续接口工作，当前阶段无须用户测试。
