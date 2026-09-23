# 资料与审阅范围

核对日期：2026-09-19。软件在线文档的 stable/latest 地址会变化；执行时下载或记录确切版本、访问日期和原始文件哈希。以下为原厂文档、项目源码或厂家数据手册；不将搜索摘要、商城宣传参数或第三方接线示例作为电路放行依据。

## 仓库来源

R1. 仓库 README：软件功能、UE 5.8.2、现有资产与已报告验收范围。
https://github.com/fukawachan/DollSimulation/blob/7c22e075fe0efe295ce2935a8bb2a92cff0b6def/README.md

R2. 架构实现：校准所有权、独立数学、故障状态、Control Rig、Clutch/接触/采集和物理验证边界。
https://github.com/fukawachan/DollSimulation/blob/7c22e075fe0efe295ce2935a8bb2a92cff0b6def/ARCHITECTURE_PoseDoll.md

R3. 44 轴虚拟机械 profile：轴 ID、顺序、54 节点及“非制造设计”声明。
https://github.com/fukawachan/DollSimulation/blob/7c22e075fe0efe295ce2935a8bb2a92cff0b6def/Shared/Profiles/virtual_humanoid_44_v1.json
Git blob SHA-1：54f4718d5aeb3b25060c5e2b17648c69b5a8a352。
本交接包的轴清单通过与当前会话中原始设计 ZIP 的同名内容比较 Git blob 哈希一致后生成；未修改仓库。

R4. sample schema：字段、字符串序号与时间戳、null/status、禁止额外字段。
https://github.com/fukawachan/DollSimulation/blob/7c22e075fe0efe295ce2935a8bb2a92cff0b6def/Shared/Contracts/sample.schema.json

R5. 当前 C++ profile 加载与 session 初始化：固定虚拟配置与校准文件的迁移点。
https://github.com/fukawachan/DollSimulation/blob/7c22e075fe0efe295ce2935a8bb2a92cff0b6def/Plugins/PoseDoll/Source/PoseDollCore/Private/PoseDollCore.cpp
https://github.com/fukawachan/DollSimulation/blob/7c22e075fe0efe295ce2935a8bb2a92cff0b6def/Plugins/PoseDoll/Source/PoseDollEditor/Private/PoseDollSession.cpp

本次读取了上述关键文档/配置和相关源码段，不代表对全部仓库的代码、安全或测试做了完整审计。没有在本环境运行 Unreal Editor。

## 工具与器件原始资料

S1. Bambu Lab A1 mini 官方规格/FAQ：180×180×180 mm，适配材料类别。页面可能按地区重定向。
https://bambulab.com/en/a1-mini/tech-specs
https://wiki.bambulab.com/en/a1-mini/manual/faq
https://eu.store.bambulab.com/products/a1-mini

S2. CadQuery 官方文档：脚本式参数化 CAD、导出与装配。
https://cadquery.readthedocs.io/en/latest/intro.html
https://cadquery.readthedocs.io/en/latest/assy.html

S3. KiCad CLI 官方文档（核对的是 9.0 文档中的能力，不把它声称为当前唯一/最新版本）。
https://docs.kicad.org/9.0/en/cli/cli.html

S4. Infineon AS5048A 官方产品页：绝对角测量、14-bit、SPI/PWM。页面部分参数加载不全；经营状态/确切料号在采购时重新核对。不要把网页中的绝对极限电压范围当作推荐工作电压。
https://www.infineon.com/part/AS5048A

S5. ams AS5048A/AS5048B 厂家数据手册，v1-11, 2018-Jan-29（由 Mouser 托管的原厂 PDF）。实际采购前再次核对对应料号的有效最新版。重点核对接口/诊断、供电、磁铁选择与安装。
https://www.mouser.com/datasheet/2/588/AS5048_DS000298_4-00-1100510.pdf
本次读取了相关文本，并查看打印页码 7、30、31 的页面图像。最终设计不能仅用此链接标题或商城模块照片代替规格审核。

S6. Espressif ESP32-S3 TWAI：外部收发器、经典CAN而非CAN-FD。
https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/twai.html

S7. KiCad IPC API：对运行中的 KiCad 实例提供编程访问；不是无界面的自动设计工具。
https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/index.html

S8. ESP-IDF 官方 idf.py 文档；USB 设备栈文档。
https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/tools/idf-py.html
https://docs.espressif.com/projects/esp-usb/en/latest/esp32s3/usb_device.html

## 工程推导与假设

500 mm 身高、六区域分配、SPI 起始时钟、CAN 500 kbit/s/100 Hz、采样时间窗口、打印件160 mm优选包络、扭矩余量和验收阈值均为本项目设计选择，不是上述厂商保证。

扭矩与总线带宽的数字是由文档中明确的假设计算所得，必须以实际尺寸、质量、数据包开销和实测更新。资料核对不等于已经完成硬件设计或验证。
