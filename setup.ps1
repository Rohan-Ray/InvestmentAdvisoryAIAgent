# setup.ps1 — Download Prometheus and Grafana for Windows, install Python deps
# Run once from the project root: .\setup.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot

# ── 1. Python dependencies ────────────────────────────────────────────────────
Write-Host "`n[1/3] Installing Python dependencies..." -ForegroundColor Cyan
pip install -r "$root\requirements.txt" --quiet
Write-Host "  Python deps OK" -ForegroundColor Green

# ── 2. Prometheus ─────────────────────────────────────────────────────────────
$promDir  = "$root\tools\prometheus"
$promExe  = "$promDir\prometheus.exe"
$promVer  = "2.53.4"
$promZip  = "$root\tools\prometheus.zip"
$promUrl  = "https://github.com/prometheus/prometheus/releases/download/v$promVer/prometheus-$promVer.windows-amd64.zip"

Write-Host "`n[2/3] Setting up Prometheus $promVer..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "$root\tools" | Out-Null

if (-not (Test-Path $promExe)) {
    Write-Host "  Downloading from GitHub..."
    Invoke-WebRequest -Uri $promUrl -OutFile $promZip -UseBasicParsing
    Write-Host "  Extracting..."
    Expand-Archive -Path $promZip -DestinationPath "$root\tools\prom_tmp" -Force
    $extracted = Get-ChildItem "$root\tools\prom_tmp" -Directory | Select-Object -First 1
    New-Item -ItemType Directory -Force -Path $promDir | Out-Null
    Move-Item "$($extracted.FullName)\*" $promDir -Force
    Remove-Item "$root\tools\prom_tmp" -Recurse -Force
    Remove-Item $promZip -Force
    Write-Host "  Prometheus installed -> tools\prometheus\" -ForegroundColor Green
} else {
    Write-Host "  Prometheus already present, skipping." -ForegroundColor Yellow
}

# ── 3. Grafana ────────────────────────────────────────────────────────────────
$grafDir  = "$root\tools\grafana"
$grafExe  = "$grafDir\bin\grafana.exe"
$grafVer  = "11.4.0"
$grafZip  = "$root\tools\grafana.zip"
$grafUrl  = "https://dl.grafana.com/oss/release/grafana-$grafVer.windows-amd64.zip"

Write-Host "`n[3/3] Setting up Grafana $grafVer..." -ForegroundColor Cyan

if (-not (Test-Path $grafExe)) {
    Write-Host "  Downloading from grafana.com (~120 MB, please wait)..."
    Invoke-WebRequest -Uri $grafUrl -OutFile $grafZip -UseBasicParsing
    Write-Host "  Extracting..."
    Expand-Archive -Path $grafZip -DestinationPath "$root\tools\graf_tmp" -Force
    $extracted = Get-ChildItem "$root\tools\graf_tmp" -Directory | Select-Object -First 1
    New-Item -ItemType Directory -Force -Path $grafDir | Out-Null
    Move-Item "$($extracted.FullName)\*" $grafDir -Force
    Remove-Item "$root\tools\graf_tmp" -Recurse -Force
    Remove-Item $grafZip -Force
    Write-Host "  Grafana installed -> tools\grafana\" -ForegroundColor Green
} else {
    Write-Host "  Grafana already present, skipping." -ForegroundColor Yellow
}

Write-Host "`nSetup complete. Run .\start-all.ps1 to launch all services." -ForegroundColor Green
