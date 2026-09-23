[CmdletBinding()]
param(
 [ValidateSet('OfflineTests','CAD','Firmware','Reports')][string]$Stage='OfflineTests',
 [string]$Python='',
 [string]$VcVars='D:/ProgramFiles/Microsoft Visual Studio/2022/Community/VC/Auxiliary/Build/vcvars64.bat'
)
$ErrorActionPreference='Stop'
$repoRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if(!$Python){$Python=Join-Path $repoRoot '.venv/Scripts/python.exe'}
if(!(Test-Path -LiteralPath $Python)){throw 'Create .venv and install requirements.txt first, or pass -Python.'}
function Invoke-Checked([string]$Program,[string[]]$CommandArgs){
 & $Program @CommandArgs
 if($LASTEXITCODE -ne 0){throw "Command failed: $Program (exit $LASTEXITCODE)"}
}
Push-Location $repoRoot
$previousPythonPath=$env:PYTHONPATH
try{
 if($Stage -eq 'OfflineTests'){
  $env:PYTHONPATH=(Join-Path $repoRoot 'Tools/PoseDollSimulator/src')+';'+(Join-Path $repoRoot 'Tools/PoseDollHardwareBridge')
  Invoke-Checked $Python @('scripts/check_repository.py')
  Invoke-Checked $Python @('Firmware/PoseDollFullBody/tools/generate_config.py','--check')
  Invoke-Checked $Python @('-m','pytest','Tools/PoseDollHardwareBridge','Tools/PoseDollSimulator/tests','-q','-p','no:cacheprovider')
  Invoke-Checked (Join-Path $PSScriptRoot 'Run-CoreTests.cmd') @($VcVars)
  Invoke-Checked $Python @('scripts/check_repository.py','--golden','.local/core/golden_pd41.bin')
 }else{
  if($Stage -eq 'Firmware'){
   $fwRoot=(Resolve-Path -LiteralPath 'Firmware/PoseDollFullBody').Path
   foreach($i in 1..6){
    $build=Join-Path $fwRoot "build_node$i";$cache=Join-Path $build 'CMakeCache.txt'
    if(Test-Path -LiteralPath $cache){
     $line=Get-Content -LiteralPath $cache | Where-Object {$_ -like 'CMAKE_HOME_DIRECTORY:INTERNAL=*'} | Select-Object -First 1
     $oldHome=if($line){$line.Substring($line.IndexOf('=')+1)}else{''}
     if(!$oldHome -or [IO.Path]::GetFullPath($oldHome) -ne $fwRoot){
      $actual=(Resolve-Path -LiteralPath $build).Path
      $archive=[IO.Path]::GetFullPath((Join-Path $repoRoot ('.local/legacy-firmware-builds/node'+$i+'-'+[guid]::NewGuid().ToString('N'))))
      if(!( $actual.StartsWith($fwRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) -or !( $archive.StartsWith($repoRoot+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase))){throw 'Unsafe cache archive path'}
      New-Item -ItemType Directory -Path (Split-Path $archive -Parent) -Force | Out-Null
      Move-Item -LiteralPath $actual -Destination $archive
      Write-Host "Archived relocated firmware cache: $archive"
     }
    }
   }
  }
  New-Item -ItemType Directory -Path 'Hardware/PoseDoll44/generated/revM/cache' -Force | Out-Null
  & ./Hardware/PoseDoll44/tools/Build-RevM.ps1 -Stage $Stage -CodePython $Python -NumericPython $Python
 }
}finally{$env:PYTHONPATH=$previousPythonPath;Pop-Location}
