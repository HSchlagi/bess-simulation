#!/usr/bin/env python3
"""
Behebt die Chart-Vorschau in der Hauptseite data_import_center.html
"""

def fix_main_chart_preview():
    """Behebt die Chart-Vorschau in der Hauptseite"""
    
    print("🔧 BEHEBE CHART-VORSCHAU IN DER HAUPTSEITE")
    print("=" * 50)
    
    # Lese das Template
    with open('app/templates/data_import_center.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Erstelle verbesserte JavaScript-Funktion
    improved_show_chart_preview = '''
    // Verbesserte Chart-Vorschau anzeigen
    async showChartPreview() {
        try {
            console.log("🔄 Lade Chart-Vorschau...");
            
            const response = await fetch('/api/water-levels?river_name=Steyr&start_date=2024-01-01&end_date=2025-12-31');
            const data = await response.json();
            
            console.log("📊 API-Antwort:", data);
            
            if (data.success && data.data && data.data.length > 0) {
                console.log(`✅ ${data.data.length} Datenpunkte geladen`);
                this.createChart(data.data);
                this.showNotification(`Chart-Vorschau geladen: ${data.data.length} Datenpunkte`, 'success');
            } else {
                console.log("⚠️ Keine Daten verfügbar");
                this.showNoDataMessage();
                this.showNotification('Keine Daten für Chart-Vorschau verfügbar', 'warning');
            }
        } catch (error) {
            console.error('❌ Fehler beim Laden der Chart-Daten:', error);
            this.showNoDataMessage();
            this.showNotification('Fehler beim Laden der Chart-Daten', 'error');
        }
    },
    
    // Verbesserte Chart erstellen
    createChart(data) {
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
    },
    
    // Keine Daten Nachricht
    showNoDataMessage() {
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
    },
    
    // Notification Funktion
    showNotification(message, type = 'info') {
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
    
    # Ersetze die alte showChartPreview Funktion
    old_function_start = '// Chart-Vorschau anzeigen\n    async showChartPreview() {'
    old_function_end = '    }\n};'
    
    if old_function_start in content:
        # Finde die Position der alten Funktion
        start_pos = content.find(old_function_start)
        end_pos = content.find(old_function_end, start_pos)
        
        if start_pos != -1 and end_pos != -1:
            # Ersetze die alte Funktion
            new_content = content[:start_pos] + improved_show_chart_preview + content[end_pos + len(old_function_end):]
            
            # Speichere die verbesserte Datei
            with open('app/templates/data_import_center_fixed.html', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ Chart-Vorschau in data_import_center_fixed.html behoben")
            print("🌐 Öffnen Sie: http://127.0.0.1:5000/data_import_center_fixed")
            
        else:
            print("❌ Alte Funktion nicht gefunden")
    else:
        print("❌ showChartPreview Funktion nicht gefunden")
    
    # Erstelle auch eine einfache Test-Route
    test_route = '''
@main_bp.route('/data_import_center_fixed')
def data_import_center_fixed():
    return render_template('data_import_center_fixed.html')
    '''
    
    print("\n📝 Fügen Sie diese Route zu app/routes.py hinzu:")
    print(test_route)
    
    print("\n" + "=" * 50)
    print("🎯 Chart-Vorschau Behebung abgeschlossen!")

if __name__ == "__main__":
    fix_main_chart_preview() 