# BESS Backup Automation PowerShell Script
# Führt automatische Datenbank-Backups durch

param(
    [string]$BackupType = "daily",
    [switch]$TestRestore,
    [switch]$ListBackups,
    [switch]$ShowStats
)

# Konfiguration
$PythonPath = "python"
$BackupScript = "backup_automation.py"
$LogFile = "backup_automation.log"

# Funktion zum Logging
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp [$Level] $Message"
    Write-Host $logMessage
    Add-Content -Path $LogFile -Value $logMessage
}

# Funktion zum Prüfen der Python-Installation
function Test-PythonInstallation {
    try {
        $pythonVersion = & $PythonPath --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Python gefunden: $pythonVersion"
            return $true
        }
    }
    catch {
        Write-Log "Python nicht gefunden. Bitte installieren Sie Python." "ERROR"
        return $false
    }
    return $false
}

# Funktion zum Prüfen der Datenbank
function Test-DatabaseExists {
    $dbPath = "instance/bess.db"
    if (Test-Path $dbPath) {
        $dbSize = (Get-Item $dbPath).Length / 1MB
        Write-Log "Datenbank gefunden: $dbPath ($([math]::Round($dbSize, 2)) MB)"
        return $true
    }
    else {
        Write-Log "Datenbank nicht gefunden: $dbPath" "ERROR"
        return $false
    }
}

# Funktion zum Ausführen des Backups
function Start-Backup {
    param([string]$Type = "daily")
    
    Write-Log "🚀 Starte $Type Backup..."
    
    try {
        # Backup-Script ausführen
        $arguments = @($BackupScript)
        $result = & $PythonPath $arguments 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ $Type Backup erfolgreich abgeschlossen"
            return $true
        }
        else {
            Write-Log "❌ $Type Backup fehlgeschlagen: $result" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "❌ Fehler beim Ausführen des Backups: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Funktion zum Anzeigen der Backup-Statistiken
function Show-BackupStats {
    Write-Log "📊 Zeige Backup-Statistiken..."
    
    try {
        $statsFile = "backup_stats.json"
        if (Test-Path $statsFile) {
            $stats = Get-Content $statsFile | ConvertFrom-Json
            Write-Log "   Gesamte Backups: $($stats.total_backups)"
            Write-Log "   Erfolgreiche Backups: $($stats.successful_backups)"
            Write-Log "   Fehlgeschlagene Backups: $($stats.failed_backups)"
            
            if ($stats.total_backups -gt 0) {
                $successRate = [math]::Round(($stats.successful_backups / $stats.total_backups) * 100, 1)
                Write-Log "   Erfolgsrate: $successRate%"
            }
            
            Write-Log "   Gesamtgröße: $([math]::Round($stats.total_size_mb, 2)) MB"
            
            if ($stats.last_backup) {
                try {
                    $lastBackup = [datetime]::Parse($stats.last_backup)
                    Write-Log "   Letztes Backup: $($lastBackup.ToString('yyyy-MM-dd HH:mm:ss'))"
                }
                catch {
                    Write-Log "   Letztes Backup: $($stats.last_backup)"
                }
            }
        }
        else {
            Write-Log "Keine Backup-Statistiken gefunden"
        }
    }
    catch {
        Write-Log "Fehler beim Laden der Statistiken: $($_.Exception.Message)" "ERROR"
    }
}

# Funktion zum Auflisten der Backups
function List-Backups {
    Write-Log "📋 Liste verfügbare Backups auf..."
    
    $backupDir = "backups"
    if (Test-Path $backupDir) {
        $backupFiles = Get-ChildItem -Path $backupDir -Filter "*.sql*" | Sort-Object LastWriteTime -Descending
        
        if ($backupFiles.Count -gt 0) {
            foreach ($file in $backupFiles) {
                $sizeMB = [math]::Round($file.Length / 1MB, 2)
                $date = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                Write-Log "   📄 $($file.Name) ($sizeMB MB) - $date"
            }
        }
        else {
            Write-Log "Keine Backup-Dateien gefunden"
        }
    }
    else {
        Write-Log "Backup-Verzeichnis nicht gefunden: $backupDir"
    }
}

# Funktion zum Testen der Wiederherstellung
function Test-BackupRestore {
    Write-Log "🧪 Teste Backup-Wiederherstellung..."
    
    try {
        $arguments = @($BackupScript, "--test-restore")
        $result = & $PythonPath $arguments 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "✅ Wiederherstellungstest erfolgreich"
            return $true
        }
        else {
            Write-Log "❌ Wiederherstellungstest fehlgeschlagen: $result" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "❌ Fehler beim Wiederherstellungstest: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# Hauptfunktion
function Main {
    Write-Log "🔧 BESS Backup Automation gestartet"
    Write-Log "Parameter: BackupType=$BackupType, TestRestore=$TestRestore, ListBackups=$ListBackups, ShowStats=$ShowStats"
    
    # Prüfungen durchführen
    if (-not (Test-PythonInstallation)) {
        exit 1
    }
    
    if (-not (Test-DatabaseExists)) {
        exit 1
    }
    
    # Aktionen ausführen
    if ($ShowStats) {
        Show-BackupStats
    }
    
    if ($ListBackups) {
        List-Backups
    }
    
    if ($TestRestore) {
        Test-BackupRestore
    }
    
    if (-not $ShowStats -and -not $ListBackups -and -not $TestRestore) {
        # Normales Backup ausführen
        $success = Start-Backup -Type $BackupType
        
        if ($success) {
            Write-Log "🎉 Backup-Prozess erfolgreich abgeschlossen"
            exit 0
        }
        else {
            Write-Log "💥 Backup-Prozess fehlgeschlagen" "ERROR"
            exit 1
        }
    }
}

# Script ausführen
Main
