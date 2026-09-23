param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$url = 'http://127.0.0.1:8874/generated/revM/RevM_Full_Body_Review.html'
$page = Join-Path $root 'generated/revM/RevM_Full_Body_Review.html'
if (-not (Test-Path -LiteralPath $page)) { throw "Viewer file missing: $page" }
$expected = [IO.File]::ReadAllBytes($page)
function Test-Viewer {
    $client = New-Object System.Net.WebClient
    try {
        $actual = $client.DownloadData($url)
        return [Convert]::ToBase64String($actual).Equals([Convert]::ToBase64String($expected))
    } catch { return $false } finally { $client.Dispose() }
}
if (-not (Test-Viewer)) {
    $listener = Get-NetTCPConnection -LocalPort 8874 -State Listen -ErrorAction SilentlyContinue
    if ($listener) { throw 'Port 8874 is used by another server. No process was stopped.' }
    $python = Join-Path $env:LOCALAPPDATA 'Programs/Python/Python313/python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        $candidate = Get-Command python.exe -ErrorAction SilentlyContinue
        if (-not $candidate) { throw 'Python 3 was not found. Install Python before opening the viewer.' }
        $python = $candidate.Source
    }
    $logs = Join-Path $root 'verification/viewer_runtime'
    New-Item -ItemType Directory -Path $logs -Force | Out-Null
    $server = Start-Process -FilePath $python -ArgumentList @('-m','http.server','8874','--bind','127.0.0.1') -WorkingDirectory $root -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logs 'server.stdout.log') -RedirectStandardError (Join-Path $logs 'server.stderr.log') -PassThru
    $ready = $false
    for ($i=0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-Viewer) { $ready = $true; break }
        if ($server.HasExited) { break }
    }
    if (-not $ready) { throw "Viewer server did not start. See $logs/server.stderr.log" }
    Write-Host "Started local viewer (PID $($server.Id))."
} else { Write-Host 'Local viewer is already running.' }
Write-Host $url
if (-not $NoBrowser) { Start-Process $url }
