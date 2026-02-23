# Static Frontend auf Port 5500 starten (für Aktivierungs-Link etc.)
# Stoppen: Strg+C
Set-Location $PSScriptRoot
Write-Host "Starte Frontend auf http://127.0.0.1:5500"
Write-Host "Aktivierungsseite: http://127.0.0.1:5500/pages/auth/activate.html"
Write-Host "Beenden mit Strg+C"
python -m http.server 5500
