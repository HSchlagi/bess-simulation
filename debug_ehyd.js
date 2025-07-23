// Debug-Skript für EHYD-Integration
// In der Browser-Konsole ausführen

console.log("🔍 Debug EHYD-Integration...");

// Test 1: Elemente finden
console.log("📋 Test 1: Elemente finden");
const hydroProjectSelect = document.getElementById('hydroProjectSelect');
const hydroProfileName = document.getElementById('hydroProfileName');
const riverSelect = document.getElementById('riverSelect');
const loadEHYDButton = document.getElementById('loadEHYDButton');

console.log("hydroProjectSelect:", hydroProjectSelect);
console.log("hydroProfileName:", hydroProfileName);
console.log("riverSelect:", riverSelect);
console.log("loadEHYDButton:", loadEHYDButton);

// Test 2: Werte prüfen
console.log("📋 Test 2: Werte prüfen");
if (hydroProjectSelect) console.log("Projekt-ID:", hydroProjectSelect.value);
if (hydroProfileName) console.log("Profilname:", hydroProfileName.value);
if (riverSelect) console.log("Fluss:", riverSelect.value);

// Test 3: EHYD-Fetcher prüfen
console.log("📋 Test 3: EHYD-Fetcher prüfen");
console.log("ehydFetcher:", typeof ehydFetcher);
if (typeof ehydFetcher !== 'undefined') {
    console.log("ehydFetcher.rivers:", ehydFetcher.rivers);
    console.log("ehydFetcher.selectedRiver:", ehydFetcher.selectedRiver);
    console.log("ehydFetcher.selectedStations:", ehydFetcher.selectedStations);
}

// Test 4: API-Test
console.log("📋 Test 4: API-Test");
fetch('/api/ehyd/rivers')
    .then(response => response.json())
    .then(data => {
        console.log("API Rivers Response:", data);
        if (data.success && data.rivers.steyr) {
            console.log("✅ Steyr gefunden in API");
        } else {
            console.log("❌ Steyr nicht gefunden in API");
        }
    })
    .catch(error => {
        console.error("❌ API-Fehler:", error);
    });

// Test 5: Event-Listener prüfen
console.log("📋 Test 5: Event-Listener prüfen");
if (loadEHYDButton) {
    console.log("loadEHYDButton onclick:", loadEHYDButton.onclick);
    console.log("loadEHYDButton event listeners:", loadEHYDButton._listeners);
}

console.log("🔍 Debug abgeschlossen!"); 