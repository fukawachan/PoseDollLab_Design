param([string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
$poseDollRunner = Join-Path $PSScriptRoot 'run_cad.py'
& $Python $poseDollRunner (Join-Path $poseDollRoot 'cad/revF/verify_design.py') --begin
if ($LASTEXITCODE -ne 0) { throw 'Failed: source snapshot' }
foreach ($poseDollStage in @('pivot.py','fork_joint.py','arm_packaging.py','build_review.py','verify_design.py')) {
    Write-Host ('Rev F: ' + $poseDollStage)
    & $Python $poseDollRunner (Join-Path $poseDollRoot ('cad/revF/' + $poseDollStage))
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $poseDollStage) }
}
& $Python (Join-Path $poseDollRoot 'tools/report_revF.py')
if ($LASTEXITCODE -ne 0) { throw 'Failed: report_revF.py' }
Write-Host 'Rev F development CAD and numerical checks rebuilt. Manufacturing release remains false.'
