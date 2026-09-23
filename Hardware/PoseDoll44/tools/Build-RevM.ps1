[CmdletBinding()]
param(
  [ValidateSet('All','CAD','Electronics','Firmware','OfflineTests','Reports','Delivery')][string]$Stage='OfflineTests',
  [string]$CodePython='C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe',
  [string]$NumericPython='',
  [string]$KiCadPython='D:/ProgramFiles/KiCad/10.0/bin/python.exe',
  [string]$NodeRuntime='C:/Users/Ding/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
)
$ErrorActionPreference='Stop'
$HardwareRoot=Split-Path $PSScriptRoot -Parent
$RepoRoot=Split-Path (Split-Path $HardwareRoot -Parent) -Parent
if (!$NumericPython) { $NumericPython=Join-Path $RepoRoot '.venv/Scripts/python.exe' }
function Invoke-Checked([string]$Program,[string[]]$CommandArgs) {
  & $Program @CommandArgs
  if ($LASTEXITCODE -ne 0) { throw "Command failed: $Program $CommandArgs" }
}
function Invoke-CAD([string]$Script) {
  Invoke-Checked $CodePython @('-X','utf8','Hardware/PoseDoll44/tools/run_cad.py',"Hardware/PoseDoll44/cad/revM/$Script")
}
Push-Location $RepoRoot
try {
  if ($Stage -in @('All','Firmware')) {
    Invoke-Checked $CodePython @('-X','utf8','Hardware/PoseDoll44/tools/build_firmware_revM.py')
    Invoke-Checked $CodePython @('-X','utf8','Hardware/PoseDoll44/tools/package_firmware_revM.py')
  }
  if ($Stage -in @('All','Electronics')) { Invoke-Checked $KiCadPython @('Hardware/PoseDoll44/tools/package_electronics_revM.py') }
  if ($Stage -in @('All','CAD')) {
    Invoke-CAD 'final_model.py'
    Invoke-CAD 'export_complete.py'
    Invoke-CAD 'export_print_meshes.py'
    Invoke-CAD 'export_delivery_details.py'
    Invoke-Checked $NumericPython @('-X','utf8','Hardware/PoseDoll44/tools/build_harness_revM.py')
    Invoke-Checked $NumericPython @('-X','utf8','Hardware/PoseDoll44/tools/verify_harness_power_revM.py')
    Invoke-CAD 'audit_complete.py'
    Invoke-CAD 'check_assembly_access.py'
    Invoke-CAD 'check_print_process.py'
  }
  if ($Stage -in @('All','OfflineTests')) {
    Invoke-Checked $CodePython @('-X','utf8','Firmware/PoseDollFullBody/tools/generate_config.py','--check')
    Invoke-Checked './Firmware/PoseDollFullBody/tools/run_core_tests.cmd' @()
    Invoke-Checked $NumericPython @('-X','utf8','Hardware/PoseDoll44/tools/run_offline_tests_revM.py')
  }
  if ($Stage -in @('All','Reports','CAD')) {
    Invoke-Checked $NumericPython @('-X','utf8','Hardware/PoseDoll44/tools/verify_print_exports_revM.py')
    Invoke-Checked $NumericPython @('-X','utf8','Hardware/PoseDoll44/tools/verify_proportions_revM.py')
    Invoke-Checked $NumericPython @('-X','utf8','Hardware/PoseDoll44/tools/verify_kinematic_mapping_revM.py')
    Invoke-Checked $CodePython @('-X','utf8','Hardware/PoseDoll44/tools/build_procurement_revM.py')
    Invoke-Checked $CodePython @('-X','utf8','Hardware/PoseDoll44/tools/strength_handling_revM.py')
  }
  if ($Stage -in @('All','Delivery')) {
    Invoke-Checked $NodeRuntime @('Hardware/PoseDoll44/tools/check_viewer_revM.cjs')
    Invoke-Checked $CodePython @('-X','utf8','Hardware/PoseDoll44/tools/finalize_delivery_revM.py')
  }
  Write-Output 'Selected stage complete. No firmware was flashed and no hardware port was opened.'
} finally { Pop-Location }
