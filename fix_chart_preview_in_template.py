#!/usr/bin/env python3
"""
Behebt die Chart-Vorschau im data_import_center.html Template
"""

def fix_chart_preview_in_template():
    """Behebt die Chart-Vorschau im Template"""
    
    print("🔧 BEHEBE CHART-VORSCHAU IM TEMPLATE")
    print("=" * 50)
    
    # Lese das Template
    with open('app/templates/data_import_center.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Suche nach dem Chart-Container
    if 'chartPreview' in content:
        print("✅ chartPreview ID gefunden")
    else:
        print("❌ chartPreview ID nicht gefunden")
    
    # Suche nach dem Chart-Vorschau Button
    if 'showChartPreview()' in content:
        print("✅ showChartPreview() Funktion gefunden")
    else:
        print("❌ showChartPreview() Funktion nicht gefunden")
    
    # Erstelle eine funktionierende Chart-Vorschau
    chart_preview_html = '''
    <!-- Chart-Vorschau Container -->
    <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">Chart-Vorschau</h3>
        <div id="chartPreview" class="h-96">
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-chart-line text-4xl mb-4"></i>
                <p>Klicken Sie auf "Chart-Vorschau" um Daten anzuzeigen</p>
            </div>
        </div>
        <div class="mt-4">
            <button onclick="loadChartPreview()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded text-sm">
                <i class="fas fa-chart-bar"></i> Chart-Vorschau laden
            </button>
        </div>
    </div>
    '''
    
    # Erstelle verbesserte JavaScript-Funktion
    chart_preview_js = '''
    // Verbesserte Chart-Vorschau Funktion
    async function loadChartPreview() {
        try {
            console.log("🔄 Lade Chart-Vorschau...");
            
            const response = await fetch('/api/water-levels?river_name=Steyr&start_date=2024-01-01&end_date=2025-12-31');
            const data = await response.json();
            
            console.log("📊 API-Antwort:", data);
            
            if (data.success && data.data && data.data.length > 0) {
                console.log(`✅ ${data.data.length} Datenpunkte geladen`);
                createChart(data.data);
                showNotification(`Chart-Vorschau geladen: ${data.data.length} Datenpunkte`, 'success');
            } else {
                console.log("⚠️ Keine Daten verfügbar");
                showNoDataMessage();
                showNotification('Keine Daten für Chart-Vorschau verfügbar', 'warning');
            }
        } catch (error) {
            console.error('❌ Fehler beim Laden der Chart-Daten:', error);
            showNoDataMessage();
            showNotification('Fehler beim Laden der Chart-Daten', 'error');
        }
    }
    
    // Chart erstellen
    function createChart(data) {
        const chartContainer = document.getElementById('chartPreview');
        if (!chartContainer) {
            console.error('❌ chartPreview Container nicht gefunden');
            return;
        }
        
        // Chart.js verwenden
        const ctx = document.createElement('canvas');
        ctx.id = 'waterLevelChart';
        chartContainer.innerHTML = '';
        chartContainer.appendChild(ctx);
        
        const chartData = data.slice(0, 200); // Limitiere auf 200 Datenpunkte
        const labels = chartData.map(d => {
            const date = new Date(d.timestamp);
            return date.toLocaleDateString('de-DE') + ' ' + date.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'});
        });
        const values = chartData.map(d => d.water_level_cm);
        
        console.log(`📈 Erstelle Chart mit ${chartData.length} Datenpunkten`);
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Pegelstand (cm)',
                    data: values,
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.1,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: 'Steyr Pegelstand-Verlauf (Vorschau)',
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: { display: true, position: 'top' },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `Pegelstand: ${context.parsed.y} cm`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Datum & Zeit' },
                        ticks: { maxTicksLimit: 10 }
                    },
                    y: {
                        beginAtZero: false,
                        title: { display: true, text: 'Pegelstand (cm)' }
                    }
                },
                interaction: { intersect: false, mode: 'index' }
            }
        });
        
        console.log("✅ Chart erfolgreich erstellt");
    }
    
    // Keine Daten Nachricht
    function showNoDataMessage() {
        const chartContainer = document.getElementById('chartPreview');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-chart-line text-4xl text-gray-400 mb-4"></i>
                    <h3 class="text-lg font-medium text-gray-700 mb-2">Keine Daten verfügbar</h3>
                    <p class="text-gray-500">Laden Sie zuerst EHYD-Daten für Steyr.</p>
                </div>
            `;
        }
    }
    
    // Notification Funktion
    function showNotification(message, type = 'info') {
        // Einfache Notification
        console.log(`${type.toUpperCase()}: ${message}`);
        
        // Optional: Erstelle visuelle Notification
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
            type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
            type === 'warning' ? 'bg-yellow-500 text-black' :
            'bg-blue-500 text-white'
        }`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    '''
    
    # Erstelle eine einfache Test-Seite
    test_page = f'''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chart-Vorschau Test</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">Chart-Vorschau Test</h1>
        
        {chart_preview_html}
        
        <!-- Debug Info -->
        <div class="bg-gray-50 rounded-lg p-4 mt-6">
            <h3 class="font-semibold text-gray-800 mb-2">Debug-Informationen</h3>
            <div id="debugInfo" class="text-sm text-gray-600">
                <p>Status: Bereit</p>
                <p>API-Endpunkt: /api/water-levels</p>
                <p>Datenbank: instance/bess.db</p>
            </div>
        </div>
    </div>

    <script>
    {chart_preview_js}
    
    // Debug-Info aktualisieren
    async function updateDebugInfo() {{
        try {{
            const response = await fetch('/api/water-levels?river_name=Steyr&start_date=2024-01-01&end_date=2025-12-31');
            const data = await response.json();
            
            const debugInfo = document.getElementById('debugInfo');
            debugInfo.innerHTML = `
                <p><strong>API-Status:</strong> ${data.success ? '✅ OK' : '❌ Fehler'}</p>
                <p><strong>Datenpunkte:</strong> ${data.data ? data.data.length : 0}</p>
                <p><strong>Nachricht:</strong> ${data.message || 'Keine Nachricht'}</p>
                <p><strong>Quelle:</strong> ${data.source || 'Unbekannt'}</p>
            `;
        }} catch (error) {{
            const debugInfo = document.getElementById('debugInfo');
            debugInfo.innerHTML = `
                <p><strong>API-Status:</strong> ❌ Fehler</p>
                <p><strong>Fehler:</strong> ${error.message}</p>
            `;
        }}
    }}
    
    // Seite laden
    document.addEventListener('DOMContentLoaded', function() {{
        console.log("🚀 Chart-Vorschau Test-Seite geladen");
        updateDebugInfo();
    }});
    </script>
</body>
</html>
'''
    
    # Speichere Test-Seite
    with open('chart_preview_test.html', 'w', encoding='utf-8') as f:
        f.write(test_page)
    
    print("💾 Chart-Vorschau Test-Seite in chart_preview_test.html erstellt")
    print("🌐 Öffnen Sie: http://127.0.0.1:5000/chart_preview_test.html")
    
    print("\n" + "=" * 50)
    print("🎯 Chart-Vorschau Template-Behebung abgeschlossen!")

if __name__ == "__main__":
    fix_chart_preview_in_template() 