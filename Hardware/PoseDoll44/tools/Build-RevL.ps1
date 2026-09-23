param([string]$Python='C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference='Stop'
$poseDollRoot=Split-Path $PSScriptRoot -Parent
& $Python (Join-Path $PSScriptRoot 'run_cad.py') (Join-Path $poseDollRoot 'cad/revL/build_all_l.py')
if ($LASTEXITCODE -ne 0) { throw 'Rev L CAD build or verification failed.' }
& $Python (Join-Path $PSScriptRoot 'report_revL.py')
if ($LASTEXITCODE -ne 0) { throw 'Rev L evidence report failed.' }
Write-Host 'Rev L rebuilt. Browser evidence is separate; no manufacturing release.'
