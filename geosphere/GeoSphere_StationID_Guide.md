# GeoSphere – Stations-ID finden und für BESS/Wind-Simulation nutzen
Diese Anleitung erklärt, wie du die **Stations-ID (station_ids)** der GeoSphere Austria API findest und in deiner **Phoenyra BESS Simulation** verwendest.  
Optimiert für **Cursor AI**, Python-Module, n8n und BESS-Workflows.

---

# 1. Warum benötigst du die Stations-ID?
GeoSphere liefert Messdaten (Wind, Temperatur, Strahlung, etc.) pro Messstation.  
Jede Station hat eine eindeutige ID, z. B.:

- Wien Hohe Warte → `11035`
- Linz Hörsching → `11010`
- Innsbruck Flughafen → `11320`

Die ID wird im API-Request verwendet:

```
&station_ids=11035
```

---

# 2. Methode A – Stations-ID über den Metadata-Endpunkt bekommen
Jeder GeoSphere-Datensatz hat einen **metadata**‑Endpunkt.

Beispiel für 10‑Minuten‑Daten (TAWES):

```
https://dataset.api.hub.geosphere.at/v1/station/historical/tawes-v1-10min/metadata
```

Antwort enthält u. a.:

```json
{
  "stations": [
    {
      "id": "11035",
      "name": "Wien/Hohe Warte",
      "altitude": 203,
      "geometry": {...}
    },
    {
      "id": "11010",
      "name": "Linz/Hörsching"
    }
  ]
}
```

→ Perfekt geeignet für automatisches Scraping im Python‑Script.

---

# 3. Methode B – Alle Datensätze durchsuchen (API Docs)
Du findest alle GeoSphere‑Datensätze inkl. Stationen hier:

```
https://dataset.api.hub.geosphere.at/v1/docs
```

Dort steht:
- Liste aller Datensätze  
- Link zum jeweiligen Metadata-Endpunkt  
- Parameterbeschreibung (z. B. FF = Windgeschwindigkeit)  

---

# 4. Methode C – Stationsvorfilterung nach Namen (Python)
Falls du z. B. „Linz“ suchst:

```python
import requests

url = "https://dataset.api.hub.geosphere.at/v1/station/historical/tawes-v1-10min/metadata"
meta = requests.get(url).json()

stations = meta["stations"]
for s in stations:
    if "Linz" in s["name"]:
        print(s)
```

Ergebnis:
```json
{
  "id": "11010",
  "name": "Linz/Hörsching"
}
```

---

# 5. Methode D – Stationssuche nach Koordinaten
Wenn du Standort (PV, Windrad, BESS) als Koordinaten hast:

```python
target_lat = 48.306
target_lon = 14.286

def dist(s):
    lat = s["geometry"]["coordinates"][1]
    lon = s["geometry"]["coordinates"][0]
    return ((lat - target_lat)**2 + (lon - target_lon)**2)**0.5

nearest = sorted(meta["stations"], key=dist)[:5]

print(nearest)
```

Damit findest du die **nächste Messstation** zu deinem Projektstandort.

---

# 6. Beispiel: Vollständiger GeoSphere API‑Request
Für Winddaten der Station *Wien Hohe Warte (11035)*:

```
https://dataset.api.hub.geosphere.at/v1/station/historical/tawes-v1-10min
  ?parameters=FF
  &station_ids=11035
  &start=2024-01-01T00:00:00Z
  &end=2024-12-31T23:50:00Z
  &format=csv
```

`FF` = Mittelwindgeschwindigkeit in m/s.

---

# 7. Integration in Cursor AI – Config für Wind-Engine

Konfigurationsdatei `config_wind_geosphere.json`:

```json
{
  "geosphere": {
    "base_url": "https://dataset.api.hub.geosphere.at/v1",
    "resource_id": "tawes-v1-10min",
    "station_id": "11035",
    "parameters": ["FF"],
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T23:50:00Z"
  }
}
```

Diese ID wird direkt in der Python-Windengine genutzt.

---

# 8. Integration in n8n

**HTTP Request Node → GET**

```
URL:
https://dataset.api.hub.geosphere.at/v1/station/historical/tawes-v1-10min

Query Params:
parameters: FF
station_ids: 11010
start: 2024-01-01T00:00:00Z
end: 2024-12-31T23:50:00Z
format: csv
```

Weiterverarbeiten mit:
- Spreadsheet Node
- Function Node (Hubhöhe, Power Curve)
- Merge Node (mit PV/Last/BESS)

---

# 9. Häufig verwendete Stations-IDs (Österreich)
| Ort | ID |
|-----|----|
| Wien Hohe Warte | 11035 |
| Linz Hörsching | 11010 |
| Graz Flughafen | 11301 |
| Innsbruck Flughafen | 11320 |
| Salzburg Flughafen | 11310 |
| Klagenfurt Flughafen | 11240 |
| Bregenz | 11810 |

---

# 10. Empfehlung für Phoenyra BESS Studio UI
Für maximale Benutzerfreundlichkeit:
- Dropdown „Beliebte Stationen“ (Top 20)  
- Freie Eingabe der Station-ID  
- Automatische Stationssuche via Koordinaten  
- Prüffunktion „Station verfügbar?“  

Damit ist die Windintegration clean & professionell.

---

# 11. Fazit
Die Stations-ID erhältst du über:
1. `metadata` Endpunkt  
2. API-Dokumentation  
3. Name filtern  
4. Koordinaten vergleichen  

Diese Anleitung ist 100 % Cursor‑kompatibel und optimiert für deine BESS Wind-Engine.

Fertig!
