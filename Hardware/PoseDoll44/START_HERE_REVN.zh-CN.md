# Rev N1 · 胸口取消罩壳与背部外置评估

**已实施：两款人偶取消胸口罩壳、两颗螺钉和两颗螺母。** 胸部承重骨架和所有关节中心保持 Rev M，另修正左肩支座与旋转限位拨片的局部刮碰；各有 186 个打印件。背部仍保留原六个电子仓，外置方案是待重新布局的架构建议。

- [打开新三维查看器](http://127.0.0.1:8874/generated/revN/RevN_Chest_Review.html) · [本地 HTML](generated/revN/RevN_Chest_Review.html)
- [胸壳改动、接触减少数据与外置方案利弊](docs/CHEST_AND_EXTERNAL_REVN.zh-CN.md)
- [Manny 修订总装 STEP](generated/revN/manny/Manny_RevN1_assembly.step) · [Quinn 修订总装 STEP](generated/revN/quinn/Quinn_RevN1_assembly.step)
- [Manny 当前制造清单](generated/revN/manny/manufacturing_manifest.json) · [Quinn 当前制造清单](generated/revN/quinn/manufacturing_manifest.json)
- [碰撞复核记录](verification/revN_chest_audit.json) · [本轮文件清单](generated/revN/delivery_manifest.json)
- [原完整装配、电路和校准资料](START_HERE.zh-CN.md)（剔除取消的 5 件，左肩支座使用 N1 图纸）

新查看器增加双手背后姿态，并保留仍存在的后背设备干涉。不要把该姿态或外置方案理解成已经制造验证。无需现在采购或打印。

本轮 CAD 入口为 [chest_clearance.py](cad/revN/chest_clearance.py)。原版完整交付清单是 Rev M 时点的快照；当前入口提示的文字更新不会改变其几何文件。
