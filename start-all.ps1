# start-all.ps1 — Launch all 5 Investment Advisory AI Agent services
# Run from the project root: .\start-all.ps1
# Prerequisite: run .\setup.ps1 once first.

$root = $PSScriptRoot

function Start-Service {
    param([string]$Title, [string]$Command)
    Write-Host "  Starting: $Title" -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root'; $Command" `
        -WindowStyle Normal
}

# ── Validate tools exist ──────────────────────────────────────────────────────
$promExe = "$root\tools\prometheus\prometheus.exe"
$grafExe = "$root\tools\grafana\bin\grafana.exe"

if (-not (Test-Path $promExe)) {
    Write-Host "Prometheus not found. Run .\setup.ps1 first." -ForegroundColor Red; exit 1
}
if (-not (Test-Path $grafExe)) {
    Write-Host "Grafana not found. Run .\setup.ps1 first." -ForegroundColor Red; exit 1
}

Write-Host "`nStarting all services...`n" -ForegroundColor Green

# Terminal 1 — Streamlit App (:8501)
Start-Service "Streamlit App" `
    "Write-Host 'Streamlit App -> http://localhost:8501' -ForegroundColor Green; streamlit run src/frontend/app.py"

Start-Sleep -Seconds 1

# Terminal 2 — Knowledge Vault Viewer (:8503)
Start-Service "Knowledge Vault Viewer" `
    "Write-Host 'Knowledge Vault -> http://localhost:8503' -ForegroundColor Green; python knowledge-vault/vault_viewer.py"

Start-Sleep -Seconds 1

# Terminal 3 — Prometheus (:9091)
Start-Service "Prometheus" `
    "Write-Host 'Prometheus -> http://localhost:9091' -ForegroundColor Green; & '$promExe' --config.file='$root\observability\prometheus.yml' --storage.tsdb.path='$root\tools\prometheus-data' --web.listen-address=0.0.0.0:9091"

Start-Sleep -Seconds 1

# Terminal 4 — Grafana (:3000)
Start-Service "Grafana" `
    "Write-Host 'Grafana -> http://localhost:3000' -ForegroundColor Green; `$env:GF_SERVER_HTTP_PORT='3000'; `$env:GF_SECURITY_ADMIN_USER='admin'; `$env:GF_SECURITY_ADMIN_PASSWORD='admin'; `$env:GF_AUTH_ANONYMOUS_ENABLED='true'; `$env:GF_AUTH_ANONYMOUS_ORG_ROLE='Viewer'; `$env:GF_AUTH_DISABLE_LOGIN_FORM='true'; & '$grafExe' server --homepath '$root\tools\grafana'"

Write-Host @"

All services launched in separate windows:
  http://localhost:8501          — Streamlit App (also serves metrics on :8502)
  http://localhost:8502/metrics  — Prometheus metrics feed
  http://localhost:8503          — Knowledge Vault Viewer
  http://localhost:9091          — Prometheus UI
  http://localhost:3000          — Grafana
"@ -ForegroundColor Green
