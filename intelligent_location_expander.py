#!/usr/bin/env python3
"""
Intelligente Standort-Erweiterung für PVGIS
Erweitert die Standort-Datenbank basierend auf Projektauswahl und PVGIS-Verfügbarkeit
"""

import sqlite3
import requests
import json
from typing import Dict, List, Optional
from pvgis_data_fetcher import PVGISDataFetcher

class IntelligentLocationExpander:
    def __init__(self, db_path: str = "instance/bess.db"):
        self.db_path = db_path
        self.fetcher = PVGISDataFetcher(db_path)
        
        # Intelligente Standort-Vorschläge basierend auf Regionen
        self.region_suggestions = {
            "Oberösterreich": [
                {"name": "Vöcklabruck", "lat": 48.0047, "lon": 13.6567, "altitude": 433},
                {"name": "Ried im Innkreis", "lat": 48.2106, "lon": 13.4897, "altitude": 433},
                {"name": "Schärding", "lat": 48.4567, "lon": 13.4347, "altitude": 313},
                {"name": "Freistadt", "lat": 48.5111, "lon": 14.5047, "altitude": 560},
                {"name": "Rohrbach", "lat": 48.5722, "lon": 13.9947, "altitude": 605}
            ],
            "Salzburg": [
                {"name": "Hallein", "lat": 47.6833, "lon": 13.1000, "altitude": 447},
                {"name": "Saalfelden", "lat": 47.4267, "lon": 12.8489, "altitude": 744},
                {"name": "Bischofshofen", "lat": 47.4167, "lon": 13.2167, "altitude": 544},
                {"name": "St. Johann im Pongau", "lat": 47.3500, "lon": 13.2000, "altitude": 565}
            ],
            "Steiermark": [
                {"name": "Leoben", "lat": 47.3833, "lon": 15.1000, "altitude": 541},
                {"name": "Bruck an der Mur", "lat": 47.4167, "lon": 15.2667, "altitude": 468},
                {"name": "Judenburg", "lat": 47.1667, "lon": 14.6667, "altitude": 737},
                {"name": "Mürzzuschlag", "lat": 47.6000, "lon": 15.6833, "altitude": 670}
            ],
            "Kärnten": [
                {"name": "Spittal an der Drau", "lat": 46.8000, "lon": 13.5000, "altitude": 560},
                {"name": "Wolfsberg", "lat": 46.8333, "lon": 14.8333, "altitude": 463},
                {"name": "Feldkirchen", "lat": 46.7167, "lon": 14.1000, "altitude": 554},
                {"name": "St. Veit an der Glan", "lat": 46.7667, "lon": 14.3667, "altitude": 482}
            ],
            "Tirol": [
                {"name": "Kitzbühel", "lat": 47.4500, "lon": 12.3833, "altitude": 762},
                {"name": "Lienz", "lat": 46.8333, "lon": 12.7667, "altitude": 673},
                {"name": "Schwaz", "lat": 47.3500, "lon": 11.7000, "altitude": 545},
                {"name": "Wörgl", "lat": 47.4833, "lon": 12.0667, "altitude": 511}
            ]
        }
    
    def get_project_locations(self, project_id: int) -> List[Dict]:
        """Ermittelt Standorte basierend auf Projekt-ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Projekt-Details abrufen
            cursor.execute("SELECT name, location FROM project WHERE id = ?", (project_id,))
            project = cursor.fetchone()
            
            if not project:
                return []
            
            project_name, project_location = project
            
            # Basierend auf Projekt-Location intelligente Vorschläge
            suggestions = []
            
            # Oberösterreich-Projekte
            if "oberösterreich" in project_location.lower() or "linz" in project_location.lower():
                suggestions.extend(self.region_suggestions["Oberösterreich"])
            
            # Salzburg-Projekte
            elif "salzburg" in project_location.lower():
                suggestions.extend(self.region_suggestions["Salzburg"])
            
            # Steiermark-Projekte
            elif "steiermark" in project_location.lower() or "graz" in project_location.lower():
                suggestions.extend(self.region_suggestions["Steiermark"])
            
            # Kärnten-Projekte
            elif "kärnten" in project_location.lower() or "klagenfurt" in project_location.lower():
                suggestions.extend(self.region_suggestions["Kärnten"])
            
            # Tirol-Projekte
            elif "tirol" in project_location.lower() or "innsbruck" in project_location.lower():
                suggestions.extend(self.region_suggestions["Tirol"])
            
            # Standard: Alle Regionen
            else:
                for region, locations in self.region_suggestions.items():
                    suggestions.extend(locations[:2])  # Nur die ersten 2 pro Region
            
            conn.close()
            return suggestions
            
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der Projekt-Standorte: {e}")
            return []
    
    def test_pvgis_availability(self, lat: float, lon: float) -> bool:
        """Testet PVGIS-Verfügbarkeit für einen Standort"""
        try:
            # Schneller Test mit minimalen Parametern
            test_url = f"https://re.jrc.ec.europa.eu/api/v5_2/seriescalc?lat={lat}&lon={lon}&startyear=2020&endyear=2020&use_horizon=1&hourly=1&outputformat=csv&peakpower=1.0&loss=14.0&angle=35&aspect=0"
            
            response = requests.get(test_url, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"⚠️ PVGIS-Test fehlgeschlagen für {lat}, {lon}: {e}")
            return False
    
    def expand_locations_for_project(self, project_id: int) -> Dict:
        """Erweitert Standorte für ein spezifisches Projekt"""
        try:
            print(f"🔄 Erweitere Standorte für Projekt {project_id}...")
            
            # Projekt-Standorte ermitteln
            suggestions = self.get_project_locations(project_id)
            
            if not suggestions:
                return {"success": False, "error": "Keine Standort-Vorschläge gefunden"}
            
            # PVGIS-Verfügbarkeit testen
            available_locations = []
            for suggestion in suggestions:
                if self.test_pvgis_availability(suggestion["lat"], suggestion["lon"]):
                    available_locations.append(suggestion)
                    print(f"✅ {suggestion['name']} verfügbar")
                else:
                    print(f"❌ {suggestion['name']} nicht verfügbar")
            
            # Neue Standorte zur Datenbank hinzufügen
            added_count = 0
            for location in available_locations[:5]:  # Maximal 5 neue Standorte
                key = location["name"].lower().replace(" ", "_").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
                
                success = self.fetcher.add_custom_location(
                    key=key,
                    name=location["name"],
                    lat=location["lat"],
                    lon=location["lon"],
                    altitude=location["altitude"],
                    description=f"Intelligent hinzugefügt für Projekt {project_id}"
                )
                
                if success:
                    added_count += 1
                    print(f"✅ {location['name']} zur Datenbank hinzugefügt")
            
            return {
                "success": True,
                "project_id": project_id,
                "suggestions_count": len(suggestions),
                "available_count": len(available_locations),
                "added_count": added_count,
                "new_locations": available_locations[:added_count]
            }
            
        except Exception as e:
            print(f"❌ Fehler bei Standort-Erweiterung: {e}")
            return {"success": False, "error": str(e)}
    
    def get_expanded_locations(self) -> Dict:
        """Gibt alle verfügbaren Standorte zurück (inkl. erweiterte)"""
        try:
            return self.fetcher.get_available_locations()
        except Exception as e:
            print(f"❌ Fehler beim Abrufen der erweiterten Standorte: {e}")
            return {}

def main():
    """Test-Funktion"""
    expander = IntelligentLocationExpander()
    
    # Test für Projekt 1 (Hinterstoder)
    result = expander.expand_locations_for_project(1)
    print(f"Erweiterungsergebnis: {result}")
    
    # Alle Standorte anzeigen
    locations = expander.get_expanded_locations()
    print(f"Verfügbare Standorte: {len(locations)}")

if __name__ == "__main__":
    main() 