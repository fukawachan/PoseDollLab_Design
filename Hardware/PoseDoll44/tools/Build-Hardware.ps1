param([switch]$Regenerate,[switch]$Firmware,[switch]$SkipGeometry,[switch]$MechanicalOnly)
if ($MechanicalOnly -and $Firmware) { throw 'MechanicalOnly cannot include a firmware rebuild.' }
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$repoRoot=Split-Path (Split-Path $taskRoot -Parent) -Parent
$verify=Join-Path $taskRoot 'verification'
$cfg=Get-Content (Join-Path $PSScriptRoot 'local_toolchain.json') -Raw | ConvertFrom-Json
$results=[Collections.Generic.List[object]]::new()
function Run-Check([string]$name,[string]$exe,[string[]]$argv) {
    Write-Host "[$name]"
    $log=Join-Path $verify ($name+'.txt')
    $old=$ErrorActionPreference
    $ErrorActionPreference='Continue'
    & $exe @argv 2>&1 | Out-File -LiteralPath $log -Encoding utf8
    $exit=$LASTEXITCODE
    $ErrorActionPreference=$old
    $results.Add([pscustomobject]@{name=$name;exit_code=$exit;log=$log})
    if ($exit -ne 0) { throw "$name failed; read $log" }
}
Push-Location $repoRoot
try {
    if ($Regenerate) {
        Run-Check 'cad_build' $cfg.python @((Join-Path $PSScriptRoot 'run_cad.py'),(Join-Path $taskRoot 'cad/build.py'))
        if (-not $MechanicalOnly) { Run-Check 'electronics_build' $cfg.kicad_python @((Join-Path $PSScriptRoot 'build_electronics.py')) }
    }
    if (-not $SkipGeometry) {
        Run-Check 'geometry_screen' $cfg.python @((Join-Path $PSScriptRoot 'run_cad.py'),(Join-Path $taskRoot 'cad/inspect_geometry.py'))
    }
    if (-not $MechanicalOnly) {
    $base=Join-Path $taskRoot 'electronics/sensor_revA/PoseDoll_AS5048A_revA'
    Run-Check 'sensor_erc_run' $cfg.kicad @('sch','erc','--exit-code-violations','--format','json','-o',(Join-Path $verify 'sensor_erc.json'),($base+'.kicad_sch'))
    Run-Check 'sensor_drc_run' $cfg.kicad @('pcb','drc','--schematic-parity','--exit-code-violations','--format','json','-o',(Join-Path $verify 'sensor_parity_drc.json'),($base+'.kicad_pcb'))
    Run-Check 'schematic_export' $cfg.kicad @('sch','export','svg','-o',(Join-Path $taskRoot 'generated/schematic'),($base+'.kicad_sch'))
    Run-Check 'pcb_render' $cfg.kicad @('pcb','render','--width','1000','--height','800','--side','top','--background','opaque','-o',(Join-Path $taskRoot 'generated/images/sensor_pcb.png'),($base+'.kicad_pcb'))
    Run-Check 'h1_protocol_tests' $cfg.python @('-m','unittest','discover','-s','Tools/PoseDollHardwareBridge','-p','test_*.py','-v')
    Run-Check 'diagnostic_gui_smoke' $cfg.idf_python @('Tools/PoseDollHardwareBridge/diagnostic_gui.py','--smoke-test')
    $savedPath=$env:PYTHONPATH
    try {
        $env:PYTHONPATH=Join-Path $repoRoot 'Tools/PoseDollSimulator/src'
        Run-Check 'simulator_regression' $cfg.simulator_python @('-m','pytest','Tools/PoseDollSimulator/tests','-q','-p','no:cacheprovider')
    } finally {$env:PYTHONPATH=$savedPath}
    if ($Firmware) {
        . $cfg.idf_activation
        Push-Location (Join-Path $repoRoot 'Firmware/PoseDollHardware')
        try {
            Run-Check 'firmware_build' $cfg.idf_python @((Join-Path $cfg.idf_root 'tools/idf.py'),'build')
        } finally {Pop-Location}
    }
    }
    Run-Check 'fit_geometry_check' $cfg.python @((Join-Path $PSScriptRoot 'run_cad.py'),(Join-Path $taskRoot 'cad/inspect_fits.py'))
    Run-Check 'print_fit_sensitivity' $cfg.python @((Join-Path $PSScriptRoot 'analyze_print_fits.py'))
    Run-Check 'design_consistency' $cfg.python @((Join-Path $PSScriptRoot 'validate_design.py'))
    Run-Check 'handoff_documents' $cfg.python @((Join-Path $PSScriptRoot 'make_handoff.py'))
} finally {
    [pscustomobject]@{time=(Get-Date -Format o);checks=$results;mechanical_only=[bool]$MechanicalOnly;user_testing_requested_now=$false;physical_tests='not_run';full_body_release=$false} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $verify 'build_results.json') -Encoding utf8
    Pop-Location
}
Write-Host 'Digital checks completed. Continue design; physical testing is deferred. Read START_HERE.zh-CN.md.'
