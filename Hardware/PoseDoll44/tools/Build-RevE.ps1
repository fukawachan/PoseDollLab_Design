param([string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe')
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
$poseDollRunner = Join-Path $PSScriptRoot 'run_cad.py'
foreach ($poseDollStage in @('character_reference.py','check_proportions.py','build_layout.py','build_review.py')) {
    Write-Host ('Rev E: ' + $poseDollStage)
    & $Python $poseDollRunner (Join-Path $poseDollRoot ('cad/revE/' + $poseDollStage))
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $poseDollStage) }
}
& $Python (Join-Path $PSScriptRoot 'report_revE.py')
if ($LASTEXITCODE -ne 0) { throw 'Failed: report_revE.py' }
$poseDollResults = Get-Content -LiteralPath (Join-Path $poseDollRoot 'verification/revE_kinematic_comparison.json') -Raw | ConvertFrom-Json
foreach ($poseDollName in @('manny','quinn')) {
    $poseDollCharacter = $poseDollResults.characters.$poseDollName
    if (-not $poseDollCharacter.neutral_proportion_gate_passed) { throw ('Neutral proportion check failed: ' + $poseDollName) }
    if (-not $poseDollCharacter.position_gate_passed) { Write-Warning ($poseDollName + ': dynamic position target not met. Read verification/REVE_REPORT.zh-CN.md. Manufacturing release remains false.') }
}
Write-Host 'Rev E references and reports rebuilt. This command does not release manufacturing.'
