param(
    [string]$Python = 'C:/Users/Ding/AppData/Local/Programs/Python/Python313/python.exe',
    [string]$KiCadPython = 'D:/ProgramFiles/KiCad/10.0/bin/python.exe',
    [string]$KiCad = 'D:/ProgramFiles/KiCad/10.0/bin/kicad-cli.exe'
)
$ErrorActionPreference = 'Stop'
$poseDollRoot = Split-Path $PSScriptRoot -Parent
function Run-PoseDollK([string]$exe, [string[]]$argsList) {
    & $exe @argsList
    if ($LASTEXITCODE -ne 0) { throw ('Failed: ' + $exe + ' ' + ($argsList -join ' ')) }
}
$poseDollBase = Join-Path $poseDollRoot 'electronics/sensor_revC_mini/PoseDoll_AS5048A_revC_mini'
Run-PoseDollK $KiCadPython @((Join-Path $PSScriptRoot 'build_sensor_revC_mini.py'))
Run-PoseDollK $KiCadPython @((Join-Path $PSScriptRoot 'export_sensor_revC_mini_interface.py'))
Run-PoseDollK $KiCad @('sch','erc','--exit-code-violations','--format','json','-o',(Join-Path $poseDollRoot 'verification/sensor_revC_mini_erc.json'),($poseDollBase+'.kicad_sch'))
Run-PoseDollK $KiCad @('pcb','drc','--schematic-parity','--exit-code-violations','--format','json','-o',(Join-Path $poseDollRoot 'verification/sensor_revC_mini_drc.json'),($poseDollBase+'.kicad_pcb'))
Run-PoseDollK $KiCad @('pcb','export','step','--force','--subst-models','--user-origin','100x100mm','-o',(Join-Path $poseDollRoot 'generated/revK/components/sensor_revC_mini.step'),($poseDollBase+'.kicad_pcb'))
Run-PoseDollK $KiCad @('pcb','export','svg','--layers','F.Cu,F.Fab,Edge.Cuts','--page-size-mode','2','--exclude-drawing-sheet','--mode-single','--sketch-pads-on-fab-layers','-o',(Join-Path $poseDollRoot 'generated/revK/components/sensor_front.svg'),($poseDollBase+'.kicad_pcb'))
Run-PoseDollK $KiCad @('pcb','export','svg','--layers','B.Cu,B.Fab,Edge.Cuts','--mirror','--page-size-mode','2','--exclude-drawing-sheet','--mode-single','--sketch-pads-on-fab-layers','-o',(Join-Path $poseDollRoot 'generated/revK/components/sensor_back.svg'),($poseDollBase+'.kicad_pcb'))
foreach ($poseDollStage in @('verify_k.py','check_legacy_tools_k.py','check_new_tools_k.py','check_readout_k.py','export_components_k.py','load_budget_k.py','build_review_k.py')) {
    Run-PoseDollK $Python @((Join-Path $PSScriptRoot 'run_cad.py'),(Join-Path $poseDollRoot ('cad/revK/'+$poseDollStage)))
}
Run-PoseDollK $Python @((Join-Path $PSScriptRoot 'report_revK.py'))
Write-Host 'Rev K rebuilt. CAD/electrical candidate only; no manufacturing release.'
