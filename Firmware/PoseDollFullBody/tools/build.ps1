param([ValidateRange(1,6)][int]$Node=1)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path -LiteralPath "$PSScriptRoot/..").Path
$env:IDF_PATH='D:/ProgramFiles/esp/v6.1/esp-idf'
$env:IDF_TOOLS_PATH='C:/Espressif/tools'
$env:IDF_PYTHON_ENV_PATH='C:\Espressif\tools\python\v6.1\venv'
$env:ESP_ROM_ELF_DIR='C:/Espressif/tools/esp-rom-elfs/20241011'
$env:IDF_COMPONENT_LOCAL_STORAGE_URL='file://C:/Espressif/tools'
$env:PYTHONUTF8='1'
$env:IDF_PY_BUILD_JOBS='4'
$env:ESP_IDF_VERSION='6.1'
$env:IDF_VERSION='6.1.0'
$env:PATH='C:/Espressif/tools/python/v6.1/venv/Scripts;C:/Espressif/tools/cmake/4.0.3/bin;C:/Espressif/tools/ninja/1.12.1;C:/Espressif/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin;C:/Espressif/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin;'+$env:PATH
Set-Location -LiteralPath $taskRoot
$taskDefaults=(Get-Content -LiteralPath "$taskRoot/sdkconfig.defaults" -Raw).Replace('CONFIG_PD_NODE_ID=1',"CONFIG_PD_NODE_ID=$Node")
Set-Content -LiteralPath "$taskRoot/sdkconfig.node$Node.defaults" -Value $taskDefaults -Encoding utf8
& "$env:IDF_PYTHON_ENV_PATH/Scripts/python.exe" "$env:IDF_PATH/tools/idf.py" -B "build_node$Node" "-DSDKCONFIG=$taskRoot/build_node$Node/sdkconfig" "-DSDKCONFIG_DEFAULTS=$taskRoot/sdkconfig.node$Node.defaults" build
exit $LASTEXITCODE
