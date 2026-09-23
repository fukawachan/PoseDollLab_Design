# 资料与尺寸来源

核对日期 2026-09-20。外部资料不等同于供应商对当前实物版本的确认。

| 原始资料 | 本轮用途 / 限制 |
|---|---|
| [ams AS5048A/B DS000298 v1-11，2018-01-29，分销商保存的原厂PDF](https://www.mouser.com/datasheet/2/588/AS5048_DS000298_4-00-1100510.pdf) | 引脚、3.3V、SPI mode1/延迟响应/校验、诊断、封装；优先于旧评估板示例代码 |
| [ams AS5048-AB-v1.1 Rev1.2，RS保存的原厂PDF](https://docs.rs-online.com/0657/A700000006921305.pdf) | 老板22×28、孔位、Ø6×2.5径向磁铁；不证明现售EK_AB修订，不能套用自制板针脚 |
| [Espressif DevKitC-1 v1.1](https://documentation.espressif.com/esp-dev-kits/en/latest/esp32s3/esp32-s3-devkitc-1/user_guide_v1.1.html) | 开发板信号/供电/USB，到货后核对实物 |
| [DevKitC-1 尺寸图](https://dl.espressif.com/dl/PCB_ESP32-S3-DevKitC-1_V1_20210312CB.pdf) | 约25.4×62.74；不能声称完整DevKit能塞进40×58区域板框，区域板仍为自制占位 |
| [Waveshare CAN 板](https://www.waveshare.com/wiki/SN65HVD230_CAN_Board) | 后续台架候选，终端电阻未实测 |
| [JST GH 图纸](https://www.jst.com/wp-content/uploads/2021/08/eGH-new.pdf) | 连接器及线束，最终线序需逐线检验 |
| [KiCad 10 CLI](https://docs.kicad.org/10.0/en/cli/cli.html) | 实际运行10.0.6的ERC、DRC、网表和渲染 |
| [CadQuery](https://cadquery.readthedocs.io/en/latest/) | 实际库2.7.0，加载器另有说明 |

自行设计的占位假设：S/M/L关节圆柱、区域板40×58×12、网关70×45×20、支架与关节偏移。质量、力矩能力、线束余量为预算输入。

自制PCB的32×32/孔距26和H1托架是确切的设计尺寸；制造公差尚未验证。摩擦材料、胶接、五金公差、磁性能及桌夹额定力矩均未冻结。

## Rev B 打印配合来源

2026-09-20 读取用户提供的 [PLA材料比较](chatgpt-conversation://6aaf5e4b-487c-83ea-80e1-e14bc6727b53)。本地落实方式见 [设计依据](DESIGN_BASIS.zh-CN.md)。

| 来源 | 支持的结论与边界 |
|---|---|
| [Bambu Studio 2.0 官方发布说明](https://github.com/bambulab/BambuStudio/releases/tag/v02.00.00.95) | 具有自动圆孔/轮廓补偿；此版本说明不保证 A1 mini 的成品孔径 |
| [Bambu Studio 官方 PrintConfig.cpp](https://raw.githubusercontent.com/bambulab/BambuStudio/master/src/libslic3r/PrintConfig.cpp) | XY 孔与外轮廓补偿分开；正孔补偿使孔变大 |
| [A1 mini 用户原始报告](https://www.reddit.com/r/BambuLab/comments/1izxcl4/) | 个例称孔约小 0.4 mm；缺少完整试验条件，不能外推成固定误差 |

官方 Wiki 两个补偿说明页面本次未能读取；未将其正文当作已核对证据。工程中的 -0.4/-0.2/0/+0.1 mm 为主动选择的直径情景，未给它们附加概率或“官方公差”含义。该材料选择与软件配方尚未经用户机器验证。


## Rev C / H2 新增来源

- [SCHNORR 原厂碟簧目录](https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf)：000300 的 8×3.2×0.3 mm 尺寸、自由高度及指定挠度下的力；组弹力是设计推算，尚未实测。
- [AS5048 原厂数据手册](https://look.ams-osram.com/m/287d7ad97d1ca22e/original/AS5048-DS000298.pdf)：接口、电源、磁铁布置与场强验收的依据。实板磁场、邻近金属和多磁铁影响尚未验证。
- 安装的 KiCad 10.0.6 官方符号、封装与 3D 库：Rev B 电路板和机械 STEP 的直接来源；以实际 PCB/STEP 和机械接口文件为准。

## Rev M 完整人偶追加资料（2026-09-23）

上方 Rev A/B/C 的区域板、关节和支架尺寸是历史记录。当前交付以 [START_HERE](../START_HERE.zh-CN.md) 和 Rev M 清单为准。

| 来源 | 本轮使用与限制 |
|---|---|
| [AS5048A 原厂数据手册](https://look.ams-osram.com/m/287d7ad97d1ca22e/original/AS5048-DS000298.pdf) | 供电、SPI、磁场与 15 mA 电流预算；不把 14 位分辨率当实际测角精度 |
| [ams OSRAM 磁铁选型指南，2025-04-10](https://look.ams-osram.com/m/1f9fec31c21d8f4d/original/Magnet-selection-guide-rotary-magnetic-position-sensors.pdf) | AS5000-MD6H-2、Ø6×2.5、径向充磁；具体磁场及到货情况未实测 |
| [JST SH](https://www.jst-mfg.com/product/pdf/eng/eSH.pdf)、[JST GH](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)、[JST PH](https://order.jst-mfg.com/InternetShop/app/pdf_show?kbn=1&key=ePH.pdf) | 接头尺寸、针序标记、端子导体与绝缘外径范围；不是只看 AWG 名称 |
| [Alpha Wire 原厂目录](https://www.alphawire.com/-/media/Project/AlphaWire/AlphaWire/2023-Master-Catalog/2023-MasterCat-English-20230609.pdf?rev=08a9584660404c8dad92412e1b961875) | 2841/7、5851、3049 的导体与外径；并未宣称这些线有本项目的连续弯折寿命评级 |
| [Murata C2 原厂 PDF，Arrow 保存](https://static6.arrow.com/aropdfconversion/aad06a23287b10a4c30c6326cae87fb115e24ef/grm219r61e106ka12.pdf) | GRM219R61E106KA12D，10 μF / 25 V / X5R；最大本体高 0.95 mm。另加 0.10 mm 焊接高度是本设计分配 |
| [ESP32-S3-WROOM-1/1U](https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf) | 160 MHz 双核全时钟约 81.1 mA 为典型条件，不是最大电流保证；本设计 150 mA 模块预算需实测 |
| [TCAN332](https://www.ti.com/lit/ds/symlink/tcan332.pdf) | 3.3 V CAN、显性状态耗流及断电行为；总线线束仍需实机检验 |
| [TPS62162](https://www.ti.com/lit/ds/symlink/tps62162.pdf)、[TS3USB221E](https://www.ti.com/lit/ds/symlink/ts3usb221e.pdf) | 降压布局、USB 隔离和 Ioff；80% 效率为本设计预算假设 |
| [AO4409](https://www.aosmd.com/res/datasheets/AO4409.pdf) | 反接保护管 −4.5 V 条件导通电阻；未实测整板浪涌 |
| [Littelfuse 1206L](https://www.littelfuse.com/assetdocs/littelfuse-ptc-1206l-datasheet?assetguid=2b6a1515-d4ee-4c83-8bd4-152b4901b8f5)、[451/453](https://www.littelfuse.com/assetdocs/fuse-451-and-453-datasheet?assetguid=533cd5cc-956c-4243-867f-6ab5a62f6ba1) | 1206L075/13.2WR 的温度降额与阻值；0451003.MRL 为 3 A，不是曾讨论的 3.5 A |
| [Same Sky PJ-002AH](https://www.sameskydevices.com/product/resource/pj-002ah.pdf) | 插座外形、安装槽孔与额定值。图纸已另做 PDF 页面视觉核对；系统仍仅允许 5 V 输入 |
| [Panasonic EEEFP1C101AP](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-smd/models/EEEFP1C101AP) | 100 μF / 16 V，6.3×5.8 mm 电容；不可用旧 8 mm 高包络 |
| [Lite-On LTST-C190KGKT](https://optoelectronics.liteon.com/upload/download/DS22-2000-074/LTST-C190KGKT.PDF) | 电源指示灯尺寸与电气参数 |
| [SCHNORR 碟簧目录](https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf) | 本版使用 001200、001800、002050、002100、002200；并串联堆叠力为设计计算，不是实测 |
| [Ensinger TECAPEEK natural](https://www.ensingerplastics.com/en-us/shapes/peek-tecapeek-natural) | 未填充 PEEK 候选、密度及材料性质。摩擦系数 0.15 是本项目假设，非该资料保证的最小值 |
| [SKF 复合滑动轴承资料](https://cdn.skfmediahub.skf.com/api/public/0901d19680090e01/pdf_preview_medium/0901d19680090e01_pdf_preview_medium.pdf) | PCMW 102001.5 E 止推垫圈尺寸；整机耐磨和保持仍须验证 |
| [Accu SSB-M3-8-TI5](https://accu-components.com/us/socket-button-screws/422924-SSB-M3-8-TI5) | Grade 5 钛按钮头，5.7×1.65 mm 包络、2 mm 内六角；网页不是按钮头在本预紧力下的保载证书或现货承诺 |
| [Henkel LOCTITE 222](https://datasheets.tdx.henkel.com/LOCTITE-222-en_GL.pdf)、[3M DP460](https://www.3m.com.cn/3M/zh_CN/p/d/b40066439/) | 全金属小螺纹防松、磁铁杯胶接候选；塑料相容性、固化与滑移需要首件验证 |
| [KiCad 库许可](https://www.kicad.org/libraries/license/) | 自包含项目携带的官方库子集保留来源；项目中的定制尺寸包络不是供应商精确 STEP |

人物比例来自本地项目先前导出的 `/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple` 和 `SKM_Quinn_Simple` 的骨骼/参考网格数据；原始来源哈希在 Rev E 比例基线及最终 CAD 输入清单内。当前缩放 0.5；旧 Rev E 图表的 1/3 数值需要乘以 1.5 才能与当前毫米尺寸比较。
