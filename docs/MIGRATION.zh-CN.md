# 独立设计仓库迁移记录

迁移日期：2026-09-23。旧位置 `E:/UnrealProjects/DollSimulation`，新位置为本 `design/` 仓库。

## 保存和归类

已移动 `Hardware/PoseDoll44`、`Firmware/PoseDollHardware`、`Firmware/PoseDollFullBody`、`Tools/PoseDollHardwareBridge`。原 `tmp/pdfs/posedoll_datasheets` 的两张元件图纸截图移入 `Hardware/PoseDoll44/references/migrated_datasheets`。

移动前逐文件记录长度与 SHA-256，移动后、路径修复前全部重新读取验证：**18,285 个文件，6,872,350,860 字节一致**。原五个源目录均已不存在。摘要见 [migration_file_verification.json](migration_file_verification.json)，完整清单保留在本机 `.local/migration/before.json`。

UE 工程、插件、Content、模拟器及其环境留在原位置。硬件工具使用的 `Shared/`、四个 Python 核心模块和三份原有测试复制为独立兼容快照，来源见 [software_snapshot.json](software_snapshot.json)。`planning/` 是原规划包的副本。

## 搬迁后调整

- 新增根 README、Git 忽略规则、原始行尾保留规则和独立 Python 环境说明。
- 原硬件 README 指向 Rev N1 和新的根入口。
- `sensor_revC_mini/fp-lib-table` 的自定义封装库由旧绝对路径改为 `${KIPRJMOD}/PoseDoll.pretty`；没有改变 PCB 布局。
- `export_character_reference_ue.py` 改为根据脚本位置选择输出目录，避免再次向 UE 工程创建硬件目录。
- 本地 `local_toolchain.json` 与 Rev M 构建入口默认数值环境均指向本仓库 `.venv`；本机配置不入 Git，另附配置示例。当前构建说明也改为独立仓库入口。
- 新增独立检查/构建/查看器入口。固件旧路径缓存由新构建入口保留式归档，原始固件代码未改。

机械 CAD、关节参数、41 轴数据含义、电路网络和固件逻辑均未在本次迁移中重新设计。历史交付清单保留原内容；其中覆盖说明文件或工具文件的哈希可能因上述整理变化，不能直接把整份历史清单当作本次提交的完整快照。69 个当前机械来源文件的哈希另行核对保持一致。

## 本轮检查

- 独立仓库检查：69 个机械来源、30 个协议/配置快照文件通过。
- Python：81 个已有测试通过；C：9 个采集批次/序列化场景通过；C/Python 黄金数据帧逐字节一致。
- 从仅含 Git 暂存文件的独立副本复测，同样通过 81 个 Python 测试、9 个 C 场景和黄金帧一致性检查。
- CAD 从新目录加载两款原始模型并在内存应用 N1 修订，各 1,994 实体。三维查看器无控制台错误，两款 STEP/BOM 下载链接正常。
- Git 必要设计输入完整收录，无单文件达到 50 MB；具体结果见 [migration_checks.json](migration_checks.json)。

没有重新执行耗时的全身碰撞和制造验证；也没有打开硬件串口、烧录、采购、推送远端或修改正在使用的 UE 配置。

## 哪些文件不在 Git

大型导出和缓存仍位于各自原相对目录，避免打断本机查看器和历史交付引用。`.gitignore` 只控制版本收录，没有删除这些文件。源码仓库包含所需的小型生成输入（例如板级 STEP、角色基准点）、交付清单、数字检查数据；不包含全部导出实物。

原固件构建缓存保存了旧 CMake 绝对路径。后续请使用根 `scripts/Build-Design.ps1 -Stage Firmware`，它会先归档不匹配的缓存；不要把缓存直接当作可在任何目录重用的源工程。
