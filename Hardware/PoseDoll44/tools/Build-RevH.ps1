param([string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
foreach ($poseDollStage in @('shoulder_mechanism.py','build_review.py')) {
    & $Python (Join-Path $PSScriptRoot 'run_cad.py') (Join-Path $poseDollRoot ('cad/revH/' + $poseDollStage))
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $poseDollStage) }
}
& $Python (Join-Path $PSScriptRoot 'report_revH.py')
if ($LASTEXITCODE -ne 0) { throw 'Failed: report_revH.py' }
Write-Host 'Rev H packaging rebuilt. Review pose restrictions and incomplete holding/readout assemblies.'
