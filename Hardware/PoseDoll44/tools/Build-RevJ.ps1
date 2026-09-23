param([string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
foreach ($poseDollStage in @('build_and_verify.py','check_tool_access.py','check_readout.py','export_components.py','load_budget.py','build_review.py')) {
    & $Python (Join-Path $PSScriptRoot 'run_cad.py') (Join-Path $poseDollRoot ('cad/revJ/' + $poseDollStage))
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $poseDollStage) }
}
& $Python (Join-Path $PSScriptRoot 'report_revJ.py')
if ($LASTEXITCODE -ne 0) { throw 'Failed: report_revJ.py' }
Write-Host 'Rev J drive and readout candidate rebuilt; not released for manufacture.'
