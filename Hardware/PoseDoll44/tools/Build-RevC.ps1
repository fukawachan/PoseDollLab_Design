param([switch]$Regenerate)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$repoRoot=Split-Path (Split-Path $taskRoot -Parent) -Parent
$cfg=Get-Content (Join-Path $PSScriptRoot 'local_toolchain.json') -Raw | ConvertFrom-Json
$results=[Collections.Generic.List[object]]::new()
function Run-RevC([string]$name,[string]$exe,[string[]]$arguments) {
    Write-Host "[$name]"
    $log=Join-Path $taskRoot ('verification/revC_'+$name+'.txt')
    $savedPreference=$ErrorActionPreference
    try {
        $ErrorActionPreference='Continue'
        & $exe @arguments 2>&1 | Out-File -LiteralPath $log -Encoding utf8
        $code=$LASTEXITCODE
    } finally { $ErrorActionPreference=$savedPreference }
    $results.Add([pscustomobject]@{name=$name;exit_code=$code;log=$log})
    if ($code -ne 0) { throw "$name failed; see $log" }
}
Push-Location $repoRoot
try {
    if ($Regenerate) {
        Run-RevC 'sensor_build' $cfg.kicad_python @((Join-Path $PSScriptRoot 'build_sensor_revB.py'))
        $base=Join-Path $taskRoot 'electronics/sensor_revB/PoseDoll_AS5048A_revB'
        Run-RevC 'erc' $cfg.kicad @('sch','erc','--exit-code-violations','--format','json','-o',(Join-Path $taskRoot 'verification/sensor_revB_erc.json'),($base+'.kicad_sch'))
        Run-RevC 'drc' $cfg.kicad @('pcb','drc','--schematic-parity','--exit-code-violations','--format','json','-o',(Join-Path $taskRoot 'verification/sensor_revB_drc.json'),($base+'.kicad_pcb'))
        Run-RevC 'sensor_step' $cfg.kicad @('pcb','export','step','--force','--subst-models','--user-origin','109x110mm','-o',(Join-Path $taskRoot 'generated/revC/step/sensor_revB.step'),($base+'.kicad_pcb'))
        Run-RevC 'sensor_interface' $cfg.kicad_python @((Join-Path $PSScriptRoot 'export_sensor_revB_interface.py'))
        foreach ($script in @('design.py','clutch.py','check_motion.py','loads.py','inspect_sensor.py')) {
            Run-RevC $script $cfg.python @((Join-Path $PSScriptRoot 'run_cad.py'),(Join-Path $taskRoot ('cad/revC/'+$script)))
        }
        foreach ($side in @('top','bottom')) {
            Run-RevC ('sensor_view_'+$side) $cfg.kicad @('pcb','render','--width','900','--height','750','--zoom','0.8','--background','opaque','--side',$side,'-o',(Join-Path $taskRoot ('generated/revC/images/sensor_revB_'+$(if($side -eq 'top'){'front'}else{'back'})+'.png')),($base+'.kicad_pcb'))
        }
    }
    Run-RevC 'review' $cfg.python @((Join-Path $PSScriptRoot 'report_revC.py'))
} finally {
    [pscustomobject]@{time=(Get-Date -Format o);checks=$results;physical_tests='not_run';manufacturing_release=$false} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskRoot 'verification/revC_build_results.json') -Encoding utf8
    Pop-Location
}
Write-Host 'Revision C digital checks completed. Physical testing is deferred. Read START_HERE.zh-CN.md.'
