#!/usr/bin/env python3
"""
Behebt die Chart-Vorschau direkt mit verfügbaren Daten
"""

import sqlite3
import json
from datetime import datetime

def fix_chart_preview():
    """Behebt die Chart-Vorschau direkt"""
    
    print("🔧 Behebe Chart-Vorschau...")
    print("=" * 60)
    
    try:
        # Direkte Datenbankverbindung
        conn = sqlite3.connect('instance/bess.db')
        cursor = conn.cursor()
        
        # Lade Steyr-Daten für Chart
        cursor.execute("""
            SELECT timestamp, water_level_cm, station_name, river_name, source 
            FROM water_level 
            WHERE river_name LIKE '%Steyr%'
            ORDER BY timestamp DESC 
            LIMIT 100
        """)
        
        rows = cursor.fetchall()
        print(f"📊 {len(rows)} Steyr-Datenpunkte für Chart gefunden")
        
        if len(rows) > 0:
            # Daten für Chart vorbereiten
            chart_data = []
            for row in rows:
                chart_data.append({
                    'timestamp': row[0],
                    'water_level_cm': float(row[1]),
                    'station_name': row[2],
                    'river_name': row[3],
                    'source': row[4]
                })
            
            # Chart-API-Response erstellen
            api_response = {
                'success': True,
                'data': chart_data,
                'source': 'EHYD (Demo) - Basierend auf echten österreichischen Mustern',
                'message': f'{len(chart_data)} Pegelstanddaten für Chart-Vorschau geladen'
            }
            
            # Speichere Chart-Daten
            with open('chart_data.json', 'w', encoding='utf-8') as f:
                json.dump(api_response, f, indent=2, ensure_ascii=False)
            
            print("💾 Chart-Daten in chart_data.json gespeichert")
            
            # Erstelle einfache HTML-Chart-Seite
            create_chart_html(chart_data)
            
        else:
            print("⚠️ Keine Steyr-Daten in der Datenbank")
            print("💡 Laden Sie zuerst EHYD-Daten mit: python test_fix_ehyd.py")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Chart-Vorschau Behebung abgeschlossen!")

def create_chart_html(chart_data):
    """Erstellt eine einfache HTML-Seite mit funktionierendem Chart"""
    
    html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Steyr Chart-Vorschau - FUNKTIONIERT</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-gray-800 mb-8">🏔️ Steyr Chart-Vorschau - FUNKTIONIERT</h1>
        
        <!-- Status -->
        <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
            <div class="flex">
                <div class="flex-shrink-0">
                    <i class="fas fa-check-circle text-green-400"></i>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-green-800">Chart-Vorschau funktioniert!</h3>
                    <div class="mt-2 text-sm text-green-700">
                        <p><strong>{len(chart_data)} Datenpunkte</strong> erfolgreich geladen</p>
                        <p><strong>Quelle:</strong> EHYD (Demo) - Basierend auf echten österreichischen Mustern</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Chart-Container -->
        <div class="bg-white rounded-lg shadow-md p-6">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">📈 Steyr Pegelstand-Verlauf</h2>
            <div id="chartContainer" class="h-96">
                <canvas id="waterLevelChart"></canvas>
            </div>
        </div>
        
        <!-- Daten-Info -->
        <div class="bg-blue-50 rounded-lg p-4 mt-6">
            <h3 class="font-semibold text-blue-800 mb-2">📊 Daten-Informationen</h3>
            <ul class="text-blue-700 text-sm space-y-1">
                <li>• <strong>Datenpunkte:</strong> {len(chart_data)}</li>
                <li>• <strong>Stationen:</strong> {len(set(d['station_name'] for d in chart_data))}</li>
                <li>• <strong>Zeitraum:</strong> {chart_data[-1]['timestamp'][:10]} bis {chart_data[0]['timestamp'][:10]}</li>
                <li>• <strong>Quelle:</strong> EHYD (Demo)</li>
            </ul>
        </div>
    </div>

    <script>
        // Chart-Daten
        const chartData = {json.dumps(chart_data)};
        
        // Chart erstellen
        function createChart() {{
            const ctx = document.getElementById('waterLevelChart');
            
            // Daten für Chart vorbereiten
            const labels = chartData.map(d => {{
                const date = new Date(d.timestamp);
                return date.toLocaleDateString('de-DE') + ' ' + date.toLocaleTimeString('de-DE', {{hour: '2-digit', minute: '2-digit'}});
            }});
            const values = chartData.map(d => d.water_level_cm);
            
            console.log(`📊 Erstelle Chart mit ${{chartData.length}} Datenpunkten`);
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Pegelstand (cm)',
                        data: values,
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.1,
                        pointRadius: 2,
                        pointHoverRadius: 5,
                        fill: true
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Steyr Pegelstand-Verlauf (Vorschau)',
                            font: {{ size: 16, weight: 'bold' }}
                        }},
                        legend: {{ display: true, position: 'top' }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                            callbacks: {{
                                label: function(context) {{
                                    return `Pegelstand: ${{context.parsed.y}} cm`;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{ display: true, text: 'Datum & Zeit' }},
                            ticks: {{ maxTicksLimit: 10 }}
                        }},
                        y: {{
                            beginAtZero: false,
                            title: {{ display: true, text: 'Pegelstand (cm)' }}
                        }}
                    }},
                    interaction: {{ intersect: false, mode: 'index' }}
                }}
            }});
            
            console.log("✅ Chart erfolgreich erstellt");
        }}
        
        // Seite laden
        document.addEventListener('DOMContentLoaded', function() {{
            console.log("🚀 Chart-Vorschau-Seite geladen");
            createChart();
        }});
    </script>
</body>
</html>
"""
    
    with open('working_chart_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("💾 Funktionsfähige Chart-Seite in working_chart_preview.html erstellt")

if __name__ == "__main__":
    fix_chart_preview() 