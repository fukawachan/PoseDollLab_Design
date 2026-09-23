# 完整 44 轴与区域端口清单

来源：实际仓库虚拟 profile；轴顺序保持一致。端口为逻辑编号，不是连接器针脚。参考范围不可直接当作实体制造限位。

| 协议索引（从0） | 轴 ID | 动作 | 区域节点 / 端口 | 软件参考范围（度） |
|---:|---|---|---|---|
| 0 | `pelvis.yaw` | 骨盆支架左右转动 | N1 / P01 | -90 至 90 |
| 1 | `pelvis.pitch` | 骨盆支架前后俯仰 | N1 / P02 | -30 至 45 |
| 2 | `pelvis.roll` | 骨盆支架左右侧倾 | N1 / P03 | -25 至 25 |
| 3 | `waist.yaw` | 腰部左右转动 | N1 / P04 | -35 至 35 |
| 4 | `waist.pitch` | 腰部前后俯仰 | N1 / P05 | -20 至 40 |
| 5 | `waist.roll` | 腰部左右侧倾 | N1 / P06 | -25 至 25 |
| 6 | `chest.yaw` | 胸部左右转动 | N2 / P01 | -35 至 35 |
| 7 | `chest.pitch` | 胸部前后俯仰 | N2 / P02 | -20 至 30 |
| 8 | `chest.roll` | 胸部左右侧倾 | N2 / P03 | -20 至 20 |
| 9 | `head.yaw` | 颈头左右转动 | N2 / P04 | -75 至 75 |
| 10 | `head.pitch` | 颈头前后俯仰 | N2 / P05 | -45 至 55 |
| 11 | `head.roll` | 颈头左右侧倾 | N2 / P06 | -35 至 35 |
| 12 | `clavicle_l.protract` | 左肩带前伸/后收 | N3 / P01 | -20 至 30 |
| 13 | `clavicle_l.elevate` | 左肩带抬高/下压 | N3 / P02 | -15 至 30 |
| 14 | `upperarm_l.flex` | 左肩前举/后摆 | N3 / P03 | -50 至 160 |
| 15 | `upperarm_l.abduct` | 左肩外展/内收 | N3 / P04 | -30 至 150 |
| 16 | `upperarm_l.twist` | 左上臂轴向旋转 | N3 / P05 | -90 至 90 |
| 17 | `elbow_l.flex` | 左肘屈曲 | N3 / P06 | 0 至 145 |
| 18 | `forearm_l.twist` | 左前臂轴向旋转 | N3 / P07 | -90 至 90 |
| 19 | `hand_l.flex` | 左手腕掌背屈 | N3 / P08 | -65 至 65 |
| 20 | `hand_l.deviate` | 左手腕侧偏 | N3 / P09 | -25 至 35 |
| 21 | `thigh_l.flex` | 左髋前抬/后伸 | N5 / P01 | -30 至 125 |
| 22 | `thigh_l.abduct` | 左髋外展/内收 | N5 / P02 | -25 至 65 |
| 23 | `thigh_l.twist` | 左大腿轴向旋转 | N5 / P03 | -50 至 50 |
| 24 | `calf_l.flex` | 左膝屈曲 | N5 / P04 | 0 至 145 |
| 25 | `foot_l.dorsiflex` | 左脚踝抬脚尖/压脚尖 | N5 / P05 | -45 至 30 |
| 26 | `foot_l.invert` | 左脚踝侧倾 | N5 / P06 | -25 至 25 |
| 27 | `ball_l.flex` | 左前脚掌弯曲 | N5 / P07 | -20 至 60 |
| 28 | `clavicle_r.protract` | 右肩带前伸/后收 | N4 / P01 | -20 至 30 |
| 29 | `clavicle_r.elevate` | 右肩带抬高/下压 | N4 / P02 | -15 至 30 |
| 30 | `upperarm_r.flex` | 右肩前举/后摆 | N4 / P03 | -50 至 160 |
| 31 | `upperarm_r.abduct` | 右肩外展/内收 | N4 / P04 | -30 至 150 |
| 32 | `upperarm_r.twist` | 右上臂轴向旋转 | N4 / P05 | -90 至 90 |
| 33 | `elbow_r.flex` | 右肘屈曲 | N4 / P06 | 0 至 145 |
| 34 | `forearm_r.twist` | 右前臂轴向旋转 | N4 / P07 | -90 至 90 |
| 35 | `hand_r.flex` | 右手腕掌背屈 | N4 / P08 | -65 至 65 |
| 36 | `hand_r.deviate` | 右手腕侧偏 | N4 / P09 | -25 至 35 |
| 37 | `thigh_r.flex` | 右髋前抬/后伸 | N6 / P01 | -30 至 125 |
| 38 | `thigh_r.abduct` | 右髋外展/内收 | N6 / P02 | -25 至 65 |
| 39 | `thigh_r.twist` | 右大腿轴向旋转 | N6 / P03 | -50 至 50 |
| 40 | `calf_r.flex` | 右膝屈曲 | N6 / P04 | 0 至 145 |
| 41 | `foot_r.dorsiflex` | 右脚踝抬脚尖/压脚尖 | N6 / P05 | -45 至 30 |
| 42 | `foot_r.invert` | 右脚踝侧倾 | N6 / P06 | -25 至 25 |
| 43 | `ball_r.flex` | 右前脚掌弯曲 | N6 / P07 | -20 至 60 |
