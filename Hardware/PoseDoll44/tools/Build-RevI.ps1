param([string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
foreach ($poseDollStage in @('check_cartridge.py','check_tool_access.py','build_and_verify.py','load_budget.py','build_review.py')) {
    & $Python (Join-Path $PSScriptRoot 'run_cad.py') (Join-Path $poseDollRoot ('cad/revI/' + $poseDollStage))
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $poseDollStage) }
}
& $Python (Join-Path $PSScriptRoot 'report_revI.py')
if ($LASTEXITCODE -ne 0) { throw 'Failed: report_revI.py' }
Write-Host 'Rev I shoulder clutch candidate rebuilt; not released for manufacture.'
