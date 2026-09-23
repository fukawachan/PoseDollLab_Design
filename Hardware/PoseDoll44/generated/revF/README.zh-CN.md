# Rev F 文件目录

当前是按新比例建立的机械集成候选，尚未制造放行。

- [可旋转的机械查看页](RevF_Mechanical_Review.html)
- [CQ-editor 入口](../../cad/revF/open_in_cq_editor.py)
- [Manny 左臂部分总装](variants/manny/Manny_arm_packaging.step)
- [Quinn 左臂部分总装](variants/quinn/Quinn_arm_packaging.step)
- [S6 独立叉架](joints/J_S6/RevF_J_S6.step) · [M6](joints/J_M6/RevF_J_M6.step) · [H6](joints/J_H6/RevF_J_H6.step) · [L8](joints/J_L8/RevF_J_L8.step)
- 摩擦端与测角端组件：`joints/S6`、`M6`、`H6`、`L8`、`E6`、`E8`，各含组件 STEP 和部分独立零件 STEP。
- 两款独立连接件位于各自 `variants` 文件夹：`upperarm_datum_link.step`、`forearm_return_link.step`。

每款手臂只有肘屈伸、腕屈伸两轴已装入；顶部为临时肩部集成接口。其余转轴、完整手部、右侧和全身机构尚未完成。

[完整结构说明](../../docs/FORK_JOINT_REVF.zh-CN.md) · [验证报告](../../verification/REVF_REPORT.zh-CN.md) · [重建方法](../../docs/BUILD_REVF.zh-CN.md)
