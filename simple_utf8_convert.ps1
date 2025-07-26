# Einfaches Script: Templates in UTF-8 konvertieren

Write-Host "Konvertiere Templates in UTF-8..."

$templateDir = "app\templates"
$templateFiles = Get-ChildItem -Path $templateDir -Filter "*.html"

Write-Host "Gefundene Dateien: $($templateFiles.Count)"

foreach ($file in $templateFiles) {
    try {
        Write-Host "Konvertiere: $($file.Name)"
        
        # Backup erstellen
        $backupPath = "backup_$($file.Name)"
        Copy-Item $file.FullName $backupPath
        
        # Dateiinhalt lesen und in UTF-8 speichern
        $content = Get-Content $file.FullName -Raw
        $content | Out-File -FilePath $file.FullName -Encoding UTF8 -NoNewline
        
        Write-Host "OK: $($file.Name)"
        
    } catch {
        Write-Host "FEHLER: $($file.Name) - $($_.Exception.Message)"
    }
}

Write-Host "Konvertierung abgeschlossen!" 