// Verbesserte Chart-Vorschau-Funktion für EHYD-Daten
const ChartPreview = {
    
    // Chart-Vorschau anzeigen
    async showChartPreview() {
        try {
            console.log("📊 Lade Chart-Vorschau für Steyr...");
            
            // Lade die neuesten Steyr-Daten aus der Datenbank
            const response = await fetch('/api/water-levels?river_name=Steyr&start_date=2024-01-01&end_date=2025-12-31');
            const data = await response.json();
            
            console.log("📊 Chart-Daten Response:", data);
            
            if (data.success && data.data && data.data.length > 0) {
                console.log(`📊 ${data.data.length} Datenpunkte für Chart gefunden`);
                this.createChart(data.data);
            } else {
                console.log("⚠️ Keine Daten für Chart-Vorschau verfügbar");
                this.showNoDataMessage();
            }
        } catch (error) {
            console.error('❌ Fehler beim Laden der Chart-Daten:', error);
            this.showErrorMessage();
        }
    },
    
    // Chart erstellen
    createChart(data) {
        // Chart-Container finden oder erstellen
        let chartContainer = document.getElementById('chartPreview');
        if (!chartContainer) {
            console.log("⚠️ Chart-Container nicht gefunden, erstelle ihn...");
            const previewSection = document.querySelector('.intelligent-preview');
            if (previewSection) {
                chartContainer = document.createElement('div');
                chartContainer.id = 'chartPreview';
                chartContainer.className = 'mt-4 p-4 bg-white rounded-lg shadow border';
                previewSection.appendChild(chartContainer);
            }
        }
        
        if (!chartContainer) {
            console.error("❌ Chart-Container konnte nicht erstellt werden");
            return;
        }
        
        // Chart.js verwenden
        chartContainer.innerHTML = '<canvas id="waterLevelChart" height="400"></canvas>';
        const ctx = document.getElementById('waterLevelChart');
        
        // Daten für Chart vorbereiten (nur die ersten 200 Punkte für bessere Performance)
        const chartData = data.slice(0, 200);
        const labels = chartData.map(d => {
            const date = new Date(d.timestamp);
            return date.toLocaleDateString('de-DE') + ' ' + date.toLocaleTimeString('de-DE', {hour: '2-digit', minute: '2-digit'});
        });
        const values = chartData.map(d => d.water_level_cm);
        
        console.log(`📊 Erstelle Chart mit ${chartData.length} Datenpunkten`);
        
        // Bestehenden Chart zerstören falls vorhanden
        if (window.waterLevelChart) {
            window.waterLevelChart.destroy();
        }
        
        window.waterLevelChart = new Chart(ctx, {
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
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
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
                        title: {
                            display: true,
                            text: 'Datum & Zeit'
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Pegelstand (cm)'
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
        
        console.log("✅ Chart erfolgreich erstellt");
        this.showSuccessMessage();
    },
    
    // Keine Daten Nachricht
    showNoDataMessage() {
        const chartContainer = document.getElementById('chartPreview');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center p-8">
                    <i class="fas fa-chart-line text-4xl text-gray-400 mb-4"></i>
                    <h3 class="text-lg font-medium text-gray-700 mb-2">Keine Daten verfügbar</h3>
                    <p class="text-gray-500 mb-4">Laden Sie zuerst EHYD-Daten für Steyr, um eine Chart-Vorschau zu sehen.</p>
                    <button onclick="ehydFetcher.loadEHYDData()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">
                        <i class="fas fa-download mr-2"></i>EHYD-Daten laden
                    </button>
                </div>
            `;
        }
    },
    
    // Fehler Nachricht
    showErrorMessage() {
        const chartContainer = document.getElementById('chartPreview');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center p-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                    <h3 class="text-lg font-medium text-gray-700 mb-2">Fehler beim Laden</h3>
                    <p class="text-gray-500">Es gab einen Fehler beim Laden der Chart-Daten.</p>
                </div>
            `;
        }
    },
    
    // Erfolg Nachricht
    showSuccessMessage() {
        // Erfolg-Benachrichtigung anzeigen
        if (typeof showNotification === 'function') {
            showNotification('Chart-Vorschau erfolgreich geladen!', 'success');
        }
    }
};

// Globale Funktion für Chart-Vorschau
function showChartPreview() {
    ChartPreview.showChartPreview();
} 