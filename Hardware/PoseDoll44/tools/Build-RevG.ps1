param([string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
$poseDollRunner = Join-Path $PSScriptRoot 'run_cad.py'
foreach ($poseDollStage in @('analyze_envelopes.py','centerline_study.py','shoulder_study.py')) {
    Write-Host ('Rev G: ' + $poseDollStage)
    & $Python $poseDollRunner (Join-Path $poseDollRoot ('cad/revG/' + $poseDollStage))
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $poseDollStage) }
}
& $Python (Join-Path $poseDollRoot 'tools/report_revG.py')
if ($LASTEXITCODE -ne 0) { throw 'Failed: report_revG.py' }
Write-Host 'Rev G study rebuilt. Physical shoulder and compliant covers remain unvalidated.'
