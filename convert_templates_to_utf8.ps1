# PowerShell Script: Alle Templates in UTF-8 Format konvertieren
# Für Hetzner Server Deployment

Write-Host "🔄 Konvertiere alle Template-Dateien in UTF-8 Format..." -ForegroundColor Yellow

# Template-Verzeichnis
$templateDir = "app\templates"

# Alle HTML-Dateien im Template-Verzeichnis finden
$templateFiles = Get-ChildItem -Path $templateDir -Filter "*.html" -Recurse

Write-Host "📁 Gefundene Template-Dateien: $($templateFiles.Count)" -ForegroundColor Cyan

# Backup-Verzeichnis erstellen
$backupDir = "templates_backup_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "💾 Backup-Verzeichnis erstellt: $backupDir" -ForegroundColor Green

$convertedCount = 0
$errorCount = 0

foreach ($file in $templateFiles) {
    try {
        Write-Host "🔄 Konvertiere: $($file.Name)" -ForegroundColor White
        
        # Backup erstellen
        $backupPath = Join-Path $backupDir $file.Name
        Copy-Item $file.FullName $backupPath
        
        # Dateiinhalt lesen (automatische Encoding-Erkennung)
        $content = Get-Content $file.FullName -Raw -Encoding UTF8 -ErrorAction SilentlyContinue
        
        # Falls UTF8 fehlschlägt, versuche andere Encodings
        if (-not $content) {
            $content = Get-Content $file.FullName -Raw -Encoding UTF8BOM -ErrorAction SilentlyContinue
        }
        if (-not $content) {
            $content = Get-Content $file.FullName -Raw -Encoding Unicode -ErrorAction SilentlyContinue
        }
        if (-not $content) {
            $content = Get-Content $file.FullName -Raw -Encoding Default -ErrorAction SilentlyContinue
        }
        
        if ($content) {
            # In UTF-8 ohne BOM speichern
            $content | Out-File -FilePath $file.FullName -Encoding UTF8 -NoNewline
            $convertedCount++
            Write-Host "✅ Erfolgreich konvertiert: $($file.Name)" -ForegroundColor Green
        } else {
            throw "Konnte Dateiinhalt nicht lesen"
        }
        
    } catch {
        $errorCount++
        Write-Host "❌ Fehler bei $($file.Name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n📊 Konvertierung abgeschlossen!" -ForegroundColor Yellow
Write-Host "✅ Erfolgreich konvertiert: $convertedCount Dateien" -ForegroundColor Green
Write-Host "❌ Fehler: $errorCount Dateien" -ForegroundColor Red
Write-Host "💾 Backup gespeichert in: $backupDir" -ForegroundColor Cyan

# Prüfe Encoding der konvertierten Dateien
Write-Host "`n🔍 Prüfe Encoding der konvertierten Dateien..." -ForegroundColor Yellow

foreach ($file in $templateFiles) {
    try {
        $bytes = [System.IO.File]::ReadAllBytes($file.FullName)
        $encoding = "UTF-8"
        
        # Prüfe auf BOM
        if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
            $encoding = "UTF-8 mit BOM"
        } elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFF -and $bytes[1] -eq 0xFE) {
            $encoding = "UTF-16 LE"
        } elseif ($bytes.Length -ge 2 -and $bytes[0] -eq 0xFE -and $bytes[1] -eq 0xFF) {
            $encoding = "UTF-16 BE"
        }
        
        Write-Host "📄 $($file.Name): $encoding" -ForegroundColor White
        
    } catch {
        Write-Host "❌ Fehler beim Prüfen von $($file.Name)" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Alle Templates sind jetzt in UTF-8 Format für den Hetzner Server bereit!" -ForegroundColor Green 