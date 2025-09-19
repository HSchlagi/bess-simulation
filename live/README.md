# BESS Live Integration (SQLite Edition)
MQTT (Mosquitto) → FastAPI (Ingestion) → **SQLite** (`/data/bess.db`)

## Inhalt
- `docker-compose.yml` — startet **mosquitto** und **app**
- `mosquitto/` — `mosquitto.conf`, `create_user.sh`, Ordner für TLS
- `app/` — `main.py` (FastAPI), `Dockerfile`, `requirements.txt`, `.env.example`
- `examples/` — `mqtt_sample_publisher.py`, `n8n_mqtt_to_http.json`
- `data/` — Persistenzordner für `bess.db` (wird automatisch angelegt)

## Quickstart
```bash
# 1) ENV anlegen
cp app/.env.example app/.env
# API_TOKEN ggf. ändern, DB_FILE belassen (/data/bess.db)

# 2) Mosquitto-User anlegen (Passwort wird abgefragt)
docker compose run --rm mosquitto sh /mosquitto/config/create_user.sh bessuser

# 3) Stack starten
docker compose up -d

# 4) Test: MQTT Publish (lokal)
python3 examples/mqtt_sample_publisher.py

# 5) Prüfen (per HTTP)
curl -H "Authorization: Bearer changeme_token_123" http://localhost:8080/healthz
curl -H "Authorization: Bearer changeme_token_123" http://localhost:8080/api/last?limit=3
```

## Sicherheit
- Produktion: **8883/TLS** aktivieren (Zertifikate in `mosquitto/certs/` ablegen, siehe `mosquitto.conf`).
- Ingestion verlangt **Bearer Token** im Header.
- Nur Telemetrie (kein Write-Back).

## Datenmodell (Minimal)
```json
{
  "ts":"2025-01-01T00:00:00Z",
  "site":"site1",
  "device":"bess1",
  "soc":57.1,
  "p":-120.0,
  "p_ch":0.0,
  "p_dis":120.0,
  "v_dc":780.5,
  "i_dc":160.2,
  "t_cell_max":31.5,
  "soh":98.6,
  "alarms":[]
}
```
